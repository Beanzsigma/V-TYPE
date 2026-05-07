import random
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
paused =False
after_id = None
main_window = ctk.CTk()
main_window.title('V-TYPE')
main_window.geometry('400x400')
main_window.resizable(False, False)
typing = False
textarea = None
buttoncheck = None
speedslider = None
pausebutton = None
pausecheck = None
togglepause = None
stopflag = threading.Event()
typer = Controller()
def get_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except AttributeError:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)
FR_PRIVATE = 0x10
def typetext(text, jitter, canvas, countdown_label, speed, pausebutton):
    global typing, paused
    typing = True
    stopflag.clear()
    main_window.after(0, lambda: canvas.lift(countdown_label))
    for i in range(3, 0, -1):
        main_window.after(0, lambda i=i: canvas.itemconfig(countdown_label, text=str(i)))
        time.sleep(1)
    main_window.after(0, lambda: canvas.delete(countdown_label))
    main_window.after(0, lambda: canvas.itemconfigure('textwin', state='normal'))
    main_window.after(0,lambda:canvas.itemconfigure('sliderwin', state='normal') )
    for char in text:
        while paused:
            time.sleep(0.1)
        if stopflag.is_set():
            break
        if jitter and random.random() < 0.05:
            typoscount = random.randint(1, 5)
            wrongchars = [random.choice('abcdefghijklmnopqrstuvwxyz') for _ in range(typoscount) ]
            for w in wrongchars:
                typer.type(w)
                time.sleep(random.uniform(0.05, 0.2))
            time.sleep(random.uniform(0.3, 0.7))
            for _ in range(typoscount):
                time.sleep(random.uniform(0.05, 0.1))
                typer.press(Key.backspace)
                time.sleep(random.uniform(0.05, 0.1))
                typer.release(Key.backspace)
                time.sleep(random.uniform(0.08, 0.14))
            time.sleep(random.uniform(0.05, 0.2))
        typer.type(char)
        if jitter:
            if random.random() <0.03:
                time.sleep(random.uniform(0.5, 2))
            if char == " " or char =="\n":
                time.sleep(random.uniform(0.1, 0.4))
            if char == " " and random.random() <0.03:
                typer.type(' ')
                time.sleep(0.1)
                typer.press(Key.backspace)
                typer.release(Key.backspace)
            time.sleep(random.uniform(speed * 0.5, speed * 3.5))
        else:
            time.sleep(speed)
    if char == " " and random.random() <0.03:
        typer.type(' ')
        time.sleep(0.1)
        typer.press(Key.backspace)
        typer.release(Key.backspace)
    typing = False
    paused = False
    main_window.after(0, lambda: canvas.itemconfig(pausebutton, text="⏸"))
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
loadfont(get_path('Honor.ttf'))

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
def starttyping(textarea, buttoncheck, canvas, speedslider, pausebutton):
    if typing:
        return
    text = textarea.get('1.0', "end-1c")
    if not text.strip():
        return
    countdown_label = canvas.create_text(200, 200, text="3", font=('Banshee Pilot Bold', 60), fill="white", anchor="center")
    canvas.lift(countdown_label)
    canvas.itemconfigure("textwin", state='hidden')
    canvas.itemconfigure("sliderwin", state='hidden')
    time.sleep(0.1)
    threading.Thread(target=typetext, args=(text, buttoncheck[0], canvas, countdown_label, speedslider.get(), pausebutton), daemon=True).start()
