import tkinter as tk
from tkinter import filedialog as fd
from tkinter import colorchooser
from watermark import *
from threading import Thread
from time import sleep

BG = "#41AEA9"
FG = "#E8FFFF"
FONT_TYPE = "Helvetica Neue"


class EZMark(tk.Tk):
    def __init__(self, *args, **kwargs):
        tk.Tk.__init__(self, *args, **kwargs)
        self.title("EZ Mark")
        self.config(background=BG)
        self.minsize(500, 750)
        self.maxsize(500, 750)
        self.watermark_engine = Watermarker()
        self.text_start_image_path = None
        self.image_start_image_path = None
        self.text_start_image_path = None
        self.image_start_image_path = None
        self.text_preview_image = None
        self.image_preview_image = None
        self.current_frame = None
        self.watermark_path = None
        self.text_position = "bottom-right"
        self.image_position = "bottom-right"
        self.margin_y = 15
        self.margin_x = 15
        self.font_size = 30
        self.watermark_text = None
        self.watermark_colour = "#FF6B6B"
        self.preview_width = None
        self.preview_height = None
        self.result_img = None

        # Put the base frame on screen, initialize the other screens and display the welcome page
        container = tk.Frame(self, background=BG, width=500, height=750)
        container.pack()
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)

        self.frames = {}
        for F in (WelcomePage, TextWatermarkScreen, ImageWatermarkScreen):
            page_name = F.__name__
            frame = F(parent=container, controller=self)
            self.frames[page_name] = frame
            frame.grid(row=0, column=0, sticky="nsew")
        self.show_frame("WelcomePage")

        self.thread = Thread(target=self.update_preview)
        self.thread.daemon = True
        self.thread.start()

    def show_frame(self, page_name):
        """Put the requested frame on screen and reset other frames when returning to the welcome page."""
        frame = self.frames[page_name]
        frame.tkraise()
        self.current_frame = page_name
        if page_name == "WelcomePage":
            self.frames["TextWatermarkScreen"].preview_canvas.delete("all")
            self.frames["ImageWatermarkScreen"].preview_canvas.delete("all")
            self.frames["TextWatermarkScreen"].image_text_entry.delete(0, tk.END)
            self.text_start_image_path = None
            self.image_start_image_path = None

    def open_start_image_file_dialog(self, mode):
        """Handles the base image import into the program."""
        file = fd.askopenfile(mode='r', filetypes=[('image files', ('.png', '.jpg', '.JPEG'))])
        if file:
            if mode == "text":
                self.text_start_image_path = file.name
            if mode == "image":
                self.image_start_image_path = file.name
        self.update()

    def save_result_img(self, mode):
        """Saves the result file in the desired location."""
        file = fd.asksaveasfile(mode='w', defaultextension=".png")
        if file:
            if mode == "text":
                text = self.frames["TextWatermarkScreen"].image_text_entry.get()
                if text == "":
                    text = None
                self.result_img = self.watermark_engine.place_text_watermark(image=Image.open(self.text_start_image_path),
                                                                             font_size=self.font_size,
                                                                             position=self.frames["TextWatermarkScreen"].clicked.get(),
                                                                             margin_y=self.margin_y, margin_x=self.margin_x,
                                                                             colour=self.watermark_colour, text=text)
            elif mode == "image":
                self.result_img = self.watermark_engine.place_image_watermark(image=Image.open(self.image_start_image_path),
                                                                              watermark_image=Image.open(self.watermark_path),
                                                                              size=self.frames["ImageWatermarkScreen"].clicked_size.get(),
                                                                              position=self.frames["ImageWatermarkScreen"].clicked.get(),
                                                                              margin_x=self.margin_x, margin_y=self.margin_y)
            self.result_img.save(file.name)

    def open_watermark_image(self):
        """Imports the watermark image into the program"""
        file = fd.askopenfile(mode='r', filetypes=[('image files', ('.png', '.jpg', '.JPEG'))])
        if file:
            self.watermark_path = file.name

    def choose_colour(self):
        """Handles the font color pick prompt"""
        self.watermark_colour = colorchooser.askcolor()
        self.watermark_colour = self.watermark_colour[1]
        self.update()

    def update_preview(self):
        """Periodically updates the preview image"""
        while True:
            if self.frames[self.current_frame].__class__.__name__ == "TextWatermarkScreen" and self.text_start_image_path is not None:
                text = self.frames["TextWatermarkScreen"].image_text_entry.get()
                if text == "":
                    text = None
                self.watermark_engine.watermark_preview(controller=self, operation="text",
                                                        path=self.text_start_image_path,
                                                        position=self.frames["TextWatermarkScreen"].clicked.get(),
                                                        margin_x=self.margin_x,
                                                        margin_y=self.margin_y,
                                                        font_size=self.frames["TextWatermarkScreen"].font_scale.get(),
                                                        text=text,
                                                        colour=self.watermark_colour)
                self.text_preview_image = tk.PhotoImage(file=TEXT_PREVIEW_PATH)
                self.frames["TextWatermarkScreen"].preview_canvas.create_image(250, 250, anchor="center",
                                                                               image=self.text_preview_image)
            elif self.frames[self.current_frame].__class__.__name__ == "ImageWatermarkScreen" and self.image_start_image_path is not None:
                self.watermark_engine.watermark_preview(controller=self, operation="image",
                                                        path=self.image_start_image_path,
                                                        position=self.frames["ImageWatermarkScreen"].clicked.get(),
                                                        margin_x=self.margin_x,
                                                        margin_y=self.margin_y, watermark_path=self.watermark_path,
                                                        image_size=self.frames[
                                                            "ImageWatermarkScreen"].clicked_size.get())
                self.image_preview_image = tk.PhotoImage(file=IMAGE_PREVIEW_PATH)
                self.frames["ImageWatermarkScreen"].preview_canvas.create_image(250, 250, anchor="center",
                                                                                image=self.image_preview_image)
            sleep(0.01)


