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

import yaml
class DebugHandler:
  def __init__(self, args):
    pass
  def action(self, client, channel, name, message):
    print "%s/%s did %s" % (channel, name, message,)
    return False
  def channelMessage(self, client, channel, name, message):
    print "%s/%s: %s" % (channel, name, message,)
    return False
  def notice(self, client, channel, user, message):
    print "Notice on channel %s by user %s: %s" % (channel, user, message,)
    return False
  def privateMessage(self, client, name, message):
    print "Private message from %s: %s" % (name, message,)
    return False
  def unknownCommand(self, client, prefix, command, params):
    print "%s %s %s" % (prefix, command, params,)
    return False
