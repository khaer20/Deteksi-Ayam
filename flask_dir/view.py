from flask import Blueprint,render_template,Response,redirect,session,request
from .deteksi import DeteksiYolo
from pygrabber.dshow_graph import FilterGraph
import pythoncom
from win32com.client import Dispatch
from twilio.rest import Client
import asyncio

views = Blueprint('views', __name__)

#pythoncom function
def pythonCom():
        # Initialize COM for this thread
        pythoncom.CoInitialize() 

        # Now, safely use win32com.client
        excel_app = Dispatch("Excel.Application")
        excel_app.Visible = True
        # ... perform desired Excel operations ...
        excel_app.Quit()


@views.route('/video_feed')
def video_feed():
    """Video streaming route. Put this in the src attribute of an img tag."""
    cam = session['cam']
    deteksi = DeteksiYolo(nomor_camera=int(cam))
    return Response(deteksi.gen_frames(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')


@views.route('detect/<int:cam>')
def detect(cam):
    session['cam'] = int(cam)
    return render_template('index.html')

@views.route('device')
def device():

    pythonCom()
    graph = FilterGraph()
    devices = graph.get_input_devices()
    list = []

    for i, device in enumerate(devices):
            print(f"{i}: {device}")
            list.append(str(device))
    pythoncom.CoUninitialize()

    return render_template('device.html',list=list)

@views.route('/')
def home():
    return render_template('home.html')


     