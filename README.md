## **NSFW bot**

### Brief overview
Reply to a message with `/nsfw` command and this bot will forward the message to another (nsfw) chat and delete the message in original chat afterwards.

### Usage
Fisrt, set up nsfw chat, to which nsfw content will be send using command `/setnsfw`. To move a message to nsfw chat, reply to the message with `/nsfw` command.

### Variables
| Variable        | Description                                                                                                    |
| --------------- | -------------------------------------------------------------------------------------------------------------- |
| `token `        | The bot's token.                                                                                               |


### Commands
| Command         | Description                                                                                                    |
| --------------- | -------------------------------------------------------------------------------------------------------------  |
| `/setnsfw <id>` | Sets chat to which nsfw content will be forwarded. `<id>` must be either `@groupname` or `-id` or `id` format. |
| `/nsfw`         | Mark message as nsfw. You should use this command only when replying to another message.                       |