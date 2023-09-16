from PyQt5.uic import loadUi
from PyQt5 import QtWidgets,QtCore
from PyQt5.QtWidgets import QDialog,QApplication,QWidget,QFileDialog
from PyQt5.QtWidgets import QApplication, QMainWindow, QTableWidget, QTableWidgetItem, QVBoxLayout, QWidget,QCheckBox



import threading,sys
import time
from PyQt5.QtGui import QPixmap

from PIL import ImageGrab
import cv2
import numpy as np
import pyautogui,json
import os

def pil_image_to_cv2_array(pil_image):
    # Convert PIL image to NumPy array
    numpy_array = pil_image.convert("RGB")
    numpy_array = np.array(numpy_array)

    # Convert BGR to RGB (OpenCV uses BGR format)
    numpy_array_rgb = cv2.cvtColor(numpy_array, cv2.COLOR_BGR2RGB)

    return numpy_array_rgb
def crop_selected_region(image):
    # Display the image and allow the user to select a region
    roi = cv2.selectROI(image)

    # Crop the selected region from the image
    cropped_region = image[int(roi[1]):int(roi[1] + roi[3]), int(roi[0]):int(roi[0] + roi[2])]
    x, y, width, height = roi
    return [cropped_region,x,y,width,height]


class EdtitScreen(QDialog):
    def __init__(self,title,status,checktitle,detailTable):
        super().__init__()
        loadUi("setting.ui",self)
        self.browserImageButton.clicked.connect(self.BrowseProcess)
        self.title=title
        self.imagesToTrack=[]
        self.saveButton.clicked.connect(self.saveFile)
        self.status=status
        self.checktitle=checktitle
        self.detailTable=detailTable
        self.keysCheck.stateChanged.connect(self.checkboxStateChanged)
        self.muoseCheck.stateChanged.connect(self.checkboxStateChanged)
        self.cancel.clicked.connect(self.cancelGui)
        if(self.status=="edit"):
            pixmap = QPixmap(f"images/{self.title}/{checktitle}.png")
            self.imageFrame.setPixmap(pixmap.scaled(self.imageFrame.size()))
            with open("filedetail.json") as f:
                jsonFile=json.load(f)
            self.keyInput.setText(jsonFile[title][checktitle]['keyEvent'].split("+")[0])
            self.modifiers.setCurrentText(jsonFile[title][checktitle]['keyEvent'].split("+")[1])
            self.mouseCombo.setCurrentText(jsonFile[title][checktitle]['mouseEvent'])
            self.priority.setText(jsonFile[title][checktitle]['priority'])
            self.discriptionInput.setText(checktitle)
            self.heightInput.setText(jsonFile[title][checktitle]['coordinates'][0])
            self.widthInput.setText(jsonFile[title][checktitle]['coordinates'][1])
            self.xInput.setText(jsonFile[title][checktitle]['coordinates'][2])
            self.yInput.setText(jsonFile[title][checktitle]['coordinates'][3])
        
    def cancelGui(self):
        self.close()
    def checkboxStateChanged(self, state):
        sender = self.sender()  # Get the checkbox that triggered the signal
        checkboxes = [w for w in self.findChildren(QCheckBox) if w != sender]  # Get all other checkboxes
        if state == 2:  # Checked state
            for checkbox in checkboxes:
                checkbox.setChecked(False)
    def BrowseProcess(self):
        t=threading.Thread(target=self.BrowserImageFunction)
        t.daemon=True

        t.start()
    def BrowserImageFunction(self):
        if self.discriptionInput.text()=="":
            self.titleCheck.setText("*Please add title.")
            return 0
        ss = ImageGrab.grab()  # Capture the entire screen
        main_image = pil_image_to_cv2_array(ss)
        cropped_image,x,y,width,height=crop_selected_region(main_image)
        self.heightInput.setText(str(height))
        self.widthInput.setText(str(width))
        self.xInput.setText(str(x))
        self.yInput.setText(str(y))

        cv2.imshow("Selected Region", cropped_image)
        cv2.waitKey(0)
        cv2.destroyAllWindows()
        if not os.path.isdir(f"{os.getcwd()}\\images\\{self.title}"):
            os.mkdir(f"{os.getcwd()}\\images\\{self.title}")

        cv2.imwrite(f"{os.getcwd()}\\images\\{self.title}\\{self.discriptionInput.text()}.png", cropped_image)
        pixmap = QPixmap(f"{os.getcwd()}\\images\\{self.title}\\{self.discriptionInput.text()}.png")
        self.imageFrame.setPixmap(pixmap.scaled(self.imageFrame.size()))
        print("done")
    def saveFile(self):

        if self.keysCheck.isChecked():
            evenTohit="keyEvent"
        elif self.muoseCheck.isChecked():
            evenTohit="mouseEvent"

        with open("filedetail.json") as f:
            jsonFile=json.load(f)
        jsonFile[self.title][self.discriptionInput.text()]={
            "keyEvent":f"{self.modifiers.currentText()}+{self.keyInput.text()}"
            
                ,
            "mouseEvent":self.mouseCombo.currentText(),
            
            "deviceTocheck":evenTohit,

            "imagePath":f"images/{self.title}/{self.discriptionInput.text()}.png",
            "priority":self.priority.text(),
            "coordinates":[ 
                self.heightInput.text(),
                self.widthInput.text(),
                self.xInput.text(),
                self.yInput.text()]
        }
        

        with open("filedetail.json","w") as f:
            json.dump(jsonFile,f)
        self.updateTable()
        self.close()
    def updateTable(self):
        with open("filedetail.json") as f:
            jsonFile=json.load(f)
        data=[]
        try:
            for key,value in  jsonFile[self.title].items():
                    data.append([key,value['priority'],value['deviceTocheck'],value[value['deviceTocheck']],value['imagePath'],QCheckBox()])
        except:
            pass
        data = sorted(data, key=lambda x: x[1])
        print(data)
        self.detailTable.setRowCount(len(data))
        for row, rowData in enumerate(data):
            for col, text in enumerate(rowData):
                if col==len(rowData)-1:
            
                    self.detailTable.setCellWidget(row, col, text)
                else:
                    item = QTableWidgetItem(text)
                    self.detailTable.setItem(row, col, item)