class WelcomePage(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent, width=500, height=750, bg=BG)
        self.controller = controller
        self.controller.one = tk.PhotoImage(file="EZ.png")
        logo_canvas = tk.Canvas(self, width=500, height=500, highlightthickness=0, background=BG)
        logo_canvas.create_image(250, 250, anchor="center", image=self.controller.one)
        logo_canvas.pack()
        welcome_frame_top = tk.Frame(self, background=BG, width=500)
        welcome_text = tk.Label(welcome_frame_top,
                                text="Welcome to EZ Mark",
                                anchor="center", background=BG,
                                font=(FONT_TYPE, 18), fg=FG)
        welcome_text.pack()
        name_text = tk.Label(welcome_frame_top, text="by Csongor Szabó",
                             anchor="center", background=BG,
                             font=(FONT_TYPE, 16), fg=FG)
        name_text.pack()
        intro_text = tk.Label(welcome_frame_top, text="This EZ to use app lets you watermark your images.",
                              background=BG, font=(FONT_TYPE, 18), fg=FG)
        intro_text.pack()
        welcome_frame_top.pack()
        welcome_frame_bottom = tk.Frame(self, background=BG, width=500)
        start_text_wm_btn = tk.Button(welcome_frame_bottom, text="Create Text Watermark",
                                      command=lambda: controller.show_frame("TextWatermarkScreen"), background=BG,
                                      highlightthickness=0)
        start_text_wm_btn.grid(column=0, row=0, sticky="W", padx=40, pady=40)
        start_image_wm_btn = tk.Button(welcome_frame_bottom, text="Create Image Watermark",
                                       command=lambda: controller.show_frame("ImageWatermarkScreen"), background=BG,
                                       highlightthickness=0)

        start_image_wm_btn.grid(column=1, row=0, sticky="E", padx=40, pady=40)
        welcome_frame_bottom.pack()


