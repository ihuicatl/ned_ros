#!/usr/bin/env python

import rospy
import logging
from niryo_robot_sound.sound_manager import SoundManager


class SoundInterfaceNode:

    def __init__(self):
        self.__sound_interface_core = SoundManager()

    def on_shutdown(self):
        self.__sound_interface_core.sound_end_event.wait(10)
        pass


if __name__ == '__main__':
    rospy.init_node('niryo_robot_sound', anonymous=False, log_level=rospy.INFO)

    # change logger level according to node parameter
    log_level = rospy.get_param("~log_level")
    logger = logging.getLogger("rosout")
    logger.setLevel(log_level)

    try:
        node = SoundInterfaceNode()
        rospy.on_shutdown(node.on_shutdown)
        rospy.spin()
    except rospy.ROSInterruptException:
        pass
