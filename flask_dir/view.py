from flask import Blueprint,render_template,Response,redirect,session,request
from .deteksi import DeteksiYolo
from twilio.rest import Client

views = Blueprint('views', __name__)



@views.route('/video_feed')
def video_feed():
    """Video streaming route. Put this in the src attribute of an img tag."""
    deteksi = DeteksiYolo()
    return Response(deteksi.gen_frames(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')


@views.route('detect')
def detect():
    return render_template('index.html')

@views.route('device')
def device():

    return render_template('device.html')

@views.route('/')
def home():
    return render_template('home.html')


     