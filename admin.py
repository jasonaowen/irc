# admin.py
# Bot administration commands.

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

class Admin:
  def __init__(self, args):
    pass

  def privateMessage(self, client, name, message):
    nick = name.split('!')[0]
    if client.factory.operator != nick:
      return False

    if message.lower().find("!quit") == 0:
      self.quit(client, nick, message)
      return True
    else:
      return False

  def quit(self, client, nick, message):
    if len(message.split(' ')) == 1:
      client.quit()
    else:
      client.quit(message.split(' ', 1)[1])
