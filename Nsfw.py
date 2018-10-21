from telegram.ext import Updater, Dispatcher, CommandHandler
from telegram import Chat
from telegram.error import BadRequest, Unauthorized
import logging, json, time
from os.path import exists
from os import environ
import psycopg2
from random import choice

class NsfwBot:

	token: str
	updater: Updater
	dispatcher: Dispatcher

	conn: psycopg2.extensions.connection
	cur: psycopg2.extensions.cursor

	lulz: list

	@staticmethod
	def init():
		NsfwBot.token = environ.get('TG_NSFW_TOKEN')
		NsfwBot.lulz =[
			'Do not expect NSFW from me.',
			'Disgusting.',
			'Sorry, I don\'t have horn to pleasure you. Talk to Rem.',
			'Korosu.',
			'I am not Emilia.',
			'One more and I will ban you',
			'Do you like guro?'
		]

		# check if db exists
		NsfwBot.conn = psycopg2.connect(environ.get('DATABASE_URL'))
		NsfwBot.cur = NsfwBot.conn.cursor()
		NsfwBot.cur.execute("SELECT EXISTS(SELECT * FROM information_schema.tables WHERE table_name=%s)", ('chats',))
		if not NsfwBot.cur.fetchone()[0]:
			NsfwBot.cur.execute("CREATE TABLE chats(id SERIAL PRIMARY KEY, chat BIGINT UNIQUE, nsfw BIGINT)")
			NsfwBot.conn.commit()

		# init bot
		NsfwBot.updater = Updater(token=NsfwBot.token)
		NsfwBot.dispatcher = NsfwBot.updater.dispatcher

		# set up commands
		NsfwBot.dispatcher.add_handler(CommandHandler('nsfw', NsfwBot.nsfw))
		NsfwBot.dispatcher.add_handler(CommandHandler('setnsfw', NsfwBot.setnsfw, pass_args=True))
		NsfwBot.dispatcher.add_handler(CommandHandler('start', NsfwBot.start_))
		NsfwBot.dispatcher.add_handler(CommandHandler('help', NsfwBot.help))


	@staticmethod
	def start():
		NsfwBot.updater.start_polling()
		NsfwBot.updater.idle()


	@staticmethod
	def start_(bot, update):
		bot.sendMessage(update.message.chat.id, 'What?')


	@staticmethod
	def help(bot, update):
		bot.sendMessage(update.message.chat.id, 'Visit gitlab.com/dovaogedot/nsfw-bot for help.')


	@staticmethod
	def nsfw(bot, update):
		if update.message.chat.id == update.message.from_user.id:
			bot.sendMessage(update.message.chat.id, choice(NsfwBot.lulz))
			return
		# fetch data from db
		nsfw_chats = dict()
		NsfwBot.cur.execute("SELECT * FROM chats")
		q = NsfwBot.cur.fetchall()
		for _, chat, nsfw in q:
			nsfw_chats[chat] = nsfw

		if update.message.reply_to_message is not None:
			try:
				# forward nsfw message
				if update.message.chat.id in nsfw_chats.keys():
					# do not forward FROM nsfw chat
					if update.message.chat.id != nsfw_chats[update.message.chat.id]:
						# forward nsfw
						bot.forwardMessage(
							nsfw_chats[update.message.chat.id],
							update.message.reply_to_message.chat.id,
							message_id=update.message.reply_to_message.message_id)
						# send hashtag
						hashtag = '#nsfw%d' % int(time.time())
						try:
							chat = bot.getChat(nsfw_chats[update.message.chat.id])
							if chat.type in ('supergroup', 'channel'):
								hashtag += ' @%s' % chat.username
						except:
							pass
						source = bot.sendMessage(nsfw_chats[update.message.chat.id], hashtag)
						# forward hashtag back
						bot.forwardMessage(
							update.message.chat.id,
							source.chat.id,
							message_id=source.message_id)
					else:
						bot.sendMessage(update.message.chat.id, 'This is the NSFW chat.')
			except BadRequest as e:
				logging.debug('Something wrong. %s' % e.with_traceback)
			except Unauthorized:
				bot.sendMessage(update.message.chat.id, 'Add me to NSFW group first.')

			try:
				# delete messages
				bot.deleteMessage(update.message.chat.id, update.message.reply_to_message.message_id)
				bot.deleteMessage(update.message.chat.id, update.message.message_id)
			except BadRequest:
				bot.sendMessage(update.message.chat.id, 'I need to have admin priviliges to delete messages.')
		else:
			bot.sendMessage(update.message.chat.id, 'Reply to a message with /nsfw.')


	@staticmethod
	def setnsfw(bot, update, args):
		try:
			admins = bot.getChatAdministrators(update.message.chat.id)
			if update.message.from_user.id not in [x.user.id for x in admins]:
				bot.sendMessage(update.message.chat.id, 'You are not allowed to set NSFW chat. Only admins can do this.')
				return
			try:
				if args[0] == '/dev/null':
					# remove from db
					NsfwBot.cur.execute("DELETE FROM chats WHERE chat = %s", (update.message.chat.id,))
					bot.sendMessage(update.message.chat.id, 'Okay. Just delete.')
				else:
					# add to db
					chat = bot.getChat(args[0])
					NsfwBot.cur.execute("INSERT INTO chats (chat, nsfw) VALUES (%s, %s) ON CONFLICT (chat) DO UPDATE SET nsfw=%s",
										(update.message.chat.id, chat.id, chat.id))
					NsfwBot.conn.commit()
					bot.sendMessage(update.message.chat.id,
								'NSFW messages will be sent to "%s".' %
								(chat.first_name if chat.title is None else chat.title))
			except BadRequest:
				bot.sendMessage(update.message.chat.id,
								'Please, send a valid chat id. For users only IDs are allowed, not usernames. For groups, don\'t miss:\n"-" symbol before ids\n"@" symbol before usernames')
		except BadRequest:
			if update.message.chat.id == update.message.from_user.id:
				bot.sendMessage(update.message.chat.id, choice(NsfwBot.lulz))



if __name__ == '__main__':
	logging.basicConfig(format='%(asctime)-16s %(levelname)-8s %(message)s', datefmt='%d-%m %H:%M:%S', level=logging.DEBUG)
	NsfwBot.init()
	NsfwBot.start()
