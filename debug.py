# debug.py
# Print every message received.

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

import datetime

class DebugHandler:
  def __init__(self, args):
    if args is not None and "ignore" in args:
      self.ignore = set(args["ignore"])
    else:
      self.ignore = set()
  def action(self, client, channel, name, message):
    self.log(client, "%s/%s did %s" % (channel, name, message,))
    return False
  def channelMessage(self, client, channel, name, message):
    self.log(client, "%s/%s: %s" % (channel, name, message,))
    return False
  def joined(self, client, channel):
    self.log(client, "Joined %s." % (channel,))
    return False
  def kickedFrom(self, client, channel, kicker, message):
    self.log(client, "Kicked from %s by %s because %s." % (channel, kicker, message,))
    return False
  def modeChanged(self, client, user, channel, set, modes, args):
    # Mode change: user: ChanServ!chanserv@services.irc.cat.pdx.edu, channel: #storytime-test, set: True, modes: o, args: ('Starybot',)
    self.log(client, "%s/%s set [%s%s %s]" % (channel, user, self.strFor(set), modes, args,))
  def nickChanged(self, client, nick):
    self.log(client, "Nickname changed to %s" % (nick,))
    return False
  def notice(self, client, channel, user, message):
    self.log(client, "Notice on channel %s by user %s: %s" % (channel, user, message,))
    return False
  def privateMessage(self, client, name, message):
    self.log(client, "Private message from %s: %s" % (name, message,))
    return False
  def unknownCommand(self, client, prefix, command, params):
    if command not in self.ignore:
      self.log(client, "%s %s %s" % (prefix, command, params,))
    return False
  def userJoined(self, client, user, channel):
    self.log(client, "%s joins %s" % (user, channel,))
    return False
  def userLeft(self, client, user, channel):
    self.log(client, "%s leaves %s" % (user, channel,))
    return False
  def userQuit(self, client, user, quitMessage):
    self.log(client, "%s quits: %s" % (user, quitMessage,))
    return False
  def userRenamed(self, client, oldname, newname):
    self.log(client, "%s is now %s" % (oldname, newname,))
    return False
  def log(self, client, message):
    print "%s %s: %s" % (client.nickname, self.now(), message,)
  def now(self):
    return datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
  def strFor(self, set):
    if set:
      return "+"
    else:
      return "-"
