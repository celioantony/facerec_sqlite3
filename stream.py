from __future__ import print_function
import tkinter as tk
import threading
import cv2
import numpy as np
import logging
# from faces.recognition import face_identity
import imutils
from PIL import Image, ImageTk
from threading import Thread

logger = logging.getLogger(__name__)

class VideoStreamGUI:

    def __init__(self, stream, processes, queue_recog, queue_stream, capframe_time, name='WebcamVideoStream'):
        self.stream = stream
        
        # processes to recognition
        self.processes = processes
        
        # time of capture frame to recognition
        self.capframe_time = capframe_time

        # self.output = output
        self.name = name

        # flag to stop thread when needed
        self.stopped_stream = threading.Event()

        # Capture frame
        self.stopped_capframe = threading.Event()

        # Queue of frames
        self.queue_recog = queue_recog

        # Queue of faces on stream
        self.queue_stream = queue_stream

        # recognized people
        self.people = []
        
        # User GUI
        self.root = tk.Tk()
        self.panel = None

        # initialization stream
        self.t_stream = self.start()

        # initialization capture frame
        self.t_capframe = self.start_capture_frame()

        # initialization recognition worker
        # draw animation recognition in video
        self.t_recworker = self.start_recognition_worker()
        

        # initialize face recognition
        # self.start_recognition()

        # self.thread = None
        # self.stopEvent = None

        # btn = tk.Button(self.root, text='Snapshot', command=self.snapshot)
        # btn.pack(side="bottom", fill="both", expand="yes", padx=10, pady=10)

        # self.stopEvent = threading.Event()
        # self.thread = threading.Thread(target=self.video_loop, args={})
        # self.thread.start()

        self.root.wm_title("Face Recognition Python")
        self.root.wm_protocol("WM_DELETE_WINDOW", self.stop)

    def start(self):
        thread = Thread(target=self.update, name=self.name, args=())
        thread.daemon = True
        thread.start()
        
        print(' ')
        logger.info('Thread stream started.')
        
        return thread

    def start_capture_frame(self):
        # time in float to capture current frame
        thread = Thread(target=self.capture_frame,
                        name='Thread Capture Frame', args=(self.capframe_time,))
        thread.daemon = True
        thread.start()
        
        print(' ')
        logger.info('Thread start_capture_frame started.')
        
        return thread

    def start_recognition_worker(self):
        thread = Thread(target=self.recognition_worker,
                        name='Thread Capture Frame', args=())
        thread.daemon = True
        thread.start()
        
        print(' ')
        logger.info('Thread start_recognition_worker started.')
        
        return thread

    def update(self):
        try:
            while not self.stopped_stream.is_set():
                self.frame = self.stream.read()

                self.frame = imutils.resize(self.frame, width=800)
                
                self.draw_in_stream()

                self.display()

        except RuntimeError:
            print('[INFO] COUNGHT A RuntimeError') 

    def read(self):
        return self.frame

    def stop(self):
        self.stream.stop()
        self.stopped_stream.set()
        self.stopped_capframe.set()
        [process.terminate() for process in self.processes]
        self.root.destroy()

    def display(self):
        
        image = cv2.cvtColor(self.frame, cv2.COLOR_BGR2RGB)
        image = Image.fromarray(image)
        image = ImageTk.PhotoImage(image)

        if self.panel is None:
            self.panel = tk.Label(image=image)
            self.panel.image = image
            self.panel.pack(side="left", padx=10, pady=10)

        else:
            self.panel.configure(image=image)
            self.panel.image = image

    def draw_in_stream(self):
        if len(self.people) > 0:

            for p in self.people:
                fullname = p['fullname']
                registration = p['registration']
                top, right, bottom, left = p['frame_pos']

                # Draw a box around the face
                cv2.rectangle(self.frame, (left, top),
                              (right, bottom), (0, 0, 255), 2)

                # Draw a label with a name below the face
                cv2.rectangle(self.frame, (left, bottom - 15),
                              (right, bottom), (0, 0, 255), cv2.FILLED)

                font = cv2.FONT_HERSHEY_DUPLEX
                cv2.putText(self.frame, fullname, (left + 6, bottom - 6),
                            font, 0.5, (255, 255, 255), 1)
                # cv2.putText(self.frame, registration, (left + 6, bottom + 8),
                #             font, 0.5, (255, 255, 255), 1)

    def capture_frame(self, time):
        if time > 0:
            while not self.stopped_capframe.wait(time) \
                    and not self.stopped_capframe.is_set():
                self.queue_recog.put(self.read())
        else:
            while not self.stopped_capframe.is_set():
                self.queue_recog.put(self.read())

    def recognition_worker(self):
        while True:
            try:
                self.people = self.queue_stream.get()
            finally:
                pass
                # self.queue_stream.task_done()

    # def video_loop(self):
    #     try:
    #         while not self.stopEvent.is_set():
    #             self.frame = self.vs.read()

    #             self.frame = imutils.resize(self.frame, width=640)

            # self.rgb_frame = np.ascontiguousarray(self.frame[:, :, ::-1])

            # self.queue_recog.put(self.frame)

            # self.queue_recog.join()

            # identified_people = face_identity(self.rgb_frame)

            # if len(identified_people) > 0:

            #     for people in identified_people:
            #         fullname = people['fullname']
            #         registration = people['registration']
            #         top, right, bottom, left = people['frame_pos']

            #         # Draw a box around the face
            #         cv2.rectangle(self.frame, (left, top),
            #                       (right, bottom), (0, 0, 255), 2)

            #         # Draw a label with a name below the face
            #         cv2.rectangle(self.frame, (left, bottom - 15),
            #                       (right, bottom), (0, 0, 255), cv2.FILLED)

            #         font = cv2.FONT_HERSHEY_DUPLEX
            #         cv2.putText(self.frame, fullname, (left + 6, bottom - 6),
            #                     font, 0.5, (255, 255, 255), 1)
            #         cv2.putText(self.frame, registration, (left + 6, bottom + 8),
            #                     font, 0.5, (255, 255, 255), 1)

        #         image = cv2.cvtColor(self.frame, cv2.COLOR_BGR2RGB)
        #         image = Image.fromarray(image)
        #         image = ImageTk.PhotoImage(image)

        #         if self.panel is None:
        #             self.panel = tk.Label(image=image)
        #             self.panel.image = image
        #             self.panel.pack(side="left", padx=10, pady=10)

        #         else:
        #             self.panel.configure(image=image)
        #             self.panel.image = image

        # except RuntimeError:
        #     print('[INFO] COUNGHT A RuntimeError')

    # def snapshot(self):
    #     ts = datetime.datetime.now()
    #     filename = "{}.jpg".format(ts.strftime('%Y-%m%d_%H-%M-%S'))
    #     p = os.path.sep.join((self.output, filename))
    #     cv2.imwrite(p, self.frame.copy())
    #     print('[INFO] saved {}'.format(filename))

    # def on_close(self):
    #     print('[INFO] closing...')
    #     self.stopEvent.set()
    #     self.vs.stop()
    #     self.root.quit()
