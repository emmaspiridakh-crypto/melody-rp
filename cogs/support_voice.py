"""
cogs/support_voice.py
------------------------
Requirement: όταν κάποιος μπαίνει στο Support voice channel
(config.SUPPORT_VOICE_CHANNEL_ID), στέλνεται ένα Components V2 "Notifier"
panel στο config.SUPPORT_VOICE_NOTIFIER_CHANNEL_ID (= STAFF_PING_CHANNEL_ID):
bell τίτλος, "i - User Details :", Username / Mention / ID / Ping / Time,
όλα με custom emoji — ίδιο στυλ με το reference panel.

Ενεργοποιείται ΜΟΝΟ όταν κάποιος μπαίνει στο πραγματικό Support voice
channel — όχι στο "Join to Create" temp-voice channel (cogs/temp_voice.py
δεν κάνει πια ping εκεί, το ανέλαβε αποκλειστικά αυτό το cog).

Το scan των timeouts είναι ξεχωριστό command: /scan-timeouts
(cogs/timeout_tools.py), Manager/Ownership only — δεν υπάρχει κουμπί εδώ.
"""

from __future__ import annotations

import logging

import discord
from discord import ui
from discord.ext import commands

import config
from emojis import emoji
from utils.components import build_base_container, add_separator, add_text

log = logging.getLogger("support_voice")


class SupportVoice(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    # ---------------------------------------------------
    # Notifier panel (Components V2)
    # ---------------------------------------------------
    def _build_view(self, member: discord.Member, ping_role: discord.Role | None) -> ui.LayoutView:
        ping_value = ping_role.mention if ping_role else "—"

        container = build_base_container(title=f"{emoji('notifier', 'bell')} Notifier")
        add_separator(container)
        add_text(container, "**i - User Details :**")
        add_text(
            container,
            f"{emoji('notifier', 'hash')} **Username:** `{member.name}`\n"
            f"{emoji('notifier', 'hash')} **Mention:** {member.mention}\n"
            f"{emoji('notifier', 'person')} **ID:** `{member.id}`\n"
            f"{emoji('notifier', 'bell')} **Ping:** {ping_value}\n"
            f"{emoji('notifier', 'clock')} **Time:** {discord.utils.format_dt(discord.utils.utcnow(), style='F')}",
        )

        view = ui.LayoutView(timeout=None)
        view.add_item(container)
        return view

    # ---------------------------------------------------
    # Voice join detection — ΜΟΝΟ Support voice channel
    # ---------------------------------------------------
    @commands.Cog.listener()
    async def on_voice_state_update(self, member: discord.Member, before: discord.VoiceState, after: discord.VoiceState):
        if member.bot:
            return

        after_id = after.channel.id if after.channel else None
        log.info(f"[support_voice] voice_state_update: {member} -> after.channel={after_id}")

        if before.channel and before.channel.id == config.SUPPORT_VOICE_CHANNEL_ID:
            return  # ήταν ήδη μέσα -> δεν είναι νέο join (π.χ. mute/unmute)
        if not after.channel or after.channel.id != config.SUPPORT_VOICE_CHANNEL_ID:
            return  # μπήκε σε ΑΛΛΟ voice channel -> δεν μας αφορά

        log.info(f"[support_voice] {member} μπήκε στο SUPPORT_VOICE_CHANNEL_ID={config.SUPPORT_VOICE_CHANNEL_ID}")

        guild = member.guild
        notify_channel = guild.get_channel(config.SUPPORT_VOICE_NOTIFIER_CHANNEL_ID)
        if not notify_channel:
            log.warning(
                f"[support_voice] Δεν βρέθηκε notify_channel με ID={config.SUPPORT_VOICE_NOTIFIER_CHANNEL_ID} "
                f"(guild.get_channel γύρισε None — ή λάθος ID ή το bot δεν το βλέπει)."
            )
            return

        ping_role = guild.get_role(config.SUPPORT_VOICE_PING_ROLE_ID)
        if not ping_role:
            log.warning(f"[support_voice] Δεν βρέθηκε ρόλος με ID={config.SUPPORT_VOICE_PING_ROLE_ID}.")

        view = self._build_view(member, ping_role)

        try:
            await notify_channel.send(
                content=ping_role.mention if ping_role else None,
                view=view,
                allowed_mentions=discord.AllowedMentions(roles=True),
            )
            log.info(f"[support_voice] Στάλθηκε notify στο #{notify_channel} για {member}.")
        except discord.Forbidden:
            log.error(
                f"[support_voice] Forbidden: το bot δεν έχει δικαίωμα να στείλει μήνυμα στο "
                f"#{notify_channel} (channel ID {config.SUPPORT_VOICE_NOTIFIER_CHANNEL_ID})."
            )
        except discord.HTTPException as e:
            log.error(f"[support_voice] HTTPException κατά την αποστολή notify: {e}")


async def setup(bot: commands.Bot):
    await bot.add_cog(SupportVoice(bot))
