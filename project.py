import cv2
import random
import numpy as np
import tkinter as tk
from PIL import Image, ImageTk

import mediapipe as mp

class Model:
    def __init__(self) -> None:
        self.mp_face_detection = mp.solutions.face_detection # type: ignore
        self.face_detection = self.mp_face_detection.FaceDetection(
            model_selection=1, min_detection_confidence=0.5
        )

    def apply_model(self, frame):
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = self.face_detection.process(frame)

        if results.detections:
            for detection in results.detections:
                # mp_draw.draw_detection(frame, detection)
                loc = detection.location_data.relative_bounding_box
                xmin = int(loc.xmin * frame.shape[1])
                ymin = int(loc.ymin * frame.shape[0])
                xmax = xmin + int(loc.width * frame.shape[1])
                ymax = ymin + int(loc.height * frame.shape[0])

                return (xmin + xmax)//2, ymin


class VideoGenerate:
    __COLORS = [
        (255, 0, 0),
        (36, 47, 16),
        (103, 30, 1),
        (82, 92, 15),
        (104, 63, 87),
        (176, 125, 56),
        (97, 122, 62),
        (84, 94, 42),
        (50, 18, 134),
        (60, 20, 220),
    ]

    def __init__(self, cap):
        self.cap = cap
        self.frame: np.ndarray
        self.colors = {}

        self.window = tk.Tk()
        self.is_initialized = False
        # self.window.geometry("640x580")

        """Radio Buttons"""
        OPTIONS = ["Single Track", "Multi Track"]
        self.var = tk.IntVar()
        self.var.set(1)  # Setting multi mode as default

        radio_frame = tk.Frame(self.window)
        radio_frame.pack(side=tk.TOP)

        text_label = tk.Label(radio_frame, text="Tracking Option")
        text_label.config(font=("Arial", 12, "bold"))
        text_label.pack(side=tk.TOP)

        r1 = tk.Radiobutton(
            radio_frame,
            text=OPTIONS[0],
            variable=self.var,
            value=0,
            command=self.input_field,
        )
        r1.configure(padx=2, pady=2, font=("Arial", 10, "bold"))
        r1.pack(side=tk.LEFT)

        r2 = tk.Radiobutton(
            radio_frame,
            text=OPTIONS[1],
            variable=self.var,
            value=1,
            command=self.input_field,
        )
        r2.configure(padx=2, pady=2, font=("Arial", 10, "bold"))
        r2.pack(side=tk.LEFT)
        """Radio Buttons"""

        self.input_entry = tk.Entry(self.window)
        self.input_entry.config(
            font=("Roboto Mono", 12, "bold"), width=12, state="disabled"
        )
        self.input_entry.pack(padx=5, pady=5, side=tk.TOP)

        self.button = tk.Button(self.window, text="OK", command=self.get_roll)
        self.button.configure(
            height=1,
            width=4,
            font=("Roboto Mono", 13, "bold"),
            padx=5,
            pady=3,
            state="disabled",
        )
        self.button.pack(side=tk.TOP)

        self.label = tk.Label(self.window)
        self.label.pack()

        self.window.protocol("WM_DELETE_WINDOW", self.on_window_close)

    def initialize_window_size(self):
        self.is_initialized = True
        self.window.geometry(f"{self.frame.shape[1]}x{self.frame.shape[0] + 100}")
        self.window.resizable(False, False)

    def read_cap(self):
        ret, self.frame = cap.read()
        return ret, self.frame

    def display_window(self):
        self.read_cap()
        self.initialize_window_size()
        model = Model()

        while True:
            ret, frame = self.read_cap()
            if not ret:
                break

            point = model.apply_model(frame)
            if point is not None:
                self.put_labels( {'170111': point} )

            image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            image = Image.fromarray(image)
            image = ImageTk.PhotoImage(image)
            self.label.configure(image=image)
            self.label.image = image  # type: ignore

            self.window.update()

    def put_labels(self, student: dict):
        BASE_HEIGHT_RATIO = 0.85
        HEIGHT = 17
        BASE = int(HEIGHT * BASE_HEIGHT_RATIO)
        THICKNESS = 4

        for roll in student.keys():
            if not self.colors.__contains__(roll):
                color = random.choice(VideoGenerate.__COLORS)
                self.colors[roll] = color

            point = student[roll]
            color = self.colors[roll]

            point1 = point
            point2 = (point1[0] - BASE // 2), (point1[1] - HEIGHT)
            point3 = (point1[0] + BASE // 2), (point1[1] - HEIGHT)

            cv2.line(self.frame, point1, point2, color=color, thickness=THICKNESS)
            cv2.line(self.frame, point2, point3, color=color, thickness=THICKNESS)
            cv2.line(self.frame, point1, point3, color=color, thickness=THICKNESS)

            '''Label Box'''
            BOX_HEIGHT = 22
            BOX_WIDTH = max(50, len(roll) * 13)
            BOX_GAP = 5

            start_x = point[0] - BOX_WIDTH // 2
            start_y = point[1] - (HEIGHT + BOX_HEIGHT + BOX_GAP)

            end_x = point[0] + BOX_WIDTH // 2
            end_y = start_y + BOX_HEIGHT

            start = start_x, start_y
            end = end_x, end_y

            cv2.rectangle(
                self.frame,
                start,
                end,
                color=color,
                thickness=-1,
                lineType=cv2.LINE_AA,
            )

            '''Putting Text'''
            FONT = cv2.FONT_HERSHEY_COMPLEX_SMALL
            FONTSCALE = 0.8
            text_size = cv2.getTextSize(roll, FONT, FONTSCALE, 1)[0]

            text_x = (start_x + end_x - text_size[0]) // 2
            text_y = (start_y + end_y + text_size[1]) // 2
            cv2.putText(
                self.frame,
                roll,
                (text_x, text_y),
                FONT,
                FONTSCALE,
                (255, 255, 255),
                1,
                cv2.LINE_AA,
            )

    def get_roll(self):
        std_id = self.input_entry.get()
        return std_id

    def input_field(self):
        if self.var.get() == 0:
            # * single track
            self.input_entry.config(state="normal")
            self.button.config(state="normal")

        else:
            # * Multi track
            # self.input_entry.delete(0, tk.END)
            self.input_entry.config(state="disabled")
            self.button.config(state="disabled")

    def on_window_close(self):
        self.cap.release()
        cv2.destroyAllWindows()
        self.window.destroy()


if __name__ == "__main__":
    cap = cv2.VideoCapture(0)
    video = VideoGenerate(cap=cap)
    video.display_window()
