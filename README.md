# Modmail Dev CloseRequest Plugin

This plugin adds a `.closerequest` command to the Modmail.dev bot.

## Features
- `.closerequest *reason*`: Sends a request to close the ticket directly to the user via DM.
- The user can decide via buttons (`Accept` / `Decline`).
- If the user accepts, the ticket is automatically closed.
- If the user declines, the ticket remains open and the auto-close timer is stopped.
- If the user does not react within 6 hours, the ticket is automatically closed.
- All messages are sent as Embeds.
- When closed, the reason is automatically sent to the specified log channel.

## Installation
Use the following command in your Modmail server:
```
?plugin add breadybread123/modmail-dev-closerequest/plugin-folder
```
*(Replace `?` with your bot's prefix)*
