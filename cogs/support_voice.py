"""
cogs/support_voice.py
------------------------
Requirement: όταν κάποιος μπαίνει στο Support voice channel (config.SUPPORT_VOICE_CHANNEL_ID),
στέλνεται ένα Components V2 "Notifier" panel — ίδιο στυλ με αυτό των tickets
(bell τίτλος, "i - User Details :", Username / Mention / ID / Ping / Time,
όλα με custom emoji) — στο config.SUPPORT_VOICE_NOTIFIER_CHANNEL_ID, με ping
στον ρόλο config.SUPPORT_VOICE_PING_ROLE_ID.

Το panel έχει επιπλέον ένα κουμπί "🔎 Scan Timeouts" που ανοίγει (ephemeral)
το ίδιο panel με το /scan-timeouts (cogs/timeout_tools.py) — μόνο για
Manager/Ownership.
"""

from __future__ import annotations

import discord
from discord import ui
from discord.ext import commands

import config
from emojis import emoji
from utils.components import build_notifier_container
from utils.permissions import has_roles

from cogs.timeout_tools import build_scan_timeouts_embed

SCAN_BUTTON_CUSTOM_ID = "support_voice_scan_timeouts"


class SupportVoice(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    # ---------------------------------------------------
    # Notifier panel (Components V2) με το κουμπί scan
    # ---------------------------------------------------
    def _build_view(self, member: discord.Member, ping_role: discord.Role | None) -> ui.LayoutView:
        ping_value = ping_role.mention if ping_role else "—"

        fields = [
            (emoji("notifier", "hash"), "Username", f"`{member.name}`"),
            (emoji("notifier", "hash"), "Mention", member.mention),
            (emoji("notifier", "person"), "ID", f"`{member.id}`"),
            (emoji("notifier", "bell"), "Ping", ping_value),
            (emoji("notifier", "clock"), "Time", discord.utils.format_dt(discord.utils.utcnow(), style="F")),
        ]
        container = build_notifier_container(
            title="Notifier",
            intro="**i - User Details :**",
            fields=fields,
        )
        container.add_item(ui.Separator(spacing=discord.SeparatorSpacing.small))

        row = ui.ActionRow()
        row.add_item(ui.Button(
            style=discord.ButtonStyle.secondary,
            label="Scan Timeouts",
            emoji=emoji("panel", "scan"),
            custom_id=SCAN_BUTTON_CUSTOM_ID,
        ))
        container.add_item(row)

        view = ui.LayoutView(timeout=None)
        view.add_item(container)
        return view

    # ---------------------------------------------------
    # Voice join detection
    # ---------------------------------------------------
    @commands.Cog.listener()
    async def on_voice_state_update(self, member: discord.Member, before: discord.VoiceState, after: discord.VoiceState):
        if member.bot:
            return
        if before.channel and before.channel.id == config.SUPPORT_VOICE_CHANNEL_ID:
            return  # ήταν ήδη μέσα -> δεν είναι νέο join (π.χ. mute/unmute)
        if not after.channel or after.channel.id != config.SUPPORT_VOICE_CHANNEL_ID:
            return

        guild = member.guild
        notify_channel = guild.get_channel(config.SUPPORT_VOICE_NOTIFIER_CHANNEL_ID)
        if not notify_channel:
            return

        ping_role = guild.get_role(config.SUPPORT_VOICE_PING_ROLE_ID)
        view = self._build_view(member, ping_role)

        try:
            await notify_channel.send(
                content=ping_role.mention if ping_role else None,
                view=view,
                allowed_mentions=discord.AllowedMentions(roles=True),
            )
        except discord.HTTPException:
            pass

    # ---------------------------------------------------
    # Κεντρικός interaction listener (persistent components)
    # ---------------------------------------------------
    @commands.Cog.listener()
    async def on_interaction(self, interaction: discord.Interaction):
        if interaction.type != discord.InteractionType.component:
            return
        if interaction.data.get("custom_id") != SCAN_BUTTON_CUSTOM_ID:
            return

        if not has_roles(interaction.user, [config.MANAGER_ROLE_ID, config.OWNERSHIP_ROLE_ID]):
            await interaction.response.send_message(
                "Μόνο Manager/Ownership κάνει scan timeouts.", ephemeral=True,
            )
            return

        await interaction.response.defer(ephemeral=True, thinking=True)
        embed = build_scan_timeouts_embed(interaction.guild)
        await interaction.followup.send(embed=embed, ephemeral=True)


async def setup(bot: commands.Bot):
    await bot.add_cog(SupportVoice(bot))
