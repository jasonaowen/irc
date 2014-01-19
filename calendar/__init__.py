# Google Calendar watcher module

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

from apiclient.discovery import build
import datetime
from dateutil import parser
from pytz import timezone
from twisted.words.protocols import irc
from twisted.internet import reactor

class ConfigurationException(Exception):
  pass

class Calendar:
  def __init__(self, args):
    if args is None:
      raise ConfigurationException('no arguments')
    if 'developerKey' not in args:
      raise ConfigurationException('developer key not specified')

    self.service = build('calendar', 'v3', developerKey=args['developerKey'])
    self.pendingEvents = []
    self.calendars = {}
    self.channelWatches = {}
    self.todaysEvents = {}
    if 'timezone' in args:
      self.timezone = timezone(args['timezone'])
    else:
      self.timezone = timezone('UTC')
    if 'calendars' in args:
      for calendar in args['calendars']:
        self.calendars[calendar['name']] = calendar['calendarId']
        self.todaysEvents[calendar['name']] = self.getEventsForCalendarAndDate(
          calendar['calendarId'],
          datetime.datetime.now(self.timezone)
        )
    if 'channels' in args:
      for channel in args['channels']:
        self.channelWatches[ channel['name'] ] = channel['calendars']
    if 'startNotice' in args:
      self.startNotice = args['startNotice']
    else:
      self.startNotice = 10

  def joined(self, client, channel):
    if channel in self.channelWatches:
      for calendar in self.channelWatches[channel]:
        for event in self.todaysEvents[calendar]:
          self.addEventStartingCallback(client, channel, event)
          self.addEventEndingCallback(client, channel, event)
    return False

  def channelMessage(self, client, channel, name, message):
    return False
  def privateMessage(self, client, name, message):
    return False

  def addEventStartingCallback(self, client, channel, event):
    now = datetime.datetime.now(self.timezone)
    start = event['start'] - datetime.timedelta(minutes=self.startNotice)
    if (now > start):
      return
    delta = start - now
    self.pendingEvents.append(reactor.callLater(
      delta.total_seconds(),
      self.eventStarting,
      client,
      channel,
      event
    ))

  def eventStarting(self, client, channel, event):
    message = "%(event)s is starting in %(location)s in %(notice)i minutes" % {
      "event": event['name'],
      "location": event['calendarName'],
      "notice": self.startNotice,
    }
    client.say(channel, message.encode('utf-8', 'replace'))

  def addEventEndingCallback(self, client, channel, event):
    now = datetime.datetime.now(self.timezone)
    if (now > event['end']):
      return
    delta = event['end'] - now
    reactor.callLater(
      delta.total_seconds(),
      self.eventEnding,
      client,
      channel,
      event
    )

  def eventEnding(self, client, channel, event):
    message = "%(event)s is ending in %(location)s" % {
      "event": event['name'],
      "location": event['calendarName'],
    }
    client.say(channel, message.encode('utf-8', 'replace'))

  def getEventsForCalendarAndDate(self, calendarId, date):
    timeMin = self.midnight(date)
    timeMax = date + datetime.timedelta(days=1)
    eventCall = self.service.events().list(
      calendarId = calendarId,
      timeMin = timeMin.isoformat(),
      timeMax = timeMax.isoformat()
    )
    response = eventCall.execute()
    return self.parseResponse(response)

  def midnight(self, date):
    midnight = datetime.datetime.combine(date, datetime.time.min)
    if date.tzinfo is not None:
      midnight = midnight.replace(tzinfo=date.tzinfo)
    else:
      midnight.replace(tzinfo=self.timezone)
    return midnight

  def parseResponse(self, response):
    calendarName = response.get('summary')
    events = []
    for event in response.get('items', []):
      events.append({
        'calendarName': calendarName,
        'name': event['summary'],
        'start': parser.parse(event['start']['dateTime']),
        'end': parser.parse(event['end']['dateTime']),
      })
    return events
