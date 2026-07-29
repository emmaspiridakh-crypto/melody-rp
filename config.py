"""
config.py
---------
ΟΛΑ τα IDs του server μπαίνουν εδώ. Κάθε placeholder λέει ΤΙ ΑΚΡΙΒΩΣ πρέπει να βάλεις.
Βάλε τα IDs σαν integers (χωρίς εισαγωγικά), π.χ. OWNERSHIP_ROLE_ID = 123456789012345678

Tip: Discord Developer Mode -> Right click role/channel/category -> Copy ID
"""

import os
from dotenv import load_dotenv

load_dotenv()

# =========================================================
# BOT TOKEN (μπαίνει στο .env locally, ή Environment Variable στο Render)
# =========================================================
TOKEN = os.getenv("DISCORD_TOKEN")

GUILD_ID = 1489977148725788722   # PLACEHOLDER: το ID του server σου
PREFIX = "!"

# =========================================================
# ROLES
# =========================================================
OWNERSHIP_ROLE_ID        = 1532024309202026496 # PLACEHOLDER
MANAGER_ROLE_ID          = 1531987866228363315 # PLACEHOLDER
STAFF_ROLE_ID            = 1531262921278099569# PLACEHOLDER
DEVELOPER_ROLE_ID        = 1531987093461667921 # PLACEHOLDER
CIVILIAN_MANAGER_ROLE_ID = 1530985516499992776  # PLACEHOLDER
CRIMINAL_MANAGER_ROLE_ID = 1530985516499992776  # PLACEHOLDER
DONATE_MANAGER_ROLE_ID   = 1532035699375608039  # PLACEHOLDER
FOUNDER_ROLE_ID          = 1530985002148433930  # PLACEHOLDER
ON_DUTY_ROLE_ID          = 1532038134278389991
ANTICHEAT_MANAGER_ID = 1532038774215676075# PLACEHOLDER
APPLICATION_ACCEPTED_ROLES = {
    "staff": 1532038506887643267  , 
    "manager": 1532038506887643267 ,  
}
AUTOROLE_ID = 1530986809914425514 # PLACEHOLDER (μπαίνει σε accepted applicants)

# Ρόλοι που θεωρούνται "staff team" γενικά (χρησιμοποιείται σε αρκετά permission checks)
STAFF_TEAM_ROLE_IDS = [STAFF_ROLE_ID, MANAGER_ROLE_ID, OWNERSHIP_ROLE_ID]

# =========================================================
# TICKET SYSTEM #1 - SUPPORT (dropdown, 4 κατηγορίες, ξεχωριστό category η κάθε μία)
# =========================================================
TICKET_SUPPORT_CHANNEL_ID = 1530982949942595683  # PLACEHOLDER: πού θα σταλεί το panel (slash command target)
TICKET_SUPPORT_BANNER_URL = "https://i.imgur.com/1QO13J1.jpeg"
TICKET_SUPPORT_THUMBNAIL_URL = "https://i.imgur.com/pXVPwRN.gif"

CAT_TICKET_OWNERSHIP_ID = 1531299362620047621 
CAT_TICKET_BANAPEAL_ID  = 1531299110219419678  
CAT_TICKET_SUPPORT_ID   = 1532020980380209173 
CAT_TICKET_STREAMER_ID  = 1531298299204599818
CAT_TICKET_ANTICHEAT_ID = 1532056211917377607
CAT_TICKET_REWARD_ID    = 1532052105005760533

# =========================================================
# TICKET SYSTEM #2 - JOBS (button, civilian + criminal, ΙΔΙΟ category και τα δύο)
# =========================================================
CAT_JOBS_ID = 1532054279328763965  # PLACEHOLDER (ΚΟΙΝΟ category civilian + criminal)

TICKET_JOBS_BANNER_URL = "https://i.imgur.com/NtKATej.jpeg"
TICKET_JOBS_THUMBNAIL_URL = "https://i.imgur.com/pXVPwRN.gif"

# =========================================================
# TICKET SYSTEM #3 - DONATE (button, δικό του category)
# =========================================================
CAT_DONATE_ID = 1532021724680425654 # PLACEHOLDER category

TICKET_DONATE_BANNER_URL = "https://i.imgur.com/IFArJVp.jpeg"
TICKET_DONATE_THUMBNAIL_URL = "https://i.imgur.com/pXVPwRN.gif"

# Channel όπου γίνεται ping το staff team όταν ανοίγει ΟΠΟΙΟΔΗΠΟΤΕ ticket (support/jobs/donate) ή temp voice
STAFF_PING_CHANNEL_ID = 1532059202636349630  # PLACEHOLDER

# Ticket logs (open + close) - ΞΕΧΩΡΙΣΤΟ από το STAFF_PING_CHANNEL_ID
LOG_TICKETS_CHANNEL_ID = 1531009060285976796    # PLACEHOLDER

