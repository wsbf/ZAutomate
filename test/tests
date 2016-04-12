import sys

import ao
import mad

if len(sys.argv) < 2:
   print "Parameter: A path to an arbitrary MP3 file."
   sys.exit(1)

dev = ao.AudioDevice(0)
mr = mad.MadFile(sys.argv[1])

while True:
   buf = mr.read()
   if buf is None:
      print "Nothing more to play."
      sys.exit(0)
   dev.play(buf, len(buf))