def control(canvas, canvas_img):
    global togglepause
    global textarea, buttoncheck, speedslider, pausebutton, pausecheck
    clear(canvas, canvas_img)
    pausecheck = [False]
    pausebutton = canvas.create_text(366, 160, text="⏸", font=('Arial', 30), fill='white', )
    def togglepause(e):
        global paused
        pausecheck[0] = not pausecheck[0]
        paused = pausecheck[0]
        canvas.itemconfig(pausebutton, text="▶" if pausecheck[0] else"⏸")
    canvas.tag_bind(pausebutton, "<Button-1>", togglepause)
    canvas.tag_bind(pausebutton, "<Enter>", lambda e: canvas.itemconfig(pausebutton, fill="#577891"))
    canvas.tag_bind(pausebutton, "<Leave>", lambda e: canvas.itemconfig (pausebutton, fill="white"))
    restartbutton = canvas.create_text(366, 240, text="↺", font=('Arial', 30), fill="white")
    canvas.create_text(366, 120, text="f7", font=('honor', 13), fill="white")
    def restart(e):
        global paused, typing
        stopflag.set()
        paused = False
        typing = False
        control(canvas, canvas_img)
    canvas.tag_bind(restartbutton, "<Button-1>", restart)
    canvas.tag_bind(restartbutton, "<Enter>", lambda e: canvas.itemconfig(restartbutton, fill="#577891"))
    canvas.tag_bind(restartbutton, "<Leave>", lambda e: canvas.itemconfig(restartbutton, fill="white"))
    exitcode = canvas.create_text(20, 20, text="Exit", font=('essedicom', 30), fill="white", anchor="nw")
    speedslider = ctk.CTkSlider(canvas, from_=0.3, to=0.01, bg_color="#0C4169", button_hover_color="#577891", fg_color="#0C4169", orientation="vertical", height=200, width=10)
    canvas.create_window(40, 200, window=speedslider, anchor="center", tags="sliderwin")
    speedslider.set(0.05)
    canvas.create_text(40, 316, text="SPEED", font=('essedicom', 34), fill="white", anchor="center")
    canvas.tag_bind(exitcode, "<Button-1>", lambda e:main_window.destroy())
    canvas.tag_bind(exitcode, "<Enter>", lambda e: canvas.itemconfig(exitcode, fill="#577891"))
    canvas.tag_bind(exitcode, "<Leave>", lambda e: canvas.itemconfig(exitcode, fill="white") )
    canvas.create_text(200, 30, text="V-TYPE", font=('Banshee Pilot Bold', 30), fill="white", anchor="center")
    textarea = ctk.CTkTextbox(canvas, width =270, height=185, bg_color="#0C4169", fg_color="#0C4169", border_color="white", border_width=2, text_color="white", corner_radius=4, font=('Honor', 16), wrap="word")
    canvas.create_window(200, 198, window=textarea, anchor="center", tags="textwin")
    canvas.create_text(200, 72, text="Enter text", font=('essedicom', 34), fill='white', anchor='center')
    buttoncheck = [False]
    typecode = canvas.create_text(179, 360, text="Start", font=('essedicom', 43), fill="white", anchor="center")
    typecode2 = canvas.create_text(243, 365, text="(f6)", font=('Honor', 17), fill='white', anchor="center")
    canvas.tag_bind(typecode, "<Button-1>", lambda e: starttyping(textarea, buttoncheck, canvas, speedslider, pausebutton))
    canvas.tag_bind(typecode, "<Enter>", lambda e: canvas.itemconfig(typecode, fill="#577891"))
    canvas.tag_bind(typecode, "<Leave>", lambda e: canvas.itemconfig(typecode, fill="white"))
    canvas.tag_bind(typecode2, "<Button-1>", lambda e: starttyping(textarea, buttoncheck, canvas, speedslider, pausebutton))
    canvas.tag_bind(typecode2, "<Enter>", lambda e: canvas.itemconfig(typecode, fill="#577891"))
    canvas.tag_bind(typecode2, "<Leave>", lambda e: canvas.itemconfig(typecode, fill="white"))
    chexbox = canvas.create_rectangle(148, 302, 168, 322, outline="white", width=2, fill="black", stipple="gray12")
    buttoncheck1 = canvas.create_text(158, 312, text="✓", font=('Arial', 14), fill='white')
    canvas.itemconfig(buttoncheck1, state='hidden')
    def togglebutton(e):
        buttoncheck[0] = not buttoncheck[0]
        canvas.itemconfig(buttoncheck1, state="normal" if buttoncheck[0] else "hidden")
    canvas.tag_bind(chexbox, "<Button-1>", togglebutton)
    canvas.tag_bind(buttoncheck1, "<Button-1>", togglebutton)
    canvas.create_text(210, 309, font=('essedicom', 30), fill="white", anchor='center', text="Jitter")
def onpress(key):
    if key == keyboard.Key.f6:
        if not typing:
            main_window.after(0, lambda: starttyping(textarea, buttoncheck, canvas, speedslider, pausebutton))
    if key == keyboard.Key.f7:
        if togglepause:
            main_window.after(0, lambda: togglepause(None))
def welcome(canvas, canvasbg):
    canvas.create_text(200, 150, text="V-TYPE", font=('Banshee Pilot Bold', 42), fill='white', anchor="center")
    continuetext = canvas.create_text(200, 235, text="CONTINUE", font=('essedicom', 39), fill='white', anchor="center")
    canvas.tag_bind(continuetext, "<Button-1>", lambda e: control(canvas, canvasbg))
    canvas.tag_bind(continuetext, "<Enter>", lambda e: canvas.itemconfig(continuetext, fill="#577891"))
    canvas.tag_bind(continuetext, "<Leave>", lambda e: canvas.itemconfig(continuetext, fill="white"))
welcome(canvas, canvasbg)
listener = keyboard.Listener(on_press=onpress)
listener.daemon =True
listener.start()
main_window.mainloop()