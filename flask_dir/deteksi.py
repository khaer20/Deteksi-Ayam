import cv2
from ultralytics import YOLO
import supervision as sv
from typing import Dict, Iterable, List, Optional, Set
from twilio.rest import Client
import time
import asyncio
from datetime import datetime


class DeteksiYolo:
    
    def __init__(self,nomor_camera:int) -> None:
        # self.camera = cv2.VideoCapture(nomor_camera)  # konfigurasi kamera
        self.camera = cv2.VideoCapture('rtsp://192.168.1.12:554/stream0:0')  # konfigurasi kamera
        # for cctv camera use rtsp://username:password@ip_address:554/user=username_password='password'_channel=channel_number_stream=0.sdp' instead of camera
        self.model = YOLO('flask_dir/weightYOLOv9s.pt') # konfigurasi model YOLO
        self.COLORS = sv.ColorPalette.from_hex(["#E6194B", "#3CB44B", "#FFE119", "#3C76D1"]) # konfigurasi warna anotasi bounding box
        self.tracker = sv.ByteTrack()
        self.box_annotator = sv.BoxAnnotator(color=self.COLORS)
        self.label_annotator = sv.LabelAnnotator(color=self.COLORS, text_color=sv.Color.BLACK)
        self.trace_annotator = sv.TraceAnnotator(color=self.COLORS, position=sv.Position.CENTER, thickness=2, trace_length=100)
        self.tampung_kelas_tracker : Dict[int,int] = {}
        self.x = False
        self.minutes = 0

    
    # fitur mengambil detik jedah pesan ke whatsapp
    def minute(self):
        # Mendapatkan waktu sekarang
        current_time = datetime.now()

        # Mengambil detik
        minute_now = current_time.minute
        self.minutes = minute_now
    

    # fitur/function untuk kirim notif Whatsapp
    def notifWhatsapp(self):     
           
        account_sid = 'ACa0ce8a759e9ec1173cb589be5caf902b'
        auth_token = '234c333675f5a115c7162ee6879ec03c'
        client = Client(account_sid, auth_token)

        message = client.messages.create(
        from_='whatsapp:+14155238886',
        to='whatsapp:+6281524046616',
        body= f'Notifikasi Aplikasi Deteksi Kesehatan Ayam : Terdeteksi ayam dengan kondisi sakit'
        )
 

            


    def annotasiBoundingBox(self,frame,detections):

        # membuat label
        labels = [
            f'Class : {self.model.names[class_id]}, Track ID : {tracker_id}'
            for _, _, confidence, class_id, tracker_id, _ in detections
            ]
        frame = self.box_annotator.annotate(scene=frame, detections=detections)
        frame = self.label_annotator.annotate(scene=frame, detections=detections, labels=labels)
        frame = self.trace_annotator.annotate(scene=frame, detections=detections)

        return frame


    # fitur/function untuk seleksi kelas
    def seleksiKelas(self,tampung_detect: List[sv.Detections]):
        
        # looping/perulangan mengambil output deteksi yolo yang terdiri dari kelas dan tracker
        for detect in tampung_detect:
            # looping/perulangan untuk mendapatkan daftar id tracker 
            for tracker_id in detect.tracker_id:
                # looping/perulangan untuk mendapatkan daftar id class
                for class_id in detect.class_id:
                    
                    # membuat kumpulan data Dictonary untuk menampung daftar id tracker dan id kelas
                    self.tampung_kelas_tracker.setdefault(
                    'tracker_id',[])
                    self.tampung_kelas_tracker.setdefault(
                    'class',[])
                    
                    # mengecek id tracker sudah tertampung, jika tidak akan ditampung
                    if tracker_id not in self.tampung_kelas_tracker['tracker_id']:

                        # menampung atau menambahkan id tracker ke Dictonary
                        self.tampung_kelas_tracker['tracker_id'].append(tracker_id)
                        # menampung atau menambahkan id kelas ke Dictonary
                        self.tampung_kelas_tracker['class'].append(class_id)
                        
                        # Class ID 0 = Mati, 1 = Sakit dan 2 = Sehat
 
                        # mencari jika ada data dengan kelas ayam yang sakit berdasarkan data di dictonary
                        sakit = self.tampung_kelas_tracker['class'].count(1)
                        # mencari jika ada data dengan kelas ayam yang mati berdasarkan data di dictonary
                        mati = self.tampung_kelas_tracker['class'].count(0)
                        # menyeleksi jika ada ayam yang sakit
                        # sehat = self.tampung_kelas_tracker['class'].count(2)
                        # menyeleksi jika ada ayam yang sakit

                        if sakit:
                            # menjalankan fitur/function mengirim notif ke Whatsapp
                            if self.x == False:
                                self.notifWhatsapp()
                                self.x = True
                                self.minute()            
                        if mati:
                            # menjalankan fitur/function mengirim notif ke Whatsapp
                            if self.x == False:
                                self.notifWhatsapp()
                                self.x = True
                                self.minute()      
                        # if sehat:
                        #     # menjalankan fitur/function mengirim notif ke Whatsapp
                        #     if self.x == False:
                        #         self.notifWhatsapp()
                        #         self.x = True
                        #         self.detik()      
    def delay(self):
        current_time = datetime.now()
        minute_now = current_time.minute 
        
        if self.x == True and int(self.minutes) != int(minute_now):
            self.x = False

    def gen_frames(self):  # generate frame by frame from camera
        while True:
            # Capture frame-by-frame
            success, frame = self.camera.read()  # read the camera frame
            if not success:
                break
            else:
                
                self.delay()
                # menjalankan model pada frame dan mengatur nms untuk menghilangkan doble bounding box
                result = self.model(frame, agnostic_nms=True)[0]
                frame2 = frame.copy()
                ret, buffer = cv2.imencode('.jpg', frame)
                frame = buffer.tobytes()

                # mengatur format hasil deteksi yolo dengan yolov8
                detections = sv.Detections.from_ultralytics(result)

                # tambahkan tracker
                detections = self.tracker.update_with_detections(detections)

                # menampung detections
                tampung_detect = []
                tampung_detect.append(detections)
                
                # memanggil fitur/function seleksi kelas
                self.seleksiKelas(tampung_detect=tampung_detect)
                
                # memanggil fitur/function annotasi bounding box
                frame = self.annotasiBoundingBox(frame=frame2,detections=detections)

                # konversi frame agar dapat di tampilkan ke view
                ret, buffer = cv2.imencode('.jpg', frame)
                frame = buffer.tobytes()
                
                # mengirim frame menjadi objek ke tampilan website
                yield (b'--frame\r\n'
                    b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')  # concat frame one by one and show result


