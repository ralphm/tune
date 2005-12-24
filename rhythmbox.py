import bonobo
import semaphore
from twisted.words.xish import utility

IID_RHYTHMBOX = "OAFIID:GNOME_Rhythmbox"
IID_ACTIVATION = "OAFIID:Bonobo_Activation_EventSource"
IDL_EVENTSOURCE = "IDL:Bonobo/EventSource:1.0"
EVT_REG = "Bonobo/ObjectDirectory:activation:register"
EVT_UNREG = "Bonobo/ObjectDirectory:activation:unregister"
EVT_SONG = "Bonobo/Property:change:song"
EVT_PLAYING = "Bonobo/Property:change:playing"

class Rhythmbox(utility.EventDispatcher):
	def __init__(self):
		utility.EventDispatcher.__init__(self)
		self.semaphore = semaphore.Semaphore(1)
		self.connected = False
		self.monitor_activation()
		self.connect()

	def monitor_activation(self):
		es = bonobo.get_object(IID_ACTIVATION, IDL_EVENTSOURCE)
		bonobo.event_source_client_add_listener(es, self.on_register, EVT_REG)
		bonobo.event_source_client_add_listener(es, self.on_unregister, EVT_UNREG)
		print "Watching application activations"

	def connect(self):
		if not self.connected:
			try:
				self.rhythmbox = bonobo.activation.activate_from_id(IID_RHYTHMBOX, 0, None)
				self.connected = True
			except Exception:
				self.connected = False
				return

			self.dispatch(False, '//event/connected')
			props = self.rhythmbox.getPlayerProperties()
			bonobo.event_source_client_add_listener(props, self.on_song, EVT_SONG)
			bonobo.event_source_client_add_listener(props, self.on_playing, EVT_PLAYING)
	
	def check_connection(self):
		if self.connected:
			try:
				song = self.rhythmbox.getPlayerProperties()
				getValue("playing")
			except Exception:
				self.dispatch(None, '//event/disconnected')
				self.connected = False

	def get_song(self):
		try:
			props = self.rhythmbox.getPlayerProperties()
			return props.getValue("song").value()
		except Exception:
			return None

	def get_playing(self):
		try:
			props = self.rhythmbox.getPlayerProperties()
			return props.getValue("playing").value()
		except Exception:
			return None

	def on_register(self, *args, **kwargs):
		self.semaphore.run(self.connect)

	def on_unregister(self, *args, **kwargs):
		self.semaphore.run(self.check_connection)

	def on_song(self, listener, event_name, any):
		self.dispatch(any.value(), '//event/song')

	def on_playing(self, listener, event_name, any):
		self.dispatch(any.value(), '//event/playing')
