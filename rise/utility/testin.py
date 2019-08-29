import gi
gi.require_version('Gst', '1.0')
from gi.repository import Gst, GObject
import sys
import time
Gst.init(sys.argv)

s = """rtpbin name=rtpbin udpsrc caps="application/x-rtp,media=(string)video,clock-rate=(int)90000,
encoding-name=(string)JPEG,payload=(int)26" port=5000 ! rtpbin.recv_rtp_sink_0 rtpbin. !
rtpjpegdepay ! jpegdec ! videoconvert ! autovideosink sync=false udpsrc port=5001 !
rtpbin.recv_rtcp_sink_0 rtpbin.send_rtcp_src_0 ! udpsink port=5005 host=127.0.0.1 sync=false async=false"""

pipeline = Gst.parse_launch(s)
pipeline.set_state(Gst.State.PLAYING)
time.sleep(10)
pipeline.set_state(Gst.State.NULL)
time.sleep(3)
pipeline = Gst.parse_launch(s) 
pipeline.set_state(Gst.State.PLAYING)
