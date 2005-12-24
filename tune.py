#!/usr/local/bin/python

import sys
from twisted.internet import gtk2reactor
gtk2reactor.install()
from twisted.internet import reactor

from twisted.python import usage
from twisted.application import internet
from twisted.words.protocols.jabber import client, jid, xmlstream
import publisher

class Options(usage.Options):
	optParameters = [
		["username", "u", None,				"your Jabber username"],
		["host", "h", None,					"the Jabber server"],
		["resource", "r", "tune_publisher",	"the Jabber resource"],
		["secret", "", None,				"your password"],
		["port", "p", 5222,					"the Jabber server's port"],
		["service", "s", None,				"the pubsub service"],
		["node", "n", None,					"the pubsub node"]
	]

	def postOptions(self):
		if (self["username"] == None or
		   self["host"] == None or
		   self["secret"] == None or
		   self["service"] == None or
		   self["node"] == None):
		   raise usage.UsageError, "Please provide all parameters"


config = Options()
try:
	config.parseOptions()
except usage.UsageError, errortext:
	print '%s: %s' % (sys.argv[0], errortext)
	Options().parseOptions(["--help"])
	sys.exit(1)

		
tp = publisher.TunePublisher(config["service"], config["node"])
j = jid.JID(tuple=(config["username"], config["host"], config["resource"]))
cf = client.basicClientFactory(j, config["secret"])
cf.addBootstrap(xmlstream.STREAM_AUTHD_EVENT, tp.connected)
reactor.connectTCP(config["host"], config["port"], cf)
reactor.run()
