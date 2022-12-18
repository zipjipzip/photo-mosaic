import cv2
from scipy import spatial as spt
from tkinter import filedialog as fd
from tkinter import messagebox as mb
from typing import Callable, Any
import glob as gl
import numpy as np
import os
import tkinter as tk
import tkinter.ttk as ttk

class _Photo_Mosaic:
    def __init__(self, target_image: np.ndarray, tiles: list[np.ndarray], tile_size: int, output_name: str):
        self.target_image = target_image
        self.tiles_path = tiles
        self.tile_size = (tile_size, tile_size)
        self.output: np.ndarray
        self.output_name = output_name
        self.colors_list: list[np.ndarray] = []
        self.calculate_dominant_color()
        self.pixelate_target_image()
        self.find_closest_tile_img_for_every_pixel()
        self.create_output_image()
        self.draw_tiles()

    def calculate_dominant_color(self):
        for tile in self.tiles_path:
            mean_color = np.array(tile).mean(axis=0).mean(axis=0)
            if type(mean_color) == np.float64:
                mean_color = np.array([mean_color] * 3)
            self.colors_list.append(mean_color)

    def pixelate_target_image(self):
        self.target_image_width = int(np.round(self.target_image.shape[1] / self.tile_size[0]))
        self.target_image_height = int(np.round(self.target_image.shape[0] / self.tile_size[1]))
        self.resized_target_image = cv2.resize(self.target_image, dsize=(self.target_image_width, self.target_image_height), interpolation=cv2.INTER_LINEAR)
    
    def find_closest_tile_img_for_every_pixel(self):
        tree = spt.KDTree(self.colors_list)
        self.closest_tiles = np.zeros((self.target_image_width, self.target_image_height), dtype=np.uint8)

        for i in range(self.target_image_width):
            for j in range(self.target_image_height):
                closest = tree.query(self.resized_target_image[j, i])
                self.closest_tiles[i, j] = closest[1]

    def create_output_image(self):
        self.output = np.zeros((self.target_image.shape[0], self.target_image.shape[1], 3), dtype=np.uint8)

    def draw_tiles(self):
        for i in range(self.target_image_width):
            for j in range(self.target_image_height):
                x, y = i * self.tile_size[0], j * self.tile_size[1]
                index = self.closest_tiles[i, j]
                temp = self.tiles_path[index][0:self.tile_size[0], 0:self.tile_size[1]]
                try:
                    self.output[y:(y+self.tile_size[1]), x:(x+self.tile_size[0])] = temp
                except:
                    pass # 

