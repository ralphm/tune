from twisted.words.protocols.jabber.client import IQ
from twisted.words.protocols.jabber import jid, xmlstream
import rhythmbox

NS_PUBSUB = "http://jabber.org/protocol/pubsub"
NS_TUNE = "http://jabber.org/protocol/tune"

class TunePublisher:

	def __init__(self, pubsub_service, pubsub_node):
		self.pubsub_service = pubsub_service
		self.pubsub_node = pubsub_node
		self.xmlstream = None
		self.rb = None
		self.playing = False
		self.song = None
	
	def publish(self):
		print "yeah"
		iq = IQ(self.xmlstream, "set")
		iq["to"] = self.pubsub_service
		iq.addElement((NS_PUBSUB, "pubsub"), NS_PUBSUB)
		iq.pubsub.addElement("publish")["node"] = self.pubsub_node
		iq.pubsub.publish.addElement("item")["id"] = "current"
		tune = iq.pubsub.publish.item.addElement((NS_TUNE, "tune"))

		if self.song and self.playing:
			title = self.song.title
			if title.endswith('.mp3') or title.endswith('.ogg'):
				title = title[:-4]
			tune.addElement("title", None, title)
			if (self.song.artist):
				tune.addElement("artist", None, self.song.artist)
			if (self.song.album):
				tune.addElement("source", None, self.song.album)
			if (self.song.track_number > 0):
				tune.addElement("track", None, str(self.song.track_number))
			if (self.song.duration):
				tune.addElement("length", None, str(self.song.duration))
			
		iq.send()
	
	def on_song(self, song):
		self.song = song
		if self.playing:
			self.publish()

	def on_playing(self, playing):
		if playing != self.playing:
			self.playing = playing
			if self.song or not self.playing:
				self.publish()

	def on_rb_connected(self, object):
		self.playing = self.rb.get_playing()
		self.song = self.rb.get_song()
		self.publish()

	def on_rb_disconnected(self, object):
		self.song = None
		if self.playing:
			self.playing = False
			self.publish()

	def connected(self, xmlstream):
		self.xmlstream = xmlstream
		if not self.rb:
			self.rb = rhythmbox.Rhythmbox()
			self.rb.addObserver('//event/song', self.on_song)
			self.rb.addObserver('//event/playing', self.on_playing)
			self.rb.addObserver('//event/connected', self.on_rb_connected)
			self.rb.addObserver('//event/disconnected', self.on_rb_disconnected)
			self.playing = self.rb.get_playing()
			self.song = self.rb.get_song()
		self.publish()
