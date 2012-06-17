from twisted.words.protocols import irc
from twisted.internet import protocol
import yaml

class Storybot(irc.IRCClient):
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
      print "Joining %s with key %s..." % (channel["name"], channel["key"])
      self.join(channel["name"], channel["key"])

  def joined(self, channel):
    print "Joined %s." % (channel,)

  def privmsg(self, user, channel, msg):
    if channel == self.nickname:
      print "PRIVMSG from %s: %s" % (user, msg,)
    else:
      print "%s: %s said %s" % (channel, user, msg,)

  def nickChanged(self, nick):
    print "Nickname changed to %s" % (nick,)

class StorybotFactory(protocol.ClientFactory):
  protocol = Storybot

  def __init__(self, username, password, operator, nickname, channels, messages):
    self.username = username
    self.password = password
    self.operator = operator
    self.nickname = nickname
    self.channels = channels
    self.messages = messages

  def clientConnectionLost(self, connector, reason):
    print "Lost connection (%s), reconnecting." % (reason,)
    #connector.connect()

  def clientConnectionFailed(self, connector, reason):
    print "Could not connect: %s" % (reason,)

import sys
from twisted.internet import reactor, ssl

if __name__ == "__main__":
  configFile = open("config.yaml")
  config = yaml.load(configFile)
  configFile.close()

  if config["irc"]["server"]["ssl"]:
    reactor.connectSSL(config["irc"]["server"]["address"],
                       config["irc"]["server"]["port"],
                       StorybotFactory(config["irc"]["server"]["username"],
                                       config["irc"]["server"]["password"],
                                       config["irc"]["operator"],
                                       config["irc"]["nickname"],
                                       config["irc"]["channels"],
                                       config["messages"]),
                       ssl.ClientContextFactory())
  else: # not ssl
    reactor.connectTCP(config["irc"]["server"]["address"],
                       config["irc"]["server"]["port"],
                       StorybotFactory(config["irc"]["nick"], config["irc"]["channels"]))
  reactor.run()
