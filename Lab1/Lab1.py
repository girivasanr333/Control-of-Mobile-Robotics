# Tools
import collections
import statistics
import time
import numbers
import math
import pigpio

# Robot sensors and motors
import board
import busio
import adafruit_tca9548a
import adafruit_vl53l4cd
import adafruit_bno055

# Initialize the main I2C bus
i2c = busio.I2C(board.SCL, board.SDA)

# Initialize the TCA9548A with the I2C bus
tca = adafruit_tca9548a.TCA9548A(i2c, address=0x70)

# Initialize VL53L4CD distance sensor on channel 0
distance_sensor = adafruit_vl53l4cd.VL53L4CD(tca[0])

# Initialize BNO055 on channel 1
imu = adafruit_bno055.BNO055_I2C(tca[1])

# RobotController
class RobotController:
    def __init__(self, distance_sensor, imu):
        self.distance_sensor = distance_sensor
        self.imu = imu
        # Initialize other properties if necessary
        self.sampling_time = 0.02  # example value, you should adjust
        # ... other initialization ...

    def get_sensor_data(self):
        # Implement your data acquisition logic here
        distance = self.distance_sensor.range
        orientation = self.imu.euler  # or whatever IMU data you need
        return distance, orientation

    def control_logic(self, Vl, Vr, D, T#)#:
        # control logic here using the sensor data
        pass

    def move(self, Vl, Vr, D, T):
        # Logic to move the robot with left speed Vl, right speed Vr for time T
        # and distance D (assuming D is the total distance to travel)
        start_time = time.time()
        
        while (time.time() - start_time) < T:
            distance, orientation = self.get_sensor_data()
            self.control_logic(Vl, Vr, D, T)
            time.sleep(self.sampling_time - ((time.time() - start_time) % self.sampling_time))

        # Stopping the robot
    

    def cancel(self):
        # Add logic here if you need to cancel operations, stop motors, or cleanup
        pass

# Instantiate the controller
controller = RobotController(distance_sensor, imu)

# Move the robot
controller.move(5, 5, 1000, 0.2)
