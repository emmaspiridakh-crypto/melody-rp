from __future__ import annotations

import datetime
import uuid

import discord
from discord import ui, app_commands
from discord.ext import commands

import config
from utils import storage

STORE_NAME = "blacklist"


def _get_blacklist_entries(user_id: int, guild_id: int) -> list[dict]:
    store = storage.get_store(STORE_NAME)
    return [b for b in store.get(str(user_id), []) if b.get("guild_id") == guild_id]


def _is_blacklisted(user_id: int, guild_id: int) -> bool:
    return len(_get_blacklist_entries(user_id, guild_id)) > 0


def _add_blacklist(user_id: int, guild_id: int, *, reason: str, moderator_id: int) -> dict:
    store = storage.get_store(STORE_NAME)
    user_entries = store.setdefault(str(user_id), [])
    record = {
        "id": uuid.uuid4().hex[:8],
        "guild_id": guild_id,
        "reason": reason,
        "moderator_id": moderator_id,
        "timestamp": datetime.datetime.now(datetime.timezone.utc).timestamp(),
    }
    user_entries.append(record)
    storage.save(STORE_NAME, store)
    return record


def _remove_blacklist(user_id: int, guild_id: int, entry_id: str) -> dict | None:
    store = storage.get_store(STORE_NAME)
    user_entries = store.get(str(user_id), [])
    removed = next((b for b in user_entries if b["id"] == entry_id and b.get("guild_id") == guild_id), None)
    if removed:
        user_entries.remove(removed)
        store[str(user_id)] = user_entries
        storage.save(STORE_NAME, store)
    return removed


def _log_embed(guild: discord.Guild, *, title: str, color: int, fields: list[tuple[str, str, bool]]) -> discord.Embed:
    embed = discord.Embed(title=title, color=color, timestamp=datetime.datetime.now(datetime.timezone.utc))
    for name, value, inline in fields:
        embed.add_field(name=name, value=value, inline=inline)
    if guild.icon:
        embed.set_thumbnail(url=guild.icon.url)
    return embed


async def _send_log(guild: discord.Guild, embed: discord.Embed):
    channel = guild.get_channel(config.LOG_BLACKLIST_CHANNEL_ID)
    if channel:
        try:
            await channel.send(embed=embed)
        except discord.HTTPException:
            pass


def _simple_view(text: str, color: discord.Colour) -> ui.LayoutView:
    container = ui.Container(accent_colour=color)
    container.add_item(ui.TextDisplay(text))
    view = ui.LayoutView(timeout=None)
    view.add_item(container)
    return view


class BlacklistReasonModal(ui.Modal, title="Λόγος Blacklist"):
    reason = ui.TextInput(
        label="Reason", style=discord.TextStyle.paragraph, max_length=500, required=True,
        placeholder="Γράψε τον λόγο του blacklist...",
    )

    def __init__(self, cog: "Blacklist", target: discord.Member):
        super().__init__()
        self.cog = cog
        self.target = target

    async def on_submit(self, interaction: discord.Interaction):
        await self.cog.finalize_blacklist(interaction, self.target, str(self.reason))


class BlacklistUserSelect(ui.UserSelect):
    def __init__(self, cog: "Blacklist"):
        super().__init__(placeholder="Επίλεξε τον χρήστη που θες να κάνεις blacklist...", min_values=1, max_values=1)
        self.cog = cog

    async def callback(self, interaction: discord.Interaction):
        raw = self.values[0]
        target = interaction.guild.get_member(raw.id)
        if target is None:
            await interaction.response.send_message("Δεν βρέθηκε ο χρήστης στο server.", ephemeral=True)
            return
        if target.bot:
            await interaction.response.send_message("Δεν μπορείς να κάνεις blacklist τα bot βλακα.", ephemeral=True)
            return
        if _is_blacklisted(target.id, interaction.guild.id):
            await interaction.response.send_message(f"Ο {target.mention} είναι ήδη blacklisted.", ephemeral=True)
            return

        await interaction.response.send_modal(BlacklistReasonModal(self.cog, target))


class BlacklistUserSelectView(ui.LayoutView):
    def __init__(self, cog: "Blacklist"):
        super().__init__(timeout=180)
        container = ui.Container(accent_colour=discord.Colour.dark_red())
        container.add_item(ui.TextDisplay("## Blacklist System\nΕπίλεξε τον χρήστη που θέλεις να κάνεις blacklist:"))
        container.add_item(ui.Separator(spacing=discord.SeparatorSpacing.small))
        row = ui.ActionRow()
        row.add_item(BlacklistUserSelect(cog))
        container.add_item(row)
        self.add_item(container)


class RemoveBlacklistSelect(ui.Select):
    def __init__(self, cog: "Blacklist", target: discord.Member, entries: list[dict]):
        options = [
            discord.SelectOption(
                label=f"#{b['id']}",
                value=b["id"],
                description=(b["reason"][:95] if b["reason"] else "—"),
            )
            for b in entries[:25]
        ]
        super().__init__(placeholder="Επίλεξε ποιο blacklist να αφαιρεθεί...", min_values=1, max_values=1, options=options)
        self.cog = cog
        self.target = target

    async def callback(self, interaction: discord.Interaction):
        await self.cog.finalize_remove(interaction, self.target, self.values[0])


