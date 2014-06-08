import thread

import ao
import mad

AO_DEVICE_INDEX = 0


class MadAoPlayer():

   def __init__(self, filename, **kwargs):
      self.filename = filename
      self.ao_device = kwargs.get('ao_device', None)
      if not self.ao_device:
         self.ao_device = ao.AudioDevice(AO_DEVICE_INDEX)
      self.mad_resource = mad.MadFile(self.filename)
      self.length = self.mad_resource.total_time()
      self.elapsed = 0
      self.thread_instance = None

   def get_ao_device(self):
      return self.ao_device

   def get_length(self):
      return self.length

   def get_position(self):
      return self.mad_resource.current_time()

   def _play_thread(self):
       try:
           while self.keep_going:
               buffer = self.mad_resource.read()
               if buffer is None:
                   break
               self.ao_device.play(buffer, len(buffer))
       except:
           pass
           #Player_madao :: play_internal :: Something went terribly terribly wrong.

       if self.callback and self.keep_going:
           #Player_Madao :: play_internal :: Executing callback"
           self.callback()

   def play(self, callback=None):
       self.callback = callback
       if self.thread_instance:
           #Player_madao :: play :: Tried to start, but already playing"
           return
       self.keep_going = True
       try:
           #Player_madao :: play :: starting new play thread"
           self.thread_instance = thread.start_new_thread(self._play_thread, ())
       except:
           pass
           #Player_madao :: play :: Could not start new play thread"

   def stop(self):
       if not self.thread_instance:
           #Player :: stop :: Tried to stop, but not playing"
           return
       self.keep_going = False
       self.callback = None
