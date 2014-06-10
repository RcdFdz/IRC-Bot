import irc.bot
import irc.strings
from irc.client import ip_numstr_to_quad, ip_quad_to_numstr

import random
import sched, time
import thread

import youtube
import login

authUsers = { }
insultosList = [
	'Calla puta',
	'Paso de ti..',
	'Eres mu feo!'
]

def isAllowed(nick):
	return (nick in authUsers)

def random_line(afile):
	line = random.choice(open(afile).readlines())
	return line

def autoFrasesCelebres(sc, self):
	self.connection.privmsg(self.channel, random_line('texto').replace("\n", "").decode('utf-8'))
	sc.enter(3600, 1, autoFrasesCelebres, (sc, self))

def addSong(song, nick):
	if youtube.existVideo(song):
		youtube.add_video(song)
		file = open('songHistory','a')
		print>> file, song + " " + nick
		msg = " Added: '" + youtube.info_video(song) +"'"
	else:
		msg = " No added song, hash invalid!"
	return msg

class TestBot(irc.bot.SingleServerIRCBot):

	def __init__(self, channel, nickname, realname, server, port=6667):
		irc.bot.SingleServerIRCBot.__init__(self, [(server, port)], nickname, realname)
		self.channel = channel

	def on_nicknameinuse(self, c, e):
		c.nick(c.get_nickname() + "_")

	def on_welcome(self, c, e):
		c.join(self.channel)

	def on_privmsg(self, c, e):
		if not isAllowed(e.source.nick):
			if e.arguments[0].startswith("identify"):
				self.logguin(e, e.arguments[0])
			elif e.arguments[0].startswith("register"):
				self.register(e, e.arguments[0])
			elif e.arguments[0].startswith("help"):
				self.help(e, e.arguments[0])
		else:
			self.do_command(e, e.arguments[0])

	def on_pubmsg(self, c, e):
		if isAllowed(e.source.nick):
			a = e.arguments[0].split(":", 1)
			if len(a) > 1 and irc.strings.lower(a[0]) == irc.strings.lower(self.connection.get_nickname()):
				self.do_command(e, a[1].strip())
		return

	def on_join(self, c, e ):
		nick = e.source.nick
		channel = self.channel
		c.privmsg(self.channel, "Hola " + nick + "! :D!")

	def help(self, e, cmd):
		nick = e.source.nick
		c = self.connection
		c.privmsg(nick, "The actual commands are: ")
		c.privmsg(nick, "    help")
		c.privmsg(nick, "    register <pass>")
		c.privmsg(nick, "    identify <pass>")

	def register(self, e, cmd):
		nick = e.source.nick
		c = self.connection
		cmdSplit = cmd.split(" ")
		passwd = cmdSplit[1]
		if len(cmdSplit) > 1: 
			if login.isUserRegistred(nick):
				c.privmsg(nick, "The user '" + nick + "' already exists!")
			else:
				login.register(nick, passwd)
				c.privmsg(nick, "Done! Now you can use 'identify'")
		else:
			c.privmsg(nick, "Your command is incorrect, use: register <pass>")
	def logguin(self, e, cmd):
		nick = e.source.nick
		c = self.connection
		cmdSplit = cmd.split(" ")
		passwd = cmdSplit[1]
                if len(cmdSplit) > 1:
			if login.identify(nick,passwd):
				authUsers[nick] = 1
				c.privmsg(nick, "Now you are logued!")
			else:
				c.privmsg(nick, "Wrong credentials!")

	def do_command(self, e, cmd):
		nick = e.source.nick
		c = self.connection
		cmdSplit = cmd.split(" ")

		if cmd == "die" and nick == 'rfernandez':
			self.die()

		elif cmd == "help":
			c.privmsg(nick, "The actual commands are: ")
			c.privmsg(nick, "    add_Song <hash>")
			c.privmsg(nick, "    saluda")
			c.privmsg(nick, "    stats")
			c.privmsg(nick, "    guapo, hermoso, bello and bonido")
			c.privmsg(nick, "    frase")
			c.privmsg(nick, "    auto_frases")
			c.privmsg(nick, "    insulta")

		elif cmdSplit[0] == "add_Song":
	                if len(cmdSplit) > 1:
				song = addSong(cmdSplit[1],nick)
				c.notice(self.channel, song)
			else:
	                        c.privmsg(nick, "Your command is incorrect, use: add_Song <hash>")			
		elif cmd.startswith("saluda"):
			c.privmsg(self.channel, "Hi everybody!")

		elif cmd == "stats":
			for chname, chobj in self.channels.items():
				c.notice(nick, "--- Channel statistics ---")
				c.notice(nick, "Channel: " + chname)
				users = chobj.users()
				users.sort()
				c.notice(nick, "Users: " + ", ".join(users))
				opers = chobj.opers()
				opers.sort()
				c.notice(nick, "Opers: " + ", ".join(opers))
				voiced = chobj.voiced()
				voiced.sort()
				c.notice(nick, "Voiced: " + ", ".join(voiced))

		elif cmd == 'test':
			c.privmsg(self.channel, str(e.type))
			c.privmsg(self.channel, str(e.source))
			c.privmsg(self.channel, str(e.target))
			c.privmsg(self.channel, str(e.arguments))

		elif cmd == 'guapo' or cmd == 'hermoso' or cmd == 'bello' or cmd == 'bonico':
			c.privmsg(self.channel, "Tu si que eres bonico " + nick +"!")

		elif cmd == 'frase':
			c.privmsg(self.channel, random_line('texto').replace("\n", "").decode('utf-8'))

		elif cmd == 'auto_frases':
			s = sched.scheduler(time.time, time.sleep)
			s.enter(1, 1, autoFrasesCelebres, (s,self))
			thread.start_new_thread(s.run, ())

		elif cmd.startswith('insulta'):
			c.privmsg(self.channel, random.choice(insultosList))

		else:
			c.notice(nick, "Not understood: " + cmd)

def main():
	import sys

	if len(sys.argv) != 5:
		print("Usage: testbot <server[:port]> <channel> <nickname> <realname>")
		sys.exit(1)

	s = sys.argv[1].split(":", 1)
	server = s[0]
	if len(s) == 2:
		try:
			port = int(s[1])
		except ValueError:
			print("Error: Erroneous port.")
			sys.exit(1)
	else:
		port = 6667

	channel = '#' + (sys.argv[2])
	nickname = sys.argv[3]
	realname = sys.argv[4]

	bot = TestBot(channel, nickname, realname, server, port)
	bot.start()

if __name__ == "__main__":
	main()