class RemoveBlacklistView(ui.LayoutView):
    def __init__(self, cog: "Blacklist", target: discord.Member, entries: list[dict]):
        super().__init__(timeout=180)
        container = ui.Container(accent_colour=discord.Colour.red())
        lines = "\n".join(f"> `#{b['id']}` — {b['reason'][:60]}" for b in entries[:10])
        container.add_item(ui.TextDisplay(
            f"## Remove Blacklist\n**Χρήστης:** {target.mention}\n\n{lines}\n\n"
            f"Επίλεξε ποιο blacklist θέλεις να αφαιρέσεις:"
        ))
        container.add_item(ui.Separator(spacing=discord.SeparatorSpacing.small))
        row = ui.ActionRow()
        row.add_item(RemoveBlacklistSelect(cog, target, entries))
        container.add_item(row)
        self.add_item(container)


class Blacklist(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    async def finalize_blacklist(self, interaction: discord.Interaction, target: discord.Member, reason: str):
        guild = interaction.guild
        moderator = interaction.user

        record = _add_blacklist(target.id, guild.id, reason=reason, moderator_id=moderator.id)

        role_note = ""
        role = guild.get_role(config.BLACKLIST_ROLE_ID)
        if role:
            try:
                await target.add_roles(role, reason=f"Blacklist by {moderator} (#{record['id']})")
                role_note = f"\nΠροστέθηκε ο ρόλος {role.mention}"
            except discord.Forbidden:
                role_note = "\nΔεν προστέθηκε το role (λείπουν permissions)."
        else:
            role_note = "\nΔεν βρέθηκε το blacklist role (έλεγξε το config)."

        await interaction.response.edit_message(view=_simple_view(
            f"## Blacklist Καταγράφτηκε\n"
            f"**Χρήστης:** {target.mention}\n**Reason:** {reason}\n"
            f"**Moderator:** {moderator.mention}{role_note}",
            discord.Colour.green(),
        ))

        try:
            await target.send(f"Μπήκες σε **Blacklist** στον **{guild.name}**.\n**Λόγος:** {reason}")
        except discord.Forbidden:
            pass

        await _send_log(guild, _log_embed(
            guild, title="Member Blacklisted", color=0x992D22,
            fields=[
                ("Χρήστης", f"{target.mention} (`{target.id}`)", False),
                ("Blacklist ID", f"`#{record['id']}`", True),
                ("Moderator", f"{moderator.mention} (`{moderator.id}`)", False),
                ("Reason", reason, False),
            ],
        ))

    async def finalize_remove(self, interaction: discord.Interaction, target: discord.Member, entry_id: str):
        guild = interaction.guild
        removed = _remove_blacklist(target.id, guild.id, entry_id)
        if not removed:
            await interaction.response.edit_message(view=_simple_view(
                "❌ Αυτό το blacklist δεν υπάρχει πια (ίσως αφαιρέθηκε ήδη).", discord.Colour.red(),
            ))
            return

        role_note = ""
        role = guild.get_role(config.BLACKLIST_ROLE_ID)
        if role and role in target.roles and not _is_blacklisted(target.id, guild.id):
            try:
                await target.remove_roles(role, reason=f"Blacklist #{entry_id} removed by {interaction.user}")
                role_note = f"\nΑφαιρέθηκε ο ρόλος {role.mention}"
            except discord.Forbidden:
                role_note = "\nΔεν αφαιρέθηκε το role (λείπουν permissions)."

        await interaction.response.edit_message(view=_simple_view(
            f"## Blacklist Αφαιρέθηκε\n**Χρήστης:** {target.mention}\n**ID:** `#{entry_id}`{role_note}",
            discord.Colour.green(),
        ))

        await _send_log(guild, _log_embed(
            guild, title="Blacklist Removed", color=0x57F287,
            fields=[
                ("Χρήστης", f"{target.mention} (`{target.id}`)", False),
                ("Blacklist ID", f"`#{entry_id}`", True),
                ("Αφαιρέθηκε από", f"{interaction.user.mention} (`{interaction.user.id}`)", False),
            ],
        ))

    @app_commands.command(name="blacklist", description="Ανοίγει το blacklist panel")
    @app_commands.checks.has_any_role(config.OWNERSHIP_ROLE_ID, config.STAFF_MANAGER_ID, config.GENERAL_MANAGER_ID)
    async def blacklist_cmd(self, interaction: discord.Interaction):
        await interaction.response.send_message(view=BlacklistUserSelectView(self), ephemeral=True)

    @app_commands.command(name="remove-blacklist", description="Αφαιρεί έναν χρήστη από το blacklist")
    @app_commands.describe(user="Ο χρήστης που θα αφαιρεθεί από το blacklist")
    @app_commands.checks.has_any_role(config.OWNERSHIP_ROLE_ID, config.STAFF_MANAGER_ID, config.GENERAL_MANAGER_ID)
    async def remove_blacklist_cmd(self, interaction: discord.Interaction, user: discord.Member):
        existing = _get_blacklist_entries(user.id, interaction.guild.id)
        if not existing:
            await interaction.response.send_message(f"Ο {user.mention} δεν είναι blacklisted.", ephemeral=True)
            return
        await interaction.response.send_message(view=RemoveBlacklistView(self, user, existing), ephemeral=True)

    async def cog_app_command_error(self, interaction: discord.Interaction, error: app_commands.AppCommandError):
        if isinstance(error, app_commands.MissingAnyRole):
            msg = "Μόνο οι staff managers, general managers και το ownership μπορούν να χρησιμοποιήσουν αυτή την εντολή."
            if interaction.response.is_done():
                await interaction.followup.send(msg, ephemeral=True)
            else:
                await interaction.response.send_message(msg, ephemeral=True)
        else:
            raise error


async def setup(bot: commands.Bot):
    await bot.add_cog(Blacklist(bot))
