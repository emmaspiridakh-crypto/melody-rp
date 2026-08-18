from __future__ import annotations

import datetime

import discord
from discord.ext import commands

import config
from utils import activity_log


def _base_embed(guild: discord.Guild, *, title: str, color: int = config.EMBED_COLOR) -> discord.Embed:
    embed = discord.Embed(title=title, color=color, timestamp=datetime.datetime.now(datetime.timezone.utc))
    if guild.icon:
        embed.set_thumbnail(url=guild.icon.url)
    return embed


async def _send(guild: discord.Guild, channel_id: int, embed: discord.Embed):
    channel = guild.get_channel(channel_id)
    if channel:
        await channel.send(embed=embed)


async def _audit_actor(guild: discord.Guild, action: discord.AuditLogAction, target_id: int) -> discord.Member | None:
    """Ψάχνει στα audit logs ποιος έκανε μια ενέργεια (best effort)."""
    try:
        async for entry in guild.audit_logs(action=action, limit=5):
            if entry.target and getattr(entry.target, "id", None) == target_id:
                return entry.user
    except (discord.Forbidden, discord.NotFound, discord.HTTPException):
        return None
    return None


class LoggingEvents(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_member_join(self, member: discord.Member):
        embed = _base_embed(member.guild, title="📥 Member Join", color=0x57F287)
        embed.add_field(name="Μέλος", value=f"{member.mention} (`{member.id}`)", inline=False)
        embed.add_field(name="Account created", value=discord.utils.format_dt(member.created_at, style="R"), inline=False)
        embed.add_field(name="Ώρα", value=discord.utils.format_dt(datetime.datetime.now(datetime.timezone.utc), style="F"), inline=False)
        await _send(member.guild, config.LOG_JOIN_LEAVE_CHANNEL_ID, embed)
        activity_log.record(member.guild.id, member.id, "join_leave", f"Join: {member} (`{member.id}`)")

    @commands.Cog.listener()
    async def on_member_remove(self, member: discord.Member):
        embed = _base_embed(member.guild, title="📤 Member Leave", color=0xED4245)
        embed.add_field(name="Μέλος", value=f"{member.mention} (`{member.id}`)", inline=False)
        roles = ", ".join(r.mention for r in member.roles if r.name != "@everyone") or "—"
        embed.add_field(name="Είχε ρόλους", value=roles, inline=False)
        embed.add_field(name="Ώρα", value=discord.utils.format_dt(datetime.datetime.now(datetime.timezone.utc), style="F"), inline=False)
        await _send(member.guild, config.LOG_JOIN_LEAVE_CHANNEL_ID, embed)
        activity_log.record(member.guild.id, member.id, "join_leave", f"Leave: {member} (`{member.id}`) — Ρόλοι: {roles}")

    @commands.Cog.listener()
    async def on_member_update(self, before: discord.Member, after: discord.Member):
        if before.roles == after.roles:
            return
        added = [r for r in after.roles if r not in before.roles]
        removed = [r for r in before.roles if r not in after.roles]
        if not added and not removed:
            return

        actor = await _audit_actor(after.guild, discord.AuditLogAction.member_role_update, after.id)
        embed = _base_embed(after.guild, title=" Role Update")
        embed.add_field(name="Μέλος", value=f"{after.mention} (`{after.id}`)", inline=False)
        if added:
            embed.add_field(name="Προστέθηκαν", value=", ".join(r.mention for r in added), inline=False)
        if removed:
            embed.add_field(name="Αφαιρέθηκαν", value=", ".join(r.mention for r in removed), inline=False)
        embed.add_field(name="Από", value=actor.mention if actor else "Άγνωστο (audit log)", inline=False)
        embed.add_field(name="Ώρα", value=discord.utils.format_dt(datetime.datetime.now(datetime.timezone.utc), style="F"), inline=False)
        await _send(after.guild, config.LOG_ROLES_CHANNEL_ID, embed)
        summary = f"Role Update: {after} (`{after.id}`)"
        if added:
            summary += f" | +{', '.join(r.name for r in added)}"
        if removed:
            summary += f" | -{', '.join(r.name for r in removed)}"
        summary += f" | Από: {actor} ({actor.id})" if actor else " | Από: Άγνωστο"
        activity_log.record(after.guild.id, after.id, "roles", summary, moderator_id=actor.id if actor else None)

    @commands.Cog.listener()
    async def on_guild_channel_create(self, channel: discord.abc.GuildChannel):
        actor = await _audit_actor(channel.guild, discord.AuditLogAction.channel_create, channel.id)
        embed = _base_embed(channel.guild, title="➕ Channel Created", color=0x57F287)
        embed.add_field(name="Channel", value=f"{channel.mention if hasattr(channel, 'mention') else channel.name}", inline=False)
        embed.add_field(name="Από", value=actor.mention if actor else "Άγνωστο", inline=False)
        embed.add_field(name="Ώρα", value=discord.utils.format_dt(datetime.datetime.now(datetime.timezone.utc), style="F"), inline=False)
        await _send(channel.guild, config.LOG_CHANNELS_CHANNEL_ID, embed)
        if actor:
            activity_log.record(channel.guild.id, actor.id, "channels", f"Δημιούργησε το #{channel.name} (`{channel.id}`)")

    @commands.Cog.listener()
    async def on_guild_channel_delete(self, channel: discord.abc.GuildChannel):
        actor = await _audit_actor(channel.guild, discord.AuditLogAction.channel_delete, channel.id)
        embed = _base_embed(channel.guild, title="➖ Channel Deleted", color=0xED4245)
        embed.add_field(name="Channel", value=f"#{channel.name}", inline=False)
        embed.add_field(name="Από", value=actor.mention if actor else "Άγνωστο", inline=False)
        embed.add_field(name="Ώρα", value=discord.utils.format_dt(datetime.datetime.now(datetime.timezone.utc), style="F"), inline=False)
        await _send(channel.guild, config.LOG_CHANNELS_CHANNEL_ID, embed)
        if actor:
            activity_log.record(channel.guild.id, actor.id, "channels", f"Διέγραψε το #{channel.name} (`{channel.id}`)")

    @commands.Cog.listener()
    async def on_guild_channel_update(self, before: discord.abc.GuildChannel, after: discord.abc.GuildChannel):
        if before.name == after.name:
            return
        actor = await _audit_actor(after.guild, discord.AuditLogAction.channel_update, after.id)
        embed = _base_embed(after.guild, title=" Channel Updated")
        embed.add_field(name="Πριν", value=before.name, inline=True)
        embed.add_field(name="Μετά", value=after.name, inline=True)
        embed.add_field(name="Από", value=actor.mention if actor else "Άγνωστο", inline=False)
        embed.add_field(name="Ώρα", value=discord.utils.format_dt(datetime.datetime.now(datetime.timezone.utc), style="F"), inline=False)
        await _send(after.guild, config.LOG_CHANNELS_CHANNEL_ID, embed)
        if actor:
            activity_log.record(after.guild.id, actor.id, "channels", f"Μετονόμασε #{before.name} → #{after.name}")

    @commands.Cog.listener()
    async def on_message_delete(self, message: discord.Message):
        if message.author.bot or not message.guild:
            return
        embed = _base_embed(message.guild, title="Message Deleted", color=0xED4245)
        embed.add_field(name="Χρήστης", value=f"{message.author.mention} (`{message.author.id}`)", inline=False)
        embed.add_field(name="Channel", value=message.channel.mention, inline=False)
        embed.add_field(name="Περιεχόμενο", value=(message.content or "*[χωρίς κείμενο / attachment]*")[:1000], inline=False)
        embed.add_field(name="Ώρα", value=discord.utils.format_dt(datetime.datetime.now(datetime.timezone.utc), style="F"), inline=False)
        await _send(message.guild, config.LOG_MESSAGES_CHANNEL_ID, embed)
        activity_log.record(
            message.guild.id, message.author.id, "messages",
            f"Διαγραφή σε {message.channel.mention if hasattr(message.channel, 'mention') else message.channel}: "
            f"{(message.content or '[χωρίς κείμενο]')[:200]}",
            channel_id=message.channel.id,
        )

    @commands.Cog.listener()
    async def on_message_edit(self, before: discord.Message, after: discord.Message):
        if before.author.bot or not before.guild or before.content == after.content:
            return
        embed = _base_embed(before.guild, title="Message Edited")
        embed.add_field(name="Χρήστης", value=f"{before.author.mention} (`{before.author.id}`)", inline=False)
        embed.add_field(name="Channel", value=before.channel.mention, inline=False)
        embed.add_field(name="Πριν", value=(before.content or "—")[:500], inline=False)
        embed.add_field(name="Μετά", value=(after.content or "—")[:500], inline=False)
        embed.add_field(name="Ώρα", value=discord.utils.format_dt(datetime.datetime.now(datetime.timezone.utc), style="F"), inline=False)
        await _send(before.guild, config.LOG_MESSAGES_CHANNEL_ID, embed)
        activity_log.record(
            before.guild.id, before.author.id, "messages",
            f"Επεξεργασία σε {before.channel.mention if hasattr(before.channel, 'mention') else before.channel}: "
            f"'{(before.content or '—')[:100]}' → '{(after.content or '—')[:100]}'",
            channel_id=before.channel.id,
        )

    @commands.Cog.listener()
    async def on_voice_state_update(self, member: discord.Member, before: discord.VoiceState, after: discord.VoiceState):
        if before.channel == after.channel:
            return
        embed = _base_embed(member.guild, title="Voice Update")
        embed.add_field(name="Μέλος", value=f"{member.mention} (`{member.id}`)", inline=False)
        embed.add_field(name="Από", value=before.channel.mention if before.channel else "—", inline=True)
        embed.add_field(name="Σε", value=after.channel.mention if after.channel else "—", inline=True)
        embed.add_field(name="Ώρα", value=discord.utils.format_dt(datetime.datetime.now(datetime.timezone.utc), style="F"), inline=False)
        await _send(member.guild, config.LOG_VOICE_CHANNEL_ID, embed)
        activity_log.record(
            member.guild.id, member.id, "voice",
            f"{before.channel.name if before.channel else '—'} → {after.channel.name if after.channel else '—'}",
        )


async def setup(bot: commands.Bot):
    await bot.add_cog(LoggingEvents(bot))
