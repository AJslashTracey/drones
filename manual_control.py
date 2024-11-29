from djitellopy import Tello
import cv2
import manual_control
import numpy as np
import time

# Speed of the drone
S = 60
# Frames per second of the pygame window display
# A low number also results in input lag, as input information is processed once per frame.
FPS = 120


class FrontEnd(object):
    """ Maintains the Tello display and moves it through the keyboard keys.
        Press escape key to quit.
        The controls are:
            - T: Takeoff
            - L: Land
            - Arrow keys: Forward, backward, left and right.
            - A and D: Counter clockwise and clockwise rotations (yaw)
            - W and S: Up and down.
    """

    def __init__(self):
        # Init pygame
        # 初始化pygame
        manual_control.init()

        # Creat pygame window
        # 创建pygame窗口
        manual_control.display.set_caption("Tello video stream")
        self.screen = manual_control.display.set_mode([960, 720])

        # Init Tello object that interacts with the Tello drone
        # 初始化与Tello交互的Tello对象
        self.tello = Tello()

        # Drone velocities between -100~100
        self.for_back_velocity = 0
        self.left_right_velocity = 0
        self.up_down_velocity = 0
        self.yaw_velocity = 0
        self.speed = 10

        self.send_rc_control = False

        # create update timer
        manual_control.time.set_timer(manual_control.USEREVENT + 1, 1000 // FPS)

    def run(self):

        self.tello.connect()
        self.tello.set_speed(self.speed)

        # In case streaming is on. This happens when we quit this program without the escape key.
        self.tello.streamoff()
        self.tello.streamon()

        frame_read = self.tello.get_frame_read()

        should_stop = False
        while not should_stop:

            for event in manual_control.event.get():
                if event.type == manual_control.USEREVENT + 1:
                    self.update()
                elif event.type == manual_control.QUIT:
                    should_stop = True
                elif event.type == manual_control.KEYDOWN:
                    if event.key == manual_control.K_ESCAPE:
                        should_stop = True
                    else:
                        self.keydown(event.key)
                elif event.type == manual_control.KEYUP:
                    self.keyup(event.key)

            if frame_read.stopped:
                break

            self.screen.fill([0, 0, 0])

            frame = frame_read.frame
            # battery n. 电池
            text = "Battery: {}%".format(self.tello.get_battery())
            cv2.putText(frame, text, (5, 720 - 5),
                cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            frame = np.rot90(frame)
            frame = np.flipud(frame)

            frame = manual_control.surfarray.make_surface(frame)
            self.screen.blit(frame, (0, 0))
            manual_control.display.update()

            time.sleep(1 / FPS)

        # Call it always before finishing. To deallocate resources.
        self.tello.end()

    def keydown(self, key):
        """ Update velocities based on key pressed
        Arguments:
            key: pygame key
        """
        if key == manual_control.K_UP:  # set forward velocity
            self.for_back_velocity = S
        elif key == manual_control.K_DOWN:  # set backward velocity
            self.for_back_velocity = -S
        elif key == manual_control.K_LEFT:  # set left velocity
            self.left_right_velocity = -S
        elif key == manual_control.K_RIGHT:  # set right velocity
            self.left_right_velocity = S
        elif key == manual_control.K_w:  # set up velocity
            self.up_down_velocity = S
        elif key == manual_control.K_s:  # set down velocity
            self.up_down_velocity = -S
        elif key == manual_control.K_a:  # set yaw counter clockwise velocity
            self.yaw_velocity = -S
        elif key == manual_control.K_d:  # set yaw clockwise velocity
            self.yaw_velocity = S

    def keyup(self, key):
        """ Update velocities based on key released
        Arguments:
            key: pygame key
        """
        if key == manual_control.K_UP or key == manual_control.K_DOWN:  # set zero forward/backward velocity
            self.for_back_velocity = 0
        elif key == manual_control.K_LEFT or key == manual_control.K_RIGHT:  # set zero left/right velocity
            self.left_right_velocity = 0
        elif key == manual_control.K_w or key == manual_control.K_s:  # set zero up/down velocity
            self.up_down_velocity = 0
        elif key == manual_control.K_a or key == manual_control.K_d:  # set zero yaw velocity
            self.yaw_velocity = 0
        elif key == manual_control.K_t:  # takeoff
            self.tello.takeoff()
            self.send_rc_control = True
        elif key == manual_control.K_l:  # land
            not self.tello.land()
            self.send_rc_control = False

    def update(self):
        """ Update routine. Send velocities to Tello.
        """
        if self.send_rc_control:
            self.tello.send_rc_control(self.left_right_velocity, self.for_back_velocity,
                self.up_down_velocity, self.yaw_velocity)


def main():
    frontend = FrontEnd()

    # run frontend

    frontend.run()


if __name__ == '__main__':
    main()