# top_button.py
# Copyright (C) 2021 Niryo
# All rights reserved.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import rospy
import RPi.GPIO as GPIO
from threading import Thread
import rosnode

from niryo_robot_rpi.common.rpi_ros_utils import *

# Command Status
from niryo_robot_msgs.msg import CommandStatus

# Messages
from std_msgs.msg import Int32, Bool, Int8
from niryo_robot_arm_commander.msg import PausePlanExecution
from niryo_robot_programs_manager.msg import ProgramIsRunning

# Services
from niryo_robot_msgs.srv import Trigger, SetInt
from niryo_robot_rpi.srv import LedBlinker, LedBlinkerRequest


class ButtonMode:
    def __init__(self):
        pass

    DO_NOTHING = 0
    TRIGGER_SEQUENCE_AUTORUN = 1
    BLOCKLY_SAVE_POINT = 2


class TopButton:
    def __init__(self):
        rospy.logdebug("NiryoButton - Entering in Init")

        self.pin = rospy.get_param("~button/gpio")
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        rospy.sleep(0.1)

        self.debug_loop_repetition = 5

        self.pause_time = None
        self.resume = None
        self._pause_state = None

        self.__program_manager_is_running = False
        rospy.Subscriber('/niryo_robot_programs_manager/program_is_running', ProgramIsRunning,
                         self.__callback_program_is_running)

        rospy.Subscriber('/niryo_robot/rpi/led_state', Int8, self.__callback_led_state)

        self.button_mode = ButtonMode.TRIGGER_SEQUENCE_AUTORUN
        self.last_time_button_mode_changed = rospy.Time.now()
        rospy.Service("/niryo_robot/rpi/change_button_mode", SetInt, self.callback_change_button_mode)

        self.__set_led_state_service = rospy.ServiceProxy('/niryo_robot_rpi/set_led_custom_blinker', LedBlinker)

        # - Publishers
        self.__pause_movement_publisher = rospy.Publisher('~pause_state',
                                                          PausePlanExecution, latch=True, queue_size=1)
        self.send_pause_state(PausePlanExecution.STANDBY)

        # Publisher used to send info to Niryo Studio, so the user can add a move block
        # by pressing the button
        self.save_point_publisher = rospy.Publisher(
            "/niryo_robot/blockly/save_current_point", Int32, queue_size=10)

        self.__button_state_publisher = rospy.Publisher(
            "/niryo_robot/rpi/is_button_pressed", Bool, latch=True, queue_size=1)

        self.__button_state = None
        self.__button_state = self.read_value()
        self.__led_state = LedState.OK

        rospy.on_shutdown(self.shutdown)
        rospy.loginfo("Niryo Button started")

        # Seems to be overkill over that value due to reading IO time
        self.__button_loop_frequency = rospy.Rate(10)
        self.__button_loop_thread = Thread(target=self.check_button_loop)
        self.__button_loop_thread.start()

    def __del__(self):
        pass

    def read_value(self):
        try:
            value = GPIO.input(self.pin)
        except RuntimeError:
            return False
        self.__button_state = value

        self.__button_state_publisher.publish(self.__is_button_pressed())
        return self.__button_state

    def __is_button_pressed(self):
        return not self.__button_state

    def __callback_program_is_running(self, msg):
        self.__program_manager_is_running = msg.program_is_running

    def __callback_led_state(self, msg):
        self.__led_state = msg.data

    def __trigger_blockly_save_point(self):
        self.blockly_save_current_point()

    def __trigger_sequence_autorun(self):
        rospy.loginfo("Button Manager - Run Auto-sequence")
        self.send_pause_state(PausePlanExecution.PLAY)
        _status, _message = send_trigger_program_autorun()

    def check_button_loop(self):
        self.__button_loop_frequency.sleep()
        last_press_time = rospy.Time.now()
        elapsed_seconds = 15

        while not rospy.is_shutdown():
            button_was_pressed = self.__is_button_pressed()

            self.read_value()
            if self.__is_button_pressed():
                if not button_was_pressed:
                    last_press_time = rospy.Time.now()
                elapsed_seconds = (rospy.Time.now() - last_press_time).to_sec()
                self.led_advertiser(elapsed_seconds)

            # Was pressed and is not anymore (release)
            elif button_was_pressed:
                # Check if there is an action to do
                if elapsed_seconds >= 10:
                    pass
                elif elapsed_seconds >= 6:
                    send_hotspot_command()
                elif elapsed_seconds >= 3:
                    send_shutdown_command()
                elif 0.02 < elapsed_seconds < 3:
                    # Detect if a prog is running
                    python_prog_is_running = self.__is_prog_running()
                    # If a programm is running
                    if python_prog_is_running:
                        self.__manage_python_program()
                    elif self.button_mode == ButtonMode.BLOCKLY_SAVE_POINT:
                        self.__trigger_blockly_save_point()
                    elif self.button_mode == ButtonMode.TRIGGER_SEQUENCE_AUTORUN:
                        self.__trigger_sequence_autorun()

            self.__button_loop_frequency.sleep()

    def __manage_python_program(self):
        # Pause the current move
        if self._pause_state in [PausePlanExecution.PLAY]:
            rospy.loginfo("Button Manager - Sequence paused")
            self.pause_time = rospy.Time.now()
            self.send_pause_state(PausePlanExecution.PAUSE)
            # Pause led advertiser
            self.__set_led_state_service(True, 5, LedBlinkerRequest.LED_WHITE, PausePlanExecution.PAUSE_TIMEOUT)
        # Double press on pause: activate learning mode
        elif self._pause_state == PausePlanExecution.PAUSE and (rospy.Time.now() - self.pause_time).to_sec() < 1:
            activate_learning_mode(True)
            self.__set_led_state_service(True, 5, LedBlinkerRequest.LED_WHITE, 0)
            rospy.loginfo("Button Manager - Sequence paused with learning mode")
        # Program paused: resume or cancel
        elif self._pause_state == PausePlanExecution.PAUSE:
            # wait if double clic occurs
            if self.double_press():
                rospy.logwarn("Button Manager - Cancel sequence")
                self.__set_led_state_service(False, 0, 0, 0)
                activate_learning_mode(True)
                self.send_pause_state(PausePlanExecution.CANCEL)
                if self.__program_manager_is_running:
                    self.cancel_program_from_program_manager()

                self.read_value()
                while not rospy.is_shutdown() and self.__is_button_pressed():
                    self.__button_loop_frequency.sleep()
                    self.read_value()
            else:
                rospy.loginfo("Button Manager - Resume sequence")
                self.__set_led_state_service(False, 0, 0, 0)
                activate_learning_mode(False)
                rospy.sleep(0.2)
                self.send_pause_state(PausePlanExecution.RESUME)
                self._pause_state = PausePlanExecution.PLAY

    def double_press(self):
        start_time = rospy.Time.now()
        self.read_value()
        button_pressed = self.__is_button_pressed()
        while not rospy.is_shutdown() and (rospy.Time.now() - start_time).to_sec() < 1:
            self.read_value()
            if not button_pressed and self.__is_button_pressed():
                return True
            button_pressed = self.__is_button_pressed()
            self.__button_loop_frequency.sleep()
        return False

    def __is_prog_running(self):
        if self.__program_manager_is_running:
            python_prog_is_running = True
        else:
            python_prog_running_nodes = [s for s in rosnode.get_node_names() if "ros_wrapper" in s]
            python_prog_is_running = bool(python_prog_running_nodes)

        # Deal with new state
        if not python_prog_is_running:
            # if the state is paused, it means that the pause timeout has appeared.
            # Otherwise it's a program that has ended.
            if self._pause_state == PausePlanExecution.PAUSE:
                activate_learning_mode(True)
            self.send_pause_state(PausePlanExecution.STANDBY)
            self.__set_led_state_service(False, 0, 0, 0)

        elif self._pause_state not in [PausePlanExecution.PLAY, PausePlanExecution.PAUSE]:
            # detect a new execution of a program
            self.send_pause_state(PausePlanExecution.PLAY)
            self.__set_led_state_service(False, 0, 0, 0)

        return python_prog_is_running

    @staticmethod
    def cancel_program_from_program_manager():
        srv = rospy.ServiceProxy('/niryo_robot_programs_manager/stop_program', Trigger)
        resp = srv()
        return resp.status, resp.message

    def led_advertiser(self, elapsed_seconds):
        # Use LED to help user know which action to execute
        if elapsed_seconds >= 10:
            self.__led_state = LedState.OK
            send_led_state(LedState.OK)
        elif elapsed_seconds >= 6:
            self.__led_state = LedState.WAIT_HOTSPOT
            send_led_state(LedState.WAIT_HOTSPOT)
        elif elapsed_seconds >= 3:
            self.__led_state = LedState.SHUTDOWN
            send_led_state(LedState.SHUTDOWN)

    @staticmethod
    def shutdown():
        rospy.loginfo("Button Manager - Shutdown cleanup GPIO")
        rospy.sleep(0.5)
        GPIO.cleanup()

    def blockly_save_current_point(self):
        msg = Int32()
        msg.data = 1
        self.save_point_publisher.publish(msg)

    def callback_change_button_mode(self, req):
        # message = ""
        if req.value == ButtonMode.TRIGGER_SEQUENCE_AUTORUN:
            message = "Successfully changed button mode to trigger sequence autorun"
        elif req.value == ButtonMode.BLOCKLY_SAVE_POINT:
            message = "Successfully changed button mode to save point"
        elif req.value == ButtonMode.DO_NOTHING:
            message = "Successfully changed button mode to disabled"
        else:
            return {"status": CommandStatus.BUTTON_ERROR, "message": "Incorrect button mode."}
        self.button_mode = req.value
        self.last_time_button_mode_changed = rospy.Time.now()
        return {"status": CommandStatus.SUCCESS, "message": message}

    def send_pause_state(self, state):
        self._pause_state = state
        self.__pause_movement_publisher.publish(self._pause_state)
