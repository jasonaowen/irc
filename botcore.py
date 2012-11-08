# botcore.py
# This is the common core of the irc bot which parses the config file,  makes
# the connection to the irc server, loads the specified modules, joins the
# channels, and dispatches the various messages.

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

from twisted.internet import protocol, reactor, ssl
from twisted.words.protocols import irc
import sys
import yaml

class BotCore(irc.IRCClient):
  def _get_username(self):
    return self.factory.username
  def _get_password(self):
    return self.factory.password
  def _get_nickname(self):
    return self.factory.nickname
  username = property(_get_username)
  password = property(_get_password)
  nickname = property(_get_nickname)

  def signedOn(self):
    print "Signed on as %s." % (self.nickname,)
    for channel in self.factory.channels:
      print "Joining %s with key %s..." % (channel["name"], channel["key"],)
      if "ChanservInvite" in channel and channel["ChanservInvite"] == True:
        self.msg("Chanserv", "invite %s" % (channel["name"],))
      self.join(channel["name"], channel["key"])

  def action(self, user, channel, data):
    self.handleEvent("action", self, channel, user, data)

  def irc_unknown(self, prefix, command, params):
    self.handleEvent("unknownCommand", self, prefix, command, params)

  def joined(self, channel):
    self.handleEvent("joined", self, channel)

  def kickedFrom(self, channel, kicker, message):
    self.handleEvent("kickedFrom", self, channel, kicker, message)

  def modeChanged(self, user, channel, set, modes, args):
    self.handleEvent("modeChanged", self, user, channel, set, modes, args)

  def nickChanged(self, nick):
    self.handleEvent("nickChanged", self, nick)
    self.nickname = nick

  def noticed(self, user, channel, message):
    self.handleEvent("notice", self, channel, user, message)

  def privmsg(self, user, channel, msg):
    if channel == self.nickname:
      self.handleEvent("privateMessage", self, user, msg)
    else:
      self.handleEvent("channelMessage", self, channel, user, msg)

  def userJoined(self, user, channel):
    self.handleEvent("userJoined", self, user, channel)

  def userLeft(self, user, channel):
    self.handleEvent("userLeft", self, user, channel)

  def userQuit(self, user, quitMessage):
    self.handleEvent("userQuit", self, user, quitMessage)

  def userRenamed(self, oldname, newname):
    self.handleEvent("userRenamed", self, oldname, newname)

  def handleEvent(self, methodName, *args):
    handled = False
    for handler in self.factory.messageHandlers:
      if not handled and methodName in dir(handler):
        method = getattr(handler, methodName, False)
        if callable(method):
          handled = method(*args)

class BotCoreFactory(protocol.ClientFactory):
  protocol = BotCore

  def __init__(self, username, password, operator, nickname, channels, modules):
    self.username = username
    self.password = password
    self.operator = operator
    self.nickname = nickname
    self.channels = channels

    self.messageHandlers = []
    for module in modules:
      m = __import__(module["module"])
      c = getattr(m, module["class"])
      print "Adding class '%s' from module '%s' as message handler." % \
        (module["class"], module["module"],)
      if hasattr(module["args"], "get") and module["args"].has_key("yaml"):
        yamlFileName = module["args"].pop("yaml")
        print "  Loading yaml file '%s'." % (yamlFileName,)
        print "  Passing argument '%s'." % (module["args"],)
        yamlFile = open(yamlFileName)
        module["args"]["yaml"] = yaml.load(yamlFile)
        yamlFile.close()
      else:
        print "  Passing argument '%s'." % (module["args"],)
      self.messageHandlers.append(c(module["args"]))

  def clientConnectionLost(self, connector, reason):
    print "Lost connection (%s), reconnecting." % (reason,)
    connector.connect()

  def clientConnectionFailed(self, connector, reason):
    print "Could not connect: %s" % (reason,)

if __name__ == "__main__":
  if len(sys.argv) != 2:
    print "Usage: python %s config.yaml" % (__file__,)
    sys.exit(1)

  configFile = open(sys.argv[1])
  config = yaml.load(configFile)
  configFile.close()

  bcf = BotCoreFactory(config["irc"]["server"]["username"],
                       config["irc"]["server"]["password"],
                       config["irc"]["operator"],
                       config["irc"]["nickname"],
                       config["irc"]["channels"],
                       config["modules"])

  if config["irc"]["server"]["ssl"]:
    reactor.connectSSL(config["irc"]["server"]["address"],
                       config["irc"]["server"]["port"],
                       bcf, ssl.ClientContextFactory())
  else: # not ssl
    reactor.connectTCP(config["irc"]["server"]["address"],
                       config["irc"]["server"]["port"],
                       bcf)
  reactor.run()
