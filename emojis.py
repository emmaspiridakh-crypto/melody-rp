
EMOJIS = {
    "tickets": {
        "ownership": "<:ownership:1531999528633241660>",
        "banapeal": "<a:banapeal:1532334999410442350>",
        "support": "<a:support:1532130695433027794>",
        "streamer": "<:streamer:1498769681161388203>",
        "anticheat": "<:anticheat:1532130590885810411>",
        "close": "<:close:1532130509331632359>",
        "ping": "<a:ping:1532130668107005982>",
        "ticket": "<:ticket:1535587061216579724>",
        "reward": "<:reward:1492571665333223607>", 
        "bullet": "<:bullet:1535605416757825646>",  
    },
    "jobs": {
        "civilian": "<:civilian:1532335931099709581>",
        "criminal": "<a:criminal:1497912956053094410>",
    },
    "donate": {
        "donate": "<a:donate:1532336271295250542>", 
    },
    "suggestions": {
        "upvote": "<:upvote:1494068515169370253>",
        "downvote": "<:downvote:1494068533917651125>",
        "suggestion": "<a:suggestion:1498777433753653359>",
        "submitted": "<a:submitted:1492271082336551104>", 
        "bullet": "<:bullet:1535605416757825646>",       
    },
    "moderation": {
        "ban": "<:ban:1532334999410442350>",
        "unban": "<:unban:1532334999410442350>",
        "kick": "<a:kick:1493964242343432193>",
        "timeout": "<:timeout:1532336564049412188>",
        "untimeout": "<:untimeout:1532336564049412188>",
        "clear": "<:clear:1493964254435479673>",
    },
    "voice": {
        "join": "<a:voice_join:1494013796535107584>",
        "leave": "<a:voice_leave:1494013821344415746>",
        "temp": "<a:temp_voice:1532130695433027794>",
        "support_join": "<a:support_voice_join:1532130695433027794>",
    },
    "staff_activity": {
        "on_duty": "<a:on_duty:1494013796535107584>",
        "off_duty": "<a:off_duty:1494013821344415746>",
        "leaderboard": "<:leaderboard:1535586964416495707>",
    },
    "applications": {
        "elas": "<:elas:1535550649910165534>",
        "ekab": "<:ekab:1532337538595946616>",
        "staff": "<:staff:1532337651020075189>",
        "manager": "<:manager:1493964247993028698>",
        "accept": "<:accept:1532337940821315634>",
        "deny": "<:deny:1532130509331632359>",
        "apply": "<:apply:1532338098304712836>",
        "send": "<:send:1532337940821315634>",
        "yes": "<:app_yes:1532337940821315634>",  
        "no": "<:app_no:1532130509331632359>",    
        "ping_staff": "<a:ping_staff:1532130668107005982>",
        "status_open": "<a:status_open:1494013796535107584>",     
        "status_closed": "<a:status_closed:1494013821344415746>",
    },
    "notifier": {
        "bell": "<a:notif_bell:1532130668107005982>",    
        "hash": "<:notif_hash:1533548060175765644>",    
        "person": "<:notif_person:1532335931099709581>",  
        "clock": "<:notif_clock:1532336564049412188>",    
        "check": "<:notif_check:1511631201662799925>",  
    },
    "panel": {
        "list": "<:list:1532338541055709386>",
        "scan": "<:scan:1532341506055709386>", 
    },
"giveaway": {
    "giveaway":      "<:giveaway:1493964674201288965>",
    "join":          "<:gw_join:1532130548351500348>",
    "leave":         "<:gw_leave:1532338786237943960>",
    "info":          "<:gw_info:1532339034095878214>",
    "edit":          "<:gw_edit:1500469927696404501>",
    "reroll":        "<:gw_reroll:1532339177423765544>",
    "end":           "<a:gw_end:1494013821344415746>",
    "participants":  "<:gw_participants:1532335931099709581>",
    "winner":        "<:gw_winner:1498777413037854850>",
    "prize":         "<:gw_prize:1502681777829974239>",
    "host":          "<:gw_host:1504444608900497498>",
    "winners_count": "<:gw_winners:1493689037301612616>",
    "entries":       "<:gw_entries:1494527933535223808>",
    "time":          "<:gw_time:1532336564049412188>",
    "id":            "<:gw_id:1532340120051646554>",
    "role":          "<:gw_role:1532340215585444000>",
    "add_member":    "<:gw_add_member:1532340330261909585>",  
    },
    "invites": {
        "invites":  "<a:invites:1493969765126115439>",  
        "joined":   "<:inv_joined:1532130548351500348>", 
        "left":     "<:inv_left:1532338786237943960>",   
        "leaderboard": "<:inv_board:1532338541055709386>", 
    },
    "game": {
        "connect": "<:game_connect:1493918780114341888>", 
        "status":  "<a:game_status:1498777433753653359>", 
    },
}


def emoji(category: str, name: str) -> str:
    try:
        return EMOJIS[category][name]
    except KeyError:
        return ""
