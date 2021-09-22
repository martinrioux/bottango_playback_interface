
from dataclasses import dataclass
import time
import requests
import logging

logging.basicConfig(level=logging.INFO, format='[%(levelname)s] %(message)s')
logger = logging.getLogger()
logger.addHandler(logging.FileHandler('bottango_python_api.log', 'a'))


@dataclass
class Effector:
    name: str
    live: bool
    identifier: str
    driverName: str
    driverLive: bool
    movement: float = None
    signal: float = None


class PlaybackState:
    def __init__(self, selectedAnimationIndex: int, selectedAnimationName: str, isPlaying: bool, playbackTimeInMS: int, durationInMS: int, effectors: 'list[Effector]'):
        self.selectedAnimationIndex= selectedAnimationIndex
        self.selectedAnimationName = selectedAnimationName
        self.isPlaying = isPlaying
        self.playbackTimeInMS = playbackTimeInMS
        self.durationInMS= durationInMS
        casted_effectors = []
        for effector in effectors:
            casted_effectors.append(Effector(**effector))
        self.effectors: list[Effector] = casted_effectors


class BottangoPlaybackInterface:
    CAN_ANIMATE_URL = "CanAnimate/"
    LIST_ANIMATIONS_URL = "Animations/"
    PLAYBACK_STATE_URL = "PlaybackState/"
    EMERGENCY_STOP = "Stop/"
    CURRENT_ANIMATION_URL = "Animations/Selected/"

    def __init__(self, host="localhost", port=59224):
        self.host = host
        self.port = port
        self._animations: dict[str, int] = {}
        self._test_connection()
        animations = self.refresh_animation_list()
        logging.info(f"Available animations are: {animations}")

    def __request(self, url, params=None) -> dict:
        responseData = None
        try:
            if params is None:
                response = requests.get(f"http://{self.host}:{self.port}/{url}")
                responseData = response.json()
            else:
                response = requests.put(f"http://{self.host}:{self.port}/{url}", json=params)
            response.raise_for_status()
        except (ConnectionRefusedError, requests.exceptions.ConnectionError) as e:
            logging.error(f"Error connecting to bottango API at {self.host}:{self.port}")
            raise SystemExit(f"Error connecting to bottango API at {self.host}:{self.port}")
        except requests.exceptions.RequestException as e:
            logging.error(f"Error in request at '{url}': {e}")

        logging.debug(f"Request '{url}' with params '{params}' returned: {responseData}")
        return responseData

    def _test_connection(self):
        if self._can_animate() is True:
            logging.info("Bottango online and ready to animate!")
        else:
            logging.error("Bottango not ready to animate or offline")

    def _can_animate(self) -> bool:
        """
        Check if Bottango is currently able to animate

        response data:
        bool canAnimate
        """
        response = self.__request(self.CAN_ANIMATE_URL)
        return response.get("canAnimate", False)

    def refresh_animation_list(self) -> 'list[str]':
        """
        Get available animations. Returns a list of strings. Index order is what is used
        to call play animation etc. in other requests

        response data:
        list[str] animations
        """
        response = self.__request(self.LIST_ANIMATIONS_URL)
        animation_list = response.get("animations", [])

        for i in range(0, len(animation_list)):
            self._animations[animation_list[i]] = i

        return animation_list

    def get_current_animation(self):
        """
        Get currently selected animation index. Returns an error if not able to animate

        response data:
        int selectedAnimationIndex
        string selectedAnimationName
        """
        response = self.__request(self.CURRENT_ANIMATION_URL)
        # animation_index = response.get('selectedAnimationIndex', None)
        animation_name = response.get('selectedAnimationName', None)
        return animation_name

    def get_playback_state(self) -> PlaybackState:
        """
        Get current state of animation playback. Returns an error if not able to animate

        response data:
        int selectedAnimationIndex
        string selectedAnimationName
        bool isPlaying
        int playbackTimeInMS
        int durationInMS
        obj[] effectors
            string name
            bool live
            string identifier
            string driverName
            bool driverLive
            float movement
            float signal

            motors/curved events return signal / movement you would expect (0.0 - 1.0 as float for movement, direct signal value for signal)

            On Off events return on off state as a bool cast to an int

            Audio keyframes (when hardware playback is enabled) signal/movement is -1 if not playing, positive value if playing.
            Audio signal is audio playback time from start of audio in MS
            Audio movement is audio playback time / audio clip length.
        """

        response = self.__request(self.PLAYBACK_STATE_URL)
        result = PlaybackState(**response)
        return result

    def resume_animation(self):
        requestParams = {}
        requestParams['isPlaying'] = True
        self.__request(self.PLAYBACK_STATE_URL, requestParams)

    def pause_animation(self):
        requestParams = {}
        requestParams['isPlaying'] = False
        self.__request(self.PLAYBACK_STATE_URL, requestParams)

    def play_animation(self, animation_name, playback_time_ms=0):
        """
        Set current state of animation playback. Returns an error if not able to animate (Send as PUT)
        request data:
        int selectedAnimationIndex
        string selectedAnimationName
        bool isPlaying
        int playbackTimeInMS
        """

        self.refresh_animation_list()

        requestParams = {}
        an_index = self._animations.get(animation_name, None)
        if an_index is not None:
            requestParams['selectedAnimationIndex'] = an_index
        requestParams['isPlaying'] = False
        self.__request(self.PLAYBACK_STATE_URL, requestParams)

        # requestParams['selectedAnimationName'] = animation_name
        requestParams['playbackTimeInMS'] = int(5000)

        requestParams = {}
        self.__request(self.PLAYBACK_STATE_URL, requestParams)

        requestParams = {}
        requestParams['isPlaying'] = True
        requestParams['playbackTimeInMS'] = int(5000)
        self.__request(self.PLAYBACK_STATE_URL, requestParams)

    def emergency_stop(self):
        """
        Set master live off. Used as an API version of a stop button. The same as pressing "Escape" on your keyboard in Bottango,
        or toggling master to not live. By design there is no API to set back live, do that manually in Bottango. (Send as PUT)

        request data:
        None
        """
        self.__request(self.EMERGENCY_STOP, '')

    def wait_animation_done(self, timeout=None):
        timer = time.time()
        while True:
            time.sleep(0.02)
            state = self.get_playback_state()
            if state.playbackTimeInMS >= state.durationInMS and state.isPlaying is False:
                break
            if timeout is not None and time.time() - timer > timeout:
                logging.error(f"Timeout while waiting for animation '{state.selectedAnimationName}' to finish. Timeout was {timeout}s, state is: {state.__dict__}")
                break
