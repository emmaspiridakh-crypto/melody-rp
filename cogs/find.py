from __future__ import annotations

import datetime

import discord
from discord import app_commands
from discord.ext import commands

import config
import emojis
from utils import storage, activity_log
from utils.permissions import slash_is_ownership_only

RESULTS_PER_PAGE = 6

LOG_CATEGORY_LABELS = {
    "join_leave": "Join/Leave",
    "roles": "Ρόλοι",
    "channels": "Channels",
    "messages": "Μηνύματα",
    "voice": "Voice",
}

CATEGORY_META: dict[str, tuple[str, str, int]] = {
    "all": ("Όλα", emojis.emoji("panel", "scan") or "🔎", config.EMBED_COLOR),
    "logs": ("Logs", emojis.emoji("notifier", "clock") or "📜", 0x5865F2),
    "moderation": ("Moderation", emojis.emoji("moderation", "ban") or "🔨", 0xED4245),
    "warnings": ("Warnings", emojis.emoji("notifier", "bell") or "⚠️", 0xFEE75C),
    "applications": ("Applications", emojis.emoji("applications", "apply") or "📝", 0x57F287),
    "whitelist": ("Whitelist", emojis.emoji("whitelist", "accept") or "✅", 0x3BA55D),
    "tickets": ("Tickets", emojis.emoji("tickets", "ticket") or "🎫", 0x9B59B6),
}

CATEGORY_CHOICES = [
    app_commands.Choice(name=f"{meta[1]} {meta[0]}", value=key)
    for key, meta in CATEGORY_META.items()
]


def _fmt_ts(ts: float) -> str:
    dt = datetime.datetime.fromtimestamp(ts, tz=datetime.timezone.utc)
    return discord.utils.format_dt(dt, style="R")


def _gather(guild: discord.Guild, user: discord.User, category: str) -> list[dict]:
    """Επιστρέφει entries: {cat, label, text, ts} ταξινομημένα με τα πιο πρόσφατα πρώτα."""
    entries: list[dict] = []

    want_logs = category in ("all", "logs")
    want_mod = category in ("all", "moderation")
    want_warn = category in ("all", "warnings")
    want_apps = category in ("all", "applications")
    want_wl = category in ("all", "whitelist")
    want_tickets = category in ("all", "tickets")

    if want_logs or want_mod:
        for e in activity_log.search(guild.id, user.id):
            cat = e.get("category")
            if cat == "moderation" and not want_mod:
                continue
            if cat != "moderation" and not want_logs:
                continue
            label = LOG_CATEGORY_LABELS.get(cat, "Moderation" if cat == "moderation" else cat)
            mod_id = e.get("moderator_id")
            who = f" — από <@{mod_id}>" if mod_id and mod_id != user.id else ""
            entries.append({
                "cat": "moderation" if cat == "moderation" else "logs",
                "label": label,
                "text": f"{e['summary']}{who}",
                "ts": e.get("timestamp", 0),
            })

    if want_warn:
        for w in storage.get_store("warnings").get(str(user.id), []):
            if w.get("guild_id") != guild.id:
                continue
            entries.append({
                "cat": "warnings",
                "label": f"Level {w['level']}",
                "text": f"{w['reason']} — από <@{w['moderator_id']}> (`{w['id']}`)",
                "ts": w.get("timestamp", 0),
            })

    if want_apps:
        for ch_id, info in storage.get_store("applications").items():
            if info.get("user_id") != user.id:
                continue
            atype = config.APPLICATION_TYPES.get(info.get("type"), {}).get("label", info.get("type"))
            status = info.get("status", "pending")
            extra = f" — αποφασίστηκε από <@{info['decided_by']}>" if info.get("decided_by") else ""
            entries.append({
                "cat": "applications",
                "label": atype,
                "text": f"status: **{status}**{extra} (channel `{ch_id}`)",
                "ts": 0,
            })

    if want_wl:
        for ch_id, info in storage.get_store("whitelist").items():
            if info.get("user_id") != user.id:
                continue
            status = info.get("status", "pending")
            extra = f" — αποφασίστηκε από <@{info['decided_by']}>" if info.get("decided_by") else ""
            entries.append({
                "cat": "whitelist",
                "label": "Whitelist",
                "text": f"status: **{status}**{extra} (channel `{ch_id}`)",
                "ts": 0,
            })

    if want_tickets:
        for ch_id, info in storage.get_store("tickets").items():
            if info.get("opener_id") != user.id or info.get("guild_id") != guild.id:
                continue
            entries.append({
                "cat": "tickets",
                "label": info.get("type", "ticket"),
                "text": f"channel `{ch_id}`",
                "ts": 0,
            })

    entries.sort(key=lambda e: e.get("ts", 0), reverse=True)
    return entries


