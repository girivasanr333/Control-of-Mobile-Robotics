# Tools
import collections
import statistics
import time
import numbers
import math
import pigpio

# Robot sensors and motors
import board
import adafruit_tca9548a
import adafruit_vl53l4cd
import adafruit_bno055

# Cameras
from threading import Thread 
import cv2 as cv
#https://www.parallax.com/sites/default/files/downloads/900-00360-Feedback-360-HS-Servo-v1.1.pdf
#http://gpiozero.readthedocs.io/en/stable/remote_gpio.html
#https://gpiozero.readthedocs.io/en/stable/recipes.html#pin-numbering

# Threaded PiCam
class ThreadedWebcam:
    def __init__(self, src=-1, name="ThreadedWebcam"):
        # Initialize camera with a specified resolution.
        # It may take some experimenting to find other valid resolutions,
        # as the camera may end up displaying an incorrect image.
        # Alternatively, frames can be resized afterwards using the resize() function.
        self.stream = cv.VideoCapture(src)
        self.stream.set(cv.CAP_PROP_FRAME_WIDTH, 640)
        self.stream.set(cv.CAP_PROP_FRAME_HEIGHT, 480)
        #self.stream.set(cv.CAP_PROP_BUFFERSIZE, 1)

        if not self.stream.isOpened():
            print("Failed to open camera!")
            exit()
        else:
            print("Threaded webcam started.")

        (self.grabbed, self.frame) = self.stream.read()

        self.name = name
        self.stopped = False

    # Starts the camera thread.
    def start(self):
        t = Thread(target=self._update, name=self.name, args=())
        t.daemon = True
        t.start()
        return self

    # Returns the latest camera frame.
    def read(self):
        return self.frame

    # Stops the camera thread.
    def stop(self):
        self.stopped = True

    # Private function that constantly reads the camera stream.
    # Do not call this function externally.
    def _update(self):
        while not self.stopped:
            (self.grabbed, self.frame) = self.stream.read()

# Threaded Blob detection using PiCam
class ThreadedBlob:
    def __init__(self, src=0, name="ThreadedBlob"):
        self.name = name
        self.stopped = False
        print("Starting Camera")
        self.camera = ThreadedWebcam()
        self.camera.start()
        self.keypoints = []

        params = cv.SimpleBlobDetector_Params()
        self.detector = cv.SimpleBlobDetector_create(params)
        fs = cv.FileStorage("params.yaml", cv.FILE_STORAGE_READ); #yaml, xml, or json
        if fs.isOpened():
            self.detector.read(fs.root())
        else:
            print("WARNING: params file not found! Creating default file.")

            fs2 = cv.FileStorage("params.yaml", cv.FILE_STORAGE_WRITE)
            self.detector.write(fs2)
            fs2.release()

        fs.release()




    # Starts the camera thread.
    def start(self):
        t = Thread(target=self._update, name=self.name, args=())
        t.daemon = True
        t.start()
        return self

    # Returns the latest camera frame.
    def read(self):
        return self.keypoints

    # Stops the camera thread.
    def stop(self):
        self.stopped = True
        self.camera.stop()

    # Private function that constantly reads the camera stream.
    # Do not call this function externally.
    def _update(self):
        minH =  106; minS = 145; minV =  139;
        maxH = 180; maxS = 255; maxV = 255;
        while not self.stopped:
            frame = self.camera.read()

            # Blob detection works better in the HSV color space
            # (than the RGB color space) so the frame is converted to HSV.
            frame_hsv = cv.cvtColor(frame, cv.COLOR_BGR2HSV)

            # Create a mask using the given HSV range
            mask = cv.inRange(frame_hsv, (minH, minS, minV), (maxH, maxS, maxV))

            # Run the SimpleBlobDetector on the mask.
            # The results are stored in a vector of 'KeyPoint' objects,
            # which describe the location and size of the blobs.
            self.keypoints = self.detector.detect(mask)


