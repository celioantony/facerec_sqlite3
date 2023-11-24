from __future__ import print_function
import argparse
import time
import logging
from imutils.video import VideoStream
from stream import VideoStreamGUI
from multiprocessing import Process, managers, cpu_count
from queue import LifoQueue
from faces.recognition import RecognitionWorker, multiprocessor_recog
from settings import connection
from db.database import migrate

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

logger = logging.getLogger(__name__)

ap = argparse.ArgumentParser()
# ap.add_argument('-o', '--output', required=True, help='path to output directory to store snapshots')
ap.add_argument("-mp", "--multiprocess", type=int, default=2, 
                help='# define the numbers of the process to recognition')
ap.add_argument("-n", "--num-frames", type=int, default=1,
                help="# of frames to loop over for FPS test")
ap.add_argument('-p', '--picamera', type=int, default=-1,
                help='whether or not the Raspberry Pi camera should be used')
ap.add_argument("-fc", "--frame-capture", type=float, default=0, 
                help="define the time to capture frame to recognition")
args = vars(ap.parse_args())

print('[INFO] warming up camera...')
vs = VideoStream(usePiCamera=args['picamera'] > 0).start()
time.sleep(2.0)

print(args)

multiprocess_number = args['multiprocess']

lifoqueue_maxsize = args['num_frames']

frame_capture_time = args['frame_capture']

"""
Migrete database if does not exists
"""
migrate(connection)

class Manager(managers.BaseManager):
    pass
Manager.register('LifoQueue', LifoQueue)

def main():
    
    print(' ')
    logger.info(' - Resume -')
    logger.info('Numbers of process to recognition: {}'.format(multiprocess_number))
    logger.info('LifoQueue size: {}'.format(lifoqueue_maxsize))
    print(' ')

    # constant to size of recognition workers
    recog_limit_worker = multiprocess_number
    
    # size queue to draw recognition
    queue_limit_stream = lifoqueue_maxsize
    # size queue to recognition frame
    queue_limit_recog = lifoqueue_maxsize
    # time float to capture frame and recognition
    capframe_time_limit = frame_capture_time
    
    
    manager = Manager()
    manager.start()
    
    queue_stream = manager.LifoQueue(maxsize=queue_limit_stream)
    queue_recog = manager.LifoQueue(maxsize=queue_limit_recog)

    print(' - Processes - ')
    processes = list()
    for _ in range(recog_limit_worker):
        process = Process(target=multiprocessor_recog, args=(
            queue_recog, queue_stream), name='Process-{}'.format(_))
        processes.append(process)
        process.start()
        logger.info('Process: {} started.'.format(process.name))
    print(' ')
    
    video_stream_gui = VideoStreamGUI(vs, processes, queue_recog, queue_stream, capframe_time_limit)
    video_stream_gui.root.mainloop()


if __name__ == '__main__':
    main()