class CategorySelect(discord.ui.Select):
    def __init__(self, current: str):
        options = [
            discord.SelectOption(label=meta[0], value=key, emoji=meta[1], default=(key == current))
            for key, meta in CATEGORY_META.items()
        ]
        super().__init__(placeholder="Άλλαξε κατηγορία...", options=options, row=0)

    async def callback(self, interaction: discord.Interaction):
        view: ResultsView = self.view
        view.category = self.values[0]
        view.entries = _gather(interaction.guild, view.user, view.category)
        view.page = 0
        view._sync()
        await interaction.response.edit_message(embed=view.build_embed(), view=view)


class ResultsView(discord.ui.View):
    def __init__(self, guild: discord.Guild, user: discord.User, category: str):
        super().__init__(timeout=180)
        self.guild = guild
        self.user = user
        self.category = category
        self.entries = _gather(guild, user, category)
        self.page = 0
        self.select = CategorySelect(category)
        self.add_item(self.select)
        self._sync()

    @property
    def max_page(self) -> int:
        return max(0, (len(self.entries) - 1) // RESULTS_PER_PAGE)

    def _sync(self):
        self.select.options = [
            discord.SelectOption(label=meta[0], value=key, emoji=meta[1], default=(key == self.category))
            for key, meta in CATEGORY_META.items()
        ]
        self.prev_btn.disabled = self.page <= 0
        self.next_btn.disabled = self.page >= self.max_page

    def build_embed(self) -> discord.Embed:
        label, icon, color = CATEGORY_META[self.category]
        start = self.page * RESULTS_PER_PAGE
        chunk = self.entries[start:start + RESULTS_PER_PAGE]

        embed = discord.Embed(
            title=f"{icon} Αναζήτηση — {self.user}",
            color=color,
        )
        embed.set_thumbnail(url=self.user.display_avatar.url)
        embed.add_field(name="Χρήστης", value=f"{self.user.mention} (`{self.user.id}`)", inline=False)

        if not chunk:
            embed.description = "Δεν βρέθηκαν αποτελέσματα."
        else:
            for e in chunk:
                cat_icon = CATEGORY_META.get(e["cat"], ("", "•", 0))[1]
                when = _fmt_ts(e["ts"]) if e.get("ts") else "—"
                embed.add_field(
                    name=f"{cat_icon} {e['label']} • {when}",
                    value=e["text"][:1000] or "—",
                    inline=False,
                )

        embed.set_footer(text=f"{label} • {len(self.entries)} αποτελέσματα • Σελίδα {self.page + 1}/{self.max_page + 1}")
        return embed

    @discord.ui.button(label="◀", style=discord.ButtonStyle.secondary, row=1)
    async def prev_btn(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.page = max(0, self.page - 1)
        self._sync()
        await interaction.response.edit_message(embed=self.build_embed(), view=self)

    @discord.ui.button(label="▶", style=discord.ButtonStyle.secondary, row=1)
    async def next_btn(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.page = min(self.max_page, self.page + 1)
        self._sync()
        await interaction.response.edit_message(embed=self.build_embed(), view=self)


class Find(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name="find", description="[Ownership] Ψάξε έναν χρήστη σε logs / moderation / warnings / applications / whitelist / tickets")
    @app_commands.describe(user="Ο χρήστης που θες να ψάξεις", category="Τι είδος δεδομένων θες να βρεις")
    @app_commands.choices(category=CATEGORY_CHOICES)
    @slash_is_ownership_only()
    async def find(self, interaction: discord.Interaction, user: discord.User, category: app_commands.Choice[str] = None):
        await interaction.response.defer(ephemeral=True)
        cat_value = category.value if category else "all"
        view = ResultsView(interaction.guild, user, cat_value)
        await interaction.followup.send(embed=view.build_embed(), view=view, ephemeral=True)

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
