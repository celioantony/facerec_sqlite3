from __future__ import print_function
import argparse
import time
import logging
from imutils.video import VideoStream
from stream import VideoStreamGUI
from queue import Queue
from faces.recognition import RecognitionWorker
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


def main():

    # constant to size of recognition workers
    recog_limit = 1
    
    # size queue to draw recognition
    queue_limit_stream = 10
    # size queue to recognition frame
    queue_limit_recog = 100
    # time float to capture frame and recognition
    capframe_time_limit = 0.1
    
    queue_stream = Queue(maxsize=queue_limit_stream)
    queue_recog = Queue(maxsize=queue_limit_recog)

    recognition_workers = [
        RecognitionWorker(queue_recog, queue_stream, 'ThreadRecog-{}'.format(_)) \
            for _ in range(recog_limit)
    ]

    print(' ')
    for worker in recognition_workers:
        worker.daemon = True
        worker.start()
        logger.info('Thread: {} started.'.format(worker.name))
        
    queue_recog.join()
    queue_stream.join()

    video_stream_gui = VideoStreamGUI(vs, queue_recog, queue_stream, capframe_time_limit)
    video_stream_gui.root.mainloop()


if __name__ == '__main__':
    main()
