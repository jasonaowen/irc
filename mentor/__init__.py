# mentor.py
# This contains all the logic for mentor bot.

# Copyright 2012 Jason Owen <jason.a.owen@gmail.com>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

from twisted.words.protocols import irc

class Mentor:
  def __init__(self, args):
    self.state = "idle"
    self.userChannelMap = {}
    self.channelUserMap = {}
    self.reportChannel = args["reportChannel"]
    self.channelKeyMap = {}

  def privateMessage(self, client, name, message):
    (nick,remain) = name.split('!')
    (user,host) = remain.split('@')
    # client.whois(nick)
    if message.lower().find("ask") == 0:
      return self.ask(client, nick, message)
    if message.lower().find("join") == 0:
      return self.join(client, nick, message)
    return False

  def channelMessage(self, client, channel, name, message):
    return False

  def unknownCommand(self, client, prefix, command, params):
    if command == 'RPL_NAMREPLY':
      channel = params[2]
      for user in params[3].split(' '):
        if user[0] == '@' or user[0] == '+':
          user = user[1:]
        if user.lower() == "chanserv" or user == client.nickname: continue
        self.addUserChannelAssociation(user, channel)
    elif command == 'INVITE':
      channel = params[1]
      if channel in self.channelKeyMap:
        client.join(channel, self.channelKeyMap[channel])
        del self.channelKeyMap[channel]
      else:
        client.join(channel)
      return True
    return False

  def userJoined(self, client, user, channel):
    self.addUserChannelAssociation(user, channel)
    return False

  def userLeft(self, client, user, channel):
    self.removeUserChannelAssociation(user, channel)
    return False

  def userQuit(self, client, user, quitMessage):
    self.removeUser(user)
    return False

  def userRenamed(self, client, oldname, newname):
    self.renameUser(oldname, newname)
    return False

  def addUserChannelAssociation(self, user, channel):
    if user not in self.userChannelMap:
      self.userChannelMap[user] = set()
    self.userChannelMap[user].add(channel)

    if channel not in self.channelUserMap:
      self.channelUserMap[channel] = set()
    self.userChannelMap[user].add(channel)
    self.channelUserMap[channel].add(user)

  def removeUserChannelAssociation(self, user, channel):
    if user in self.userChannelMap and channel in self.userChannelMap[user]:
      self.userChannelMap[user].remove(channel)

    if channel in self.channelUserMap and user in self.channelUserMap[channel]:
      self.channelUserMap[channel].remove(user)

  def removeUser(self, user):
    if user in self.userChannelMap:
      del self.userChannelMap[user]

    for channel in self.channelUserMap:
      if user in channel:
        channel.remove(user)

  def renameUser(self, oldname, newname):
    if oldname in self.userChannelMap:
      self.userChannelMap[newname] = self.userChannelMap[oldname]
      del self.userChannelMap[oldname]

    for channel in self.channelUserMap:
      if oldname in channel:
        channel.remove(oldname)
        channel.add(newname)

  def ask(self, client, nick, message):
    channel = None
    if nick not in self.userChannelMap:
      print "Unknown user %s!" % (nick,)
      return False
    if message.lower().find("ask: ") == 0:
      if len(self.userChannelMap[nick]) == 1:
        for c in self.userChannelMap[nick]:
          return self.askQuestion(client, nick, c, message[5:])
      else:
        client.msg(nick, "You must specify the channel! (see: 'help ask')")
        return True
    elif message.lower().find("ask in ") == 0 and message.find(':') > -1:
      colonPos = message.find(':')
      channel = message[7:colonPos]
      if channel in self.userChannelMap[nick]:
        return self.askQuestion(client, nick, channel, message[colonPos+2:])
      else:
        client.msg(nick, "At least one of us is not in channel %s!" % (channel,))
        return True
    else:
      return False

  def askQuestion(self, client, nick, channel, question):
    client.say(channel, question)
    client.say(self.reportChannel,
      "%(nick)s asks in %(channel)s: %(question)s" %
      {"nick": nick, "channel": channel, "question": question})
    return True

  def join(self, client, user, message):
    params = message.split(' ')
    if len(params) != 3:
      return False
    channel = params[1]
    channelKey = params[2]
    self.channelKeyMap[channel] = channelKey
    client.msg(user, "Now invite me by saying '/invite %s %s'" % (client.nickname, channel,))
    return True
