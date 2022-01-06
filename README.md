# Installing dependencies:
`cd src`

`pip install -r requirements.txt`

[PyAudio installation / troubleshooting guide](
https://stackoverflow.com/questions/48690984/portaudio-h-no-such-file-or-directory)

# Filling environment variables 
**REDIS_HOST** _default=localhost_

**REDIS_PORT** _default=6379_

**REDIS_DB_NUMBER** _default=0_

**REDIS_PASSWORD** _default not set_

# Running Streaming Server

`python server.py --show_video --show_fps`

Available starting arguments:

--show_video  _Shows a window with a transmitted image (no sound)_

--show_fps  _Prints the FPS in stdout_

# Running Client

`python client.py --show_fps`

Available starting arguments:

--show_fps  _Prints the FPS in stdout_