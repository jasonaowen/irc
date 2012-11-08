# join.py
# Join on invite

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

class Join:
  def __init__(self, args):
    self.channelKeyMap = {}
    self.joiningChannelUserMap = {}

  def privateMessage(self, client, name, message):
    (nick,remain) = name.split('!')
    (user,host) = remain.split('@')
    # client.whois(nick)
    if message.lower().find("join") == 0:
      return self.join(client, nick, message)
    return False

  def joined(self, client, channel):
    if channel in self.joiningChannelUserMap:
      del self.joiningChannelUserMap[channel]
    if channel in self.channelKeyMap:
      del self.channelKeyMap[channel]
    return False

  def kickedFrom(self, client, channel, kicker, message):
    if channel in self.joiningChannelUserMap:
      del self.joiningChannelUserMap[channel]
    if channel in self.channelKeyMap:
      del self.channelKeyMap[channel]

  def unknownCommand(self, client, prefix, command, params):
    if command == 'INVITE':
      (nick,remain) = prefix.split('!')
      channel = params[1]
      self.joiningChannelUserMap[channel] = nick
      if channel in self.channelKeyMap:
        client.join(channel, self.channelKeyMap[channel])
      else:
        client.join(channel)
      return True
    elif command == 'ERR_BADCHANNELKEY':
      channel = params[1]
      if channel in self.joiningChannelUserMap:
        if channel in self.channelKeyMap:
          client.msg(self.joiningChannelUserMap[channel],
            "Unable to join channel '%s': bad key '%s'." % (channel, self.channelKeyMap[channel],))
        else:
          client.msg(self.joiningChannelUserMap[channel],
            "Unable to join channel '%s': bad key. See 'help join'." % (channel,))
        del self.joiningChannelUserMap[channel]
      if channel in self.channelKeyMap:
        del self.channelKeyMap[channel]
    return False

  def join(self, client, user, message):
    params = message.split(' ')
    if len(params) != 3:
      return False
    channel = params[1]
    channelKey = params[2]
    self.channelKeyMap[channel] = channelKey
    client.msg(user, "Now invite me by saying '/invite %s %s'" % (client.nickname, channel,))
    return True
