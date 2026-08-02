"""
cogs/support_voice.py
------------------------
Requirement: όταν κάποιος μπαίνει στο Support voice channel
(config.SUPPORT_VOICE_CHANNEL_ID), γίνεται ένα απλό text notify στο
config.SUPPORT_VOICE_NOTIFIER_CHANNEL_ID — ΙΔΙΑ λογική με το temp_voice.py
(cogs/temp_voice.py), απλό μήνυμα με emoji + mention, όχι Components V2 panel.

Ενεργοποιείται ΜΟΝΟ όταν κάποιος μπαίνει στο πραγματικό Support voice
channel — όχι στο "Join to Create" temp-voice channel (αυτό παραμένει
ξεχωριστό στο cogs/temp_voice.py, με το δικό του STAFF_PING_CHANNEL_ID).

Το scan των timeouts είναι ξεχωριστό command: /scan-timeouts
(cogs/timeout_tools.py), Manager/Ownership only.
"""

from __future__ import annotations

import discord
from discord.ext import commands

import config
from emojis import emoji


class SupportVoice(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    # ---------------------------------------------------
    # Voice join detection — ΜΟΝΟ Support voice channel
    # ---------------------------------------------------
    @commands.Cog.listener()
    async def on_voice_state_update(self, member: discord.Member, before: discord.VoiceState, after: discord.VoiceState):
        if member.bot:
            return
        if before.channel and before.channel.id == config.SUPPORT_VOICE_CHANNEL_ID:
            return  # ήταν ήδη μέσα -> δεν είναι νέο join (π.χ. mute/unmute)
        if not after.channel or after.channel.id != config.SUPPORT_VOICE_CHANNEL_ID:
            return  # μπήκε σε ΑΛΛΟ voice channel -> δεν μας αφορά

        guild = member.guild
        notify_channel = guild.get_channel(config.SUPPORT_VOICE_NOTIFIER_CHANNEL_ID)
        if not notify_channel:
            return

        ping_role = guild.get_role(config.SUPPORT_VOICE_PING_ROLE_ID)
        ping_text = ping_role.mention if ping_role else ""

        try:
            await notify_channel.send(
                f"{emoji('voice', 'support_join')} {ping_text} Ο {member.mention} μπήκε στο Support voice.",
                allowed_mentions=discord.AllowedMentions(roles=True),
            )
        except discord.HTTPException:
            pass


async def setup(bot: commands.Bot):
    await bot.add_cog(SupportVoice(bot))
