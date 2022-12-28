import tkinter as tk
from tkinter import ttk
import message_functions as mf
import serial
from serial import serialutil

EMPTY = ""
INIT = "i"
LIST_START = "ls\n"
FILE = "f"
FILE_START = "cs\n"
FILE_END = "ce\n"
ROW = "r"
ERROR = "e"
CURRENT_DATE = "d"
NEW = "n"
STATE = "s"

PORT = "COM5"
BAUDRATE = 115200
TIMEOUT = 0


def init_serial(port: object, baudrate: object, timeout: object) -> serial.Serial:
    return serial.Serial(port=port, baudrate=baudrate, timeout=timeout, xonxoff=False, rtscts=False, dsrdtr=False)


class App:
    def __init__(self, root):
        self.root = root
        frame = ttk.Frame(root, padding=20)
        frame.grid()

        self.time_button = tk.Button(frame, text="Set current time", command=self.send_current_time)
        self.time_button.grid(column=0, row=0, padx=10, pady=10, sticky="w")
        self.time_label = tk.Label(frame, text="")
        self.time_label.grid(column=1, row=0, padx=10, pady=10)

        self.files_button = tk.Button(frame, text="Get list of files", command=self.get_file_list)
        self.files_button.grid(column=0, row=1, padx=10, pady=10, sticky="w")
        self.scrollbar = tk.Scrollbar(frame)
        self.scrollbar.grid(column=2, row=1, sticky="nsew")
        self.file_list = tk.Listbox(frame, selectmode=tk.SINGLE)
        self.file_list.bind("<<ListboxSelect>>", self.remember)
        self.file_list.grid(column=1, row=1, sticky="nsew")
        self.file_list.config(yscrollcommand=self.scrollbar.set)
        self.scrollbar.config(command=self.file_list.yview)

        self.save_button = tk.Button(frame, text="Save files", command=self.get_file_content)
        self.save_button.grid(column=0, row=2, padx=10, pady=10, sticky="w")
        self.save_label = tk.Label(frame, text="")
        self.save_label.grid(column=1, row=2)

        try:
            self.ser = init_serial(port=PORT, baudrate=BAUDRATE, timeout=TIMEOUT)
        except serialutil.SerialException:
            print("Arduino is not connected")
            self.ser = None
        self.filename = ""
        self.file = None

    def send_current_time(self):
        if self.ser is not None:
            self.ser.write(mf.create_time_message())

    def get_file_list(self):
        if self.ser is not None:
            self.ser.write(mf.get_file_list_message())

    def get_file_content(self):
        if self.ser is not None:
            self.ser.write(mf.get_file_content(self.filename))

    def remember(self, _):
        indexes = self.file_list.curselection()
        if len(indexes) != 0:
            self.filename = self.file_list.get(indexes[0])

    def run(self):
        if self.ser is None:
            return
        while True:
            received = self.ser.readline().decode("ascii")
            if received == EMPTY:
                break
            elif received[0] == INIT or received[0] == NEW:
                print(received)
            elif received[0] == ERROR:
                print(received)
                break
            elif received[0] == CURRENT_DATE:
                self.time_label.config(text="Current time was set to " + received)
            elif received == LIST_START:
                self.file_list.delete(0, tk.END)
            elif received[0] == FILE:
                self.file_list.insert(tk.END, received[1:-1])
            elif received == FILE_START:
                self.file = open(self.filename, "w")
            elif received == FILE_END:
                self.file.close()
            elif received[0] == ROW:
                self.file.write(received[1:])

        self.root.after(100, self.run)


if __name__ == "__main__":
    root = tk.Tk(className="Application")
    root.geometry("300x300")
    root.columnconfigure(0, weight=1)
    root.columnconfigure(1, weight=3)
    root.columnconfigure(2, weight=1)

    app = App(root)

    root.after(500, app.run)
    root.mainloop()
