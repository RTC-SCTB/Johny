import gi
gi.require_version('Gst', '1.0')
from gi.repository import Gst, GObject
import sys
import time
Gst.init(sys.argv)

s = """rtpbin name=rtpbin buffer-mode=1 v4l2src device=/dev/video0 !
image/jpeg, width=(int)1280, height=(int)480, pixel-aspect-ratio=(fraction)1/1, framerate=(fraction)30/1 !
rtpjpegpay ! rtpbin.send_rtp_sink_0 rtpbin.send_rtp_src_0 !
udpsink port=5000 host=127.0.0.1 name=vrtpsink_l rtpbin.send_rtcp_src_0 !
udpsink port=5001 host=$DEST sync=false async=false name=vrtcpsink_l udpsrc port=5005 name=vrtcpsrc_l ! rtpbin.recv_rtcp_sink_0"""
pipeline = Gst.parse_launch(s) 
pipeline.set_state(Gst.State.PLAYING)
time.sleep(10)
pipeline.set_state(Gst.State.NULL)
time.sleep(3)
pipeline = Gst.parse_launch(s) 
pipeline.set_state(Gst.State.PLAYING)
