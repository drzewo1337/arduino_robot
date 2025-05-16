import threading
import tkinter as tk
from communication_orig import VideoStream, Status
from img import ImageInfo
from PIL import ImageFile, ImageTk, Image
from itertools import product
from tkinter import NW
import time
import cv2
import numpy as np


class Interface(tk.Tk):
    def __init__(self):
        super().__init__()

        # window creation
        self.title("Robot interface")
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        self.geometry(f"{screen_width}x{screen_height}")
        self.configure(bg="lightgrey")

        # communication and image process import
        self.status = Status()
        self.comm = VideoStream(self.status)
        self.imageInfo = ImageInfo()

        # variables preparation and key binds
        self.bind_keys()
        self.key_pressed = [False, False, False, False]
        self.lastKey = 0
        self.arrows = {}
        self.speeds = {}
        self.danger = False
        self.danger_photo_item = None
        self.danger_on = False
        self.lights = False
        self.lights_on = False

        self.danger_ahead = Image.open("display/danger.png")
        self.no_signal = Image.open("display/no_signal.png")

        # layout on GUI
        self.photo = ImageTk.PhotoImage(Image.new('RGB', (640, 480)))
        self.pre_layout(screen_width, screen_height, 6, 7)
        self.window_label = tk.Canvas(self, width=self.photo.width(), height=self.photo.height())
        self.window_label.grid(row=1, column=1, columnspan=3, rowspan=3)
        self.window_label.create_image(0, 0, anchor=NW, image=self.photo)
        self.layout()

        threading.Thread(target=self.load_image, daemon=True).start()

    def pre_layout(self, screen_width, screen_height, rows, columns):
        width_size = int(screen_width / columns)
        height_size = int(screen_height / rows)

        for col, row in product(range(columns + 1), range(rows + 1)):
            canvas = tk.Canvas(self, width=width_size, height=height_size, bg="lightgrey", borderwidth=0,
                               highlightthickness=0)
            canvas.grid(row=row, column=col)
            setattr(self, f"empty_canvas_{row}_{col}", canvas)

    def layout_message_box(self):
        scrollbar = tk.Scrollbar(self)
        scrollbar.grid(row=1, column=5, rowspan=3, sticky="ns")
        self.message_box = tk.Text(self, yscrollcommand=scrollbar.set)
        self.message_box.grid(row=1, column=4, columnspan=2, rowspan=3, sticky="nsew")
        scrollbar.config(command=self.message_box.yview)
        self.message_box.config(wrap="word")

    def show_message(self, msg):
        self.message_box.config(state=tk.NORMAL)
        self.message_box.insert(tk.END, msg + "\n")
        self.message_box.see(tk.END)
        self.message_box.config(state=tk.DISABLED)

    def layout_speed_buttons(self):
        for i in range(4):
            speed_image = tk.PhotoImage(file=f"display/speed_{i + 1}.png")
            self.speeds[i] = speed_image

            image_width = speed_image.width()
            image_height = speed_image.height()

            button = tk.Button(self, image=speed_image)
            button.grid(row=4 - i, column=0, sticky="e")
            button.config(width=image_width, height=image_height)

            if i == 0:
                button.config(bg="lightgreen")

            setattr(self, f"button_speed_{i}", button)

    def layout_arrow_buttons(self):
        arrow_names = [["left", 4, 1, "se"], ["right", 4, 3, "sw"], ["up", 4, 2, "s"], ["down", 5, 2, "n"]]
        for i in range(len(arrow_names)):
            name, set_row, set_col, side = arrow_names.pop()
            arrow_image = tk.PhotoImage(file=f"display/arrow_{name}.png")
            self.arrows[name] = arrow_image

            image_width = arrow_image.width()
            image_height = arrow_image.height()

            button = tk.Button(self, image=arrow_image)
            button.grid(row=set_row, column=set_col, sticky=side)
            button.config(width=image_width, height=image_height)

            setattr(self, f"button_{name}", button)

    def layout(self):
        self.layout_arrow_buttons()
        self.layout_speed_buttons()
        self.layout_message_box()

    def close_window(self, event=None):
        self.destroy()

    def bind_keys(self):
        key_bindings = {
            "<Escape>": self.close_window,
            "<KeyPress-w>": lambda event: self.move_key(0, True),
            "<KeyRelease-w>": lambda event: self.move_key(0, False),
            "<KeyPress-s>": lambda event: self.move_key(1, True),
            "<KeyRelease-s>": lambda event: self.move_key(1, False),
            "<KeyPress-a>": lambda event: self.move_key(2, True),
            "<KeyRelease-a>": lambda event: self.move_key(2, False),
            "<KeyPress-d>": lambda event: self.move_key(3, True),
            "<KeyRelease-d>": lambda event: self.move_key(3, False),
            "<Key-1>": lambda event: self.speed(0),
            "<Key-2>": lambda event: self.speed(1),
            "<Key-3>": lambda event: self.speed(2),
            "<Key-4>": lambda event: self.speed(3),
        }
        for key, action in key_bindings.items():
            self.bind(key, action)

    def speed(self, index):
        if self.lastKey != index:
            getattr(self, f"button_speed_{self.lastKey}").config(bg="white")
            self.lastKey = index
            command = ["1_down", "2_down", "3_down", "4_down"][index]
            #self.show_message(command)
            self.comm.send_to_arduino(command)
            getattr(self, f"button_speed_{index}").config(bg="lightgreen")

    def move_key(self, index, pressed):
        button_names = ["button_up", "button_down", "button_left", "button_right"]
        if not pressed:
            if not self.key_pressed[index]:
                self.key_pressed[index] = True
                command = ["W_up", "S_up", "A_up", "D_up"][index]
                #self.show_message(command)
                self.comm.send_to_arduino(command)
                getattr(self, button_names[index]).config(bg="lightgreen")
        else:
            self.key_pressed[index] = False
            command = ["W_down", "S_down", "A_down", "D_down"][index]
            #self.show_message(command)
            self.comm.send_to_arduino(command)
            getattr(self, button_names[index]).config(bg="white")

    def load_image(self):
        counter = 0
        while True:
            if self.comm.isConnected:
                try:
                    image = None
                    while not self.status.CameraQueue.empty():
                        image = self.status.CameraQueue.get()

                    if image:
                        counter +=1
                        self.photo.paste(image)
                        numpy_image = np.array(image)
                        opencv_image = cv2.cvtColor(numpy_image, cv2.COLOR_RGB2BGR)
                        if counter > 20:
                            self.lights, self.danger = self.imageInfo.process_image(opencv_image)
                            counter = 0
                        self.update_idletasks()
                except Exception as e:
                    # print("Error while updating image:", e)
                    pass
                if self.lights_on is False and self.lights is True:
                    self.show_message("Lights turned on")
                    self.lights_on = True
                elif self.lights_on and self.lights is False:
                    self.lights_on = False
                    self.show_message("Lights turned off")
                if self.danger and self.danger_on is False:
                    self.danger_on = True
                    self.show_message("Collision risk!")
                    resized_danger_ahead = self.danger_ahead.resize((self.photo.width(), self.photo.height()))
                    danger_photo = ImageTk.PhotoImage(resized_danger_ahead)
                    self.danger_photo_item = self.window_label.create_image(0, 0, anchor=NW, image=danger_photo)
                    # Keep a reference to the image to prevent it from being garbage collected
                    self.window_label.danger_photo = danger_photo
                elif self.danger_on and self.danger is False:
                    self.danger_on = False
                    if self.danger_photo_item:
                        self.window_label.delete(self.danger_photo_item)
                        self.danger_photo_item = None
            else:
                resized_no_signal = self.no_signal.resize((self.photo.width(), self.photo.height()))
                self.photo.paste(resized_no_signal)
                self.update_idletasks()
            time.sleep(0.01)  # Add a sleep interval to reduce CPU usage


if __name__ == "__main__":
    app = Interface()
    app.mainloop()
