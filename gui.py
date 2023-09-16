from PyQt5.uic import loadUi
from PyQt5 import QtWidgets, QtCore
from PyQt5.QtWidgets import QDialog, QApplication, QWidget, QFileDialog
from PyQt5.QtWidgets import QApplication, QMainWindow, QTableWidget, QTableWidgetItem, QVBoxLayout, QWidget, QCheckBox


import threading
import sys
import time
from PyQt5.QtGui import QPixmap

from PIL import ImageGrab
import cv2
import numpy as np
import pyautogui
import json
import setting

import ctypes
from ctypes import wintypes
import time

key_dict = {0: ' 0x30 ', 1: ' 0x31 ', 2: ' 0x32 ', 3: ' 0x33 ', 4: ' 0x34 ', 5: ' 0x35 ', 6: ' 0x36 ', 7: ' 0x37 ', 8: ' 0x38 ', 9: ' 0x39 ', 'A': ' 0x41 ', 'B': ' 0x42 ', 'C': ' 0x43 ', 'D': ' 0x44 ', 'E': ' 0x45 ', 'F': ' 0x46 ', 'G': ' 0x47 ', 'H': ' 0x48 ', 'I': ' 0x49 ', 'J': ' 0x4A ', 'K': ' 0x4B ', 'L': ' 0x4C ', 'M': ' 0x4D ', 'N': ' 0x4E ', 'O': ' 0x4F ', 'P': ' 0x50 ', 'Q': ' 0x51 ', 'R': ' 0x52 ', 'S': ' 0x53 ', 'T': ' 0x54 ', 'U': ' 0x55 ', 'V': ' 0x56 ', 'W': ' 0x57 ', 'X': ' 0x58 ', 'Y': ' 0x59 ', 'Z': ' 0x5A ', "L ALT": "0xA4",  "R ALT": "0xA5",
            "L SHIFT": "0xA0",
            "R SHIFT": "0xA1",
            "L CTRL": " 0xA2",
            "R CTRL": " 0xA3",
            "ENTER": " 0x0D",
            "TAB": "0x09"}
user32 = ctypes.WinDLL('user32', use_last_error=True)

INPUT_MOUSE = 0
INPUT_KEYBOARD = 1
INPUT_HARDWARE = 2

KEYEVENTF_EXTENDEDKEY = 0x0001
KEYEVENTF_KEYUP = 0x0002
KEYEVENTF_UNICODE = 0x0004
KEYEVENTF_SCANCODE = 0x0008

MAPVK_VK_TO_VSC = 0

# List of all codes for keys:
# # msdn.microsoft.com/en-us/library/dd375731
UP = 0x26
DOWN = 0x28
A = 0x57

# C struct definitions

wintypes.ULONG_PTR = wintypes.WPARAM


class MOUSEINPUT(ctypes.Structure):
    _fields_ = (("dx",          wintypes.LONG),
                ("dy",          wintypes.LONG),
                ("mouseData",   wintypes.DWORD),
                ("dwFlags",     wintypes.DWORD),
                ("time",        wintypes.DWORD),
                ("dwExtraInfo", wintypes.ULONG_PTR))


class KEYBDINPUT(ctypes.Structure):
    _fields_ = (("wVk",         wintypes.WORD),
                ("wScan",       wintypes.WORD),
                ("dwFlags",     wintypes.DWORD),
                ("time",        wintypes.DWORD),
                ("dwExtraInfo", wintypes.ULONG_PTR))

    def __init__(self, *args, **kwds):
        super(KEYBDINPUT, self).__init__(*args, **kwds)
        # some programs use the scan code even if KEYEVENTF_SCANCODE
        # isn't set in dwFflags, so attempt to map the correct code.
        if not self.dwFlags & KEYEVENTF_UNICODE:
            self.wScan = user32.MapVirtualKeyExW(self.wVk,
                                                 MAPVK_VK_TO_VSC, 0)


class HARDWAREINPUT(ctypes.Structure):
    _fields_ = (("uMsg",    wintypes.DWORD),
                ("wParamL", wintypes.WORD),
                ("wParamH", wintypes.WORD))


class INPUT(ctypes.Structure):
    class _INPUT(ctypes.Union):
        _fields_ = (("ki", KEYBDINPUT),
                    ("mi", MOUSEINPUT),
                    ("hi", HARDWAREINPUT))
    _anonymous_ = ("_input",)
    _fields_ = (("type",   wintypes.DWORD),
                ("_input", _INPUT))


LPINPUT = ctypes.POINTER(INPUT)


def _check_count(result, func, args):
    if result == 0:
        raise ctypes.WinError(ctypes.get_last_error())
    return args


