# Highmon
A modified version of the famous `highmon.pl` script.

I added a way to ignore nicknames *just* for the highmon buffer/bar item, and a custom time formatter string.

The reason I did so is because I have milliseconds in my default time string and strftime does not support Weechat's
special modifiers.

Ignore nicks is because I want to ignore a bot from that monitor.

## Configuration
- plugins.var.perl.highmon.ignore_nicks: CSV list of nicknames (only nicknames) to ignore
- plugins.var.perl.highmon.custom_time_format: standard strftime() string to use for formatting, will fallback to default if not set

## How to use
Same way as the parent `highmon.pl` script.