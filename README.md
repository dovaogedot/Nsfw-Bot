## **NSFW bot**

### Brief overview
Reply to a message with `/nsfw` command and this bot will forward the message to another (nsfw) chat and delete the message in original chat afterwards.

### Usage
Fisrt, set up nsfw chat to which nsfw content will be send using command `/setnsfw`. To move a message to nsfw chat and delete it, reply to the message with `/nsfw` command.

### Commands
| Command         | Description                                                                                                    |
| --------------- | -------------------------------------------------------------------------------------------------------------  |
| `/setnsfw <id>` | Sets chat to which nsfw content will be forwarded. Only admins can do this. Bot must be member of target chat. `<id>` must be either `@groupname` or `-id` or `id` format. If you pass `/dev/null` as `id`, messages will not be forwarded and only deleted. |
| `/nsfw`         | Mark message as nsfw. You should use this command only when replying to another message.                       |