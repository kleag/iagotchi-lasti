
#
# Copyright 2020 CEA LIST
# This file is part of Iagotchi-bot.
# Iagotchi-bot is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# Iagotchi-bot is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
# You should have received a copy of the GNU Affero General Public License
# along with Iagotchi-bot.  If not, see <http://www.gnu.org/licenses/>
# 
#

import traceback, sys
from PyQt5.QtWidgets import *
from PyQt5 import QtWidgets

from main import ASR
from PyQt5.QtGui import *
from PyQt5.QtCore import *

class ProcessRunnable(QRunnable):
    def __init__(self, botname, btn):
        QRunnable.__init__(self)
        #self.t = target
        self.b = btn
        self.signals = WorkerSignals()
        self.botname = botname
        self.asr = None
        self.finished = pyqtSignal()
        #self.args = args

    def runASR(self):
        self.asr = ASR(botname=self.botname)
        self.asr.start()
        self.finished.emit()

    def run(self):
        self.runASR()

            
    def fun_btn1(self, btn1, btn2):
        self.botname = 'iagotchi'
        print("self.asr {}".format(self.asr))
        if not self.asr is None:
            self.asr.externals.botname = self.botname
            self.asr.externals.chatscript.botname = self.botname
            self.asr.externals.chatscript.runChatscript()
            self.asr.externals.chatscript.runBot()
            if not self.asr.externals.chatscript.status is None:
                btn1.setStyleSheet("background-color: green")
                btn2.setStyleSheet("background-color: light gray")
            else:
                self.error_dialog.showMessage("Problem during start 'rencontre' dialogue")
                
        btn1.setStyleSheet("background-color: green")
        btn2.setStyleSheet("background-color: light gray")
        
    def fun_btn2(self, btn1, btn2):
        self.botname = 'iagotchig5'
        if not self.asr is None:
            self.asr.externals.botname = self.botname
            self.asr.externals.chatscript.botname = self.botname
            self.asr.externals.chatscript.runChatscript()
            self.asr.externals.chatscript.runBot()
            if not self.asr.externals.chatscript.status is None:
                btn2.setStyleSheet("background-color: green")
                btn1.setStyleSheet("background-color: light gray")
            else:
                self.error_dialog.showMessage("Problem during start 'rencontre' dialogue")
        btn2.setStyleSheet("background-color: green")
        btn1.setStyleSheet("background-color: light gray")

    def start(self):
        QThreadPool.globalInstance().start(self)
        
        
class WorkerSignals(QObject):
    '''
    Defines the signals available from a running worker thread.

    Supported signals are:

    finished
        No data
    
    error
        `tuple` (exctype, value, traceback.format_exc() )
    
    result
        `object` data returned from processing, anything

    '''
    finished = pyqtSignal()
    error = pyqtSignal(tuple)
    result = pyqtSignal(object)

class iagotchiGui(object):
    
    def __init__(self):
        self.app = QApplication([])
        self.w = QWidget()
        self.w.setWindowTitle("Iagotchi-Bot")
        self.botname = "iagotchi"
        self.asr = None
        self.p = None

        self.btn1 = QPushButton("Rencontre")
        self.btn2 = QPushButton("G5")
        self.btn3 = QPushButton("Start")
        
        self.error_dialog = QtWidgets.QErrorMessage()
        
        grid = QGridLayout(self.w)


        grid.addWidget(self.btn1,0,0)
        grid.addWidget(self.btn2,0,1)
        grid.addWidget(self.btn3,1,0,1,0)
        
            
        
        self.btn3.clicked.connect(self.mainASR)
        self.btn1.clicked.connect(self.fun_btn1)
        self.btn2.clicked.connect(self.fun_btn2)
        
    def showGui(self):
        self.w.show()
        
    def handle_result(self, result):
        self.asr = result #print("got result {}".format(result))

    def exit(self):
        sys.exit(self.app.exec_())
        
    def runASR(self):
        self.asr = ASR(botname=self.botname)
        self.asr.start()
        
    def mainASR(self):
        self.p = ProcessRunnable(botname=self.botname, btn=self.btn3)
        self.p.start()
        self.asr = self.p.asr
        if self.p.asr and self.asr.p.ready:
            self.btn3.setStyleSheet("background-color: green")

        

    def fun_btn1(self):
        if self.p is None:
            self.botname = 'iagotchi'
            self.btn1.setStyleSheet("background-color: green")
            self.btn2.setStyleSheet("background-color: light gray")
        else:
            self.p.fun_btn1(self.btn1, self.btn2)

            
    def fun_btn2(self):
        if self.p is None:
            self.botname = 'iagotchig5'
            self.btn2.setStyleSheet("background-color: green")
            self.btn1.setStyleSheet("background-color: light gray")
        else:
            self.p.fun_btn1(self.btn1, self.btn2)


if __name__ == "__main__":

    gui = iagotchiGui()
    gui.showGui()
    gui.exit()


    #sys.exit(app.exec_())
