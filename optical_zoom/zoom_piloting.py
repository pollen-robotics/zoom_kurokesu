'''Python package for optical lens piloting.'''
import serial

connector = {
    'left': 'J1',
    'right': 'J2'
}

motors = {
    'J1': {'zoom': 'X', 'focus': 'Y'},
    'J2': {'zoom': 'Z', 'focus': 'A'}
}

zoom_pos = {
    'in': {'zoom': '500 ', 'focus': '20 '},
    'inter': {'zoom': '350 ', 'focus': '320 '},
    'out': {'zoom': '50 ', 'focus': '500 '}
}


class ZoomController():
    '''Zoom controller class.'''
    def __init__(
            self,
            port: str = '/dev/ttyACM0',
            baudrate: int = 115200,
            timeout: int = 10,
            speed: int = 10000) -> None:
        self.ser = serial.Serial()
        self.ser.port = port
        self.ser.baudrate = baudrate
        self.ser.timeout = timeout
        self.ser.open()
        self.ser.flushInput()
        self.ser.flushOutput()

        self._connector = connector
        self._motors = motors
        self._zoom_pos = zoom_pos
        self.speed = speed

        init_seq = 'G100 P9 L144 N0 S0 F1 R1'
        self.ser.write(bytes(init_seq + '\n', 'utf8'))
        response = self.ser.readline()
        assert response.decode() == 'ok\r\n', \
            'Initialization of zoom controller failed,\
                 check that the control board is plugged in.'

    def send_zoom_command(self, side: str, zoom_level: str) -> None:
        '''
        Given the camera side and the zoom level required,
        produce the corresponding G-code and send it over the serial port.

        Args:
            side: 'right' or 'left'
            zoom_level: either 'in', 'inter' or 'out'. 'in' level for far
                 objects, 'out' for close objects, 'inter' is in between
                 'in' and 'out' levels
        '''
        zoom, focus = self._zoom_pos[zoom_level].values()
        mot = self._motors[self._connector[side]]
        command = 'G1 ' + mot['zoom'] + zoom + mot['focus'] + \
            focus + 'F' + str(self.speed)
        self.ser.write(bytes(command + '\n', 'utf8'))
        _ = self.ser.readline()

    def _send_custom_command(self, side: str, zoom: int, focus: int):
        assert zoom > 0 and zoom < 600,\
            'Zoom value must be between 0 and 600.'
        assert focus > 0 and focus < 500,\
            'Focus value must be between 0 and 500.'
        mot = self._motors[self._connector[side]]
        command = 'G1 ' + mot['zoom'] + str(zoom) + mot['focus'] + \
            str(focus) + 'F' + str(self.speed)
        self.ser.write(bytes(command + '\n', 'utf8'))
        _ = self.ser.readline()

    def homing(self, side: str) -> None:
        '''
        Use serial port to perform homing sequence on given camera.

        Args:
            side: 'right', 'left'.
        '''
        mot = motors[connector[side]]
        sequence = ['G91',
                    'F30000',
                    'G1 ' + mot['focus'] + '-500',
                    'G1 ' + mot['zoom'] + '-1200',
                    'G90',
                    'G92 ' + mot['zoom'] + '0 ' + mot['focus'] + '0']
        for seq in sequence:
            self.ser.write(bytes(seq + '\n', 'utf8'))
            _ = self.ser.readline()

    def set_speed(self, speed_value: int) -> None:
        '''
        Set motors speed.

        Args:
            speed_value: int between 4000 and 40000
        '''
        assert speed_value > 4000 and speed_value < 40000, \
            'Speed value must be between 4000 and 40000'
        self.speed = speed_value
