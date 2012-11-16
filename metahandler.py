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

import yaml

class MetaHandler:
  def __init__(self, modules):
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
      self.messageHandlers.append(
        {'module': m, 'classname': module['class'], 'object': c(module["args"])})

  def handleEvent(self, methodName, *args):
    handled = False
    for handler in self.messageHandlers:
      if not handled and methodName in dir(handler['object']):
        method = getattr(handler['object'], methodName, False)
        if callable(method):
          handled = method(*args)
