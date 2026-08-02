"""
cogs/temp_voice.py
---------------------
Requirement #6: Όποιος μπει στο "Join to Create" channel, παίρνει το δικό του
temp voice channel. Διαγράφεται μόλις αδειάσει.

ΣΗΜΕΙΩΣΗ: Το ping στο STAFF_PING_CHANNEL_ID αφαιρέθηκε από εδώ — αυτό το
channel το χρησιμοποιεί πλέον αποκλειστικά το Support Voice notify
(cogs/support_voice.py) όταν μπαίνει κάποιος στο Support voice channel.
Η δημιουργία/διαγραφή του temp channel συνεχίζει να δουλεύει κανονικά,
απλά χωρίς μήνυμα ping.
"""

from __future__ import annotations

import discord
from discord.ext import commands

import config

# channel_id -> owner_id (in-memory· αν restart το bot ενώ υπάρχουν ανοιχτά temp
# channels, θα παραμείνουν "ορφανά" μέχρι να αδειάσουν - δεν είναι πρόβλημα γιατί
# έτσι κι αλλιώς αδειάζουν μόνα τους).
active_temp_channels: dict[int, int] = {}


class TempVoice(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_voice_state_update(self, member: discord.Member, before: discord.VoiceState, after: discord.VoiceState):
        guild = member.guild

        # --- Join to Create ---
        if after.channel and after.channel.id == config.TEMP_VOICE_JOIN_CHANNEL_ID:
            category = guild.get_channel(config.TEMP_VOICE_CATEGORY_ID)
            new_channel = await guild.create_voice_channel(
                name=f"🔊 {member.display_name}", category=category,
            )
            await new_channel.set_permissions(member, manage_channels=True, connect=True, speak=True)
            await member.move_to(new_channel)
            active_temp_channels[new_channel.id] = member.id

        # --- Διαγραφή temp channel όταν αδειάσει ---
        if before.channel and before.channel.id in active_temp_channels:
            if len(before.channel.members) == 0:
                channel_id = before.channel.id
                try:
                    await before.channel.delete(reason="Temp voice channel άδειο")
                except discord.NotFound:
                    pass
                active_temp_channels.pop(channel_id, None)


async def setup(bot: commands.Bot):
    await bot.add_cog(TempVoice(bot))
