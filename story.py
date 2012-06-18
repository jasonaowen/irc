from twisted.words.protocols import irc

class Storybot:
  def privateMessage(self, client, name, message):
    return False
  def channelMessage(self, client, channel, name, message):
    (nick,remain) = name.split('!')
    (user,host) = remain.split('@')
    client.whois(nick)
    return False
  def unknownCommand(self, client, prefix, command, params):
    if command == '330' or command == 'RPL_WHOISACCOUNT':
      print "Nickname %s is signed in to account %s" % \
        (params[1], params[2])
    elif command == 'RPL_WHOISSERVER':
      print "%s is on server %s" % (params[1], params[2])
    return False

class User:
  def __init__(self, username):
    pass
