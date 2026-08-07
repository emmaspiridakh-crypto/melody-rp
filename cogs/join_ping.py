"""
cogs/join_ping.py
-------------------
Σύστημα "silent ping" όταν μπαίνει κάποιος στο server:
    1. Στέλνει ένα μήνυμα στο ρυθμισμένο channel που κάνει tag τον νέο χρήστη
       (και προαιρετικά έναν ρόλο/"name" μαζί, αν έχει οριστεί).
    2. Διαγράφει το μήνυμα ΑΜΕΣΩΣ μετά την αποστολή.
       (Σκοπός: να χτυπήσει notification/ping ήχος χωρίς να μείνει ορατό μήνυμα.)

Ρύθμιση από Ownership:
    /setchannel channel:<#κανάλι> ping_role:<@ρόλος (προαιρετικό)>

Persistence: αποθηκεύεται στο storage (data/join_ping.json ή Turso) ανά guild,
ώστε να μην χαθεί σε redeploy/restart.
"""

from __future__ import annotations

import discord
from discord import app_commands
from discord.ext import commands

from utils import storage
from utils.permissions import slash_is_ownership_only

STORE_NAME = "join_ping"  # data/join_ping.json


class JoinPing(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    # ---------------------------------------------------
    # /setchannel - ρυθμίζει το channel (+ προαιρετικό role) για το join ping
    # ---------------------------------------------------
    @app_commands.command(name="setchannel", description="Ορίζει το κανάλι (και προαιρετικά ρόλο) για το ping όταν μπαίνει νέο μέλος")
    @app_commands.describe(
        channel="Το κανάλι όπου θα γίνεται το tag του νέου μέλους",
        ping_role="Προαιρετικό ρόλος που θα κάνει tag μαζί με το μέλος (π.χ. @Members)",
    )
    @slash_is_ownership_only()
    async def setchannel(
        self,
        interaction: discord.Interaction,
        channel: discord.TextChannel,
        ping_role: discord.Role | None = None,
    ):
        store = storage.get_store(STORE_NAME)
        store[str(interaction.guild_id)] = {
            "channel_id": channel.id,
            "ping_role_id": ping_role.id if ping_role else None,
        }
        storage.save(STORE_NAME, store)

        msg = f"✅ Το join-ping ρυθμίστηκε: κανάλι {channel.mention}"
        if ping_role:
            msg += f", με tag του ρόλου {ping_role.mention}"
        await interaction.response.send_message(msg, ephemeral=True)

    # ---------------------------------------------------
    # on_member_join - το ίδιο το ping-and-delete σύστημα
    # ---------------------------------------------------
    @commands.Cog.listener()
    async def on_member_join(self, member: discord.Member):
        store = storage.get_store(STORE_NAME)
        info = store.get(str(member.guild.id))
        if not info:
            return

        channel = member.guild.get_channel(info["channel_id"])
        if channel is None:
            return

        content = member.mention
        role_id = info.get("ping_role_id")
        if role_id:
            role = member.guild.get_role(role_id)
            if role:
                content += f" {role.mention}"

        try:
            sent = await channel.send(content)
            await sent.delete()
        except discord.Forbidden:
            pass

    # ---------------------------------------------------
    # Error handling
    # ---------------------------------------------------
    @setchannel.error
    async def setchannel_error(self, interaction: discord.Interaction, error):
        if isinstance(error, app_commands.CheckFailure):
            await interaction.response.send_message("⛔ Δεν έχεις δικαίωμα να χρησιμοποιήσεις αυτή την εντολή.", ephemeral=True)


async def setup(bot: commands.Bot):
    await bot.add_cog(JoinPing(bot))
