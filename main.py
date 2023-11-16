from __future__ import print_function
from stream import VideoBootstrap
from imutils.video import VideoStream
import argparse
import time
import settings
from settings import connection
from db.database import migrate

ap = argparse.ArgumentParser()
ap.add_argument('-o', '--output', required=True, help='path to output directory to store snapshots')
ap.add_argument('-p', '--picamera', type=int, default=-1, help='whether or not the Raspberry Pi camera should be used')
args = vars(ap.parse_args())

print('[INFO] warming up camera...')
vs = VideoStream(usePiCamera=args['picamera'] > 0).start()
time.sleep(2.0)

"""
Migrete database if does not exists
"""
migrate(connection)


if __name__ == '__main__':
    pba = VideoBootstrap(vs, args['output'])
    pba.root.mainloop()