class _Basic_Converter_Frame:
    tiles_button_x = 10
    tiles_button_y = 10
    tiles_button_width = 130
    tiles_button_height = 20

    tiles_label_x = 150
    tiles_label_y = 10
    tiles_label_width = 275
    tiles_label_height = 20

    target_button_x = 10
    target_button_y = 40
    target_button_width = 130
    target_button_height = 20

    target_label_x = 150
    target_label_y = 40
    target_label_width = 275
    target_label_height = 20

    output_label_x = 10
    output_label_y = 70
    output_label_width = 130
    output_label_height = 20

    output_entry_x = 150
    output_entry_y = 70
    output_entry_width = 275
    output_entry_height = 20

    tile_size_label_x = 10
    tile_size_label_y = 100
    tile_size_label_width = 130
    tile_size_label_height = 20

    tile_size_entry_x = 150
    tile_size_entry_y = 100
    tile_size_entry_width = 50
    tile_size_entry_height = 20

    generate_button_x = 10
    generate_button_y = 420
    generate_button_width = 430
    generate_button_height = 25

    def __init__(self, frame_name: str) -> None:
        self.frame = tk.Frame(window)
        self.frame_name = frame_name
        self.photo_mosaic = _Photo_Mosaic
        self.validator_register = window.register(self.validate_digit_entry)
        self.tiles_button = tk.Button(self.frame, text="Browse Tiles Folder", command=self.open_tiles)
        self.tiles_label = tk.Label(self.frame, anchor="w", relief="ridge")
        self.target_button = tk.Button(self.frame, text="Browse Target File")
        self.target_label = tk.Label(self.frame, anchor="w", relief="ridge")
        self.output_label = tk.Label(self.frame, text="Output Name:", anchor="e")
        self.output_entry = tk.Entry(self.frame)
        self.tile_size_label = tk.Label(self.frame, text="Tile Size:", anchor="e")
        self.tile_size_entry = tk.Entry(self.frame, validate="all", validatecommand=(self.validator_register, "%P"))
        self.generate_button = tk.Button(self.frame, text="Generate")
        self.tiles: list[np.ndarray] = []
        notebook.add(self.frame, text=self.frame_name)
        self.set_tiles_button()
        self.set_tiles_label()
        self.set_target_button()
        self.set_target_label()
        self.set_output_label()
        self.set_output_entry()
        self.set_tile_size_label()
        self.set_tile_size_entry()
        self.set_generate_button()

    def validate_digit_entry(self, text: str):
        if text.isdigit():
            return True
        elif text == "":
            return True
        else:
            return False

    def open_tiles(self):
        folder_name = fd.askdirectory(initialdir="/", title="Select folder.")
        self.tiles_label.config(text=folder_name)

    def check_directory_labels(self):
        if self.tiles_label["text"] == "":
            mb.showinfo("", "Set the tiles folder path!")
            return True

        if self.target_label["text"] == "":
            mb.showinfo("", "Set the target file path!")
            return True

    def check_input_entries(self):
        if self.output_entry.get() == "":
            mb.showinfo("", "Set the output name!")
            return True

        if self.tile_size_entry.get() == "":
            mb.showinfo("", "Set the tile size!")
            return True

    def get_tiles(self):
        tile_size = int(self.tile_size_entry.get())
        try:
            for file in gl.glob(self.tiles_label["text"] + "/*"):
                if (file[-4:] == ".jpg") or (file[-4:] == ".png"):
                    file_array = np.fromfile(file, np.uint8)
                    tile = cv2.imdecode(file_array, cv2.IMREAD_COLOR)
                    tile = cv2.resize(tile, dsize=(tile_size, tile_size), interpolation=cv2.INTER_AREA)
                    self.tiles.append(tile)
        except:
            mb.showinfo("", "Upload the correct image!")
            return True

    def set_tiles_button(self):
        self.tiles_button.place(x=self.tiles_button_x, y=self.tiles_button_y, width=self.tiles_button_width, height=self.tiles_button_height)

    def set_tiles_label(self):
        self.tiles_label.place(x=self.tiles_label_x, y=self.tiles_label_y, width=self.tiles_label_width, height=self.tiles_label_height)

    def set_target_button(self):
        self.target_button.place(x=self.target_button_x, y=self.target_button_y, width=self.target_button_width, height=self.target_button_height)

    def set_target_label(self):
        self.target_label.place(x=self.target_label_x, y=self.target_label_y, width=self.target_label_width, height=self.target_label_height)

    def set_output_label(self):
        self.output_label.place(x=self.output_label_x, y=self.output_label_y, width=self.output_label_width, height=self.output_label_height)

    def set_output_entry(self):
        self.output_entry.place(x=self.output_entry_x, y=self.output_entry_y, width=self.output_entry_width, height=self.output_entry_height)

    def set_tile_size_label(self):
        self.tile_size_label.place(x=self.tile_size_label_x, y=self.tile_size_label_y, width=self.tile_size_label_width, height=self.tile_size_label_height)

    def set_tile_size_entry(self):
        self.tile_size_entry.place(x=self.tile_size_entry_x, y=self.tile_size_entry_y, width=self.tile_size_entry_width, height=self.tile_size_entry_height)

    def set_generate_button(self):
        self.generate_button.place(x=self.generate_button_x, y=self.generate_button_y, width=self.generate_button_width, height=self.generate_button_height)

