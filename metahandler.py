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
      (sys.modules[__name__], 'MetaMetaHandler', MetaMetaHandler(self)))
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
        (m, module['class'], c(module["args"])))

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
    if client.factory.operator == nick and message.lower() == "lsmod":
      client.msg(nick, ", ".join([x[1] for x in self.metaHandler.messageHandlers]))
