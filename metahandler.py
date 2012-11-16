# metahandler.py
# Handles operations on handlers, including loading and dispatching events.

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

import sys
import yaml

class MetaHandler:
  def __init__(self, modules):
    self.messageHandlers = [] # (module, class name, instance of class, initial args)
    self.messageHandlers.append(
      (sys.modules[__name__], 'MetaMetaHandler', MetaMetaHandler(self), self))
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
      self.messageHandlers.append(
        (m, module['class'], c(module["args"]), module["args"]))

  def handleEvent(self, methodName, *args):
    handled = False
    for handler in [x[2] for x in self.messageHandlers]:
      if not handled and methodName in dir(handler):
        method = getattr(handler, methodName, False)
        if callable(method):
          handled = method(*args)

class MetaMetaHandler:
  def __init__(self, metaHandler):
    self.metaHandler = metaHandler

  def privateMessage(self, client, name, message):
    nick = name.split('!')[0]
    if client.factory.operator != nick:
      return False

    if message.lower() == "lsmod":
      self.listModules(client, nick)
      return True
    elif message.lower().find("args") == 0:
      self.showArgs(client, nick, message)
      return True
    else
      return False

  def listModules(self, client, nick):
    client.msg(nick, ", ".join([x[1] for x in self.metaHandler.messageHandlers]))

  def showArgs(self, client, nick, message):
    if len(message.split(' ')) != 2:
      client.msg(nick, "Syntax: args ModuleName")
    else:
      moduleName = message.split(' ')[1]
      if moduleName not in [x[1] for x in self.metaHandler.messageHandlers]:
        client.msg(nick, "No such module %s" % (moduleName,))
      else:
        client.msg(nick, "%s" % ([x[3] for x in self.metaHandler.messageHandlers if x[1] == moduleName][0]),)
