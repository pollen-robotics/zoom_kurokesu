# Zoom Kurokesu

Python library to pilote the dual zoom board controller from Kurokesu. Visit [Kurokesu's website](https://www.kurokesu.com/home/) to get more information about its products. 

Install:
```bash
pip install zoom_kurokesu
```

## Use the library

You can get/set either the zoom or focus of both cameras.

There is also three pre defined positions.

- 'in': for close objects
- 'out': for further objects
- 'inter': in between the 'in' and 'out' positions

Because each predined position is relative to the starting position, you **must perform a homing sequence** before sending other commands.

The motors speed can also be changed with this library.

Check the *Demo.ipynb* notebook for use case example and more info.

---

Visit [pollen-robotics.com](https://pollen-robotics.com) to learn more or visit [our forum](https://forum.pollen-robotics.com) if you have any questions.
