import os
import cv2
import time
import pyaudio
import argparse
from redis import Redis
from multiprocessing import Process
"""
TODO:
import logging
catch connection_errors
"""


def load_redis_cnxn_credentials() -> dict:
    """
    Collects data to connect to the Redis server from enviroment variables

    :return: Dict with connection data for 'Redis' object constructor
    """

    return {
        'host': os.environ.get('REDIS_HOST', 'localhost'),
        'port': os.environ.get('REDIS_PORT', 6379),
        'db': os.environ.get('REDIS_DB_NUMBER', 0),
        'password': os.environ.get('REDIS_PASSWORD'),
    }


def process_frame(capture: cv2.VideoCapture, measure_fps: bool):
    """
    Receives a frame in the 3d numpy uint8-array format, and measures its processing time

    :param capture: opencv VideoCapture object
    :param measure_fps: If True, outputs the FPS counter to the stdout
    """
    while cap.isOpened():
        if measure_fps:
            start_time = time.time()
            _, frame = capture.read()
            yield frame
            print("FPS:", 1.0 // (time.time() - start_time))
        else:
            _, frame = capture.read()
            yield frame


def stream_audio():
    """
    Background process for writing audio buffer in redis storage
    TODO: audio_config.json
    """
    chunk_size = 1024
    p = pyaudio.PyAudio()

    stream = p.open(format=p.get_format_from_width(2),
                    channels=1,
                    rate=20000,
                    input=True,
                    output=False,
                    frames_per_buffer=chunk_size)
    redis_cnxn = Redis(**load_redis_cnxn_credentials())
    while True:
        redis_cnxn.set('audio', stream.read(chunk_size))


if __name__ == '__main__':
    args_parser = argparse.ArgumentParser()
    args_parser.add_argument('--show_video', action='store_true')
    args_parser.add_argument('--show_fps', action='store_true')
    args = args_parser.parse_args()

    redis_connection = Redis(**load_redis_cnxn_credentials())

    cap = cv2.VideoCapture()
    cap.open(0, cv2.CAP_DSHOW)  # Open webcam video stream

    audio_process = Process(target=stream_audio)
    audio_process.start()

    for img in process_frame(cap, measure_fps=args.show_fps):
        image_buffer = cv2.imencode('.jpg', img)[1].tobytes()  # Conversion image to String format
        redis_connection.set('video', image_buffer)

        if args.show_video:
            cv2.imshow('TX', img)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

    audio_process.terminate()
    redis_connection.close()

    cap.release()
    cv2.destroyAllWindows()
