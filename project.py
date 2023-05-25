import cv2
import numpy as np
import tkinter as tk
from PIL import Image, ImageTk

import mediapipe as mp
from typing import List

def showing_name(img, name, start_points: List[tuple], end_points: List[tuple], absolute_point=False):
    for start, end in zip(start_points, end_points):
        color = [255, 0, 0]        
        img_height, img_width = img.shape[:2]
        
        # Drawing Box
        if absolute_point is False:
            box_start_x = int(start[0]*img_width)
            box_start_y = int(start[1]*img_height)
            box_end_x = int(end[0]*img_width)
            box_end_y = int(end[1]*img_height)
        else:
            box_start_x, box_start_y = start
            box_end_x, box_end_y = end
            
        box_start_pos = (box_start_x, box_start_y)
        box_end_pos = (box_end_x, box_end_y)
        
        # cv2.rectangle(img, box_start_pos, box_end_pos,
        #              color= (30,129,176), thickness= 2)
        
        
        box_middle_x = (box_start_x+box_end_x)//2
        #Drawing triangle on top of the rectangle
        base_height_ratio = .85
        height = 20
        base = int(height*base_height_ratio)
        # color = (30,129,176)
        thickness = 4
        
        point1_x = box_middle_x
        point1_y = box_start_y
        point2_y = point1_y-height
        point2_x = point1_x - base//2
        point3_x = point2_x + base
        point3_y = point2_y
        
        point1 = point1_x, point1_y
        point2 = point2_x, point2_y
        point3 = point3_x, point3_y
            
        cv2.line(img, point1, point2, color=color, thickness=thickness)
        cv2.line(img, point2, point3, color=color, thickness=thickness)
        cv2.line(img, point1, point3, color=color, thickness=thickness)
        

        
        # Drawing Box top of the box
        title_box_height = 25
        title_box_width = max(50, len(name)*14)
        title_box_gap = 7
        title_box_start_x = box_middle_x - title_box_width//2
        title_box_start_y = point2_y - (title_box_height +title_box_gap)
        
        # If there is no place to show name on top of the box. 
        if box_start_y <= title_box_height+title_box_gap:
            title_box_start_y = box_end_y + title_box_gap
            
        title_box_end_x = box_middle_x + title_box_width//2
        title_box_end_y = title_box_start_y + title_box_height
        title_box_start = title_box_start_x, title_box_start_y
        title_box_end = title_box_end_x, title_box_end_y
        
        
        cv2.rectangle(img, title_box_start, title_box_end,
                    color= color, thickness= -1,
                    lineType= cv2.LINE_AA,)
        
        #putting text
        font = cv2.FONT_HERSHEY_COMPLEX_SMALL
        fontScale = .9
        thickness = 1
        text_size = cv2.getTextSize(name, font, fontScale, thickness)[0]
        
        text_x = int((title_box_start_x + title_box_end_x - text_size[0]) / 2)
        text_y = int((title_box_start_y + title_box_end_y + text_size[1]) / 2)
        cv2.putText(img, name, (text_x, text_y), font, fontScale, (255, 255, 255), thickness, cv2.LINE_AA)


        #Second Rectangle outside the first one
        # new_box_start_x = box_start_x-title_box_gap
        # new_box_start_y = box_start_y-title_box_gap
        # new_box_end_x = box_end_x+title_box_gap
        # new_box_end_y = box_end_y+title_box_gap
        # new_box_start = new_box_start_x, new_box_start_y
        # new_box_end = new_box_end_x, new_box_end_y
        # cv2.rectangle(img, new_box_start, new_box_end, 
        #               color=(30, 129, 176), thickness=2,
        #                      lineType= cv2.LINE_AA)
        
        
        
    
    return img
    

