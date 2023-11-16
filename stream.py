from __future__ import print_function
from PIL import Image, ImageTk
import tkinter as tk
import threading
import datetime
import imutils
import cv2
import os
import numpy as np
from faces.recognition import face_identity


class VideoBootstrap:

    def __init__(self, vs, output):
        self.vs = vs
        self.output = output
        self.thread = None
        self.stopEvent = None

        self.root = tk.Tk()
        self.panel = None

        self.rgb_frame = []

        # btn = tk.Button(self.root, text='Snapshot', command=self.snapshot)
        # btn.pack(side="bottom", fill="both", expand="yes", padx=10, pady=10)

        self.stopEvent = threading.Event()
        self.thread = threading.Thread(target=self.video_loop, args={})
        self.thread.start()

        self.root.wm_title("PyImageSearch PhotoBooth")
        self.root.wm_protocol("WM_DELETE_WINDOW", self.on_close)

    def video_loop(self):
        try:
            while not self.stopEvent.is_set():
                self.frame = self.vs.read()

                self.frame = imutils.resize(self.frame, width=1320)

                self.rgb_frame = np.ascontiguousarray(self.frame[:, :, ::-1])

                identified_people = face_identity(self.rgb_frame)
                
                if len(identified_people) > 0:
                
                    for people in identified_people:
                        fullname = people['fullname']
                        registration = people['registration']
                        top, right, bottom, left = people['frame_pos']

                        # Draw a box around the face
                        cv2.rectangle(self.frame, (left, top),
                                      (right, bottom), (0, 0, 255), 2)

                        # Draw a label with a name below the face
                        cv2.rectangle(self.frame, (left, bottom - 15),
                                      (right, bottom), (0, 0, 255), cv2.FILLED)
                        
                        font = cv2.FONT_HERSHEY_DUPLEX
                        cv2.putText(self.frame, fullname, (left + 6, bottom - 6),
                                    font, 0.5, (255, 255, 255), 1)
                        cv2.putText(self.frame, registration, (left + 6, bottom + 8),
                                    font, 0.5, (255, 255, 255), 1)

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

        except RuntimeError:
            print('[INFO] COUNGHT A RuntimeError')

    def snapshot(self):
        ts = datetime.datetime.now()
        filename = "{}.jpg".format(ts.strftime('%Y-%m%d_%H-%M-%S'))
        p = os.path.sep.join((self.output, filename))
        cv2.imwrite(p, self.frame.copy())
        print('[INFO] saved {}'.format(filename))

    def on_close(self):
        print('[INFO] closing...')
        self.stopEvent.set()
        self.vs.stop()
        self.root.quit()
