from enum import Enum, unique


class NiryoRosWrapperException(Exception):
    pass


class ShiftPose:
    def __init__(self):
        pass

    AXIS_X = 0
    AXIS_Y = 1
    AXIS_Z = 2
    ROT_ROLL = 3
    ROT_PITCH = 4
    ROT_YAW = 5


class ToolID:
    """
    Tools IDs (need to match tools ids in niryo_robot_tools_commander package)
    """

    def __init__(self):
        pass

    NONE = 0
    # CALIBRATION_TIP = 1
    GRIPPER_1 = 11
    GRIPPER_2 = 12
    GRIPPER_3 = 13
    GRIPPER_4 = 14
    ELECTROMAGNET_1 = 30
    VACUUM_PUMP_1 = 31


class PinMode:
    """
    Pin Mode is either OUTPUT or INPUT
    """

    def __init__(self):
        pass

    OUTPUT = 0
    INPUT = 1


class PinState:
    """
    Pin State is either LOW or HIGH
    """

    def __init__(self):
        pass

    LOW = False
    HIGH = True


class PinID:
    """
    Pins ID
    """

    def __init__(self):
        pass

    GPIO_1A = "1A"
    GPIO_1B = "1B"
    GPIO_1C = "1C"
    GPIO_2A = "2A"
    GPIO_2B = "2B"
    GPIO_2C = "2C"

    SW_1 = "SW1"
    SW_2 = "SW2"

    DO1 = "DO1"
    DO2 = "DO2"
    DO3 = "DO3"
    DO4 = "DO4"
    DI1 = "DI1"
    DI2 = "DI2"
    DI3 = "DI3"
    DI4 = "DI4"
    DI5 = "DI5"


# - Conveyor

class ConveyorID:
    def __init__(self):
        pass

    # TODO : to adapt to be able to have CAN (id 12 and 13) and TTL (id 9 and 10) conveyor in any possible combination
    NONE = 0
    ID_1 = 12   # One, Ned
    ID_2 = 13   # One, Ned
    ID_3 = 9    # Ned2
    ID_4 = 10   # Ned2


class ConveyorDirection:
    def __init__(self):
        pass

    FORWARD = 1
    BACKWARD = -1


# - Vision

class ObjectColor:
    def __init__(self):
        pass

    RED = "RED"
    GREEN = "GREEN"
    BLUE = "BLUE"
    ANY = "ANY"


class ObjectShape:
    def __init__(self):
        pass

    CIRCLE = "CIRCLE"
    SQUARE = "SQUARE"
    ANY = "ANY"


class ProgramLanguage:
    def __init__(self):
        pass

    NONE = -1
    ALL = 0
    PYTHON2 = 1
    PYTHON3 = 2
    BLOCKLY = 66


class AutorunMode:
    def __init__(self):
        pass

    DISABLE = 0
    ONE_SHOT = 1
    LOOP = 2


class ButtonAction:
    def __init__(self):
        pass

    HANDLE_HELD_ACTION = 0
    LONG_PUSH_ACTION = 1
    SINGLE_PUSH_ACTION = 2
    DOUBLE_PUSH_ACTION = 3
    NO_ACTION = 100