class Model():
    def __init__(self) -> None:
        self.mp_face_detection = mp.solutions.face_detection
        self.face_detection = self.mp_face_detection.FaceDetection(model_selection=1,
                                                min_detection_confidence=.5)

    def apply_model(self, frame):
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = self.face_detection.process(frame)
        
        if results.detections:
            for detection in results.detections:
                # mp_draw.draw_detection(frame, detection)
                loc = detection.location_data.relative_bounding_box
                xmin = int(loc.xmin*frame.shape[1])
                ymin = int(loc.ymin*frame.shape[0])
                xmax = xmin + int(loc.width*frame.shape[1])
                ymax = ymin + int(loc.height*frame.shape[0])
                
                return ((xmin, ymin), (xmax, ymax))
            

class VideoGenerate():
    def __init__(self, cap):
        self.frame: np.ndarray
        self.cap = cap

        self.window = tk.Tk()
        self.is_initialized = False
        # self.window.geometry("640x580")

        '''Radio Buttons'''
        OPTIONS = ['Single Track', 'Multi Track']
        self.var = tk.IntVar()
        self.var.set(1) #Setting multi mode as default

        radio_frame = tk.Frame(self.window)
        radio_frame.pack(side=tk.TOP)

        text_label = tk.Label(radio_frame, text= 'Tracking Option')
        text_label.config(font= ('Arial', 12, 'bold'))
        text_label.pack(side= tk.TOP)
        
        r1 = tk.Radiobutton(radio_frame, text=OPTIONS[0], variable=self.var, 
                            value=0, command=self.input_field)
        r1.configure(padx=2, pady=2, font=('Arial', 10, 'bold'))
        r1.pack(side=tk.LEFT)

        r2 = tk.Radiobutton(radio_frame, text=OPTIONS[1], variable=self.var, 
                            value=1, command=self.input_field)
        r2.configure(padx=2, pady=2, font=('Arial', 10, 'bold'))
        r2.pack(side=tk.LEFT)
        '''Radio Buttons'''

        self.input_entry = tk.Entry(self.window)
        self.input_entry.config(font= ("Roboto Mono", 12, "bold"), width=12, state= 'disabled')
        self.input_entry.pack(padx=5, pady=5, side=tk.TOP)

        self.button = tk.Button(self.window, text="OK", command=self.get_id)
        self.button.configure(height=1, width=4, font=('Roboto Mono', 13, 'bold'), padx=5, pady=3)
        self.button.pack(side=tk.TOP)

        self.label = tk.Label(self.window)
        self.label.pack()

        self.window.protocol("WM_DELETE_WINDOW", self.on_window_close)
        
    def initialize_window_size(self):
        self.is_initialized = True
        self.window.geometry(f'{self.frame.shape[1]}x{self.frame.shape[0] + 100}')
        self.window.resizable(False, False)
        
    def read_cap(self):
        ret, self.frame = cap.read()
        return ret, self.frame

    def display_window(self):
        self.read_cap()
        self.initialize_window_size()
        
        while True:
            ret, frame = self.read_cap()
            if not ret: break
            
            point = Model().apply_model(frame)
            print(point)
            if point is not None:
                self.drawing(point[0], point[1])
            
            
            image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            image = Image.fromarray(image)
            image = ImageTk.PhotoImage(image)
            self.label.configure(image=image)
            self.label.image = image #type: ignore

            self.window.update()
    
    def drawing(self, start_point, end_point):
        self.frame = showing_name(self.frame, '18011', [start_point], [end_point],  True)

    def get_id(self):
        std_id = self.input_entry.get()
        return std_id
    
    def get_frame(self):
        self.read_cap()
        return self.frame

    def input_field(self):
        if self.var.get() == 0: 
            #* single track
            self.input_entry.config(state= 'normal')

        else:
            #* Multi track
            #self.input_entry.delete(0, tk.END)
            self.input_entry.config(state= 'disabled')

    def on_window_close(self):
        self.cap.release()
        cv2.destroyAllWindows()
        self.window.destroy()

if __name__ == "__main__":
    
    cap = cv2.VideoCapture('/mnt/Coding/Codes/CV/video2.mp4')
    # cap = cv2.VideoCapture(0)
    video = VideoGenerate(cap= cap)
    video.display_window()