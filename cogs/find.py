from __future__ import annotations

import datetime

import discord
from discord import app_commands
from discord.ext import commands

import config
from utils import storage, activity_log
from utils.permissions import slash_is_ownership_only

RESULTS_PER_PAGE = 6

CATEGORY_CHOICES = [
    app_commands.Choice(name="Όλα", value="all"),
    app_commands.Choice(name="Logs (Join/Leave/Ρόλοι/Channels/Μηνύματα/Voice)", value="logs"),
    app_commands.Choice(name="Moderation (Ban/Kick/Timeout/DM)", value="moderation"),
    app_commands.Choice(name="Warnings", value="warnings"),
    app_commands.Choice(name="Applications", value="applications"),
    app_commands.Choice(name="Tickets", value="tickets"),
]

LOG_CATEGORY_LABELS = {
    "join_leave": "Join/Leave",
    "roles": "Ρόλοι",
    "channels": "Channels",
    "messages": "Μηνύματα",
    "voice": "Voice",
    "moderation": "Moderation",
}


def _fmt_ts(ts: float) -> str:
    dt = datetime.datetime.fromtimestamp(ts, tz=datetime.timezone.utc)
    return discord.utils.format_dt(dt, style="R")


def _build_results(guild: discord.Guild, user: discord.User, category: str) -> list[str]:
    lines: list[str] = []

    want_logs = category in ("all", "logs")
    want_mod = category in ("all", "moderation")
    want_warn = category in ("all", "warnings")
    want_apps = category in ("all", "applications")
    want_tickets = category in ("all", "tickets")

    if want_logs or want_mod:
        entries = activity_log.search(guild.id, user.id)
        for e in entries:
            cat = e.get("category")
            if cat == "moderation" and not want_mod:
                continue
            if cat != "moderation" and not want_logs:
                continue
            label = LOG_CATEGORY_LABELS.get(cat, cat)
            mod_id = e.get("moderator_id")
            who = f" (από <@{mod_id}>)" if mod_id and mod_id != user.id else ""
            lines.append(f"`[{label}]` {_fmt_ts(e['timestamp'])} — {e['summary']}{who}")

    if want_warn:
        store = storage.get_store("warnings")
        for w in store.get(str(user.id), []):
            if w.get("guild_id") != guild.id:
                continue
            lines.append(
                f"`[Warning]` {_fmt_ts(w['timestamp'])} — Level {w['level']} από <@{w['moderator_id']}> "
                f"— {w['reason']} (`{w['id']}`)"
            )

    if want_apps:
        store = storage.get_store("applications")
        for ch_id, info in store.items():
            if info.get("user_id") != user.id:
                continue
            atype = config.APPLICATION_TYPES.get(info.get("type"), {}).get("label", info.get("type"))
            status = info.get("status", "pending")
            extra = ""
            if info.get("decided_by"):
                extra = f" — αποφασίστηκε από <@{info['decided_by']}>"
            lines.append(f"`[Application]` {atype} — status: **{status}**{extra} (channel `{ch_id}`)")

    if want_tickets:
        store = storage.get_store("tickets")
        for ch_id, info in store.items():
            if info.get("opener_id") != user.id or info.get("guild_id") != guild.id:
                continue
            lines.append(f"`[Ticket]` type: {info.get('type')} (channel `{ch_id}`)")

    return lines


class ResultsView(discord.ui.View):
    def __init__(self, lines: list[str], user: discord.User, category_label: str):
        super().__init__(timeout=120)
        self.lines = lines
        self.user = user
        self.category_label = category_label
        self.page = 0
        self.max_page = max(0, (len(lines) - 1) // RESULTS_PER_PAGE)
        self._update_buttons()

    def _update_buttons(self):
        self.prev_btn.disabled = self.page <= 0
        self.next_btn.disabled = self.page >= self.max_page

    def build_embed(self) -> discord.Embed:
        start = self.page * RESULTS_PER_PAGE
        chunk = self.lines[start:start + RESULTS_PER_PAGE]
        embed = discord.Embed(
            title=f"🔎 Αναζήτηση: {self.user}",
            description="\n\n".join(chunk) if chunk else "Δεν βρέθηκαν αποτελέσματα.",
            color=config.EMBED_COLOR,
        )
        embed.set_thumbnail(url=self.user.display_avatar.url)
        embed.set_footer(text=f"{self.category_label} • {len(self.lines)} αποτελέσματα • Σελίδα {self.page + 1}/{self.max_page + 1}")
        return embed

    @discord.ui.button(label="◀", style=discord.ButtonStyle.secondary)
    async def prev_btn(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.page = max(0, self.page - 1)
        self._update_buttons()
        await interaction.response.edit_message(embed=self.build_embed(), view=self)

    @discord.ui.button(label="▶", style=discord.ButtonStyle.secondary)
    async def next_btn(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.page = min(self.max_page, self.page + 1)
        self._update_buttons()
        await interaction.response.edit_message(embed=self.build_embed(), view=self)


class Find(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name="find", description="[Ownership] Ψάξε έναν χρήστη σε logs / moderation / warnings / applications / tickets")
    @app_commands.describe(user="Ο χρήστης που θες να ψάξεις", category="Τι είδος δεδομένων θες να βρεις")
    @app_commands.choices(category=CATEGORY_CHOICES)
    @slash_is_ownership_only()
    async def find(self, interaction: discord.Interaction, user: discord.User, category: app_commands.Choice[str]):
        await interaction.response.defer(ephemeral=True)
        lines = _build_results(interaction.guild, user, category.value)
        view = ResultsView(lines, user, category.name)
        await interaction.followup.send(embed=view.build_embed(), view=view if lines else None, ephemeral=True)

    @find.error
    async def find_error(self, interaction: discord.Interaction, error: app_commands.AppCommandError):
        if isinstance(error, app_commands.CheckFailure):
            msg = "Μόνο η Ownership μπορεί να χρησιμοποιήσει αυτή την εντολή."
            if interaction.response.is_done():
                await interaction.followup.send(msg, ephemeral=True)
            else:
                await interaction.response.send_message(msg, ephemeral=True)


async def setup(bot: commands.Bot):
    await bot.add_cog(Find(bot))
