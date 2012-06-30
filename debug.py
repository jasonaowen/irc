class DebugHandler:
  def __init__(self, args):
    pass
  def privateMessage(self, client, name, message):
    print "Private message from %s: %s" % (name, message,)
    return False
  def channelMessage(self, client, channel, name, message):
    print "%s/%s: %s" % (channel, name, message,)
    return False
  def unknownCommand(self, client, prefix, command, params):
    print "%s %s %s" % (prefix, command, params,)
    return False
  def notice(self, client, channel, user, message):
    print "Notice on channel %s by user %s: %s" % (channel, user, message,)
    return False
