# Copyright 2016 xt <xt@bash.no>
# Python 3 Port using the 'emoji' package
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

"""
Emoji output/input shortcode helper for WeeChat.

Usage:
    Type :emojiname: from http://www.emoji-cheat-sheet.com/ or use tab completion.
"""

import re
try:
    import weechat
except ImportError:
    print("This script must be run under WeeChat.")
    raise SystemExit(1)

# TODO: add support for configurable languages
# TODO: add autocomplete list, maybe a bar item? or extend the autocomplete list
# TODO: cleanup code

import emoji

SCRIPT_NAME     = "emoji"
SCRIPT_AUTHOR   = "jcjordyn120 <onlinecloud1@gmail.com>"
SCRIPT_VERSION  = "1"
SCRIPT_LICENSE  = "GPL3"
SCRIPT_DESC     = "Emoji output helper (Python 3 port) (based on emoji.lua)"

def str2emoji(text):
    """Replaces :shortcodes: with actual emojis using the emoji package."""
    if not text:
        return ""

    # language="alias" ensures it catches standard Github/Slack style shortcodes
    return emoji.emojize(text, language = "alias")

def emoji_replace_input_string(buffer):
    """Replaces emojis in the current input buffer."""
    input_s = weechat.buffer_get_string(buffer, "input")
    
    # Skip modification if it's a settings command
    if input_s.startswith("/set "):
        return weechat.WEECHAT_RC_OK
        
    weechat.buffer_set(buffer, "input", str2emoji(input_s))
    return weechat.WEECHAT_RC_OK

def emoji_input_replacer(data, buffer, command):
    if command == "/input return":
        return emoji_replace_input_string(buffer)
    return weechat.WEECHAT_RC_OK

def emoji_live_input_replace(data, modifier, modifier_data, msg):
    return str2emoji(msg)

def emoji_out_replace(data, modifier, modifier_data, msg):
    return str2emoji(msg)

def unshortcode_cb(data, modifier, modifier_data, msg):
    return str2emoji(msg)

def emoji_complete_next_cb(data, buffer, command):
    """Handles partial matching and inline replacement for /input complete_next"""
    input_s = weechat.buffer_get_string(buffer, "input")
    
    if ":" not in input_s:
        return weechat.WEECHAT_RC_OK

    current_pos = weechat.buffer_get_integer(buffer, "input_pos") - 1
    
    while current_pos >= 0 and input_s[current_pos] != ":":
        current_pos -= 1
        
    if current_pos < 0:
        current_pos = 0

    oword = input_s[current_pos:]
    match = re.search(r":([a-zA-Z0-9\-_+]+)", oword)
    
    if match:
        word = match.group(1)
        search_term = f":{word}:"

        # Try an exact match first
        # Ex -- :joy <tab> >>>> [joy emoji]
        found_emoji = emoji.emojize(search_term)

        if found_emoji == search_term:
            found_emoji = None

        if not found_emoji:
            # Search the emoji package for a partial match
            try:
                # For emoji package >= 2.0.0
                for emo, data_dict in emoji.EMOJI_DATA.items():
                    # Combine standard names and aliases to search against
                    aliases = [data_dict.get('en', '')] + data_dict.get('alias', [])

                    # Sort so it completes in a known way
                    aliases = sorted(aliases)

                    for alias in aliases:
                        # If the typed word is inside the alias (partial match)
                        if search_term in alias:
                            found_emoji = emo
                            break

                    if found_emoji:
                        break
            except AttributeError:
                # Fallback for older emoji packages (< 2.0.0)
                for shortcode, emo in emoji.EMOJI_UNICODE_ENGLISH.items():
                    if search_term in shortcode:
                        found_emoji = emo
                        break

        # If we found a match, swap out the typed partial string for the emoji
        if found_emoji:
            # Splice the string to replace just the typed portion
            new_input = input_s[:current_pos] + found_emoji + input_s[current_pos + len(search_term):]
            weechat.buffer_set(buffer, 'input', new_input)
            
            # EAT tells WeeChat not to pass the <Tab> keypress to standard completion
            return weechat.WEECHAT_RC_OK_EAT

    return weechat.WEECHAT_RC_OK

def emoji_completion_cb(data, completion_item, buffer, completion):
    """Populates WeeChat's completion list with available emoji shortcodes."""
    # Handle dictionary structure based on 'emoji' package version
    try:
        # For emoji package >= 2.0.0
        for lang_dict in emoji.EMOJI_DATA.values():
            if "en" in lang_dict:
                weechat.hook_completion_list_add(completion, lang_dict["en"], 0, weechat.WEECHAT_LIST_POS_SORT)
            if "alias" in lang_dict:
                for alias in lang_dict["alias"]:
                    weechat.hook_completion_list_add(completion, alias, 0, weechat.WEECHAT_LIST_POS_SORT)
    except AttributeError:
        # Fallback for older emoji packages
        for k in emoji.EMOJI_UNICODE_ENGLISH.keys():
            weechat.hook_completion_list_add(completion, k, 0, weechat.WEECHAT_LIST_POS_SORT)
            
    return weechat.WEECHAT_RC_OK

def incoming_cb(data, modifier, modifier_data, msg):
    """Only replaces shortcodes in incoming messages."""
    if "nick_" in modifier_data:
        return str2emoji(msg)
    return msg

if __name__ == "__main__":
    if weechat.register(
        SCRIPT_NAME,
        SCRIPT_AUTHOR,
        SCRIPT_VERSION,
        SCRIPT_LICENSE,
        SCRIPT_DESC,
        "",
        ""):
        
        # Hook input enter
        weechat.hook_command_run("/input return", "emoji_input_replacer", "")

        # Hook irc out for relay clients
        weechat.hook_modifier("irc_out1_PRIVMSG", "emoji_out_replace", "")
        
        # Replace while typing
        weechat.hook_modifier("input_text_display_with_cursor", "emoji_live_input_replace", "")
        
        # Hook tab complete
        weechat.hook_command_run("/input complete_next", "emoji_complete_next_cb", "")
        
        # Hook for working together with other scripts
        weechat.hook_modifier("emoji_unshortcode", "unshortcode_cb", "")
        
        # Hook autocomplete list
        weechat.hook_completion("emojis", "complete :emoji:s", "emoji_completion_cb", "")

        settings = {
            "incoming": ("on", "Also try to replace shortcodes to emoji in incoming messages")
        }
        
        # Set default settings
        version_str = weechat.info_get("version_number", "") or "0"
        try:
            version = int(version_str)
        except ValueError:
            version = 0

        for option, value in settings.items():
            if not weechat.config_is_set_plugin(option):
                weechat.config_set_plugin(option, value[0])
            if version >= 0x00030500:
                weechat.config_set_desc_plugin(option, f"{value[1]} (default: '{value[0]}')")

        # Hook incoming message
        if weechat.config_get_plugin("incoming") == "on":
            weechat.hook_modifier("weechat_print", "incoming_cb", "")
