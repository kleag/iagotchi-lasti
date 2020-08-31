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
import sys, subprocess,json,socket, os
from subprocess import PIPE
from PyQt5.QtWidgets import *
from PyQt5.QtWidgets import * 
from PyQt5.QtGui import *
from PyQt5.QtCore import *

class iagotchiGui(object):
    
    def __init__(self):
        self.app = QApplication([])
        self.w = QWidget()
        self.w.setWindowTitle("Iagotchi-Bot")
        
        self.ipAddress = ""
        self.botname = "iagotchi"
        self.what_run = "bot"
        
        with open('data/config.json') as f:
            self.jsondata = json.load(f, encoding='utf-8')
            self.what_run = self.jsondata["what_run"]
            #print("WHATRUN : "+self.what_run)
            self.botname = self.jsondata['bot']['name']
            #print("BOTNAME : "+self.botname)
            self.ipAddress = self.jsondata['botresponse']['ip']
            #print("BOTRESPIP : "+self.ipAddress)
        
        try :
            self.ipAddress = socket.gethostbyname(socket.gethostname())
        except :
            text, ok = QInputDialog.getText(self.w, 'IP Address', 'Manually enter IP address:', QLineEdit.Normal, self.ipAddress)
            if len(text) > 0 & ok:
                self.ipAddress = text
                                       
        self.ipTextEdit = QLineEdit(self.ipAddress)
        self.btnUpdIp = QPushButton("Refresh IP Address")
        
        self.btnSave = QPushButton("Save Options")
        self.btnDocker = QPushButton("Start Docker")
        self.btnChrome = QPushButton("Start Chrome")
        self.btnStart = QPushButton("Start Iagotchi")
        self.btnStop = QPushButton("Stop Iagotchi")
        self.btnBuild = QPushButton("Build Iagotchi (password)")
        self.btnTrain = QPushButton("Train Iagotchi (similarity with topics)")
        self.btnTrain2 = QPushButton("Train Iagotchi 2 (similarity without topics)")
        self.btnDockerConfig = QPushButton("Open docker-compose.yml")
        self.btnDockerFile = QPushButton("Auto-config (docker-compose.yml)")
        self.btnIagoConfig = QPushButton("Open config.json")
        self.btnGitPull = QPushButton("Update (git pull)")
        self.btnMax = QPushButton("Start Max/Pd patch")
        self.btnConsole = QPushButton("Start Console")
        self.btnKill = QPushButton("Stop everything (killall)")
        # message box
        self.msg = QMessageBox()
        self.msg.setWindowTitle("Iagotchi")
        
        
        self.bot = QComboBox()
        self.bot.addItem("Rencontre")
        self.bot.addItem("G5")
        if self.botname == "iagotchi" :
            self.bot.setCurrentText("Rencontre")
        else:
            self.bot.setCurrentText("G5")
        self.bot.currentIndexChanged.connect(self.botChange)

        self.error_dialog = QErrorMessage()
        
        grid = QGridLayout(self.w)
        grid.setVerticalSpacing(3)

        #grid.addWidget(self.btnDocker,0,0)
        grid.addWidget(self.btnStart,1,0)
        grid.addWidget(self.btnChrome,2,0)
        grid.addWidget(self.btnMax,3,0)
        grid.addWidget(self.btnConsole,4,0)
        grid.addWidget(self.btnStop,5,0)
        grid.addWidget(QLabel("_ Options _"),6,0)
        grid.addWidget(QLabel("Mode :"),7,0)
        grid.addWidget(self.bot,8,0)
        grid.addWidget(QLabel("IP Address :"),9,0)
        grid.addWidget(self.btnUpdIp,10,0)
        grid.addWidget(self.ipTextEdit,11,0)
        grid.addWidget(self.btnSave,12,0)
        grid.addWidget(QLabel("_ Advanced _"),13,0)
        grid.addWidget(self.btnDockerConfig,14,0)
        grid.addWidget(self.btnDockerFile,15,0)
        grid.addWidget(self.btnIagoConfig,16,0)
        grid.addWidget(self.btnGitPull,17,0)
        grid.addWidget(self.btnBuild,18,0)
        grid.addWidget(self.btnTrain,19,0)
        grid.addWidget(self.btnTrain2,20,0)
        grid.addWidget(self.btnKill,21,0)
        
        self.btnSave.clicked.connect(self.saveOptions)
        self.btnUpdIp.clicked.connect(self.updateIp)
        self.btnStart.clicked.connect(self.startIagotchi)
        self.btnStop.clicked.connect(self.stopIagotchi)
        self.btnBuild.clicked.connect(self.buildIagotchi)
        self.btnDocker.clicked.connect(self.runDocker)
        self.btnChrome.clicked.connect(self.runChrome)
        self.btnTrain.clicked.connect(self.trainIagotchi)
        self.btnTrain2.clicked.connect(self.trainIagotchi2)
        self.btnDockerConfig.clicked.connect(self.confDocker)
        self.btnDockerFile.clicked.connect(self.autoConfig)
        self.btnIagoConfig.clicked.connect(self.confIago)
        self.btnGitPull.clicked.connect(self.gitPull)
        self.btnMax.clicked.connect(self.runMax)
        self.btnConsole.clicked.connect(self.runConsole)
        self.btnKill.clicked.connect(self.killAll)
            
    def botChange(self,i):
        if self.bot.currentText() == "Rencontre" :
            self.botname = "iagotchi"
        else:
            self.botname = "iagotchig5"
        print ("Bot : "+self.botname+ " ("+self.bot.currentText()+")")
        
    def showGui(self):
        self.w.show()
        
    def exit(self):
        sys.exit(self.app.exec_())
    
    def updateIp(self):
        self.ipAddress = socket.gethostbyname(socket.gethostname())
        self.ipTextEdit.setText(self.ipAddress)  
    
    def saveOptions(self):
        print("Saving Options...")
        self.jsondata['bot']['name'] = self.botname
        self.jsondata["what_run"] = self.what_run
        self.ipAddress = self.ipTextEdit.text()
        self.jsondata['botresponse']['ip'] = self.ipAddress
        with open('data/config.json', 'w') as json_file:
            json.dump(self.jsondata, json_file, indent=4, ensure_ascii=False)
        self.printOptions()
        print("...Done")
        
    def autoConfig(self):
        current_dir = os.getcwd().replace('/', '\/')
        print(current_dir)
        cmd = f"sed -i 's/<HOME>/{current_dir}/g' docker-compose.yml"
        print("Auto config ...")
        status = self.exec_cmd(cmd)
        if not status:
            self.user_messages('Failed', message_type='critical')
        else:
            self.user_messages('Success', message_type='information')
        
    def printOptions(self):
        print("Options")
        print("    BOTNAME "+self.botname)
        print("    WHAT_RUN "+self.what_run)
        print("    IP "+self.ipAddress)
        
        
    def user_messages(self, content, message_type='critical'):
        if message_type == 'critical':
            self.msg.setIcon(QMessageBox.Critical)
        elif message_type == 'warning':
            self.msg.setIcon(QMessageBox.Warning)
        elif message_type == 'information':
            self.msg.setIcon(QMessageBox.Information)
        self.msg.setText(content)
        x = self.msg.exec_()  # this will show our messagebox
        print(x)
        
    def runDocker(self):
        print("Starting Docker")
        subprocess.run("open -a Docker &", shell=True)
        
    def runChrome(self):
        print("Starting Chrome")
        #subprocess.run(["open", "-a", "Google Chrome", "http://localhost:8088", "&"], shell=True)
        subprocess.run("/var/opt/google/chrome/chrome http://localhost:8088 &", shell=True)
        
    def startIagotchi(self):
        self.what_run = "bot"
        self.saveOptions()
        print("Starting Iagotchi")
        subprocess.run("docker-compose up &", shell=True)

    def stopIagotchi(self):
        print("Stopping Iagotchi")
        subprocess.run("docker-compose stop &", shell=True)

    def trainIagotchi(self):
        self.what_run = "similarity-with-topics"
        self.saveOptions()
        print("Train Iagotchi")
        subprocess.run("docker-compose up &", shell=True)
        
    def trainIagotchi2(self):
        self.what_run = "similarity-without-topics"
        self.saveOptions()
        print("Train Iagotchi")
        subprocess.run("docker-compose up &", shell=True)
        
    def exec_cmd(self, cmd):
        
        try:
            output = subprocess.check_output([cmd], stderr=subprocess.STDOUT, shell=True, universal_newlines=True)
            #output = subprocess.check_output([], stderr=subprocess.STDOUT, shell=True, universal_newlines=True)
            return True
        except subprocess.CalledProcessError as exc:
            print("Status : FAIL", exc.returncode, exc.output)
            return False
        else:
            print("Output: \n{}\n".format(output))
        
        
    def buildIagotchi(self):
        self.saveOptions()
        print("Download Limaserver Image")
        status = self.exec_cmd("docker pull aymara/lima")
        if not status:
            self.user_messages('Failed', message_type='critical')
        print("Build Iagotchi")
        status = self.exec_cmd("docker-compose build")
        if not status:
            self.user_messages('Failed', message_type='critical')
        else:
            self.user_messages('Success', message_type='information')

        
        
    def confDocker(self):
        print("opening Docker Config")
        subprocess.run("kate ./docker-compose.yml &", shell=True)
        
    def confIago(self):
        print("opening Iagotchi Config")
        subprocess.run("kate ./data/config.json &", shell=True)
        
    def gitPull(self):
        print("updating Iagotchi")
        subprocess.run("git pull &", shell=True)
        
    def runMax(self):
        print("Starting Max/Pd Patch")
        subprocess.run("pd /home/rocio/Bureau/IAGO_SOUND_PD/__IAGO_SOUND__.pd &", shell=True)

    def runConsole(self):
        print("Starting Console")
        subprocess.run("/home/rocio/Bureau/console/application.linux64/console &", shell=True)

    def killAll(self):
        print("Killing Console")
        subprocess.run("killall console", shell=True)
        print("Killing Max Patch")
        subprocess.run("killall Iagotchi", shell=True)
        print("Killing Chrome")
        subprocess.run("killall \"Google Chrome\"", shell=True)
        print("Stopping Iagotchi")
        subprocess.run("docker-compose stop", shell=True)
        #print("Killing Docker")
        #subprocess.run("killall Docker", shell=True)

if __name__ == "__main__":

    gui = iagotchiGui()
    gui.showGui()
    gui.exit()
    #sys.exit(app.exec_())
