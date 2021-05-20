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
            'out': {'zoom': 0, 'focus': 455},
        },
        'right': {
            'in': {'zoom': 457, 'focus': 42},
            'inter': {'zoom': 270, 'focus': 321},
            'out': {'zoom': 0, 'focus': 445},
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

    def send_zoom_command(self, side: str, zoom_level: str) -> None:
        """Send a zoom command.

        Given the camera side and the zoom level required,
        produce the corresponding G-code and send it over the serial port.

        Args:
            side: 'right' or 'left'
            zoom_level: either 'in', 'inter' or 'out'. 'in' level for far
                 objects, 'out' for close objects, 'inter' is in between
                 'in' and 'out' levels
        """
        zoom, focus = self.zoom_pos[side][zoom_level].values()
        self._send_custom_command(side, zoom, focus)

    def send_zoom_command_two_cameras(self, left_zoom: str, right_zoom: str) -> None:
        """Send a zoom command to both cameras in a same time.

        Given the zoom level required to each cameras,
        produce the corresponding G-code and send it over the serial port.

        Args:
            left_zoom: either 'in', 'inter' or 'out'. 'in' level for far
                 objects, 'out' for close objects, 'inter' is in between
                 'in' and 'out' levels
            right_zoom: either 'in', 'inter' or 'out'. 'in' level for far
                 objects, 'out' for close objects, 'inter' is in between
                 'in' and 'out' levels
        """
        val_left = self.zoom_pos["left"][left_zoom]["zoom"]
        val_right = self.zoom_pos["right"][right_zoom]["zoom"]
        self.send_custom_zoom_two_cameras(val_left, val_right)

    def _send_custom_command(self, side: str, zoom: int, focus: int):
            mot = self.motors[self.connector[side]]
            command = f'G1 {mot["zoom"]}{zoom} F{self.speed}'
            self.ser.write(bytes(command + '\n', 'utf8'))
            _ = self.ser.readline()
            command = f'G1 {mot["focus"]}{focus} F{self.speed}'
            self.ser.write(bytes(command + '\n', 'utf8'))
            _ = self.ser.readline()

    def send_custom_zoom_two_cameras(self, left_zoom: int, right_zoom: int):
        """Send custom zoom values to both cameras.

        Given left and right zoom value,
        produce the corresponding G-code and send it over the serial port.
        motors will move at once

        Args:
            left_zoom: int between 0 and 600
            right_zoom: int between 0 and 600
        """
        if not (0 <= left_zoom <= 600 or 0 <= right_zoom <= 600):
            raise ValueError('Zoom value must be between 0 and 600.')

        mot_l = self.motors[self.connector['left']]
        mot_r = self.motors[self.connector['right']]
        command = f'G1 {mot_l["zoom"]}{left_zoom} {mot_r["zoom"]}{right_zoom} F{self.speed}'
        self.ser.write(bytes(command + '\n', 'utf8'))
        _ = self.ser.readline()

    def send_custom_focus_two_cameras(self, left_focus: int, right_focus: int):
        """Send custom focus values to both cameras.

        Given left and right focus value,
        produce the corresponding G-code and send it over the serial port.
        motors will move at once

        Args:
            left_focus: int between 0 and 600
            right_focus: int between 0 and 600
        """
        if not (0 <= left_focus <= 500 or 0 <= right_focus <= 500):
            raise ValueError('Zoom value must be between 0 and 500.')

        mot_l = self.motors[self.connector['left']]
        mot_r = self.motors[self.connector['right']]
        command = f'G1 {mot_l["focus"]}{left_focus} {mot_r["focus"]}{right_focus} F{self.speed}'
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

        self._send_custom_command(side, 0, -500)
        time.sleep(1)
        self._send_custom_command(side, -600, -500)
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