class write_pwm:
    """
    Stears a Parallax Feedback 360° High-Speed Servo `360_data_sheet`_ .

    This class stears a Parallax Feedback 360° High-Speed Servo. Out of the speed range,
    defined by ``min_speed`` and ``max_speed``, and the range of the pulsewidth, defined 
    by ``min_pw`` and ``max_pw``, the class allows setting the servo speed and automatically
    calculates the appropriate pulsewidth for the chosen speed value.

    .. note::
        ``min_pw`` and ``max_pw`` might needed to be interchanged, depending on if ``min_pw`` is 
        moving the servo max_forward/clockwise or max_backwards/counter-clockwise,
        see methods :meth:`max_forward` and  :meth:`max_backward`. 
        :meth:`max_forward` -> ``min_pw`` should let the servo rotate clockwise.

    .. warning::
        Be carefull with setting the min and max pulsewidth! Test carefully ``min_pw`` and ``max_pw``
        before setting them. Wrong values can damage the servo, see set_servo_pulsewidth_ !!!

    :param pigpio.pi pi: 
        Instance of a pigpio.pi() object.
    :param int gpio:
        GPIO identified by their Broadcom number, see elinux.org_ .
        To this GPIO the control wire of the servo has to be connected.
    :param int min_pw:
        Min pulsewidth, see **Warning**, carefully test the value before!
        **Default:** 1280, taken from the data sheet `360_data_sheet`_ .
    :param int max_pw:
        Max pulsewidth, see **Warning**, carefully test the value before!
        **Default:** 1720, taken from the data sheet `360_data_sheet`_ .
    :param int min_speed:
        Min speed which the servo is able to move. **Default:** -1. 
    :param int max_speed:
        Max speed which the servo is able to move. **Default:** 1. 

    .. _elinux.org: https://elinux.org/RPi_Low-level_peripherals#Model_A.2B.2C_B.2B_and_B2
    .. _set_servo_pulsewidth: http://abyz.me.uk/rpi/pigpio/python.html#set_servo_pulsewidth
    .. _`360_data_sheet`: https://www.parallax.com/sites/default/files/downloads/900-00360-Feedback-360-HS-Servo-v1.1.pdf
    """

    def __init__(self, pi, gpio, min_pw = 1280, max_pw = 1720, min_speed = -1, max_speed = 1):

        self.pi = pi
        self.gpio = gpio
        self.min_pw = min_pw
        self.max_pw = max_pw
        self.min_speed = min_speed
        self.max_speed = max_speed
        #calculate slope for calculating the pulse width
        self.slope = (self.min_pw - ((self.min_pw + self.max_pw)/2)) / self.max_speed
        #calculate y-offset for calculating the pulse width
        self.offset = (self.min_pw + self.max_pw)/2

    def set_pw(self, pulse_width):
        """
        Sets pulsewidth of the PWM.

        This method allows setting the pulsewidth of the PWM directly. This can be used to
        test which ``min_pw`` and ``max_pw`` are appropriate. For this the ``min_pw`` and ``max_pw`` 
        are needed to be set very small and very big, so that they do not limit the set pulsewidth. 
        Normally they are used to protect the servo by limiting the pulsewidth to a certain range.

        .. warning::
            Be carefull with setting the min and max pulsewidth! Test carefully ``min_pw`` and ``max_pw``
            before setting them. Wrong values can damage the servo, see set_servo_pulsewidth_ !!!

        :param int,float pulsewidth:
            Pulsewidth of the PWM signal. Will be limited to ``min_pw`` and ``max_pw``.
        
        .. _set_servo_pulsewidth: http://abyz.me.uk/rpi/pigpio/python.html#set_servo_pulsewidth
        """
        
        pulse_width = max(min(self.max_pw, pulse_width), self.min_pw)

        self.pi.set_servo_pulsewidth(user_gpio = self.gpio, pulsewidth = pulse_width)
        
    def calc_pw(self, speed):

        pulse_width = self.slope * speed + self.offset
        
        return pulse_width

    def set_speed(self, speed):
        """
        Sets speed of the servo.

        This method sets the servos rotation speed. The speed range is defined by 
        by ``min_speed`` and ``max_speed`` .

        :param int,float speed:
            Should be between ``min_speed`` and ``max_speed`` ,
            otherwise the value will be limited to those values.
        """

        speed = max(min(self.max_speed, speed), self.min_speed)

        calculated_pw = self.calc_pw(speed = speed)
        self.set_pw(pulse_width = calculated_pw)

    def stop(self):
        """
        Sets the speed of the servo to 0.
        """

        pulse_width = (self.min_pw+self.max_pw)/2
        self.set_pw(pulse_width = pulse_width)

    def max_backward(self):
        """
        Sets the speed of the servo to -1, so ``min_speed`` (max backwards,
        counter-clockwise)
        """

        self.set_pw(self.max_pw)

    def max_forward(self):
        """
        Sets the speed of the servo to 1, so ``max_speed`` (max forward,
        clockwise)
        """
        
        self.set_pw(self.min_pw)

class read_pwm:
    """
    Reads position of a Parallax Feedback 360° High-Speed Servo `360_data_sheet`_ .

    This class reads the position of a Parallax Feedback 360° High-Speed Servo. At the
    moment, the period for a 910 Hz signal is hardcoded.

    :param pigpio.pi pi: 
        Instance of a pigpio.pi() object.
    :param int gpio:
        GPIO identified by their Broadcom number, see elinux.org_ .
        To this GPIO the feedback wire of the servo has to be connected.

    .. todo::
        Enable the class to be able to handle different signals, not just 910 Hz.

    .. _elinux.org: https://elinux.org/RPi_Low-level_peripherals#Model_A.2B.2C_B.2B_and_B2
    .. _`360_data_sheet`: https://www.parallax.com/sites/default/files/downloads/900-00360-Feedback-360-HS-Servo-v1.1.pdf
    """

    def __init__(self, pi, gpio):

        self.pi = pi
        self.gpio = gpio
        self.period = 1/910*1000000
        self.tick_high = None
        self.duty_cycle = None
        self.duty_scale = 1000

        #http://abyz.me.uk/rpi/pigpio/python.html#set_mode
        self.pi.set_mode(gpio=self.gpio, mode=pigpio.INPUT)
        #http://abyz.me.uk/rpi/pigpio/python.html#callback
        self.cb = self.pi.callback(user_gpio=self.gpio, edge=pigpio.EITHER_EDGE, func=self.cbf)

    #calculate the duty cycle
    def cbf(self, gpio, level, tick):

        #change to low (a falling edge)
        if level == 0:
            #if first edge is a falling one the following code will fail
            #a try first time is faster than an if-statement every time 
            try:
                #http://abyz.me.uk/rpi/pigpio/python.html#callback
                # tick        32 bit    The number of microseconds since boot
                #                       WARNING: this wraps around from
                #                       4294967295 to 0 roughly every 72 minutes
                #Tested: This is handled by the tickDiff function internally, if t1 (earlier tick)
                #is smaller than t2 (later tick), which could happen every 72 min. The result will
                #not be a negative value, the real difference will be properly calculated.
                self.duty_cycle = self.duty_scale*pigpio.tickDiff(t1=self.tick_high, t2=tick)/self.period

            except Exception:
                pass

        #change to high (a rising edge)
        elif level == 1:

            self.tick_high = tick

    def read(self):
        """
        Returns the recent measured duty cycle.

        This method returns the recent measured duty cycle.

        :return: Recent measured duty cycle
        :rtype: float
        """

        return self.duty_cycle

    def cancel(self):
        """
        Cancel the started callback function.

        This method cancels the started callback function if initializing an object.
        As written in the pigpio callback_ documentation, the callback function may be cancelled
        by calling the cancel function after the created instance is not needed anymore.

        .. _callback: http://abyz.me.uk/rpi/pigpio/python.html#callback
        """

        self.cb.cancel()