class _Image_Converter_Frame(_Basic_Converter_Frame):
    target_resize_label_x = 10
    target_resize_label_y = 130
    target_resize_label_width = 130
    target_resize_label_height = 20

    target_resize_entry_x = 150
    target_resize_entry_y = 130
    target_resize_entry_width = 50
    target_resize_entry_height = 20

    resized_size_label_x = 210
    resized_size_label_y = 130
    resized_size_label_width = 100
    resized_size_label_height = 20

    def __init__(self, frame_name: str, file_type: str) -> None:
        super().__init__(frame_name=frame_name)
        self.file_type = [("*", f".{file_type}")]
        self.target_resize_label = tk.Label(self.frame, text="Target Multiply (1~10):", anchor="e")
        self.target_resize_entry = tk.Entry(self.frame, validate="all", validatecommand=(self.validator_register, "%P"))
        self.resized_size_label = tk.Label(self.frame, text="", anchor="w")
        self.loaded_target_image: np.ndarray
        self.resized_target_image: np.ndarray
        self.set_target_resize_label()
        self.set_target_resize_entry()
        self.set_resized_size_label()
        self.config_resized_size_label()

    def check_input_entries(self):
        super().check_input_entries()
        if self.target_resize_entry.get() == "":
            mb.showinfo("", "Set the resize ratio!")
            return True

    def open_target_image(self):
        try:
            file_name = fd.askopenfilename(initialdir="/", filetypes=self.file_type, title="Select file.")
            self.target_label.config(text=file_name)
            encrypted_file_array = np.fromfile(self.target_label["text"], np.uint8)
            self.loaded_target_image: np.ndarray = cv2.imdecode(encrypted_file_array, cv2.IMREAD_COLOR)
        except:
            mb.showinfo("", "Set the correct target file path!")
            self.target_label.config(text="")

    def config_resized_size_label(self):
        try:
            resize = int(self.target_resize_entry.get())
            h, w, a = self.loaded_target_image.shape
            self.resized_size_label["text"] = f"{resize * w}x{resize * h}"
        except:
            self.resized_size_label["text"] = ""
        self.resized_size_label.after(int(1000/60), self.config_resized_size_label)

    def resize_loaded_image(self):
        try:
            resize = int(self.target_resize_entry.get())
            self.resized_target_image = cv2.resize(self.loaded_target_image, dsize=(self.loaded_target_image.shape[1] * resize, self.loaded_target_image.shape[0] * resize), interpolation=cv2.INTER_AREA)
        except:
            mb.showinfo("", "Upload the correct image!")
            return True

    def generate_mosaic(self):
        tile_size = int(self.tile_size_entry.get())
        output_name = self.output_entry.get()
        completed_mosaic = self.photo_mosaic(self.resized_target_image, self.tiles, tile_size, output_name)
        return completed_mosaic.output

    def run_generate_mosaic_button(self):
        self.tiles.clear()
        self.check_directory_labels()
        self.check_input_entries()
        self.get_tiles()
        self.resize_loaded_image()
        cv2.imwrite(f"{self.output_entry.get()}{self.file_type[0][1]}", self.generate_mosaic())

    def set_target_button(self):
        super().set_target_button()
        self.target_button.config(command=self.open_target_image)

    def set_target_resize_label(self):
        self.target_resize_label.place(x=self.target_resize_label_x, y=self.target_resize_label_y, width=self.target_resize_label_width, height=self.target_resize_label_height)

    def set_target_resize_entry(self):
        self.target_resize_entry.place(x=self.target_resize_entry_x, y=self.target_resize_entry_y, width=self.target_resize_entry_width, height=self.target_resize_entry_height)

    def set_resized_size_label(self):
        self.resized_size_label.place(x=self.resized_size_label_x, y=self.resized_size_label_y, width=self.resized_size_label_width, height=self.resized_size_label_height)
    
    def set_generate_button(self):
        super().set_generate_button()
        self.generate_button.config(command=self.run_generate_mosaic_button)
    