user32.SendInput.errcheck = _check_count
user32.SendInput.argtypes = (wintypes.UINT,  # nInputs
                             LPINPUT,       # pInputs
                             ctypes.c_int)  # cbSize

# Functions


def PressKey(hexKeyCode):
    x = INPUT(type=INPUT_KEYBOARD,
              ki=KEYBDINPUT(wVk=hexKeyCode))
    user32.SendInput(1, ctypes.byref(x), ctypes.sizeof(x))


def ReleaseKey(hexKeyCode):
    x = INPUT(type=INPUT_KEYBOARD,
              ki=KEYBDINPUT(wVk=hexKeyCode,
                            dwFlags=KEYEVENTF_KEYUP))
    user32.SendInput(1, ctypes.byref(x), ctypes.sizeof(x))


# Define the necessary Windows API constants and structures
MOUSE_EVENTF_MOVE = 0x0001
MOUSE_EVENTF_ABSOLUTE = 0x8000
MOUSE_EVENTF_LEFTDOWN = 0x0002
MOUSE_EVENTF_LEFTUP = 0x0004
MOUSE_EVENTF_RIGHTDOWN = 0x0008  # Right button down
MOUSE_EVENTF_RIGHTUP = 0x0010    # Right button up
SM_CXSCREEN = 0
SM_CYSCREEN = 1

# Get the screen width and height
screen_width = ctypes.windll.user32.GetSystemMetrics(SM_CXSCREEN)
screen_height = ctypes.windll.user32.GetSystemMetrics(SM_CYSCREEN)

# Define a function to move the mouse and click (both left and right buttons)


def move_mouse_and_click(x, y, left=True, right=True):
    # Calculate the absolute coordinates
    absolute_x = int(x * 65535 / screen_width)
    absolute_y = int(y * 65535 / screen_height)

    # Move the mouse
    ctypes.windll.user32.mouse_event(
        MOUSE_EVENTF_MOVE | MOUSE_EVENTF_ABSOLUTE, absolute_x, absolute_y, 0, 0)

    # Simulate left mouse button click
    if left:
        ctypes.windll.user32.mouse_event(MOUSE_EVENTF_LEFTDOWN, 0, 0, 0, 0)
        ctypes.windll.user32.mouse_event(MOUSE_EVENTF_LEFTUP, 0, 0, 0, 0)

    # Simulate right mouse button click
    if right:
        ctypes.windll.user32.mouse_event(MOUSE_EVENTF_RIGHTDOWN, 0, 0, 0, 0)
        ctypes.windll.user32.mouse_event(MOUSE_EVENTF_RIGHTUP, 0, 0, 0, 0)


def pil_image_to_cv2_array(pil_image):
    # Convert PIL image to NumPy array
    numpy_array = pil_image.convert("RGB")
    numpy_array = np.array(numpy_array)

    # Convert BGR to RGB (OpenCV uses BGR format)
    numpy_array_rgb = cv2.cvtColor(numpy_array, cv2.COLOR_BGR2RGB)

    return numpy_array_rgb


def get_all_elements(table_widget):
    all_elements = []

    for row in range(table_widget.rowCount()):
        row_ = []
        for column in range(table_widget.columnCount()):
            item = table_widget.item(row, column)
            if column == table_widget.columnCount()-1:

                item = table_widget.cellWidget(row, column)
                row_.append(item)
                continue
            if item is not None:
                row_.append(item.text())
        all_elements.append(row_)

    return all_elements


