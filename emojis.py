"""
emojis.py
---------
Custom emojis χωρισμένα ανά κατηγορία.

ΠΩΣ ΤΟ ΣΥΜΠΛΗΡΩΝΕΙΣ:
- Static emoji:   "<:name:ID>"
- Animated emoji: "<a:name:ID>"   (πρόσεξε το "a" πριν τα δύο κόλον)

Το "name" δεν χρειάζεται να ταιριάζει 100% με το πραγματικό όνομα του emoji,
αλλά καλό είναι να το αφήσεις ίδιο για ευκολία. Το μόνο που μετράει στην
εμφάνιση είναι το σωστό ID.

Χρήση μέσα στον κώδικα:
    from emojis import emoji
    emoji("tickets", "close")
"""

EMOJIS = {
    "tickets": {
        "ownership": "<:ownership:>",
        "report": "<a:report:>",
        "support": "<a:support:>",
        "bug": "<:bug:>",
        "anticheat": "<:anticheat:>",
        "close": "<:close:>",
        "ping": "<a:ping:>",
        "ticket": "<:ticket:>",
        "reward": "<:reward:>",  # PLACEHOLDER: βάλε custom emoji αν θες
    },
    "jobs": {
        "civilian": "<:civilian:>",
        "criminal": "<a:criminal:>",
    },
    "donate": {
        "donate": "<a:donate:>",  # παράδειγμα animated
    },
    "suggestions": {
        "upvote": "<:upvote:>",
        "downvote": "<:downvote:>",
    },
    "moderation": {
        "ban": "<a:ban:>",
        "unban": "<a:unban:>",
        "kick": "<a:kick:>",
        "timeout": "<a:timeout:>",
        "untimeout": "<a:untimeout:>",
        "clear": "<:clear:>",
    },
    "voice": {
        "join": "<a:voice_join:>",
        "leave": "<a:voice_leave:>",
        "temp": "<a:temp_voice:>",
    },
    "staff_activity": {
        "on_duty": "<a:on_duty:>",
        "off_duty": "<a:off_duty:>",
        "leaderboard": "<:leaderboard:>",
    },
    "applications": {
        "elas": "<:elas:>",
        "ekab": "<:ekab:>",
        "staff": "<:staff:>",
        "limeniko": "<:limeniko:>",
        "fbi":     "<:fbi:>",
        "manager": "<:manager:>",
        "accept": "<:accept:>",
        "deny": "<:deny:>",
        "apply": "<:apply:>",
        "send": "<:send:>",
        "yes": "<:app_yes:>",  
        "no": "<:app_no:>",    
        "ping_staff": "<a:ping_staff:>",
    },
    "panel": {
        "list": "<:list:>",
    },
"giveaway": {
    "giveaway":      "<a:giveaway:>",
    "join":          "<:gw_join:>",
    "leave":         "<:gw_leave:>",
    "info":          "<:gw_info:>",
    "edit":          "<:gw_edit:>",
    "reroll":        "<:gw_reroll:>",
    "end":           "<a:gw_end:>",
    "participants":  "<:gw_participants:>",
    "winner":        "<:gw_winner:>",
    "prize":         "<a:gw_prize:>",
    "host":          "<:gw_host:>",
    "winners_count": "<a:gw_winners:>",
    "entries":       "<:gw_entries:>",
    "time":          "<a:gw_time:>",
    "id":            "<:gw_id:>",
    "role":          "<:gw_role:>",
    "add_member":    "<:gw_add_member:>",  # PLACEHOLDER: βάλε custom emoji ID
    },
    "invites": {
        "invites":  "<:invites:>",   # PLACEHOLDER: βάλε custom emoji ID
        "joined":   "<:inv_joined:>",  # PLACEHOLDER
        "left":     "<:inv_left:>",    # PLACEHOLDER
        "leaderboard": "<:inv_board:>",  # PLACEHOLDER
    },
    "game": {
        "connect": "<a:game_connect:>",  # PLACEHOLDER: βάλε custom emoji ID
        "status":  "<a:game_status:>",  # PLACEHOLDER
    },
}


def emoji(category: str, name: str) -> str:
    """Επιστρέφει το emoji string. Αν δεν βρεθεί, επιστρέφει κενό string (δεν σκάει το bot)."""
    try:
        return EMOJIS[category][name]
    except KeyError:
        return ""
