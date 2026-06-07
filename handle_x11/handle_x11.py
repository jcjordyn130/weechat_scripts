import weechat
import re

SCRIPT_NAME    = "handle_x11"
SCRIPT_AUTHOR  = "jcj"
SCRIPT_VERSION = "1.0"
SCRIPT_LICENSE = "MIT"
SCRIPT_DESC    = "Inverts the background of text enclosed in \\x11 characters"

def process_x11(data, modifier, modifier_data, string):
    """
    Callback function that modifies printed lines.
    Replaces \x11...text...\x11 with WeeChat's reverse video color codes.
    """
    # Fetch WeeChat's internal escape codes for turning reverse video on and off
    rev_on = weechat.color("reverse")
    rev_off = weechat.color("-reverse")
    
    def replace_match(match):
        # Wraps the matched text in WeeChat's reverse attributes
        return f"{rev_on}{match.group(1)}{rev_off}"
        
    # Replace all properly closed pairs of \x11
    new_string = re.sub(r'\x11([^\x11]*)\x11', replace_match, string)
    
    # Handle the edge case of a dangling \x11 (unclosed escape character)
    # This will invert the text from the \x11 up to the end of the string
    if '\x11' in new_string:
        new_string = re.sub(r'\x11(.*)$', lambda m: f"{rev_on}{m.group(1)}{rev_off}", new_string)
        
    return new_string

if __name__ == "__main__":
    if weechat.register(SCRIPT_NAME, SCRIPT_AUTHOR, SCRIPT_VERSION, SCRIPT_LICENSE, SCRIPT_DESC, "", ""):
        # Hook into the 'weechat_print' modifier to alter the text right before it renders on screen
        weechat.hook_modifier("weechat_print", "process_x11", "")
