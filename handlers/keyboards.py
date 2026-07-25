from telegram import InlineKeyboardButton, InlineKeyboardMarkup


def main_menu_kb() -> InlineKeyboardMarkup:
    rows = [
        [InlineKeyboardButton("Help", callback_data="menu:help")],
        [
            InlineKeyboardButton("Sources", callback_data="menu:sources"),
            InlineKeyboardButton("Stats", callback_data="menu:stats"),
        ],
        [InlineKeyboardButton("Sudo users", callback_data="menu:sudo")],
    ]
    return InlineKeyboardMarkup(rows)


def help_menu_kb() -> InlineKeyboardMarkup:
    rows = [
        [
            InlineKeyboardButton("Source", callback_data="help:source"),
            InlineKeyboardButton("Target", callback_data="help:target"),
        ],
        [
            InlineKeyboardButton("Forward", callback_data="help:forward"),
            InlineKeyboardButton("Controls", callback_data="help:controls"),
        ],
        [InlineKeyboardButton("Sudo", callback_data="help:sudo")],
        [InlineKeyboardButton("Back", callback_data="menu:main")],
    ]
    return InlineKeyboardMarkup(rows)


def help_section_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([[InlineKeyboardButton("Back to Help", callback_data="menu:help")]])


def sources_list_kb(sources) -> InlineKeyboardMarkup:
    rows = []
    for s in sources:
        status = "" if s.get("active", True) else "[paused] "
        label = f"{status}{s.get('name') or s['_id']}"
        rows.append([InlineKeyboardButton(label, callback_data=f"src:{s['_id']}")])
    rows.append([InlineKeyboardButton("Add Source", callback_data="menu:addsource")])
    rows.append([InlineKeyboardButton("Back", callback_data="menu:main")])
    return InlineKeyboardMarkup(rows)


def source_detail_kb(source) -> InlineKeyboardMarkup:
    sid = source["_id"]
    active = source.get("active", True)

    rows = [
        [
            InlineKeyboardButton("Targets", callback_data=f"src:{sid}:targets"),
            InlineKeyboardButton("Settings", callback_data=f"src:{sid}:settings"),
        ],
        [
            InlineKeyboardButton("Blacklist", callback_data=f"src:{sid}:blacklist"),
            InlineKeyboardButton("Pause" if active else "Resume",
                                  callback_data=f"src:{sid}:{'pause' if active else 'resume'}"),
        ],
        [InlineKeyboardButton("Remove Source", callback_data=f"src:{sid}:remove")],
        [InlineKeyboardButton("Back to Sources", callback_data="menu:sources")],
    ]
    return InlineKeyboardMarkup(rows)


def source_settings_kb(source) -> InlineKeyboardMarkup:
    """Mode + filter live on their own screen instead of crowding source_detail_kb."""
    sid = source["_id"]
    mode = source.get("mode", "clean")
    ftype = source.get("filter_type", "all")

    def tick(cond, label):
        return f"[{label}]" if cond else label

    rows = [
        [
            InlineKeyboardButton(tick(mode == "copy", "Mode: Copy"), callback_data=f"src:{sid}:mode:copy"),
            InlineKeyboardButton(tick(mode == "clean", "Mode: Clean"), callback_data=f"src:{sid}:mode:clean"),
        ],
        [
            InlineKeyboardButton(tick(ftype == "all", "All"), callback_data=f"src:{sid}:filter:all"),
            InlineKeyboardButton(tick(ftype == "media", "Media"), callback_data=f"src:{sid}:filter:media"),
            InlineKeyboardButton(tick(ftype == "text", "Text"), callback_data=f"src:{sid}:filter:text"),
        ],
        [InlineKeyboardButton("Back", callback_data=f"src:{sid}")],
    ]
    return InlineKeyboardMarkup(rows)


def source_blacklist_kb(source) -> InlineKeyboardMarkup:
    """Lists current blacklist words plus add/remove, on its own screen."""
    sid = source["_id"]
    rows = [
        [InlineKeyboardButton("Add word", callback_data=f"src:{sid}:addblacklist")],
        [InlineKeyboardButton("Remove word", callback_data=f"src:{sid}:removeblacklist")],
        [InlineKeyboardButton("Back", callback_data=f"src:{sid}")],
    ]
    return InlineKeyboardMarkup(rows)


def remove_source_confirm_kb(source_id) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("Yes, remove", callback_data=f"src:{source_id}:remove:confirm"),
            InlineKeyboardButton("Cancel", callback_data=f"src:{source_id}"),
        ]
    ])


def targets_list_kb(source_id, targets) -> InlineKeyboardMarkup:
    rows = []
    for t in targets:
        rows.append([InlineKeyboardButton(f"Remove {t}", callback_data=f"src:{source_id}:tgt:{t}:remove")])
    rows.append([InlineKeyboardButton("Add Target", callback_data=f"src:{source_id}:addtarget")])
    rows.append([InlineKeyboardButton("Back", callback_data=f"src:{source_id}")])
    return InlineKeyboardMarkup(rows)


def back_kb(callback_data="menu:main", label="Back") -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([[InlineKeyboardButton(label, callback_data=callback_data)]])


def sudo_list_kb(owner_ids, sudo_ids) -> InlineKeyboardMarkup:
    rows = []
    for uid in sudo_ids:
        rows.append([InlineKeyboardButton(f"Remove {uid}", callback_data=f"sudo:remove:{uid}")])
    rows.append([InlineKeyboardButton("Add Sudo", callback_data="menu:addsudo")])
    rows.append([InlineKeyboardButton("Back", callback_data="menu:main")])
    return InlineKeyboardMarkup(rows)