class calibrate_pwm:
    """
    Calibrates a Parallax Feedback 360° High-Speed Servo with the help of the :class:`read_pwm` class.

    This class helps to find out the min and max duty cycle of the feedback signal of a 
    servo. This values ( ``dcMin`` / ``dcMax`` ) are then needed in :ref:`lib_motion` 
    to have a more precise measurement of the position. The experience has shown that each
    servo has slightly different min/max duty cycle values, different than the once 
    provided in the data sheet 360_data_sheet_ . Values smaller and bigger than the 
    printed out once as "duty_cycle_min/duty_cycle_max" are outliers and should 
    therefore not be considered. This can be seen in the printouts of smallest/biggest 
    250 values. There are sometimes a few outliers. Compare the printouts of different
    runs to get a feeling for it.

    .. note::
        The robot wheels must be able to rotate free in the air for calibration.
        Rotating forward or backward might sometimes give slightly 
        different results for min/max duty cycle. Choose the smallest value and the 
        biggest value out of the forward and backward runs. Do both directions three 
        times for each wheel, with speed = 0.2 and -0.2. Then 
        chose the values. The speed has to be set manually, see :ref:`Examples`.

    :param pigpio.pi pi: 
        Instance of a pigpio.pi() object.
    :param int gpio:
        GPIO identified by their Broadcom number, see elinux.org_ .
        To this GPIO the feedback wire of the servo has to be connected.
    :param int,float measurement_time:
        Time in seconds for how long duty cycle values will be collected, so for how long the
        measurement will be made. **Default:** 120.
    :returns: Printouts of different measurements

    At the moment, the period for a 910 Hz signal is hardcoded, as in :meth:`read_pwm` .

    .. todo::
        Enable the class to be able to handle different signals, not just 910 Hz.

    .. _elinux.org: https://elinux.org/RPi_Low-level_peripherals#Model_A.2B.2C_B.2B_and_B2
    .. _`360_data_sheet`: https://www.parallax.com/sites/default/files/downloads/900-00360-Feedback-360-HS-Servo-v1.1.pdf
    """

    def __init__(self, pi, gpio, measurement_time = 120):
         
        self.pi = pi
        self.gpio = gpio
        self.period = 1/910*1000000
        self.tick_high = None
        self.duty_cycle = None
        self.duty_scale = 1000
        self.list_duty_cycles = []
        self.duty_cycle_min = None
        self.duty_cycle_max = None

        #http://abyz.me.uk/rpi/pigpio/python.html#set_mode
        self.pi.set_mode(gpio=self.gpio, mode=pigpio.INPUT)

        #http://abyz.me.uk/rpi/pigpio/python.html#callback
        self.cb = self.pi.callback(user_gpio=self.gpio, edge=pigpio.EITHER_EDGE, func=self.cbf)
        
        print('{}{}{}'.format('Starting measurements for: ', measurement_time, ' seconds.'))
        print('----------------------------------------------------------')
        time.sleep(measurement_time)

        #stop callback before sorting list to avoid getting added new elements unintended
        #http://abyz.me.uk/rpi/pigpio/python.html#callback
        self.cb.cancel()
        time.sleep(1)
        
        self.list_duty_cycles = sorted(self.list_duty_cycles)

        #some analyzis of the dc values
        sorted_set = list(sorted(set(self.list_duty_cycles)))
        print('{} {}'.format('Ascending sorted distinct duty cycle values:', sorted_set))
        print('----------------------------------------------------------')
        differences_list = [sorted_set[i+1]-sorted_set[i] for i in range(len(sorted_set)-1)]
        rounded_differences_list = [round(differences_list[i],2) for i in range(len(differences_list)-1)]
        counted_sorted_list = collections.Counter(rounded_differences_list)
        print('{} {}'.format('Ascending counted, sorted and rounded distinct differences between duty cycle values:',counted_sorted_list))
        print('----------------------------------------------------------')

        #Median and median_high/median_low are chosen, because the biggest 
        #and smallest values are needed, and not an avarage of the smallest 
        #and biggest values of the selection. 
        #https://docs.python.org/3/library/statistics.html#statistics.median
        print('{} {}'.format('Smallest 250 values:', self.list_duty_cycles[:250]))
        self.duty_cycle_min = statistics.median_high(self.list_duty_cycles[:20])
        print('----------------------------------------------------------')
        print('{} {}'.format('Biggest 250 values:',self.list_duty_cycles[-250:]))
        self.duty_cycle_max = statistics.median_low(self.list_duty_cycles[-20:])
        print('----------------------------------------------------------')

        print('duty_cycle_min:', round(self.duty_cycle_min,2))

        print('duty_cycle_max:', round(self.duty_cycle_max,2))
        
    def cbf(self, gpio, level, tick):

        #change to low (a falling edge)
        if level == 0:
            #if first edge is a falling one the following code will not work
            #a try first time is faster than an if-statement every time 
            try:
                self.duty_cycle = self.duty_scale*pigpio.tickDiff(t1=self.tick_high, t2=tick)/self.period
                self.list_duty_cycles.append(self.duty_cycle)

            except Exception:
                pass

        #change to high (a rising edge)
        elif level == 1:

            self.tick_high = tick
            
    def cancel(self):

        self.cb.cancel()

