# domain.py
# Look up a domain's availability

# Copyright 2015 Jason Owen <jason.a.owen@gmail.com>
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
import xmlrpclib
from twisted.internet import reactor

def repeatLookup(handler, client, channel, domain):
  handler.doLookup(client, channel, domain)

class DomainHandler:
  def __init__(self, args):
    self.apiKey = args["apiKey"]
    self.api = xmlrpclib.ServerProxy('https://rpc.gandi.net/xmlrpc/')

  def channelMessage(self, client, channel, name, message):
    if message.lower().find("!domain") == 0:
      domain = message.split(' ')[1].lower()
      self.doLookup(client, channel, domain)
      return True
    return False

  def doLookup(self, client, channel, domain):
      self.log(client, "looking up domain: %s" % (domain,))
      result = self.api.domain.available(self.apiKey, [domain])
      self.log(client, "Got result: %s" % (result,))
      self.printOrCallback(client, channel, domain, result)

  def printOrCallback(self, client, channel, domain, result):
    if (result[domain] == 'pending'):
      self.log(client, "Scheduling callback for domain %s" % (domain,))
      reactor.callLater(1, repeatLookup, self, client, channel, domain)
    else:
      self.log(client, "Domain %s is %s" % (domain, result[domain],))
      client.say(channel, "The domain %s is %s." % (domain, result[domain],))

  def log(self, client, message):
    print "%s %s: %s" % (client.nickname, self.now(), message,)
  def now(self):
    return datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
