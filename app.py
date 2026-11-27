# Imports
# -------------------------------
# Mouse Tracking via Hand Gesture
# -------------------------------

import cv2
import mediapipe as mp
import pyautogui
import math
import time

pyautogui.FAILSAFE = False

# ---------------- GESTURES ----------------
class Gest:
    PALM = 31
    FIST = 0
    INDEX = 8
    MID = 12
    TWO_FINGER_CLOSED = 34
    V_GEST = 33


# ---------------- HAND DETECTOR ----------------
class HandDetector:

    def __init__(self):
        self.mpHands = mp.solutions.hands
        self.hands = self.mpHands.Hands(
            max_num_hands=1,
            min_detection_confidence=0.7,
            min_tracking_confidence=0.7
        )
        self.mpDraw = mp.solutions.drawing_utils
        self.landmarks = None

    def findHands(self, img):
        imgRGB = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        results = self.hands.process(imgRGB)

        if results.multi_hand_landmarks:
            self.landmarks = results.multi_hand_landmarks[0]
            self.mpDraw.draw_landmarks(
                img,
                self.landmarks,
                self.mpHands.HAND_CONNECTIONS
            )
        return img

    def findPosition(self, img):
        lmList = []
        if self.landmarks:
            h, w, c = img.shape
            for id, lm in enumerate(self.landmarks.landmark):
                cx, cy = int(lm.x * w), int(lm.y * h)
                lmList.append((id, cx, cy))
        return lmList


# ---------------- CONTROLLER ----------------
class Controller:

    click_delay = 0
    CLICK_FRAMES = 8

    def __init__(self):
        self.screen_w, self.screen_h = pyautogui.size()

    def move_mouse(self, x, y, frame_w, frame_h):
        screen_x = self.screen_w * x / frame_w
        screen_y = self.screen_h * y / frame_h
        pyautogui.moveTo(screen_x, screen_y)

    def left_click(self):
        if Controller.click_delay == 0:
            pyautogui.click()
            Controller.click_delay = Controller.CLICK_FRAMES

    def right_click(self):
        if Controller.click_delay == 0:
            pyautogui.click(button='right')
            Controller.click_delay = Controller.CLICK_FRAMES

    def double_click(self):
        if Controller.click_delay == 0:
            pyautogui.doubleClick()
            Controller.click_delay = Controller.CLICK_FRAMES


# ---------------- MAIN PROGRAM ----------------
def main():

    cap = cv2.VideoCapture(0)
    detector = HandDetector()
    controller = Controller()

    while True:

        success, img = cap.read()
        if not success:
            break

        img = cv2.flip(img, 1)
        img = detector.findHands(img)
        lmList = detector.findPosition(img)

        if Controller.click_delay > 0:
            Controller.click_delay -= 1

        if len(lmList) != 0:

            # fingertip positions
            x1, y1 = lmList[8][1:]   # index
            x2, y2 = lmList[12][1:]  # middle
            x3, y3 = lmList[4][1:]   # thumb

            frame_h, frame_w, _ = img.shape

            # distance calculations
            dist_index_middle = math.hypot(x2-x1, y2-y1)
            dist_thumb_index = math.hypot(x3-x1, y3-y1)
# -------- EXIT GESTURE (OPEN PALM) --------
            fingers_open = []

            # fingertip ids
            tips = [4, 8, 12, 16, 20]

            for tip in tips:
                if lmList[tip][2] < lmList[tip-2][2]:
                    fingers_open.append(1)
                else:
                    fingers_open.append(0)

            # if all fingers open → exit
            if fingers_open.count(1) == 5:
                cv2.putText(img, "EXITING...", (50,80),
                            cv2.FONT_HERSHEY_SIMPLEX,
                            1, (0,0,255), 3)
                cv2.imshow("Mouse Tracking via Hand Gesture", img)
                cv2.waitKey(1000)
                break
            # MOVE MOUSE (index finger)
            controller.move_mouse(x1, y1, frame_w, frame_h)

            # LEFT CLICK (index + middle close)
            if dist_index_middle < 30:
                controller.left_click()
                time.sleep(0.2)

            # RIGHT CLICK (thumb + index close)
            elif dist_thumb_index < 30:
                controller.right_click()
                time.sleep(0.2)

            # DOUBLE CLICK
            elif dist_index_middle < 45 and dist_thumb_index < 45:
                controller.double_click()
                time.sleep(0.3)

        cv2.imshow("Mouse Tracking via Hand Gesture", img)

        # ESC key exit
        if cv2.waitKey(1) & 0xFF == 27:
            break

    cap.release()
    cv2.destroyAllWindows()


# ---------------- RUN ----------------
if __name__ == "__main__":
    main()