import yaml
class HelpHandler:
  def __init__(self, messageFilePath):
    messageFile = open(messageFilePath)
    self.messages = yaml.load(messageFile)
    messageFile.close()

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
