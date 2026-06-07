# weemoji
Emoji output/input shortcode helper for WeeChat.

This script allows you to type emojis with the colon short codes just like Discord.

It is based on emoji.lua but uses a dependency for the emojis that is kept up-to-date, instead of hardcoding a GIANT hashtable of shortcodes to codepoints.

This allows for newer emojis to be used and might be a bit faster.

## Configuration
- python.var.weemoji.incoming: process short codes on incoming messages

## How to use
Type in short code and press TAB (or whatever the auto completion hotkey is)