class TextWatermarkScreen(tk.Frame):
    def __init__(self, parent, controller: EZMark):
        tk.Frame.__init__(self, parent, width=500, height=750, background=BG)
        self.controller = controller
        top_frame = tk.Frame(self, background=BG, width=500, padx=10, pady=10)
        home_button = tk.Button(top_frame, text="Back to Home",
                                command=lambda: controller.show_frame("WelcomePage"),
                                background=BG,
                                highlightthickness=0)
        top_frame.pack()
        home_button.pack()
        self.preview_canvas = tk.Canvas(self, width=500, height=500, highlightthickness=0, background=BG)
        self.preview_canvas_image = self.preview_canvas.create_image(250, 250, anchor="center",
                                                                     image=self.controller.one)
        self.preview_canvas.pack()
        bottom_frame = tk.Frame(self, background=BG, width=500, padx=10, pady=10)
        base_img = tk.Label(bottom_frame, text="Starting image:", background=BG, font=(FONT_TYPE, 16), fg=FG)
        browse_base_img = tk.Button(bottom_frame, text="Browse Image",
                                    background=BG,
                                    highlightthickness=0,
                                    command=lambda: self.controller.open_start_image_file_dialog("text"))
        base_img.grid(column=0, row=0, sticky="E")
        browse_base_img.grid(column=1, row=0, sticky="W")
        image_text = tk.Label(bottom_frame, text="Watermark text:", background=BG, font=(FONT_TYPE, 16), fg=FG)
        image_text.grid(column=0, row=1, sticky="E")
        self.image_text_entry = tk.Entry(bottom_frame, highlightthickness=0)
        self.image_text_entry.grid(column=1, row=1, sticky="E")
        position_text = tk.Label(bottom_frame, text="Watermark position:", background=BG, font=(FONT_TYPE, 16), fg=FG)
        position_text.grid(column=0, row=2, sticky="E")
        self.clicked = tk.StringVar()
        self.clicked.set("top-left")
        position_drop = tk.OptionMenu(bottom_frame, self.clicked, "top-left", "top-right", "bottom-left",
                                      "bottom-right")
        position_drop.grid(column=1, row=2, sticky="W")
        colour_text = tk.Label(bottom_frame, text="Pick watermark colour", background=BG, font=(FONT_TYPE, 16), fg=FG)
        colour_text.grid(column=0, row=3, sticky="W")
        colour_button = tk.Button(bottom_frame, text="Colour", background=BG, highlightthickness=0,
                                  command=self.controller.choose_colour)
        colour_button.grid(column=1, row=3, sticky="W")
        font_text = tk.Label(bottom_frame, text="Font size:", background=BG, font=(FONT_TYPE, 16), fg=FG)
        font_text.grid(column=0, row=4, sticky="E")
        self.font_scale = tk.Scale(bottom_frame, from_=0, to=500, orient="horizontal", bg=BG)
        self.font_scale.grid(column=1, row=4, sticky="W")
        bottom_frame.pack()
        save_frame = tk.Frame(self, background=BG, width=500, padx=10, pady=10)
        save_button = tk.Button(save_frame, text="Save Image", background=BG, highlightthickness=0,
                                command=lambda: self.controller.save_result_img("text"))
        save_button.pack()
        save_frame.pack()


class ImageWatermarkScreen(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent, width=500, height=750, background=BG)
        self.controller = controller
        top_frame = tk.Frame(self, background=BG, width=500, padx=10, pady=10)
        home_button = tk.Button(top_frame, text="Back to Home",
                                command=lambda: controller.show_frame("WelcomePage"),
                                background=BG,
                                highlightthickness=0)
        home_button.pack()
        top_frame.pack()
        self.preview_canvas = tk.Canvas(self, width=500, height=500, highlightthickness=0, background=BG)
        self.preview_canvas_image = self.preview_canvas.create_image(250, 250, anchor="center",
                                                                     image=self.controller.one)
        self.preview_canvas.pack()
        bottom_frame = tk.Frame(self, background=BG, width=500, padx=10, pady=10)
        base_img = tk.Label(bottom_frame, text="Starting image:", background=BG, font=(FONT_TYPE, 16), fg=FG)
        browse_base_img = tk.Button(bottom_frame, text="Browse Image",
                                    background=BG,
                                    highlightthickness=0,
                                    command=lambda: self.controller.open_start_image_file_dialog("image"))
        base_img.grid(column=0, row=0, sticky="E")
        browse_base_img.grid(column=1, row=0, sticky="W")
        watermark_img = tk.Label(bottom_frame, text="Watermark Image:", background=BG, font=(FONT_TYPE, 16), fg=FG)
        browse_watermark_img = tk.Button(bottom_frame, text="Browse Image",
                                         background=BG,
                                         highlightthickness=0,
                                         command=self.controller.open_watermark_image)
        watermark_img.grid(column=0, row=1, sticky="E")
        browse_watermark_img.grid(column=1, row=1, sticky="W")
        position_text = tk.Label(bottom_frame, text="Watermark position:", background=BG, font=(FONT_TYPE, 16), fg=FG)
        position_text.grid(column=0, row=2, sticky="E")
        self.clicked = tk.StringVar()
        self.clicked.set("top-left")
        position_drop = tk.OptionMenu(bottom_frame, self.clicked, "top-left", "top-right", "bottom-left",
                                      "bottom-right")
        position_drop.grid(column=1, row=2, sticky="W")
        watermark_size_text = tk.Label(bottom_frame, text="Watermark size:", background=BG, font=(FONT_TYPE, 16), fg=FG)
        watermark_size_text.grid(column=0, row=3, sticky="E")
        self.clicked_size = tk.StringVar()
        self.clicked_size.set("large")
        size_drop = tk.OptionMenu(bottom_frame, self.clicked_size, "large", "medium", "small")
        size_drop.grid(column=1, row=3, sticky="W")
        bottom_frame.pack()
        save_frame = tk.Frame(self, background=BG, width=500, padx=10, pady=10)
        save_button = tk.Button(save_frame, text="Save Image", background=BG, highlightthickness=0,
                                command=lambda: self.controller.save_result_img("image"))
        save_button.pack()
        save_frame.pack()
