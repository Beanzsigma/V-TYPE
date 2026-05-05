import customtkinter as ctk
from tkinter import Canvas, Text
import threading
import time
from pynput import keyboard
from pynput.keyboard import Controller, Key
from PIL import Image, ImageSequence, ImageTk

main_window = ctk.CTk()
main_window.title('V-TYPE')
main_window.geometry('400x400')
main_window.resizable(False, False)
main_window.mainloop()