class control:
    """
    Controls the robot movement.

    This class controls the robots movement by controlling the two Parallax Feedback 360° 
    High-Speed Servos `360_data_sheet`_ . The robots local coordinate system is defined in
    the following way. X-axis positive is straight forward, y-axis positive is perpendicular 
    to the x-axis in the direction to the left wheel. The center (0/0) is where the middle
    of the robots chassi is cutting across a imaginary line through both wheels/servos.
    Angle phi is the displacement of the local coordinate system to the real world 
    coordinate system. See :ref:`Used_local_coordinate_system` for a picture of it.

    .. warning::
        Be carefull with setting the min and max pulsewidth! Test carefully ``min_pw`` and ``max_pw``
        before setting them. Wrong values can damage the servo, see set_servo_pulsewidth_ !!!

    :param pigpio.pi pi: 
        Instance of a pigpio.pi() object.
    :param int width_robot:
        Width of the robot in mm, so distance between middle right wheel and middle 
        left wheel. 
        **Default:** 102 mm, measured.
    :param diameter_wheels:
        Diameter of both wheels. 
        **Default:** 66 mm, measured and taken from the products website `wheel_robot`_ .
    :param int unitsFC:
        Units in a full circle, so each wheel is divided into X sections/ticks. 
        This value should not be changed.
        **Default:** 360
    :param float dcMin_l:
        Min duty cycle of the left wheel. 
        **Default:** 27.3, measured with method :meth:`lib_para_360_servo.calibrate_pwm` , 
        see :ref:`Examples` .
    :param float dcMax_l:
        Max duty cycle of the left wheel. 
        **Default:** 969.15,  measured with method :meth:`lib_para_360_servo.calibrate_pwm` , 
        see :ref:`Examples` .
    :param float dcMin_r:
        Min duty cycle of the right wheel. 
        **Default:** 27.3, measured with method :meth:`lib_para_360_servo.calibrate_pwm` , 
        see :ref:`Examples` .
    :param float dcMax_r:
        Max duty cycle of the left wheel. 
        **Default:** 978.25,  measured with method :meth:`lib_para_360_servo.calibrate_pwm` , 
        see :ref:`Examples` .
    :param int l_wheel_gpio:
        GPIO identified by their Broadcom number, see elinux.org_ .
        To this GPIO the feedback wire of the left servo has to be connected.
    :param int r_wheel_gpio:
        GPIO identified by their Broadcom number, see elinux.org_ .
        To this GPIO the feedback wire of the right servo has to be connected.
    :param int servo_l_gpio:
        GPIO identified by their Broadcom number, see elinux.org_ .
        To this GPIO the control wire of the left servo has to be connected.
    :param int min_pw_l:
        Min pulsewidth, see **Warning**, carefully test the value before!
        **Default:** 1280, taken from the data sheet `360_data_sheet`_ .
    :param int max_pw_l:
        Max pulsewidth, see **Warning**, carefully test the value before!
        **Default:** 1720, taken from the data sheet `360_data_sheet`_ .
    :param int min_speed_l:
        Min speed which the servo is able to move. **Default:** -1, so that 
        the speed range is also scaled between -1 and 1 as the output of 
        the inner control loop.
    :param int max_speed_l:
        Max speed which the servo is able to move. **Default:** 1, so that 
        the speed range is also scaled between -1 and 1 as the output of 
        the inner control loop. 
    :param int servo_r_gpio:
        GPIO identified by their Broadcom number, see elinux.org_ .
        To this GPIO the control wire of the right servo has to be connected.
    :param int min_pw_r:
        Min pulsewidth, see **Warning**, carefully test the value before!
        **Default:** 1280, taken from the data sheet `360_data_sheet`_ .
    :param int max_pw_r:
        Max pulsewidth, see **Warning**, carefully test the value before!
        **Default:** 1720, taken from the data sheet `360_data_sheet`_ .
    :param int min_speed_r:
        Min speed which the servo is able to move. **Default:** -1, so that 
        the speed range is also scaled between -1 and 1 as the output of 
        the inner control loop. 
    :param int max_speed_r:
        Max speed which the servo is able to move. **Default:** 1, so that 
        the speed range is also scaled between -1 and 1 as the output of 
        the inner control loop. 
    :param float sampling_time:
        Sampling time of the four PID controllers in seconds.
        **Default:** 0.01.
        1. PWM of motor feedback is 910Hz (0,001098901 s), so position changes cannot 
        be recognized faster than 1.1 ms. Therefore, it is not needed to run the outer control 
        loop more often and update the speed values which have a 50 Hz (20ms) PWM.
        2. Tests of the runtime of the code including the controller part have shown that
        writing the pulsewidth (pi.set_servo_pulsewidth()) in :meth:`lib_para_360_servo.write_pwm.set_pw` is 
        the bottleneck which drastically slows down the code by the factor ~400 
        (0,002 seconds vs 0,000005 seconds; runtime with vs without writing pulsewidth).
        3. For recognizing the RPMs of the wheels 10ms is needed to have enough changes in the
        position. This was found out by testing. See method :meth:`move` for more informations.
    :param int,float Kp_p:
        Kp value of the outer PID controllers, see method :meth:`move` 
        for more informations.
        **Default:** 0.1.
    :param int,float Ki_p:
        Ki value of the outer PID controllers, see method :meth:`move` 
        for more informations.
        **Default:** 0.1.
    :param int,float Kd_p:
        Kd value of the outer PID controllers, see method :meth:`move` 
        for more informations.
        **Default:** 0.
    :param int,float Kp_s:
        Kp value of the inner PID controllers, see method :meth:`move` 
        for more informations.
        **Default:** 0.5.
    :param int,float Ki_s:
        Ki value of the inner PID controllers, see method :meth:`move` 
        for more informations.
        **Default:** 0.
    :param int,float Kd_s:
        Kd value of the inner PID controllers, see method :meth:`move` 
        for more informations.
        **Default:** 0.

    .. _`360_data_sheet`: https://www.parallax.com/sites/default/files/downloads/900-00360-Feedback-360-HS-Servo-v1.1.pdf
    .. _`wheel_robot`: https://www.parallax.com/product/28114
    .. _elinux.org: https://elinux.org/RPi_Low-level_peripherals#Model_A.2B.2C_B.2B_and_B2
    """

    def __init__(
        self, pi, width_robot = 152, diameter_wheels = 90, unitsFC = 360,
        dcMin_l = 27.3, dcMax_l = 969.15,
        dcMin_r = 27.3, dcMax_r = 978.25,
        l_wheel_gpio = 16, r_wheel_gpio = 20,
        servo_l_gpio = 17, min_pw_l = 1280, max_pw_l = 1720, min_speed_l = -1, max_speed_l = 1,
        servo_r_gpio = 27, min_pw_r = 1280, max_pw_r = 1720, min_speed_r = -1, max_speed_r = 1,
        sampling_time = 0.01,
        Kp_p = .1, #.1 original value
        Ki_p = 0.025,
        Kd_p = 0.0,
        Kp_s = 0.5,
        Ki_s = 0,
        Kd_s = 0):

        # Create I2C bus as normal
        self.i2c = board.I2C()  # uses board.SCL and board.SDA

        # Create the TCA9548A object and give it the I2C bus
        self.tca = adafruit_tca9548a.TCA9548A(self.i2c)

        self.imu = sensor = adafruit_bno055.BNO055_I2C(self.tca[0])
        
        # For each sensor, create it using the TCA9548A channel instead of the I2C object
        self.right_ds       = adafruit_vl53l4cd.VL53L4CD(self.tca[4])
        self.front_ds       = adafruit_vl53l4cd.VL53L4CD(self.tca[0])
        self.left_ds        = adafruit_vl53l4cd.VL53L4CD(self.tca[3])
        # self.front_left_ds  = adafruit_vl53l4cd.VL53L4CD(self.tca[3])
        # self.rear_left_ds   = adafruit_vl53l4cd.VL53L4CD(self.tca[2])
        # self.rear_right_ds  = adafruit_vl53l4cd.VL53L4CD(self.tca[6])
        # self.front_right_ds = adafruit_vl53l4cd.VL53L4CD(self.tca[7])
        self.rear_ds        = adafruit_vl53l4cd.VL53L4CD(self.tca[5])

        self.right_ds.inter_measurement = 0
        self.front_ds.inter_measurement = 0
        self.left_ds.inter_measurement = 0
        # self.front_left_ds.inter_measurement = 0
        # self.rear_left_ds.inter_measurement = 0
        # self.rear_right_ds.inter_measurement = 0
        # self.front_right_ds.inter_measurement = 0
        self.rear_ds.inter_measurement = 0

        self.right_ds.timing_budget = 200
        self.front_ds.timing_budget = 200
        self.left_ds.timing_budget = 200
        # self.front_left_ds.timing_budget = 200
        # self.rear_left_ds.timing_budget = 200
        # self.rear_right_ds.timing_budget = 200
        # self.front_right_ds.timing_budget = 200
        self.rear_ds.timing_budget = 200

        self.right_ds.start_ranging()
        self.front_ds.start_ranging()
        self.left_ds.start_ranging()
        # self.front_left_ds.start_ranging()
        # self.rear_left_ds.start_ranging()
        # self.rear_right_ds.start_ranging()
        # self.front_right_ds.start_ranging()
        self.rear_ds.start_ranging()
        
        self.pi = pi
        self.width_robot = width_robot
        self.diameter_wheels = diameter_wheels
        self.unitsFC = unitsFC
        self.dcMin_l = dcMin_l
        self.dcMax_l = dcMax_l
        self.dcMin_r = dcMin_r
        self.dcMax_r = dcMax_r
        self.sampling_time = sampling_time
        self.Kp_p = Kp_p
        self.Ki_p = Ki_p
        self.Kd_p = Kd_p
        self.Kp_s = Kp_s
        self.Ki_s = Ki_s
        self.Kd_s = Kd_s

        self.l_wheel = read_pwm(pi = self.pi, gpio = l_wheel_gpio)
        self.r_wheel = read_pwm(pi = self.pi, gpio = r_wheel_gpio)
        self.servo_l = write_pwm(pi = self.pi, gpio = servo_l_gpio, min_pw = min_pw_l, max_pw = max_pw_l, min_speed = min_speed_l, max_speed = max_speed_l)
        self.servo_r = write_pwm(pi = self.pi, gpio = servo_r_gpio, min_pw = min_pw_r, max_pw = max_pw_r, min_speed = min_speed_r, max_speed = max_speed_r)

        # Blob Detection Camera
        self.blob=ThreadedBlob()
        self.blob.start()
        

        #needed time for initializing the four instances
        time.sleep(1)

    def get_distance_reading(self,ds):
        while not ds.data_ready:
            pass
        ds.clear_interrupt()
        return ds.distance

    def get_primary_distance_sensor_readings(self):
        while not self.front_ds.data_ready:
            pass
        self.front_ds.clear_interrupt()

        while not self.right_ds.data_ready:
            pass
        self.right_ds.clear_interrupt()

        while not self.rear_ds.data_ready:
            pass
        self.rear_ds.clear_interrupt()

        while not self.left_ds.data_ready:
            pass
        self.left_ds.clear_interrupt()
        return [self.front_ds.distance,self.right_ds.distance,self.rear_ds.distance,self.left_ds.distance]
    def get_secondary_distance_sensor_readings(self):
        return [self.front_right_ds.distance,self.rear_right_ds.distance,self.rear_left_ds.distance,self.front_left_ds.distance]

    #angular position in units full circle
    def get_angle_l(self):

        #driving forward will increase the angle
        angle_l = (self.unitsFC - 1) - ((self.l_wheel.read() - self.dcMin_l) * self.unitsFC) / (self.dcMax_l - self.dcMin_l + 1)

        angle_l = max(min((self.unitsFC - 1), angle_l), 0)

        return angle_l

    #angular position in units full circle
    def get_angle_r(self):

        #driving forward will increase the angle
        angle_r = (self.r_wheel.read() - self.dcMin_r) * self.unitsFC / (self.dcMax_r - self.dcMin_r + 1)

        angle_r = max(min((self.unitsFC - 1), angle_r), 0)

        return angle_r

    def set_speed_l(self, speed):

        #the value of the speed of the left wheel will always be multiplied 
        #by minus 1 before setting it.
        #this ensures that e.g. positive passed speed values/arguments
        #will let the robot drive forward, which means for the left servo 
        #that it has to rotate counter-clockwise/negative in its local 
        #orientation system as it is defined in the lib_para_360_servo module.
        self.servo_l.set_speed(-speed)

        return None

    def set_speed_r(self, speed):

        self.servo_r.set_speed(speed)

        return None

    def get_total_angle(self, angle, unitsFC, prev_angle, turns):
       
        #### counting number of rotations
        #If 4th to 1st quadrant
        if((angle < (0.25*unitsFC)) and (prev_angle > (0.75*unitsFC))):
            turns += 1
        #If in 1st to 4th quadrant
        elif((prev_angle < (0.25*unitsFC)) and (angle > (0.75*unitsFC))):
            turns -= 1

        ####total angle measurement from zero
        if(turns >= 0):
            total_angle = (turns*unitsFC) + angle
        elif(turns < 0):
            total_angle = ((turns + 1)*unitsFC) - (unitsFC - angle)

        return turns, total_angle

    def get_target_angle(self, number_ticks, angle):
        
        #positiv number_ticks will be added, negativ number_ticks substracted
        target_angle = angle + number_ticks

        return target_angle

    def tick_length(self):

        tick_length_mm = math.pi * self.diameter_wheels / self.unitsFC

        return tick_length_mm

    def arc_circle(self, degree):

        arc_circle_mm = degree * math.pi * self.width_robot / 360.0

        return arc_circle_mm

    def turn(self, degree):
        """
        Turns the robot about x degree.

        This method turns the robot x degree to the left or to the right. 
        Positive degree values turn the robot to the left,
        negative degree values to the right, see picture in :ref:`Used_local_coordinate_system` , 
        where the local coordinate system of the robot is shown. This method calls 
        :meth:`lib_motion.control.move` which controls the movement of the robot.

        :param int,float degree:
            Degree the robot has to turn.
        """

        number_ticks = self.arc_circle(degree)/self.tick_length()

        self.move(number_ticks = number_ticks, turn = True)

        # TODO: use IMU to rotate
        
        return None

    def straight(self, distance_in_mm):
        """
        Moves the robot about x mm forward or backward.

        This method moves the robot x mm forward or backward. Positive distance 
        values move the robot forward (regarding the local x-axis), negative distance 
        values backward (regarding the local x-axis), see picture in :ref:`Used_local_coordinate_system` , 
        where the local coordinate system of the robot is shown. This method calls 
        :meth:`lib_motion.control.move` which controls the movement of the robot.

        :param int,float distance_in_mm:
            Distance the robot has to move.
        """

        number_ticks = distance_in_mm/self.tick_length()

        self.move(number_ticks = number_ticks, straight = True)

        return None

    def move(
        self,
        number_ticks = 0,
        straight = False, 
        turn = False):
        """
        Core of motion control.

        This method controls the movement of the robot. It is called from :meth:`lib_motion.control.turn` 
        or :meth:`lib_motion.control.straight` and is not ment to be called directly. Four 
        digital PID controllers are used to make two cascade control loops, one cascade control loop
        for each wheel. Each cascade control loop has the same parameters (P/I/D parameters), so that 
        both wheels are controlled in the same way. Chosen default: Outer control loop is a PI 
        controller, inner control loop is a P controller. The outer loop is a position controller,
        the inner loop a speed controller. After both wheels have reached their set-point (position), 
        the method waits one second before the movement is marked as finished. This ensures that 
        overshoots/oscillations are possible and that both wheels can independently reach their
        set-point (position). The I part of each PID controller is limited to -1 and 1, so that 
        the sum of the errors is not integrated till infinity which means to very high or low values 
        which might cause problems. The output value of each inner PID controller is scaled between -1 
        and 1 and the output value of each outer PID controller is limited to -1 and 1.
        This ensures that no scaling factors are introduced in the P/I/D parameters and also that
        the output of each PID controller matches the speed range of the servos, defined in 
        :meth:`lib_para_360_servo.write_pwm.set_speed` . A sliding median window is used to filter out
        the noise in the rotation speed measurement (ticks/s) which is done indirectly by measuring the 
        position of the servo. Also a deadband filter after the error calculation of the outer control
        loop is implemented. This adjustments help to make the controllers more stable, e.g. filter out
        outliers while calculating the rotation speed and therefore avoid high value changes/jumps or
        avoid oscillations after reaching the set-point (position). The sample time of the digital PID
        controllers can also be freely chosen and does not influence the P/I/D parameters, the rotation
        speed measurement or the time before the movement is marked as finished.

        :param int,float number_ticks:
            Number of ticks the wheels have to move.
        :param bool straight:
            True or False, if robot should move straight. 
            **Default:** False.
        :param bool turn:
            True or False, if robot should turn. 
            **Default:** False.
        """

        turns_l = 0
        turns_r = 0

        angle_l = self.get_angle_l()
        angle_r = self.get_angle_r()

        target_angle_r = self.get_target_angle(number_ticks = number_ticks, angle = angle_r)

        if straight == True:

            #speed and number_ticks of servo_l must rotate in
            #SAME direction to servo_r while driving straight
            target_angle_l = self.get_target_angle(number_ticks = number_ticks, angle = angle_l)

        elif turn == True:
            
            #speed and number_ticks of servo_l must rotate in
            #OPPOSITE direction to servo_r while turning
            target_angle_l = self.get_target_angle(number_ticks = -number_ticks, angle = angle_l)

        #initial values sum_error_*
        sum_error_r_p = 0
        sum_error_r_s = 0
        sum_error_l_p = 0
        sum_error_l_s = 0
        
        #initial values error_*_old
        error_l_p_old = 0
        error_l_s_old = 0
        error_r_p_old = 0
        error_r_s_old = 0

        #empty lists for ticks_*
        list_ticks_l = []
        list_ticks_r = []

        position_reached = False
        reached_sp_counter = 0
        #position must be reached for one second to allow
        #overshoots/oscillations before stopping control loop
        wait_after_reach_sp = 1/self.sampling_time

        #start time of the control loop
        start_time = time.time()

        #control loop:
        while not position_reached:
            #DEBUGGING OPTION:
            #printing runtime of loop , see end of while true loop
            #start_time_each_loop = time.time()

            angle_l = self.get_angle_l()
            angle_r = self.get_angle_r()

            #try needed, because:
            #- first iteration of the while loop prev_angle_* is missing and the 
            #method self.get_total_angle() will throw an exception.
            #- second iteration of the while loop prev_total_angle_* is missing, 
            #which will throw another exception
            try:
                turns_l, total_angle_l = self.get_total_angle(angle_l, self.unitsFC, prev_angle_l, turns_l)
                turns_r, total_angle_r = self.get_total_angle(angle_r, self.unitsFC, prev_angle_r, turns_r)

                #### cascade control right wheel

                ## Position Control
                #Er = SP - PV
                error_r_p = target_angle_r - total_angle_r

                #Deadband-Filter to remove ocillating forwards and backwards after reaching set-point
                if error_r_p <= 2 and error_r_p >= -2:
                    error_r_p = 0
                #I-Part
                sum_error_r_p += error_r_p
                #limit I-Part to -1 and 1 
                #try needed, because Ki_p can be zero
                try:
                    sum_error_r_p = max(min(1/self.Ki_p, sum_error_r_p), -1/self.Ki_p)
                except Exception:
                    pass

                #PID-Controller
                output_r_p = self.Kp_p * error_r_p + self.Ki_p * self.sampling_time * sum_error_r_p + self.Kd_p / self.sampling_time * (error_r_p - error_r_p_old)
                #limit output of position control to speed range
                output_r_p = max(min(1, output_r_p), -1)

                error_r_p_old = error_r_p

                ## Speed Control
                #convert range output_r_p from -1 to 1 to ticks/s
                #full speed of a wheel forward and backward = +-650 ticks/s
                output_r_p_con = 650 * output_r_p
                #ticks per second (ticks/s), calculated from a moving median window with 5 values
                ticks_r = (total_angle_r - prev_total_angle_r) / self.sampling_time
                list_ticks_r.append(ticks_r)
                list_ticks_r = list_ticks_r[-5:]
                ticks_r = statistics.median(list_ticks_r)
                
                #Er = SP - PV
                error_r_s = output_r_p_con - ticks_r

                #I-Part
                sum_error_r_s += error_r_s
                #limit I-Part to -1 and 1
                #try needed, because Ki_s can be zero
                try:
                    sum_error_r_s = max(min(650/self.Ki_s, sum_error_r_s), -650/self.Ki_s)
                except Exception:
                    pass

                #PID-Controller
                output_r_s = self.Kp_s * error_r_s + self.Ki_s * self.sampling_time * sum_error_r_s + self.Kd_s / self.sampling_time * (error_r_s - error_r_s_old)

                error_r_s_old = error_r_s

                #convert range output_r_s fom ticks/s to -1 to 1
                output_r_s_con = output_r_s / 650

                self.set_speed_r(output_r_s_con)

                #### cascade control left wheel
                
                ## Position Control
                #Er = SP - PV
                error_l_p = target_angle_l - total_angle_l
                #Deadband-Filter to remove ocillating forwards and backwards after reaching set-point
                if error_l_p <= 2 and error_l_p >= -2:
                    error_l_p = 0
                #I-Part
                sum_error_l_p += error_l_p

                #limit I-Part to -1 and 1
                #try needed, because Ki_p can be zero
                try:
                    sum_error_l_p = max(min(1/self.Ki_p, sum_error_l_p), -1/self.Ki_p)
                except Exception:
                    pass

                #PID-Controller
                output_l_p = self.Kp_p * error_l_p + self.Ki_p * self.sampling_time * sum_error_l_p + self.Kd_p / self.sampling_time * (error_l_p - error_l_p_old)
                #limit output of position control to speed range
                output_l_p = max(min(1, output_l_p), -1)

                error_l_p_old = error_l_p

                ## Speed Control
                #convert range output_l_p from -1 to 1 to ticks/s
                #full speed of a wheel forward and backward = +-650 ticks/s
                output_l_p_con = 650 * output_l_p
                #ticks per second (ticks/s), calculated from a moving median window with 5 values
                ticks_l = (total_angle_l - prev_total_angle_l) / self.sampling_time
                list_ticks_l.append(ticks_l)
                list_ticks_l = list_ticks_l[-5:]
                ticks_l = statistics.median(list_ticks_l)
                #Er = SP - PV
                error_l_s = output_l_p_con - ticks_l

                #I-Part
                sum_error_l_s += error_l_s
                #limit I-Part to -1 and 1
                #try needed, because Ki_s can be zero
                try:
                    sum_error_l_s = max(min(650/self.Ki_s, sum_error_l_s), -650/self.Ki_s)
                except Exception:
                    pass

                #PID-Controller
                output_l_s = self.Kp_s * error_l_s + self.Ki_s * self.sampling_time * sum_error_l_s + self.Kd_s / self.sampling_time * (error_l_s - error_l_s_old)

                error_l_s_old = error_l_s

                #convert range output_l_s fom ticks/s to -1 to 1
                output_l_s_con = output_l_s / 650

                self.set_speed_l(output_l_s_con)

            except Exception:
                pass

            prev_angle_l = angle_l
            prev_angle_r = angle_r

            #try needed, because first iteration of the while loop prev_angle_* is
            #missing and the method self.get_total_angle() will throw an exception,
            #and therefore no total_angle_* gets calculated

            try:
                prev_total_angle_l = total_angle_l
                prev_total_angle_r = total_angle_r
            except Exception:
                pass

            try:
                if error_l_p == 0 and error_r_p == 0:
                    reached_sp_counter += 1

                    if reached_sp_counter >= wait_after_reach_sp:
                        self.set_speed_r(0.0)
                        self.set_speed_l(0.0)
                        position_reached = True
                else:
                    pass

            except Exception:
                pass

            #Pause control loop for chosen sample time
            #https://stackoverflow.com/questions/474528/what-is-the-best-way-to-repeatedly-execute-a-function-every-x-seconds-in-python/25251804#25251804
            time.sleep(self.sampling_time - ((time.time() - start_time) % self.sampling_time))

            #DEBUGGING OPTION: 
            #printing runtime of loop, see beginning of while true loop
            #print('{:.20f}'.format((time.time() - start_time_each_loop)))
        
        return None

    def cancel(self):
        """
        Cancel the started callback function.

        This method cancels the started callback function if initializing an object.
        As written in the pigpio callback_ documentation, the callback function may be cancelled
        by calling the cancel function after the created instance is not needed anymore.

        .. _callback: http://abyz.me.uk/rpi/pigpio/python.html#callback
        """
        self.front_ds.stop_ranging()
        self.right_ds.stop_ranging()
        self.rear_ds.stop_ranging()
        self.left_ds.stop_ranging()
        # self.front_right_ds.stop_ranging()
        # self.front_left_ds.stop_ranging()
        # self.rear_right_ds.stop_ranging()
        # self.rear_left_ds.stop_ranging()
        self.l_wheel.cancel()
        self.r_wheel.cancel()
        self.blob.stop()