from djitellopy import Tello
import cv2
import pygame
import numpy as np
import time

# Speed of the drone
S = 60
# Frames per second of the pygame window display
FPS = 120


class FrontEnd(object):
    def __init__(self):
        pygame.init()
        pygame.display.set_caption("Tello video stream")
        self.screen = pygame.display.set_mode([960, 720])

        self.tello = Tello()

        self.for_back_velocity = 0
        self.left_right_velocity = 0
        self.up_down_velocity = 0
        self.yaw_velocity = 0
        self.speed = 10
        self.send_rc_control = False

        self.blur_effect = False  # New: Track blur state

        pygame.time.set_timer(pygame.USEREVENT + 1, 1000 // FPS)

    def run(self):
        self.tello.connect()
        self.tello.set_speed(self.speed)

        self.tello.streamoff()
        self.tello.streamon()

        frame_read = self.tello.get_frame_read()

        should_stop = False
        while not should_stop:

            for event in pygame.event.get():
                if event.type == pygame.USEREVENT + 1:
                    self.update()
                elif event.type == pygame.QUIT:
                    should_stop = True
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        should_stop = True
                    else:
                        self.keydown(event.key)
                elif event.type == pygame.KEYUP:
                    self.keyup(event.key)
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    self.toggle_blur_effect(event.pos)  # New: Handle checkbox click

            if frame_read.stopped:
                break

            self.screen.fill([0, 0, 0])

            frame = frame_read.frame
            text = "Battery: {}%".format(self.tello.get_battery())
            cv2.putText(frame, text, (5, 720 - 5),
                        cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)

            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            if self.blur_effect:  # Apply blur if the effect is active
                frame = cv2.GaussianBlur(frame, (15, 15), 0)

            frame = np.rot90(frame)
            frame = np.flipud(frame)

            frame = pygame.surfarray.make_surface(frame)
            self.screen.blit(frame, (0, 0))

            # Draw checkbox
            self.draw_checkbox()

            if self.blur_effect:  # Show "眠気" if the effect is active
                font = pygame.font.Font(None, 74)
                text_surface = font.render("Sleepy!", True, (255, 0, 0))
                self.screen.blit(text_surface, (400, 300))

            pygame.display.update()
            time.sleep(1 / FPS)

        self.tello.end()

    def keydown(self, key):
        if key == pygame.K_UP:
            self.for_back_velocity = S
        elif key == pygame.K_DOWN:
            self.for_back_velocity = -S
        elif key == pygame.K_LEFT:
            self.left_right_velocity = -S
        elif key == pygame.K_RIGHT:
            self.left_right_velocity = S
        elif key == pygame.K_w:
            self.up_down_velocity = S
        elif key == pygame.K_s:
            self.up_down_velocity = -S
        elif key == pygame.K_a:
            self.yaw_velocity = -S
        elif key == pygame.K_d:
            self.yaw_velocity = S

    def keyup(self, key):
        if key in [pygame.K_UP, pygame.K_DOWN]:
            self.for_back_velocity = 0
        elif key in [pygame.K_LEFT, pygame.K_RIGHT]:
            self.left_right_velocity = 0
        elif key in [pygame.K_w, pygame.K_s]:
            self.up_down_velocity = 0
        elif key in [pygame.K_a, pygame.K_d]:
            self.yaw_velocity = 0
        elif key == pygame.K_t:
            self.tello.takeoff()
            self.send_rc_control = True
        elif key == pygame.K_l:
            self.tello.land()
            self.send_rc_control = False

    def update(self):
        if self.send_rc_control:
            self.tello.send_rc_control(
                self.left_right_velocity, self.for_back_velocity,
                self.up_down_velocity, self.yaw_velocity)

    def draw_checkbox(self):
        """ Draw the checkbox on the screen """
        checkbox_color = (0, 255, 0) if self.blur_effect else (255, 255, 255)
        pygame.draw.rect(self.screen, checkbox_color, (10, 10, 20, 20), 0)  # Checkbox square
        font = pygame.font.Font(None, 36)
        text_surface = font.render("Blur Effect", True, (255, 255, 255))
        self.screen.blit(text_surface, (40, 10))

    def toggle_blur_effect(self, pos):
        """ Toggle the blur effect when checkbox is clicked """
        if 10 <= pos[0] <= 30 and 10 <= pos[1] <= 30:
            self.blur_effect = not self.blur_effect


def main():
    frontend = FrontEnd()
    frontend.run()


if __name__ == '__main__':
    main()
