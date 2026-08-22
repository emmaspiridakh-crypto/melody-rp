from __future__ import annotations

import re

import aiohttp
import discord
from discord import app_commands
from discord.ext import commands

from utils.permissions import member_has_any_role
import config

MAX_EMOJI_BYTES = 256 * 1024

EMOJI_MENTION_RE = re.compile(r"<(a?):([a-zA-Z0-9_]{2,32}):(\d{15,25})>")


def _clean_name(name: str) -> str:
    name = name.strip()
    name = re.sub(r"[^a-zA-Z0-9_]", "_", name)
    name = re.sub(r"_+", "_", name).strip("_")
    return name[:32] if name else "emoji"


def _cdn_emoji_url(emoji_id: str, animated: bool) -> str:
    ext = "gif" if animated else "png"
    return f"https://cdn.discordapp.com/emojis/{emoji_id}.{ext}"


def _extract_pasted_emojis(raw: str) -> list[tuple[str, str]]:
    """Παίρνει το κείμενο που κόλλησε ο χρήστης και επιστρέφει λίστα (όνομα, cdn_url)
    για κάθε emoji άλλου server που βρέθηκε (<:name:id> ή <a:name:id>)."""
    return [
        (name, _cdn_emoji_url(emoji_id, bool(animated_flag)))
        for animated_flag, name, emoji_id in EMOJI_MENTION_RE.findall(raw)
    ]


class EmojiManager(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    async def _fetch_url_bytes(self, session: aiohttp.ClientSession, url: str) -> bytes | None:
        try:
            async with session.get(url) as resp:
                if resp.status != 200:
                    return None
                data = await resp.read()
                if len(data) > MAX_EMOJI_BYTES:
                    return None
                return data
        except Exception:
            return None

    @app_commands.command(
        name="addemoji",
        description="Προσθέτει emoji(s) κολλώντας τα από άλλο server (π.χ. <:name:id>)",
    )
    @app_commands.describe(
        emojis="Κόλλα εδώ emoji από άλλο server (π.χ. <:name:id> ή <a:name:id>) — δέχεται πολλά μαζί",
    )
    async def addemoji(self, interaction: discord.Interaction, emojis: str):
        if not member_has_any_role(interaction.user, [config.OWNERSHIP_ROLE_ID]):
            await interaction.response.send_message(" Μόνο το Ownership μπορεί να προσθέσει emojis.", ephemeral=True)
            return

        if interaction.guild is None:
            await interaction.response.send_message("Αυτή η εντολή δουλεύει μόνο μέσα σε server.", ephemeral=True)
            return

        pasted = _extract_pasted_emojis(emojis)
        if not pasted:
            await interaction.response.send_message(
                "Δεν βρήκα κανένα emoji μέσα σε αυτό που έστειλες. Κόλλα emoji από άλλο server (π.χ. `<:name:id>`).",
                ephemeral=True,
            )
            return

        await interaction.response.defer(ephemeral=True, thinking=True)

        results: list[str] = []
        failed: list[str] = []

        async with aiohttp.ClientSession() as session:
            for default_name, url in pasted:
                emoji_name = _clean_name(default_name)

                image_bytes = await self._fetch_url_bytes(session, url)
                if image_bytes is None:
                    failed.append(f"{emoji_name} (αποτυχία λήψης ή >256KB)")
                    continue

                try:
                    created = await interaction.guild.create_custom_emoji(
                        name=emoji_name,
                        image=image_bytes,
                        reason=f"Προστέθηκε από {interaction.user} μέσω /addemoji",
                    )
                    results.append(str(created))
                except discord.HTTPException as e:
                    failed.append(f"{emoji_name} ({e.text if hasattr(e, 'text') else 'σφάλμα Discord API'})")
                except Exception:
                    failed.append(f"{emoji_name} (άγνωστο σφάλμα)")

        lines = []
        if results:
            lines.append(f"Προστέθηκαν {len(results)} emojis: " + " ".join(results))
        if failed:
            lines.append("Απέτυχαν: " + ", ".join(failed))
        if not lines:
            lines.append("Δεν προστέθηκε κανένα emoji.")

        await interaction.followup.send("\n".join(lines), ephemeral=True)


async def setup(bot: commands.Bot):
    await bot.add_cog(EmojiManager(bot))