class _Video_Converter_Frame(_Basic_Converter_Frame):
    fps_label_x = 10
    fps_label_y = 130
    fps_label_width = 130
    fps_label_height = 20

    fps_entry_x = 150
    fps_entry_y = 130
    fps_entry_width = 50
    fps_entry_height = 20

    def __init__(self, frame_name: str) -> None:
        super().__init__(frame_name=frame_name)
        self.fps_label = tk.Label(self.frame, text="FPS:", anchor="e")
        self.fps_entry = tk.Entry(self.frame, validate="all", validatecommand=(self.validator_register, "%P"))
        self.set_fps_label()
        self.set_fps_entry()

    def check_input_entries(self):
        super().check_input_entries()
        if self.fps_entry.get() == "":
            mb.showinfo("", "Set the FPS!")
            return None

    def open_target_video(self):
        file_name = fd.askopenfilename(initialdir="/", filetypes=[("*", ".mp4")], title="Select file.")
        self.target_label.config(text=file_name)

    def generate_mosaic(self, image: np.ndarray):
        tile_size = int(self.tile_size_entry.get())
        output_name = self.output_entry.get()
        completed_mosaic = self.photo_mosaic(image, self.tiles, tile_size, output_name)
        return completed_mosaic.output

    def create_mosaic_to_video(self):
        output_name = self.output_entry.get()
        loaded_target_video = cv2.VideoCapture(self.target_label["text"])
        width = int(loaded_target_video.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(loaded_target_video.get(cv2.CAP_PROP_FRAME_HEIGHT))
        output = cv2.VideoWriter(f"{output_name}.mp4", cv2.VideoWriter_fourcc("m", "p", "4", "v"), fps=int(self.fps_entry.get()), frameSize=(width, height))

        while loaded_target_video.isOpened():
            ret, img = loaded_target_video.read()
            if not ret:
                break
            mosaic_image = self.generate_mosaic(img)
            output.write(mosaic_image)
            
        output.release()

    def run_generate_mosaic_button(self):
        self.tiles.clear()
        self.get_tiles()
        self.check_directory_labels()
        self.check_input_entries()
        self.create_mosaic_to_video()

    def set_target_button(self):
        super().set_target_button()
        self.target_button.config(command=self.open_target_video)

    def set_fps_label(self):
        self.fps_label.place(x=self.fps_label_x, y=self.fps_label_y, width=self.fps_label_width, height=self.fps_label_height)

    def set_fps_entry(self):
        self.fps_entry.place(x=self.fps_entry_x, y=self.fps_entry_y, width=self.fps_entry_width, height=self.fps_entry_height)

    def set_generate_button(self):
        super().set_generate_button()
        self.generate_button.config(command=self.run_generate_mosaic_button)

class _Settings_Frame:
    language_label_x = 10
    language_label_y = 10
    language_label_width = 130
    language_label_height = 20

    language_combobox_x = 150
    language_combobox_y = 10
    language_combobox_width = 275
    language_combobox_height = 20
    
    def __init__(self):
        self.frame = tk.Frame(window)
        notebook.add(self.frame, text="Settings")
        self.set_language_label()
        self.set_language_combobox()

    def set_language_label(self):
        self.language_label = tk.Label(self.frame, text="Language:", anchor="e")
        self.language_label.place(x=self.language_label_x, y=self.language_label_y, width=self.language_label_width, height=self.language_label_height)

    def set_language_combobox(self):
        self.language_combobox = ttk.Combobox(self.frame, height=10, values=["EN", "KO"])
        self.language_combobox.set("EN")
        self.language_combobox.place(x=self.language_combobox_x, y=self.language_combobox_y, width=self.language_combobox_width, height=self.language_combobox_height)

if __name__ == "__main__":
    # Window Initialize
    window = tk.Tk()

    window_width = 500
    window_height = 500

    window.title("Photo Mosaic")
    window.geometry(f"{window_width}x{window_height}")
    window.resizable(False, False)

    # Set Notebook
    notebook_width = 450
    notebook_height = 450

    notebook = ttk.Notebook(window, width=notebook_width, height=notebook_height)
    notebook.pack()

    to_png = _Image_Converter_Frame("PNG", "png")
    to_mp4 = _Video_Converter_Frame("MP4")
    to_settings = _Settings_Frame()
    window.mainloop()