# =========================================================
# SUGGESTIONS
# =========================================================
SUGGESTIONS_CHANNEL_ID = 1531099169790365778    # PLACEHOLDER (εδώ ο χρήστης γράφει -> γίνεται auto suggestion)

# =========================================================
# TEMP VOICE
# =========================================================
TEMP_VOICE_JOIN_CHANNEL_ID = 1531290031086370838    # PLACEHOLDER ("Join to Create" channel)
TEMP_VOICE_CATEGORY_ID     = 1532060398017052773   # PLACEHOLDER (εκεί δημιουργούνται τα temp channels)

# =========================================================
# STAFF ACTIVITY
# =========================================================
STAFF_ACTIVITY_VOICE_CHANNEL_ID_1 = 1492565367057551430
STAFF_ACTIVITY_VOICE_CHANNEL_ID_2 = 1492565369905221672 # PLACEHOLDER (το channel που μετράμε χρόνο)
STAFF_ACTIVITY_PANEL_CHANNEL_ID_3 = 1532001359111520428 # PLACEHOLDER (πού στέλνεται/μένει το leaderboard panel)
STAFF_ACTIVITY_LOG_CHANNEL_ID   = 1532061200991653888 # PLACEHOLDER
STAFF_ACTIVITY_BANNER_URL = "http://i.imgur.com/uYFW8Nl.png"

# =========================================================
# LOGS (Requirement 8)
# =========================================================
LOG_JOIN_LEAVE_CHANNEL_ID = 1531004433314611302 # PLACEHOLDER (join + leave μαζί)
LOG_ROLES_CHANNEL_ID      = 1531005010479943720  # PLACEHOLDER
LOG_CHANNELS_CHANNEL_ID   = 1531005065639235765 # PLACEHOLDER (create/delete/edit channels)
LOG_MESSAGES_CHANNEL_ID   = 1531004775976669336 # PLACEHOLDER (edit/delete messages)
LOG_VOICE_CHANNEL_ID      = 1531004826207391844 # PLACEHOLDER
LOG_APPLICATIONS_CHANNEL_ID = 1532032702931533864     # PLACEHOLDER (fallback + shared staff/manager channel)

# Ξεχωριστό channel ανά τύπο αίτησης όταν στέλνεται (Send) — ΕΚΤΟΣ από staff/manager
# που πάνε μαζί στο ΙΔΙΟ channel (LOG_APPLICATIONS_CHANNEL_ID).
# Βάλε το δικό σου channel ID για κάθε τύπο.
LOG_APPLICATIONS_CHANNEL_IDS = {
    "elas":  1532032751962947875   ,  # PLACEHOLDER: βάλε το channel ΕΛ.ΑΣ
    "ekab":  1532032818186813683   ,  # PLACEHOLDER: βάλε το channel ΕΚΑΒ
    "staff": 1532032702931533864   ,   # staff + manager πάνε ΜΑΖΙ εδώ
    "manager": 1532032702931533864 ,   # staff + manager πάνε ΜΑΖΙ εδώ
}

# Invite logs: ποιος προσκάλεσε ποιον, πόσα invites/μέλη μέσα/έχουν φύγει ανά inviter
INVITE_LOG_CHANNEL_ID = 1532067024573042910   # PLACEHOLDER

# Command logs (Requirement 5) - ξεχωριστό log ανά εντολή, εκτός say/say2/dmall (κοινό)
LOG_BAN_CHANNEL_ID          = 1532021145606291609 # PLACEHOLDER
LOG_UNBAN_CHANNEL_ID        = 1532021145606291609# PLACEHOLDER
LOG_KICK_CHANNEL_ID         = 1532021231434334219  # PLACEHOLDER
LOG_TIMEOUT_CHANNEL_ID      = 1532021202518802552  # PLACEHOLDER
LOG_UNTIMEOUT_CHANNEL_ID    = 1532021202518802552# PLACEHOLDER
LOG_CLEARMESSAGES_CHANNEL_ID = 1531004387068219614 # PLACEHOLDER
LOG_SAY_DMALL_CHANNEL_ID    = 1531004387068219614 # PLACEHOLDER (say, say2, dmall μαζί)

# =========================================================
# APPLICATIONS (Requirement 9)
# =========================================================
APPLICATIONS_PANEL_CHANNEL_ID =  1531096531740921877  # PLACEHOLDER (πού στέλνεται το panel)
APPLICATIONS_CATEGORY_ID      = 1532021430085222480 # PLACEHOLDER (εκεί ανοίγουν τα application channels)
APPLICATIONS_BANNER_URL = "https://i.imgur.com/C3BNhK5.jpeg"