@unique
class CommandEnum(Enum):
    """
    Enumeration of all commands used
    """
    # Main purpose
    CALIBRATE = 0
    SET_LEARNING_MODE = 1
    GET_LEARNING_MODE = 2
    SET_ARM_MAX_VELOCITY = 3
    SET_JOG_CONTROL = 4

    # - Move
    # Pose

    GET_JOINTS = 10
    GET_POSE = 11
    GET_POSE_QUAT = 12

    MOVE_JOINTS = 20
    MOVE_POSE = 21
    SHIFT_POSE = 22

    MOVE_LINEAR_POSE = 23
    SHIFT_LINEAR_POSE = 24

    JOG_JOINTS = 25
    JOG_POSE = 26

    FORWARD_KINEMATICS = 27
    INVERSE_KINEMATICS = 28

    # Saved Pose
    GET_POSE_SAVED = 50
    SAVE_POSE = 51
    DELETE_POSE = 52
    GET_SAVED_POSE_LIST = 53

    # Pick & Place

    PICK_FROM_POSE = 60
    PLACE_FROM_POSE = 61
    PICK_AND_PLACE = 62

    # Trajectories
    GET_TRAJECTORY_SAVED = 80
    EXECUTE_TRAJECTORY_FROM_POSES = 81
    EXECUTE_TRAJECTORY_SAVED = 82
    SAVE_TRAJECTORY = 83
    DELETE_TRAJECTORY = 84
    GET_SAVED_TRAJECTORY_LIST = 85
    EXECUTE_TRAJECTORY_FROM_POSES_AND_JOINTS = 86

    # - Tools
    UPDATE_TOOL = 120
    OPEN_GRIPPER = 121
    CLOSE_GRIPPER = 122
    PULL_AIR_VACUUM_PUMP = 123
    PUSH_AIR_VACUUM_PUMP = 124
    SETUP_ELECTROMAGNET = 125
    ACTIVATE_ELECTROMAGNET = 126
    DEACTIVATE_ELECTROMAGNET = 127
    GET_CURRENT_TOOL_ID = 128
    GRASP_WITH_TOOL = 129
    RELEASE_WITH_TOOL = 130
    ENABLE_TCP = 140
    SET_TCP = 141
    RESET_TCP = 142
    TOOL_REBOOT = 145

    # - Hardware
    SET_PIN_MODE = 150
    DIGITAL_WRITE = 151
    DIGITAL_READ = 152
    GET_DIGITAL_IO_STATE = 153
    GET_HARDWARE_STATUS = 154
    ANALOG_WRITE = 155
    ANALOG_READ = 156
    GET_ANALOG_IO_STATE = 157
    CUSTOM_BUTTON_STATE = 158

    # - Conveyor
    SET_CONVEYOR = 180
    UNSET_CONVEYOR = 181
    CONTROL_CONVEYOR = 182
    GET_CONNECTED_CONVEYORS_ID = 183

    # - Vision
    GET_IMAGE_COMPRESSED = 200
    GET_TARGET_POSE_FROM_REL = 201
    GET_TARGET_POSE_FROM_CAM = 202

    VISION_PICK = 203
    MOVE_TO_OBJECT = 205
    DETECT_OBJECT = 204

    GET_CAMERA_INTRINSICS = 210

    SAVE_WORKSPACE_FROM_POSES = 220
    SAVE_WORKSPACE_FROM_POINTS = 221
    DELETE_WORKSPACE = 222
    GET_WORKSPACE_RATIO = 223
    GET_WORKSPACE_LIST = 224

    SET_IMAGE_BRIGHTNESS = 230
    SET_IMAGE_CONTRAST = 231
    SET_IMAGE_SATURATION = 232
    GET_IMAGE_PARAMETERS = 235

    # - Sound
    PLAY_SOUND = 240
    SET_VOLUME = 241
    STOP_SOUND = 242
    DELETE_SOUND = 243
    IMPORT_SOUND = 244
    GET_SOUNDS = 245
    GET_SOUND_DURATION = 246
    SAY = 247

    # Led Ring
    LED_RING_SOLID = 250
    LED_RING_TURN_OFF = 251
    LED_RING_FLASH = 252
    LED_RING_ALTERNATE = 253
    LED_RING_CHASE = 254
    LED_RING_WIPE = 255
    LED_RING_RAINBOW = 256
    LED_RING_RAINBOW_CYCLE = 257
    LED_RING_RAINBOW_CHASE = 258
    LED_RING_GO_UP = 259
    LED_RING_GO_UP_DOWN = 260
    LED_RING_BREATH = 261
    LED_RING_SNAKE = 262
    LED_RING_CUSTOM = 263
    LED_RING_SET_LED = 264
