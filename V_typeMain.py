import customtkinter as ctk
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
def get_path(relativepath):
    try:
        basebath = sys._MEIPASS
    except AttributeError:
        basebath = os.path.abspath(".")
    return os.path.join(basebath, relativepath)
from ctypes import windll, byref, create_unicode_buffer, create_string_buffer
def gifbg(): 
    global after_id
    if after_id: 
        main_window.after_cancel(after_id)
    for widget in main_window.winfo_children():
        widget.destroy()

    frames = []
    gif = Image.open(get_path(''))
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





main_window.mainloop()