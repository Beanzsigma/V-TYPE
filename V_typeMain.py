import customtkinter as ctk
from ctypes import windll, byref, create_unicode_buffer, create_string_buffer
from tkinter import Canvas, Text
import sys
import os
import threading
import time
from pynput import keyboard
from pynput.keyboard import Controller, Key
from PIL import Image, ImageSequence, ImageTk
after_id = None
main_window = ctk.CTk()
main_window.title('V-TYPE')
main_window.geometry('400x400')
main_window.resizable(False, False)
def get_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except AttributeError:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)
FR_PRIVATE = 0x10
def loadfont(font_path):
    windll.gdi32.AddFontResourceExW(font_path, FR_PRIVATE, 0)

def roundedrect(canvas, x1, y1, x2, y2, r=20, color="#88bcf7", width=2):
    arc_kwargs = {"outline": color, "width": width}
    line_kwargs = {"fill": color, "width": width}
    canvas.create_arc(x1, y1, x1+2*r, y1+2*r, start=90, extent=90, style="arc", **arc_kwargs)
    canvas.create_arc(x2-2*r, y1, x2, y1+2*r, start=0, extent=90, style="arc", **arc_kwargs)
    canvas.create_arc(x1, y2-2*r, x1+2*r, y2, start=180, extent=90, style="arc", **arc_kwargs)          
    canvas.create_arc(x2-2*r, y2-2*r, x2, y2, start=270, extent=90, style="arc", **arc_kwargs)
    canvas.create_line(x1+r, y1, x2-r, y1, **line_kwargs)
    canvas.create_line(x1+r, y2, x2-r, y2, **line_kwargs)
    canvas.create_line(x1, y1+r, x1, y2-r, **line_kwargs)
    canvas.create_line(x2, y1+r, x2, y2-r, **line_kwargs)
    
loadfont(get_path("bansheepilotbold1.ttf"))
loadfont(get_path("essedicom.ttf"))

def gifbg(): 
    global after_id
    if after_id: 
        main_window.after_cancel(after_id)
    for widget in main_window.winfo_children():
        widget.destroy()

    frames = []
    gif = Image.open(get_path('coolgif.gif'))
    for frame in ImageSequence.Iterator(gif):
        frame = frame.copy().convert('RGBA')
        r, g, b, a = frame.split()
        a = a.point(lambda x:x*0.4)
        frame.putalpha(a)
        frames.append(ImageTk.PhotoImage(frame.resize((400, 400))))
    canvas = Canvas(main_window, width=400, height=400, highlightthickness=0, bd=0, bg="black")
    canvas.place(x=0, y=0)
    canvasbg = canvas.create_image(0, 0, anchor= "nw")
    def animate(frame_index= 0):
        global after_id
        canvas.itemconfig(canvasbg, image=frames[frame_index])
        canvas._frames = frames
        after_id = main_window.after(20, animate, (frame_index +1)% len(frames))
    animate()
    return canvas, canvasbg
canvas, canvasbg = gifbg()                                            # gif code end here
def clear(canvas, canvas_img):
    for item in canvas.find_all():
        if item != canvas_img:
            canvas.delete(item)

def control(canvas, canvas_img):
    clear(canvas, canvas_img)

def welcome(canvas, canvasbg):
    canvas.create_text(200, 150, text="V-TYPE", font=('Banshee Pilot Bold', 42), fill='white', anchor="center")
    continuetext = canvas.create_text(200, 235, text="CONTINUE", font=('essedicom', 39), fill='white', anchor="center")
    canvas.tag_bind(continuetext, "<Button-1>", lambda e: control(canvas, canvasbg))
    canvas.tag_bind(continuetext, "<Enter>", lambda e: canvas.itemconfig(continuetext, fill="#577891"))
    canvas.tag_bind(continuetext, "<Leave>", lambda e: canvas.itemconfig(continuetext, fill="white"))
welcome(canvas, canvasbg)
main_window.mainloop()