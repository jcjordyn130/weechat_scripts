# Original script author: Fsaev
# This is a rewrite but based from the original by Fsaev, so it is still GPLv3 licensed.
SCRIPT_NAME = 'sarcasm'
SCRIPT_AUTHOR = 'jcj'
SCRIPT_VERSION = '1.0'
SCRIPT_LICENSE = 'GPLv3'
SCRIPT_DESC = 'Adds random capitalization to your sentence/word'

import_ok = True

try:
    import weechat
except ImportError:
    print('This script must be run under WeeChat')
    print('You can obtain a copy of WeeChat, for free, at https://weechat.org')
    import_ok = False

from random import randint

# sarcasm_text - helper for text conversion
# Converts any given text to SaRcAsM TeXt
def sarcasm_text(text):
    newstring = []
    for arg in text:
        if randint(0, 1) == 1:
            newstring.append(arg.upper())
        else:
            newstring.append(arg.lower())

    return "".join(newstring)

# sarcasm_cb - command handler for /sarcasm
# Processes the entire input line with sarcasm_text()
def sarcasm_cb(data, buffer, args):
    # Get current text
    input_str = weechat.buffer_get_string(buffer, "input")

    # Replace text with sarcasm
    weechat.buffer_set(buffer, "input", sarcasm_text(input_str))

    return weechat.WEECHAT_RC_OK

# sarcasm_word_cb - command handler for /sarcasm_word
# Strips the current word and processes it alone with sarcasm_text()
def sarcasm_word_cb(data, buffer, args):
    # Get the current text and current index
    input_str = weechat.buffer_get_string(buffer, "input")
    cursor_pos = weechat.buffer_get_integer(buffer, "input_pos")

    # Don't process an empty bar
    if not input_str:
        return weechat.WEECHAT_RC_OK

    # Find the boundaries of the current word using space delimiters
    start_idx = cursor_pos - 1
    while start_idx >= 0 and input_str[start_idx] != " ":
        start_idx -= 1
    start_idx +=1 # Move right of the space or to index 0

    # Search forwards to find the end of the word (or the line)
    end_idx = cursor_pos
    while end_idx < len(input_str) and input_str[end_idx] != " ":
        end_idx += 1

    # Extract the isolated word
    current_word = input_str[start_idx:end_idx]

    # Sanity check for blank or weird input
    if not current_word:
        return weechat.WEECHAT_RC_OK

    # Convert the text to sarcasm text
    processed_word = sarcasm_text(current_word)

    # Reconstruct the full input string with the new word spliced in
    new_input = input_str[:start_idx] + processed_word + input_str[end_idx:]

    # Calculate new cursor position
    # Technically not needed as we aren't changing the line length, but is 
    # always good to do.
    new_cursor_pos = start_idx + len(processed_word)

    # Push the new text and position back to WeeChat
    weechat.buffer_set(buffer, "input", new_input)
    weechat.buffer_set(buffer, "input_pos", str(new_cursor_pos))

    return weechat.WEECHAT_RC_OK

if __name__ == "__main__" and import_ok:
    if weechat.register(SCRIPT_NAME, SCRIPT_AUTHOR, SCRIPT_VERSION, SCRIPT_LICENSE, SCRIPT_DESC, "", ""):
        weechat.hook_command(
            "sarcasm",
            """Adds random capitalization to your sentence to indicate that you are being sarcastic, e.g.
/sarcasm I love to put ketchup on my pizza

results in:
i lOVe tO Put KEtChUp oN mY pIzZa
""",
            "message", "",
            "",
            "sarcasm_cb", ""
        )

        weechat.hook_command(
            "sarcasm_word",
            """Adds random capitalization the current word""",
            "message", "",
            "",
            "sarcasm_word_cb", ""
        )
