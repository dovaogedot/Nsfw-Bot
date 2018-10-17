from telegram.ext import Updater, Dispatcher, CommandHandler
from telegram import Chat
from telegram.error import BadRequest, Unauthorized
import logging, json
from os.path import exists
from os import environ
from time import time

class NsfwBot:

	nsfw_chats: dict

	token: str
	updater: Updater
	dispatcher: Dispatcher

	chats: str

	@staticmethod
	def init():
		NsfwBot.nsfw_chats = dict()
		NsfwBot.token = environ.get('TG_NSFW_TOKEN')
		NsfwBot.chats = 'chats.json'

		# load info from file
		if exists(NsfwBot.chats):
			with open(NsfwBot.chats, 'r') as f:
				try:
					NsfwBot.nsfw_chats = json.load(f)
					logging.debug('Chats loaded from %s.' % NsfwBot.chats)
				except json.decoder.JSONDecodeError:
					logging.debug('Failed to load chats from file.')



		# init bot
		NsfwBot.updater = Updater(token=NsfwBot.token)
		NsfwBot.dispatcher = NsfwBot.updater.dispatcher

		# set up commands
		NsfwBot.dispatcher.add_handler(CommandHandler('nsfw', NsfwBot.nsfw))
		NsfwBot.dispatcher.add_handler(CommandHandler('setnsfw', NsfwBot.setnsfw, pass_args=True))


	@staticmethod
	def start():
		NsfwBot.updater.start_polling()
		NsfwBot.updater.idle()


	@staticmethod
	def nsfw(bot, update):
		try:
			if not NsfwBot.nsfw_chats[str(update.message.chat.id)]:
				bot.sendMessage(update.message.chat.id, 'Set NSFW chat first with /setnsfw <id> command.')
				return
		except KeyError:
			bot.sendMessage(update.message.chat.id,
			                'Set NSFW chat first with /setnsfw <id> command.')
			return
		# NOTE: if you reply to your own message reply_to_message is somewhy not set
		if update.message.reply_to_message is not None:
			# do not forward FROM nsfw chat
			if update.message.chat.id != NsfwBot.nsfw_chats[str(update.message.chat.id)]:
				try:
					bot.forwardMessage(
							NsfwBot.nsfw_chats[str(update.message.chat.id)],
							update.message.reply_to_message.chat.id,
							message_id=update.message.reply_to_message.message_id)
					link = ''
					try:
						chat = bot.getChat(NsfwBot.nsfw_chats[str(update.message.chat.id)])
						link ='[@%s](%s)' % (chat.username, 't.me/%s' % chat.username)
					except BadRequest:
						link = '[%s](%s)' % ('here', 't.me/%s' % NsfwBot.nsfw_chats[str(update.message.chat.id)])
					hashtag = '#%d' % int(time())
					bot.sendMessage(update.message.chat.id, 'NSFW -> %s -> %s' % (link, hashtag), 'Markdown')
					bot.sendMessage(NsfwBot.nsfw_chats[str(update.message.chat.id)], '%s' % (hashtag), 'Markdown')
					pass
				except BadRequest as e:
					logging.debug('Something wrong. %s' % e.message)
				except Unauthorized:
					bot.sendMessage(update.message.chat.id, 'Add me to NSFW group first.')
				try:
					bot.deleteMessage(update.message.chat.id, update.message.reply_to_message.message_id)
					bot.deleteMessage(update.message.chat.id, update.message.message_id)
				except BadRequest:
					bot.sendMessage(update.message.chat.id, 'I need to have admin priviliges to delete messages.')
			else:
				bot.sendMessage(update.message.chat.id, 'This is the NSFW chat.')
		else:
			bot.sendMessage(update.message.chat.id, 'Reply to a message with /nsfw.')


	@staticmethod
	def setnsfw(bot, update, args):
		admins = bot.getChatAdministrators(update.message.chat.id)
		if update.message.from_user.id not in [x.user.id for x in admins]:
			bot.sendMessage(update.message.chat.id, 'You are not allowed to set NSFW chat. Only admins can do this.')
			return
		try:
			chat = bot.getChat(args[0])
			NsfwBot.nsfw_chats[str(update.message.chat.id)] = str(chat.id)
			bot.sendMessage(update.message.chat.id,
							'NSFW messages will be sent to "%s".' %
                            (chat.first_name if chat.title is None else chat.title))
			with open(NsfwBot.chats, 'w') as f:
				json.dump(NsfwBot.nsfw_chats, f)
		except BadRequest:
			bot.sendMessage(update.message.chat.id,
			                'Please, send a valid chat id. For groups, don\'t miss:\n"-" symbol before ids\n"@" symbol before usernames')


if __name__ == '__main__':
	logging.basicConfig(format='%(asctime)-16s %(levelname)-8s %(message)s', datefmt='%d-%m %H:%M:%S', level=logging.DEBUG)
	NsfwBot.init()
	NsfwBot.start()
