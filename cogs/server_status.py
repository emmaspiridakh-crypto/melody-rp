from __future__ import annotations

import asyncio
import discord
from discord.ext import commands, tasks

import config
from emojis import emoji

_last_values: dict[str, str] = {}


def _counts(guild: discord.Guild):
    members = sum(1 for m in guild.members if not m.bot)
    online  = sum(1 for m in guild.members if not m.bot and m.status != discord.Status.offline)
    bots    = sum(1 for m in guild.members if m.bot)
    boosts  = guild.premium_subscription_count or 0
    return members, online, boosts, bots


class ServerStatus(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self._pending: dict[int, asyncio.Task] = {}


    async def update_stats(self, guild: discord.Guild):
        members, online, boosts, bots = _counts(guild)

        targets = {
            "members": (config.STATUS_MEMBERS_CHANNEL_ID, f"{emoji('status','members')} Members: {members}"),
            "online":  (config.STATUS_ONLINE_CHANNEL_ID,  f"{emoji('status','online')} Online: {online}"),
            "boosts":  (config.STATUS_BOOSTS_CHANNEL_ID,  f"{emoji('status','boost')} Boosts: {boosts}"),
            "bots":    (config.STATUS_BOTS_CHANNEL_ID,    f"{emoji('status','bots')} Bots: {bots}"),
        }

        for key, (channel_id, new_name) in targets.items():
            cache_key = f"{guild.id}:{key}"
            if _last_values.get(cache_key) == new_name:
                continue 
            channel = guild.get_channel(channel_id)
            if channel:
                try:
                    await channel.edit(name=new_name)
                    _last_values[cache_key] = new_name
                except discord.HTTPException:
                    pass  

    def _schedule_update(self, guild: discord.Guild):

        existing = self._pending.get(guild.id)
        if existing and not existing.done():
            existing.cancel()

        async def _delayed():
            await asyncio.sleep(1)
            await self.update_stats(guild)
            self._pending.pop(guild.id, None)

        self._pending[guild.id] = asyncio.create_task(_delayed())

    @tasks.loop(minutes=5)
    async def _refresh_loop(self):
        for guild in self.bot.guilds:
            await self.update_stats(guild)

    @_refresh_loop.before_loop
    async def _before_refresh(self):
        await self.bot.wait_until_ready()

    @commands.Cog.listener()
    async def on_ready(self):
        self._refresh_loop.start()
        for guild in self.bot.guilds:
            await self.update_stats(guild)

    @commands.Cog.listener()
    async def on_member_join(self, member: discord.Member):
        self._schedule_update(member.guild)

    @commands.Cog.listener()
    async def on_member_remove(self, member: discord.Member):
        self._schedule_update(member.guild)

    @commands.Cog.listener()
    async def on_presence_update(self, before: discord.Member, after: discord.Member):
        if before.status != after.status:
            self._schedule_update(after.guild)

    @commands.Cog.listener()
    async def on_guild_update(self, before: discord.Guild, after: discord.Guild):
        if before.premium_subscription_count != after.premium_subscription_count:
            self._schedule_update(after)

    @commands.Cog.listener()
    async def on_member_update(self, before: discord.Member, after: discord.Member):
        if before.bot != after.bot:
            self._schedule_update(after.guild)


async def setup(bot: commands.Bot):
    await bot.add_cog(ServerStatus(bot))
