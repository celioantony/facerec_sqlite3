from __future__ import print_function
import argparse
import time
import logging
from imutils.video import VideoStream
from stream import VideoStreamGUI
from multiprocessing import Process, managers
from queue import LifoQueue
from faces.recognition import RecognitionWorker, multiprocessor_recog
from settings import connection
from db.database import migrate

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

logger = logging.getLogger(__name__)

ap = argparse.ArgumentParser()
# ap.add_argument('-o', '--output', required=True, help='path to output directory to store snapshots')
ap = argparse.ArgumentParser()
ap.add_argument("-n", "--num-frames", type=int, default=100,
                help="# of frames to loop over for FPS test")
ap.add_argument('-p', '--picamera', type=int, default=-1,
                help='whether or not the Raspberry Pi camera should be used')
args = vars(ap.parse_args())

print('[INFO] warming up camera...')
vs = VideoStream(usePiCamera=args['picamera'] > 0).start()
time.sleep(2.0)

"""
Migrete database if does not exists
"""
migrate(connection)

class Manager(managers.BaseManager):
    pass
Manager.register('LifoQueue', LifoQueue)

def main():

    # constant to size of recognition workers
    recog_limit = 5
    
    # size queue to draw recognition
    queue_limit_stream = 1
    # size queue to recognition frame
    queue_limit_recog = 1
    # time float to capture frame and recognition
    capframe_time_limit = 0.001
    
    
    manager = Manager()
    manager.start()
    
    queue_stream = manager.LifoQueue(maxsize=queue_limit_stream)
    queue_recog = manager.LifoQueue(maxsize=queue_limit_recog)

    processes = list()
    for _ in range(recog_limit):
        process = Process(target=multiprocessor_recog, args=(
            queue_recog, queue_stream), name='Process-{}'.format(_))
        processes.append(process)
        process.start()
        logger.info('Process: {} started.'.format(process.name))

    video_stream_gui = VideoStreamGUI(vs, processes, queue_recog, queue_stream, capframe_time_limit)
    video_stream_gui.root.mainloop()


if __name__ == '__main__':
    main()
