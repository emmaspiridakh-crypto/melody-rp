from __future__ import annotations

import discord
from discord.ext import commands

import config

active_temp_channels: dict[int, int] = {}


class TempVoice(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_voice_state_update(self, member: discord.Member, before: discord.VoiceState, after: discord.VoiceState):
        guild = member.guild

        if after.channel and after.channel.id == config.TEMP_VOICE_JOIN_CHANNEL_ID:
            category = guild.get_channel(config.TEMP_VOICE_CATEGORY_ID)
            new_channel = await guild.create_voice_channel(
                name=f"{member.display_name}", category=category,
            )
            await new_channel.set_permissions(member, manage_channels=True, connect=True, speak=True)
            await member.move_to(new_channel)
            active_temp_channels[new_channel.id] = member.id

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
