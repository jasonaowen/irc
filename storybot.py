from twisted.words.protocols import irc
from twisted.internet import protocol

class Storybot(irc.IRCClient):
  def _get_nickname(self):
    return self.factory.nickname
  def _get_password(self):
    return self.factory.password
  nickname = property(_get_nickname)
  password = property(_get_password)

  def signedOn(self):
    self.join(self.factory.channel)
    print "Signed on as %s." % (self.nickname,)

  def joined(self, channel):
    print "Joined %s." % (channel,)

  def privmsg(self, user, channel, msg):
    print "PRIVMSG from %s on channel %s: %s" % (user, channel, msg,)

class StorybotFactory(protocol.ClientFactory):
  protocol = Storybot

  def __init__(self, channel, nickname, password):
    self.channel = channel
    self.nickname = nickname
    self.password = password

  def clientConnectionLost(self, connector, reason):
    print "Lost connection (%s), reconnecting." % (reason,)
    #connector.connect()

  def clientConnectionFailed(self, connector, reason):
    print "Could not connect: %s" % (reason,)

import sys
from twisted.internet import reactor, ssl

if __name__ == "__main__":
  nick = sys.argv[1]
  password = sys.argv[2]
  chan = sys.argv[3]
  reactor.connectSSL('owenja.dyndns.org', 7000, StorybotFactory(chan, nick, password), ssl.ClientContextFactory())
  reactor.run()