LOG_GIVEAWAY_CHANNEL_ID = 1532021275017347142   # PLACEHOLDER
GIVEAWAY_BANNER_URL = "http://i.imgur.com/uYFW8Nl.png"  # PLACEHOLDER (banner στο giveaway panel)

# =========================================================
# WARNING SYSTEM
# =========================================================
LOG_WARN_CHANNEL_ID = 1532021307426865182
WARN_ANNOUNCE_CHANNEL_ID = 1530999884487069836 # PLACEHOLDER (logs για /warn και /remove-warning)

# Ρόλος που παίρνει ο χρήστης ανάλογα με το επίπεδο του warning
WARN_ROLE_1_ID = 1530990052069474395  # PLACEHOLDER
WARN_ROLE_2_ID = 1532067601692233818  # PLACEHOLDER
WARN_ROLE_3_ID = 1532067803950092449 # PLACEHOLDER

# Τύποι αιτήσεων -> ερωτήσεις. Βάλε τις ερωτήσεις σου εδώ (μία λίστα string ανά τύπο).
APPLICATION_TYPES = {
    "elas": {
        "label": "ΕΛ.ΑΣ",
        "questions": [
            "Πόσο χρονών είστε;",
            "Ποιο είναι το Roblox Name σας;",
            "Έχετε εμπειρία σαν Αστυνομικός σε άλλη πόλη ? (Αν ναι. Σε ποια πόλη και μέχρι τι θέση)?.",
            "Το ονοματεπώνυμο σας (RP)?.",
            "Πόσες ώρες θα μπορείτε να διαθέτετε καθημερινά σαν Αστυνομικός?.",
            "Γιατί θέλετε να ενταχθείτε στο σώμα της Ελληνικής Αστυνομίας?.",
            "Γιατί θέλετε να ενταχθείτε στο σώμα της Ελληνικής Αστυνομίας?.",
            "Έχετε ποινικό μητρώο στην ΕΛ.ΑΣ? (in game).",
            "Πείτε μας μερικά από τα αρνητικά χαρακτηριστικά σας.",
            "Εάν έχετε έναν αντιδραστικό πολίτη στα κελιά πως θα τον ηρεμήσετε?.",
            "Καθώς είσαι σε περιπολία, βλέπεις δυο πολίτες να παλεύουν στο πεζοδρόμιο. Αφού τους περάσεις χειροπέδες, σου δίνουν και οι δύο την ίδια κατάθεση: πως ήταν σε άμυνα, και πως ο άλλος το άρχισε. Πώς χειρίζεσαι την κατάσταση?.",
            "Ανάμεσα σε 2 ζωές την δικιά σας και ενός πολίτη, ποία ζωή θα έπρεπε να διασφαλιστεί πρώτη και γιατί?.",
            "Ποιος πιστεύετε πως είναι ο ρόλος του διαπραγματευτή?.",
            "Είστε σε σκηνικό ομηρίας ενός πολίτη και ένας ανώτερος σας σας λέει να ανοίξετε πυρ ενώ εσείς ξέρετε πως είναι λάθος και μπορεί να είναι μοιραίο. Πως θα πράξετε στην προκειμένη περίπτωση?.",
            "Ένα βαν με φιμέ τζάμια είναι παρκαρισμένο έξω από ένα σπίτι στο οποίο επιβαίνουν 4 άτομα. Παρατηρείς ένα άτομο με full face να βγαίνει από το αμάξι και να κρατάει ένα Uzi. Σύντομα, ο ύποπτος επιστρέφει στο βαν και φεύγει με μεγάλη ταχύτητα. Πώς χειρίζεσαι την κατάσταση?.",
            "Ποιο είναι το πρώτο όπλο ενός αστυνομικού?",
            "Κάνεις ένα μαύρο όχημα traffic stop πες μου τις κινήσεις σου και τα λόγια σου?.",
            "Είσαι σε ληστεία και κάνεις την διαπραγμάτευση και ο ανώτερος σου λέει να πυροβολήσεις εκείνη την στιγμή τι θα έκανες?.",
            "Τι λέει το άρθρο 361",
            "Έχετε να προσθέσετε κάτι άλλο"
        ],
    },
    "ekab": {
        "label": "ΕΚΑΒ",
        "questions": [
            "Πόσο χρονών είστε;",
            "Ποιο είναι το Roblox Name σας;",
            "Ποιο είναι το πραγματικό όνομα σας;",
            "Γιατί θέλεις να μπεις στο ΕΚΑΒ",
            "Έχεις εμπειρία από ιατρικούς ρόλους σε άλλους RP servers",
            "Τι σε κάνει κατάλληλο άτομο για διασώστη",
            "Πώς θα χειριζόσουν έναν τραυματία που δεν συνεργάζεται",
            "Πώς αντιμετωπίζεις παίκτη που κάνει failRP σε ιατρική σκηνή",
            "Πώς θα αντιδρούσες σε σοβαρό τροχαίο με πολλούς τραυματίες",
            "Τι θεωρείς ως σωστό ιατρικό RP",
            "Πώς θα χειριζόσουν παίκτη που σε βρίζει ενώ προσπαθείς να τον βοηθήσεις",
            "Τι θα έκανες αν δεις συνάδελφο να κάνει λάθος ή να παραβιάζει κανόνες",
            "Ποιος είναι ο ρόλος του ΕΚΑΒ μέσα στο RP",
        ],
    },
    "staff": {
        "label": "Staff",
        "questions": [
            "Πόσο χρονόν εισαι;",
            "Πως σε λένε στο Roblox;",
            {"type": "yesno", "text": "Ξέρεις ότι θα πρέπει να γράψεις την αίτηση σου στα ελληνικά και όχι greeklish αλλιώς θα απορριφθεί;"},
            {"type": "yesno", "text": "Ξέρεις ότι άμα στείλεις κάποιο προσωπικό μήνυμα σε κάποιον ανώτερο θα απορριφθεί κατευθείαν η αίτηση σου"},
            "Πόσες ώρες θα μπορείς να είσαι on duty;",
            "Είστε διατεθειμένος/η να μειώσετε ώρες από το rp σας για της ανάγκες του staff™;",
            "Έχετε τυχών γνώσεις στα staff commands;",
            "Έχετε ξανά δουλέψει σαν staff; Και αν ναι σε ποιους servers;",
            "Τι σημαίνει ιεραρχία;",
            "Αν κάποιος κάνει livestream και κάνει report ποιος θα πάει;"
        ],
    },
    "manager": {
        "label": "Manager",
        "questions": [
            "Πόσο χρονών είστε;",
            "Ποιο είναι το Roblox Name σας;",
            {"type": "yesno", "text": "Ξέρεις ότι θα πρέπει να γράψεις την αίτηση σου στα ελληνικά και όχι greeklish αλλιώς θα απορριφθεί;"},
            {"type": "yesno", "text": "Ξέρεις ότι άμα στείλεις κάποιο προσωπικό μήνυμα σε κάποιον ανώτερο θα απορριφθεί κατευθείαν η αίτηση σου"},
            "Ένα πράγμα που θα άλλαζες στη δομή του server & γιατί",
            "Πώς αξιολογείς αν ένας staff αξίζει προαγωγή;",
            "Πρέπει να υποβιβάσεις φίλο σου — θα το κάνεις; Πώς;",
            "Server χάνει active players — διαδικασία διάγνωσης;",
            "Disagreement με owner πάνω σε απόφασή του — πώς το χειρίζεσαι;",
            "Πώς θα έφτιαχνες staff team από την αρχή αν το τωρινό διαλυόταν εντελώς; Ποια κριτήρια θα κοιτούσες πρώτα;",
            "Ανακαλύπτεις ότι ένας staff πουλάει in-game πλεονεκτήματα για πραγματικά χρήματα εκτός συστήματος του server. Ποια είναι η ακριβής διαδικασία σου βήμα-βήμα;",
            "Πού βλέπεις το server σε 6 μήνες αν γίνεις manager, με συγκεκριμένα, μετρήσιμα ορόσημα;",
            "Ποιο θα ήταν το πρώτο πράγμα που θα έκανες τις πρώτες 48 ώρες στη θέση;",
            "Δύο staff κατηγορούν ο ένας τον άλλον για κλοπή δεδομένων. Πώς το διερευνάς χωρίς να πάρεις προκατειλημμένη θέση;",
            "Πόσες ώρες θα μπορείς να είσαι on;"
        ],
    },
}
# =========================================================
# SERVER STATUS (Requirement 10) - voice channels που λειτουργούν ως "οθόνες"
# =========================================================
STATUS_MEMBERS_CHANNEL_ID = 1531997362728210524  # PLACEHOLDER (π.χ. "👥 Members: 120")
STATUS_ONLINE_CHANNEL_ID  = 1532065088243105822  # PLACEHOLDER
STATUS_BOOSTS_CHANNEL_ID  = 1532065273778278701 # PLACEHOLDER
STATUS_BOTS_CHANNEL_ID    = 1532065388907593788  # PLACEHOLDER

# =========================================================
# GAME STATUS PANEL (Roblox)
# =========================================================
ROBLOX_UNIVERSE_ID = 8011462852   # PLACEHOLDER: universe id του Roblox game
ROBLOX_GAME_URL = f"{ROBLOX_UNIVERSE_ID}"
GAME_PANEL_BANNER_URL = "https://i.imgur.com/1J0C67l.png"  # PLACEHOLDER: banner εικόνα

# =========================================================
# ΓΕΝΙΚΑ
# =========================================================
EMBED_COLOR = FEE75C