class MainScreen(QDialog):
    def __init__(self):
        super().__init__()
        loadUi("main.ui", self)

        with open("filedetail.json") as f:
            jsonFile = json.load(f)
        for file in dict.keys(jsonFile):
            self.fileList.addItem(file)
        # Creating the new game data
        self.updateTable()
        self.pause = False
        self.createButton.clicked.connect(self.createGameFile)

        self.addButton.clicked.connect(self.addGameFileEvent)
        self.editButton.clicked.connect(self.editGameFileEvent)
        self.startButton.clicked.connect(self.startProcess)
        self.fileList.currentIndexChanged.connect(self.onComboBoxChanged)
        self.pauseButton.clicked.connect(self.pausefunction)
        self.deleteButton.clicked.connect(self.deleteFunction)

    def pausefunction(self):
        if self.pause == False:
            self.pause = True

    def deleteFunction(self):
        editedTitle = self.checkSelection()
        with open("filedetail.json") as f:
            jsonFile = json.load(f)
        if editedTitle in jsonFile[self.fileList.currentText()]:
            del jsonFile[self.fileList.currentText()][editedTitle]
        with open("filedetail.json", "w") as f:
            json.dump(jsonFile, f)

        self.updateTable()

    def onComboBoxChanged(self, index):
        # This slot will be called when the combo box selection changes

        self.updateTable()

    def updateTable(self):

        with open("filedetail.json") as f:
            jsonFile = json.load(f)
        data = []
        try:
            for key, value in jsonFile[self.fileList.currentText()].items():
                data.append([key, value['priority'], value['deviceTocheck'],
                            value[value['deviceTocheck']], value['imagePath'], QCheckBox()])
        except:
            pass
        data = sorted(data, key=lambda x: x[1])

        self.detailTable.setRowCount(len(data))
        for row, rowData in enumerate(data):
            for col, text in enumerate(rowData):
                if col == len(rowData)-1:
                    self.detailTable.setCellWidget(row, col, text)
                else:
                    item = QTableWidgetItem(text)
                    self.detailTable.setItem(row, col, item)

    def addGameFileEvent(self):
        self.new_window = setting.EdtitScreen(
            self.fileList.currentText(), "new", None, self.detailTable)
        self.new_window.show()
        self.updateTable()

    def editGameFileEvent(self):
        editedTitle = self.checkSelection()
        self.new_window = setting.EdtitScreen(
            self.fileList.currentText(), "edit", editedTitle, self.detailTable)
        self.new_window.show()
        self.updateTable()

    def checkSelection(self):
        selected_items = self.detailTable.selectedItems()
        if selected_items:
            selected_item = selected_items[0]
            row = selected_item.row()
            col = selected_item.column()
            item_text = selected_item.text()
            return item_text
        else:
            return None

    def createGameFile(self):

        with open("filedetail.json") as f:
            jsonFile = json.load(f)
        jsonFile[self.craeteFileInput.text()] = {}

        with open("filedetail.json", "w") as f:
            json.dump(jsonFile, f)

        self.fileList.addItem(self.craeteFileInput.text())
        new_item_index = self.fileList.findText(self.craeteFileInput.text())
        self.fileList.setCurrentIndex(new_item_index)

    def startProcess(self):
        required_data = []
        all_elements = get_all_elements(self.detailTable)
        print("All Elements in Table:")
        for element in all_elements:
            print(element)
            if element[5].isChecked():
                required_data.append(element)

        self.logs.append(f"->Started Detecting ")
        print(required_data)
        t = threading.Thread(target=lambda: self.checkInputs(required_data))
        t.daemon = True
        t.start()

    def checkInputs(self, data):
        if self.pause:
            self.pause = False
        while self.pause == False:

            ss = ImageGrab.grab()  # Capture the entire screen
            main_image = pil_image_to_cv2_array(ss)
            for d in data:
                image = cv2.imread(d[4])
                template_image = image

                # Get the dimensions of the template
                template_height, template_width, _ = template_image.shape

                # Perform template matching
                result = cv2.matchTemplate(
                    main_image, template_image, cv2.TM_CCOEFF_NORMED)
                threshold = 0.8  # Adjust this threshold based on your needs
                locations = np.where(result >= threshold)

                # Mark the matched regions on the main image
                for loc in zip(*locations[::-1]):
                    print("matched")
                    if "keyEvent" == d[2]:
                        modifier = d[3].split("+")[0]
                        key = d[3].split("+")[1]
                        if modifier == 'None':
                            print(key)

                            print("pressing")
                            PressKey(int(key_dict[key.capitalize()], 16))
                            time.sleep(0.5)
                            ReleaseKey(int(key_dict[key.capitalize()], 16))
                        else:
                            print("pressing")
                            PressKey(int(key_dict[modifier], 16))
                            PressKey(int(key_dict[key.capitalize()], 16))
                            time.sleep(0.5)
                            ReleaseKey(int(key_dict[key.capitalize()], 16))
                            ReleaseKey(int(key_dict[modifier], 16))

                    elif "mouseEvent" == d[2]:
                        if d[3] == "left":
                            move_mouse_and_click(
                                loc[0], loc[1], left=True, right=False)
                        elif d[3] == "right":
                            move_mouse_and_click(
                                loc[0], loc[1], left=False, right=True)
                    # top_left = loc
                    # bottom_right = (top_left[0] + template_width, top_left[1] + template_height)
                    # cv2.rectangle(main_image, top_left, bottom_right, (0, 255, 0), 2)


app = QApplication(sys.argv)
widget = QtWidgets.QStackedWidget()
main = MainScreen()
widget.addWidget(main)
widget.setFixedWidth(930)
widget.setFixedHeight(640)
widget.show()
try:
    sys.exit(app.exec_())
except Exception as err:
    print(err)
    print('exiting')
