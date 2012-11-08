# episerv.py
# flood out nibzserv and try to steal its nick

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

import random

class EpiServ:
  def __init__(self, args):
    self.accessories = args["accessories"]
    self.arena = args["arena"]
    self.arenaKey = args["arenaKey"]
    self.target = args["target"]
    self.messages = args["messages"]
    self.lastKicker = None
  def joined(self, client, channel):
    if channel == self.arena and self.lastKicker is not None:
      if self.lastKicker == self.target:
        self.sendMessageToChannel(client, channel, "rejoinWar")
      elif self.lastKicker in self.accessories:
        self.sendMessageToChannel(client, channel, "rejoinAccessory")
      else:
        self.sendMessageToChannel(client, channel, "rejoin")
      return True
    else:
      return False
  def kickedFrom(self, client, channel, kicker, message):
    self.lastKicker = kicker
    if kicker == self.target:
      self.sendMessageToUser(client, kicker, "kickedWar")
    elif kicker in self.accessories:
      self.sendMessageToUser(client, kicker, "kickedAccessory")
    else:
      self.sendMessageToUser(client, kicker, "kicked")
    if channel == self.arena:
      client.join(self.arena, self.arenaKey)
    return True
  def userQuit(self, client, user, quitMessage):
    if user.split("!")[0] == self.target:
      client.setNick(self.target)
      self.sendMessageToChannel(client, self.arena, "win")
    return True

  def sendMessageToChannel(self, client, channel, message):
    if message in self.messages:
      client.say(channel, random.choice(self.messages[message]).strip()
        % {"kicker": self.lastKicker, "target": self.target, "arena": self.arena})

  def sendMessageToUser(self, client, nick, message):
    if message in self.messages:
      client.msg(nick, random.choice(self.messages[message]).strip()
        % {"kicker": self.lastKicker, "target": self.target, "arena": self.arena})
