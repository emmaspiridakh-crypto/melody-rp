from __future__ import annotations

import io
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


def _split_list(raw: str | None) -> list[str]:
    if not raw:
        return []
    parts = re.split(r"[\s,]+", raw.strip())
    return [p for p in parts if p]


def _cdn_emoji_url(emoji_id: str, animated: bool) -> str:
    ext = "gif" if animated else "png"
    return f"https://cdn.discordapp.com/emojis/{emoji_id}.{ext}"


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

    def _extract_tokens(self, raw: str | None) -> list[tuple[str, str]]:
        """Παίρνει το raw κείμενο (urls/emojis) και επιστρέφει λίστα (default_name, url).

        Αναγνωρίζει αυτόματα:
        - Επικολλημένα emojis άλλου server: <:name:id> / <a:name:id> -> CDN URL, χωρίς download/upload
        - Απλά image links (png/jpg/gif/webp)
        """
        out: list[tuple[str, str]] = []
        if not raw:
            return out

        remaining = raw

        for m in EMOJI_MENTION_RE.finditer(raw):
            animated_flag, name, emoji_id = m.group(1), m.group(2), m.group(3)
            out.append((name, _cdn_emoji_url(emoji_id, bool(animated_flag))))
            remaining = remaining.replace(m.group(0), " ")

        for token in _split_list(remaining):
            if token.startswith("http://") or token.startswith("https://"):
                guessed = token.rsplit("/", 1)[-1].split("?")[0]
                guessed = guessed.rsplit(".", 1)[0] if "." in guessed else guessed
                out.append((guessed or "emoji", token))

        return out

    @app_commands.command(name="addemoji", description="Προσθέτει emojis (static/animated) — links, attachments, ή κόλλα emoji από άλλο server")
    @app_commands.describe(
        names="Ονόματα για τα emojis, χωρισμένα με κόμμα/κενό (προαιρετικό — αλλιώς κρατάει το αρχικό όνομα)",
        emojis="Κόλλα εδώ emoji από άλλο server (π.χ. <:name:id> ή <a:name:id>) — δέχεται πολλά μαζί",
        urls="Links εικόνων χωρισμένα με κενό ή νέα γραμμή",
        attachment1="Εικόνα emoji (png/jpg/gif)",
        attachment2="Εικόνα emoji (png/jpg/gif)",
        attachment3="Εικόνα emoji (png/jpg/gif)",
        attachment4="Εικόνα emoji (png/jpg/gif)",
        attachment5="Εικόνα emoji (png/jpg/gif)",
    )
    async def addemoji(
        self,
        interaction: discord.Interaction,
        names: str | None = None,
        emojis: str | None = None,
        urls: str | None = None,
        attachment1: discord.Attachment | None = None,
        attachment2: discord.Attachment | None = None,
        attachment3: discord.Attachment | None = None,
        attachment4: discord.Attachment | None = None,
        attachment5: discord.Attachment | None = None,
    ):
        if not member_has_any_role(interaction.user, [config.OWNERSHIP_ROLE_ID]):
            await interaction.response.send_message(" Μόνο το Ownership μπορεί να προσθέσει emojis.", ephemeral=True)
            return

        if interaction.guild is None:
            await interaction.response.send_message("Αυτή η εντολή δουλεύει μόνο μέσα σε server.", ephemeral=True)
            return

        attachments = [a for a in (attachment1, attachment2, attachment3, attachment4, attachment5) if a is not None]

        raw_sources: list[tuple[str, bytes | str]] = []
        for att in attachments:
            raw_sources.append((att.filename.rsplit(".", 1)[0], att))

        raw_sources.extend(self._extract_tokens(emojis))
        raw_sources.extend(self._extract_tokens(urls))

        if not raw_sources:
            await interaction.response.send_message(
                "Πρέπει να δώσεις τουλάχιστον ένα attachment, ένα link, ή να κολλήσεις ένα emoji (`<:name:id>`).",
                ephemeral=True,
            )
            return

        await interaction.response.defer(ephemeral=True, thinking=True)

        given_names = _split_list(names)

        results: list[str] = []
        failed: list[str] = []

        async with aiohttp.ClientSession() as session:
            for i, (default_name, source) in enumerate(raw_sources):
                emoji_name = _clean_name(given_names[i]) if i < len(given_names) else _clean_name(default_name)

                if isinstance(source, discord.Attachment):
                    if source.size and source.size > MAX_EMOJI_BYTES:
                        failed.append(f"{emoji_name} (πολύ μεγάλο αρχείο, max 256KB)")
                        continue
                    try:
                        image_bytes = await source.read()
                    except Exception:
                        failed.append(f"{emoji_name} (αποτυχία λήψης attachment)")
                        continue
                else:
                    image_bytes = await self._fetch_url_bytes(session, source)
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
