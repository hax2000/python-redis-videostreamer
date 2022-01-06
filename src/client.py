import cv2
import time
import pyaudio
import argparse
import numpy as np
from redis import Redis
from multiprocessing import Process
from server import load_redis_cnxn_credentials
"""
TODO: 
import logging 
catch connection_errors
comments
"""


def receive_frame(redis_cnxn: Redis, measure_fps: bool):
    """
    Receives a frame from Redis cache, and measures its processing time

    :param redis_cnxn: Opened Redis connection
    :param measure_fps: If True, outputs the FPS counter to the stdout
    """
    while True:
        if measure_fps:
            start_time = time.time()
            frame = redis_cnxn.get('video')
            yield frame
            print("FPS:", 1.0 // (time.time() - start_time))
        else:
            frame = redis_cnxn.get('video')
            yield frame


def receive_audio():
    chunk_size = 1024
    p = pyaudio.PyAudio()

    stream = p.open(format=p.get_format_from_width(2),
                    channels=1,
                    rate=20000,
                    input=False,
                    output=True,
                    frames_per_buffer=chunk_size)
    redis_cnxn = Redis(**load_redis_cnxn_credentials())
    while True:
        stream.write(redis_cnxn.get('audio'), chunk_size)


if __name__ == '__main__':
    args_parser = argparse.ArgumentParser()
    args_parser.add_argument('--show_fps', action='store_true')
    args = args_parser.parse_args()

    redis_connection = Redis(**load_redis_cnxn_credentials())

    audio_process = Process(target=receive_audio)
    audio_process.start()

    for img in receive_frame(redis_connection, measure_fps=args.show_fps):

        img_decoded = cv2.imdecode(np.frombuffer(img, np.uint8), cv2.IMREAD_COLOR)
        cv2.imshow('RX', img_decoded)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    audio_process.terminate()
    redis_connection.close()
    cv2.destroyAllWindows()
