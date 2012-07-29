# help.py
# Read the help config file and respond to help commands (and unhandled
# commands that match the topic).

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

class HelpHandler:
  def __init__(self, messages):
    self.messages = messages

  def privateMessage(self, client, name, message):
    nick = name.split("!")[0]
    if message.lower() == "help":
      client.msg(nick, "Topics: %s" % (", ".join(self.messages.keys())))
      return True
    elif message.find("help") == 0:
      if self.messages.has_key(message[5:].lower()):
        for reply in self.messages[message[5:]]:
          client.msg(nick, reply.strip() % {"botname": client.nickname})
      else:
        client.msg(nick, "No help found for that topic.")
      return True
    elif message.lower() in self.messages:
      for reply in self.messages[message.lower()]:
        client.msg(nick, reply.strip() % {"botname": client.nickname})
      return True
    else:
      return False # no help found

  def channelMessage(self, client, channel, name, message):
    nick = name.split("!")[0]
    index = message.lower().find("help")
    if index == 0:
      print "Calling self.privateMessage"
      return self.privateMessage(client, name, message)
    elif index == 1 or (message.find(client.nickname) == 0 and index > 0):
      print "Calling self.privateMessage"
      return self.privateMessage(client, name, message[index:])
    else:
      return False
