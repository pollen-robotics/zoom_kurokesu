"""Python Package for controlling the zoom of Kurokesu's camera."""

import serial
import time


class ZoomController:
    """Zoom controller class."""

    connector = {
        'left': 'J1',
        'right': 'J2'
    }

    motors = {
        'J1': {'zoom': 'X', 'focus': 'Y'},
        'J2': {'zoom': 'Z', 'focus': 'A'}
    }

    zoom_pos = {
        'left': {
            'in': {'zoom': 457, 'focus': 70},
            'inter': {'zoom': 270, 'focus': 331},
            'out': {'zoom': 60, 'focus': 455},
        },
        'right': {
            'in': {'zoom': 457, 'focus': 42},
            'inter': {'zoom': 270, 'focus': 321},
            'out': {'zoom': 60, 'focus': 445},
        },
    }

    def __init__(
            self,
            port: str = '/dev/ttyACM0',
            baudrate: int = 115200,
            timeout: int = 10,
            speed: int = 10000) -> None:
        """Connect to the serial port and run the initialisation sequence."""
        self.ser = serial.Serial(port=port, baudrate=baudrate, timeout=timeout)
        self.speed = speed

        init_seq = 'G100 P9 L144 N0 S0 F1 R1'
        self.ser.write(bytes(init_seq + '\n', 'utf8'))
        response = self.ser.readline()

        if response.decode() != 'ok\r\n':
            raise IOError('Initialization of zoom controller failed, check that the control board is correctly plugged in.')

    def set_zoom_level(self, side: str, zoom_level: str) -> None:
        """Set zoom level of a given camera.

        Given the camera side and the zoom level required,
        produce the corresponding G-code and send it over the serial port.

        Args:
            side: 'right' or 'left'
            zoom_level: either 'in', 'inter' or 'out'. 'in' level for far
                 objects, 'out' for close objects, 'inter' is in between
                 'in' and 'out' levels
        """
        zoom, focus = self.zoom_pos[side][zoom_level].values()
        self._send_custom_command({side: {'zoom': zoom, 'focus': focus}})

    def _send_custom_command(self, commands: dict):
        """Send custom command to camera controller.

        Args:
            commands: dictionnary containing the requested camera name along
            with requested focus and zoom value. Instructions for both cameras
            can be sent in one call of this method. However, instructions will
            be sent sequentially and there is no synchronization.
        """
        for side, cmd in commands.items():
            if side not in ['left', 'right']:
                raise ValueError("Keys should be either 'left' or 'right'.")
            motor = self.motors[self.connector[side]]
            for target, value in cmd.items():
                if target not in ['zoom', 'focus']:
                    raise ValueError("Each command should be either on 'focus' or 'zoom'.")
                command = f'G1 {motor[target]}{value} F{self.speed}'
                self.ser.write(bytes(command + '\n', 'utf8'))
                _ = self.ser.readline()

    def homing(self, side: str) -> None:
        """Use serial port to perform homing sequence on given camera.

        Args:
            side: 'right', 'left'.
        """
        mot = self.motors[self.connector[side]]

        cmd = 'G92 ' + mot['zoom'] + '0 ' + mot['focus'] + '0'
        self.ser.write(bytes(cmd + '\n', 'utf8'))
        _ = self.ser.readline()
        time.sleep(0.1)
        self._send_custom_command({side: {'zoom': 0, 'focus': -500}})
        time.sleep(1)
        self._send_custom_command({side: {'zoom': -600, 'focus': -500}})
        time.sleep(1)

        cmd = 'G92 ' + mot['zoom'] + '0 ' + mot['focus'] + '0'
        self.ser.write(bytes(cmd + '\n', 'utf8'))
        _ = self.ser.readline()
        time.sleep(0.1)

    def set_speed(self, speed_value: int) -> None:
        """Set motors speed.

        Args:
            speed_value: int between 4000 and 40000
        """
        if not (4000 <= speed_value <= 40000):
            raise ValueError('Speed value must be between 4000 and 40000')
        self.speed = speed_value
