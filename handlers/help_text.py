HELP_SECTIONS = {
    "source": (
        "*Source management*\n\n"
        "`/addsource <chat_id> [name]` — register a source channel\n"
        "`/removesource <chat_id>` — remove a source and its config\n"
        "`/listsources` — list all registered sources\n\n"
        "_Same things are available under the_ Sources _button on /start._"
    ),
    "target": (
        "*Target management*\n\n"
        "`/addtarget <source_id> <target_id>` — add a forward destination\n"
        "`/removetarget <source_id> <target_id>` — remove a destination\n"
        "`/listtargets <source_id>` — list targets for a source"
    ),
    "forward": (
        "*Forward behavior*\n\n"
        "`/setmode <source_id> copy|clean` — copy = forwarded tag shown, clean = no tag\n"
        "`/setfilter <source_id> all|media|text` — restrict what gets forwarded\n"
        "`/addblacklist <source_id> <word>` — skip posts containing this word\n"
        "`/removeblacklist <source_id> <word>` — remove a blacklisted word"
    ),
    "controls": (
        "*Controls*\n\n"
        "`/pause <source_id>` — stop forwarding from this source\n"
        "`/resume <source_id>` — resume forwarding\n"
        "`/stats` — global forward/fail counters"
    ),
    "sudo": (
        "*Sudo management (owner only)*\n\n"
        "`/addsudo <user_id>`\n"
        "`/removesudo <user_id>`\n"
        "`/listsudo`"
    ),
}

HELP_INTRO = (
    "*Auto Forward Bot — Commands*\n\n"
    "Pick a category below, or type any command directly — both work the same way.\n\n"
    "The bot must be *admin* in both source and target chats.\n"
    "Get a chat's ID by forwarding a message from it to @userinfobot or similar."
)

NOT_AUTHORIZED_TEXT = (
    "You're not authorized to use this bot.\n\n"
    "Ask the owner to add you with /addsudo if you should have access."
)

ALL_COMMANDS_TEXT = (
    "*Source*\n"
    "`/addsource <chat_id> [name]`\n"
    "`/removesource <chat_id>`\n"
    "`/listsources`\n\n"
    "*Target*\n"
    "`/addtarget <source_id> <target_id>`\n"
    "`/removetarget <source_id> <target_id>`\n"
    "`/listtargets <source_id>`\n\n"
    "*Forward behavior*\n"
    "`/setmode <source_id> copy|clean`\n"
    "`/setfilter <source_id> all|media|text`\n"
    "`/addblacklist <source_id> <word>`\n"
    "`/removeblacklist <source_id> <word>`\n\n"
    "*Controls*\n"
    "`/pause <source_id>`\n"
    "`/resume <source_id>`\n"
    "`/stats`\n\n"
    "*Sudo (owner only)*\n"
    "`/addsudo <user_id>`\n"
    "`/removesudo <user_id>`\n"
    "`/listsudo`"
)

START_TEXT = (
    "*Auto Forward Bot*\n\n"
    "I forward posts from a source channel to multiple channels/groups automatically.\n"
    "The bot must be *admin* in both source and target chats.\n\n"
    "Use the buttons below, or any command directly:\n\n"
    #f"{ALL_COMMANDS_TEXT}"
)
