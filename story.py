from twisted.words.protocols import irc
import random
import datetime

class Storybot:
  def __init__(self):
    self.state = "idle"
    self.attrib = {}
    self.pendingUsers = set()
    self.readyUsers = set()
    # load names and such from db

  def privateMessage(self, client, name, message):
    (nick,remain) = name.split('!')
    (user,host) = remain.split('@')
    # client.whois(nick)
    if message.lower() == "help":
      for reply in client.factory.messages["help"]["general"]:
        client.msg(nick, reply.strip())
      return False # allow other modules to add help
    elif message.find("help") == 0:
      if client.factory.messages["help"].has_key(message[5:].lower()):
        for reply in client.factory.messages["help"][message[5:]]:
          client.msg(nick, reply.strip())
      else:
        client.msg(nick, "No help found for that topic.")
      return False
    elif message.find("attrib") == 0:
      if nick in self.pendingUsers:
        self.pendingUsers.discard(nick)
        self.readyUsers.add(nick)
      self.attrib[nick] = message[7:]
      client.msg(nick, "You will be attributed as '%s'." % (message[7:],))
    elif message.lower() == "i'm in":
      self.addUser(client, name)
    elif message.lower() in client.factory.messages["help"]:
      for reply in client.factory.messages["help"][message.lower()]:
        client.msg(nick, reply.strip())

  def channelMessage(self, client, channel, name, message):
    nick = name.split("!")[0]
    if self.state == "idle":
      if message.find(client.nickname) == 0:
        if message[len(client.nickname)+2:] == "create story":
          self.state = "pending"
          self.pendingUsers = set()
          self.readyUsers = set()
          client.say(channel, "Starting story! Tell me you're in to be a part of it, or 'start' to begin the story.")
          # do other story start stuff here
        else:
          pass # command
    elif self.state == "pending":
      if message.find(client.nickname) == 0:
        message = message[len(client.nickname)+2:]
        if message == "I'm in":
          self.addUser(client, name)
        elif message == "start story":
          if nick in self.readyUsers:
            self.state = "starting"
            self.nextUser = nick # or choose at random
            client.sendLine("NAMES %s" % channel)
          else:
            client.say(channel, "%s: you're not even taking part!" % (nick,))
        else:
          print "Unrecognized command from %s in %s: %s" % (nick, channel, message,)
      elif message == "I'm in":
        self.addUser(client, name)
    elif self.state == "starting":
      if message.find("I'm in"):
        self.addUser(client, name)
    elif self.state == "active":
      if '@' in message:
        (line, nextUser) = message.split('@')
        nextUser = nextUser.strip()
      else:
        line = message
        nextUser = None

      if nextUser not in self.readyUsers:
        nextUser = random.sample(self.readyUsers, 1)[0]
      client.mode(channel, False, "v", None, self.nextUser)
      self.readyUsers.add(self.nextUser)
      self.lines.append((nick, line))
      if line.lower().find("the end") == 0:
        finished = datetime.datetime.now().strftime("%Y-%m-%dt%H%M")
        f = open("storybot/%s.txt" % finished, "w")
        print >> f, "Story in %s, finished at %s" % (channel, finished,)
        print >> f, ""
        print >> f, "Authors:"
        for author in self.readyUsers:
          print >> f, "  %s" % self.attrib[author]
        print >> f, ""
        print >> f, "This story is published under the Creative Commons Attribution-ShareAlike 3.0 License."
        print >> f, "You may copy it, edit it, or sell it, so long as you include the Authors section above."
        print >> f, "More details at http://creativecommons.org/licenses/by-sa/3.0/"
        print >> f, ""
        for line in self.lines:
          print >> f, line[1]
        f.close()
        client.say(channel, "Story published at http://owenja.dyndns.org/%s" % f.name)
        self.state = "idle"
        client.mode(channel, False, "m")
      else:
        self.nextUser = nextUser
        self.readyUsers.remove(self.nextUser)
        client.mode(channel, True, "v", None, self.nextUser)
    return True

  def unknownCommand(self, client, prefix, command, params):
    if command == '330' or command == 'RPL_WHOISACCOUNT':
      print "Nickname %s is signed in to account %s" % \
        (params[1], params[2])
    elif command == 'RPL_NAMREPLY':
      if self.state == "starting":
        # deop and devoice everyone
        print "Debug: client.nickname = %s" % (client.nickname,)
        for user in params[3].split(' '):
          if user[1:].lower() == "chanserv" or user[1:] == client.nickname: continue
          if user[0] == '@':
            client.mode(params[2], False, "o", None, user[1:])
          if user[0] == '+':
            client.mode(params[2], False, "v", None, user[1:])
    elif command == 'RPL_ENDOFNAMES':
      if self.state == "starting":
        client.mode(params[1], True, "m")
        self.lines = []
        self.state = "active"
        client.mode(params[1], True, "v", None, self.nextUser)
    return False

  def addUser(self, client, user):
    nick = user.split("!")[0]
    if nick in self.readyUsers:
      client.msg(nick, "You are already in!")
    else:
      for message in client.factory.messages["register"]:
        client.msg(nick, message.strip())
      if not self.attrib.has_key(nick):
        for message in client.factory.messages["needAttrib"]:
          client.msg(nick, message.strip())
        if nick not in self.pendingUsers:
          self.pendingUsers.add(nick)
      else:
        self.readyUsers.add(nick)
