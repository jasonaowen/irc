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

  def privateMessage(self, client, name, message):
    (nick,remain) = name.split('!')
    (user,host) = remain.split('@')
    # client.whois(nick)
    if message.lower().find("ask") == 0:
      return self.ask(client, nick, message)
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
    return False

  def addUserChannelAssociation(self, user, channel):
    if user not in self.userChannelMap:
      self.userChannelMap[user] = set()
    self.userChannelMap[user].add(channel)

    if channel not in self.channelUserMap:
      self.channelUserMap[channel] = set()
    self.userChannelMap[user].add(channel)
    self.channelUserMap[channel].add(user)

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
