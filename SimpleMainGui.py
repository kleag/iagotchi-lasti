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
import sys, subprocess,json,socket, os, shlex
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
                                       
        #self.ipTextEdit = QLineEdit(self.ipAddress)
        #self.btnUpdIp = QPushButton("Refresh IP Address")
        
        #self.ingroupBox.setCheckable(True)
        #self.ingroupBox.setChecked(False)
        self.btnSave = QPushButton("Save Options")
        self.ingroupBox, self.inText, self.inAudio = self.createTextAudioButtons("Input")
        self.outgroupBox, self.outText, self.outAudio = self.createTextAudioButtons("Output")
        #self.btnText.setChecked(True)
        #self.btnDocker = QPushButton("Start Docker")
        #self.btnChrome = QPushButton("Start Chrome")
        self.btnStart = QPushButton("Start Iagotchi")
        #self.btnStop = QPushButton("Stop Iagotchi")
        self.btnStop = QPushButton("Stop Iagotchi")
        self.btnBuild = QPushButton("Build Iagotchi (password)")
        #self.btnTrain = QPushButton("Train Iagotchi (similarity with topics)")
        self.btnTrain2 = QPushButton("Re-train Iagotchi")
        #self.btnDockerConfig = QPushButton("Open docker-compose.yml")
        self.btnDockerFile = QPushButton("Auto-config")
        #self.btnIagoConfig = QPushButton("Open config.json")
        #self.btnGitPull = QPushButton("Update (git pull)")
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
        self.current_bot = self.botname

        self.error_dialog = QErrorMessage()
        
        grid = QGridLayout(self.w)
        grid.setVerticalSpacing(3)

        #grid.addWidget(self.btnDocker,0,0)
        grid.addWidget(self.ingroupBox, 1, 0)
        grid.addWidget(self.outgroupBox, 2, 0)
        grid.addWidget(self.btnStart,3,0)
        #grid.addWidget(self.btnChrome,2,0)
        grid.addWidget(self.btnMax,4,0)
        grid.addWidget(self.btnConsole,5,0)
        grid.addWidget(self.btnStop,6,0)
        grid.addWidget(QLabel("_ Options _"),7,0)
        grid.addWidget(QLabel("Mode :"),8,0)
        grid.addWidget(self.bot,9,0)
        #grid.addWidget(QLabel("IP Address :"),8,0)
        #grid.addWidget(self.btnUpdIp,9,0)
        #grid.addWidget(self.ipTextEdit,10,0)
        grid.addWidget(self.btnSave,10,0)
        grid.addWidget(QLabel("_ Advanced _"),11,0)
        #grid.addWidget(self.btnDockerConfig,14,0)
        grid.addWidget(self.btnDockerFile,12,0)
        #grid.addWidget(self.btnIagoConfig,16,0)
        #grid.addWidget(self.btnGitPull,17,0)
        grid.addWidget(self.btnBuild,13,0)
        #grid.addWidget(self.btnTrain,12,0)
        grid.addWidget(self.btnTrain2,14,0)
        grid.addWidget(self.btnKill,15,0)
        
        self.btnSave.clicked.connect(self.saveOptions)
        #self.btnUpdIp.clicked.connect(self.updateIp)
        self.btnStart.clicked.connect(self.startIagotchi)
        self.btnStop.clicked.connect(self.stopIagotchi)
        self.btnBuild.clicked.connect(self.buildIagotchi)
        #self.btnDocker.clicked.connect(self.runDocker)
        #self.btnChrome.clicked.connect(self.runChrome)
        #self.btnTrain.clicked.connect(self.trainIagotchi)
        self.btnTrain2.clicked.connect(self.trainIagotchi2)
        #self.btnDockerConfig.clicked.connect(self.confDocker)
        self.btnDockerFile.clicked.connect(self.autoConfig)
        #self.btnIagoConfig.clicked.connect(self.confIago)
        #self.btnGitPull.clicked.connect(self.gitPull)
        self.btnMax.clicked.connect(self.runMax)
        self.btnConsole.clicked.connect(self.runConsole)
        self.btnKill.clicked.connect(self.killAll)
            
    def createTextAudioButtons(self, mode):
        ingroupBox = QGroupBox(mode)
        btnText = QRadioButton ("Text")
        btnAudio = QRadioButton ("Audio")
        btnText.setChecked(True)
        vbox = QVBoxLayout()
        vbox.addWidget(btnText)
        vbox.addWidget(btnAudio)
        vbox.addStretch(1)
        ingroupBox.setLayout(vbox)
        
        return ingroupBox, btnText, btnAudio
            
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
    
    def saveOptions(self, input_mode="text", output_mode="text", dialog=True):
        print("Saving Options...")
        self.jsondata['bot']['name'] = self.botname
        self.jsondata["what_run"] = self.what_run
        self.jsondata["mode"]["input"] = input_mode
        self.jsondata["mode"]["output"] = output_mode
        print(f'To change: {self.what_run}; {self.botname}')
        #self.ipAddress = self.ipTextEdit.text()
        #self.jsondata['botresponse']['ip'] = self.ipAddress
        with open('data/config.json', 'w') as json_file:
            json.dump(self.jsondata, json_file, indent=4, ensure_ascii=False)
        self.printOptions()
        print("...Done")
        if dialog:
            self.user_messages('Success', message_type='information')
        
    def autoConfig(self):
        current_dir = os.getcwd().replace('/', '\/')
        print("Auto config ...")
        cmd = f"sed -i 's/<HOME>/{current_dir}/g' docker-compose.yml"
        status = self.exec_cmd(cmd)
        if not status:
            self.user_messages('Failed', message_type='critical')
        cmd = f"sed -i 's/<HOME>/{current_dir}/g' puredata/IAGO_SOUND_PD/__IAGO_SOUND__.pd"
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
        
        
    def invoke_process_popen_blocking(self, command, shellType=False, stdoutType=subprocess.PIPE):
        """runs subprocess with Popen, but output only returned when process complete"""
        try:
            process = subprocess.Popen(
                shlex.split(command), shell=shellType, stdout=stdoutType)
            (stdout, stderr) = process.communicate()
            print(stdout.decode())
            return True
        except:
            print("ERROR {} while running {}".format(sys.exc_info()[1], command))
            return False


    def invoke_process_popen_poll_live(self, command, shellType=False, stdoutType=subprocess.PIPE, operation='start'):
        """runs subprocess with Popen/poll so that live stdout is shown"""
        print('process_popen')
        try:
            process = subprocess.Popen(
                shlex.split(command), shell=shellType, stdout=stdoutType)
        except:
            print("ERROR {} while running {}".format(sys.exc_info()[1], command))
            return False
        while True:
            output = process.stdout.readline()
            # used to check for empty output in Python2, but seems
            # to work with just poll in 2.7.12 and 3.5.2
            # if output == '' and process.poll() is not None:
            if output == '' and process.poll() is not None:
                break
            if operation == 'start' and 'Please open chrome at' in output.strip().decode():
                break
            elif operation == 'train' and 'Training completed ...' in output.strip().decode():
                break
            if output:
                print(output.strip().decode())
        rc = process.poll()
        return rc
        
    def runDocker(self):
        print("Starting Docker")
        subprocess.run("open -a Docker &", shell=True)
        
    def runChrome(self):
        print("Starting Chrome")
        #subprocess.run(["open", "-a", "Google Chrome", "http://localhost:8088", "&"], shell=True)
#         subprocess.run("/var/opt/google/chrome/chrome http://localhost:8088 &", shell=True)
        subprocess.run("/usr/bin/google-chrome http://localhost:8088 &", shell=True)

        
    def checkContainers(self):
        print('Check Containers')
        statusl = self.exec_cmd(" docker ps -q --no-trunc | grep $( docker-compose ps -q limaserver)")
        statusi = self.exec_cmd(" docker ps -q --no-trunc | grep $( docker-compose ps -q iagotchi)")
        return statusl, statusi
        
    def startIagotchi(self, refresh=False):
        input_checked = self.inText.text().lower() if self.inText.isChecked()  else self.inAudio.text().lower()
        output_checked = self.outText.text().lower() if self.outText.isChecked()  else self.outAudio.text().lower()
        self.what_run = "bot"
        self.saveOptions(input_mode=input_checked, output_mode=output_checked, dialog=False)
        print(f"Stopping: {self.current_bot}#{self.botname}")
        subprocess.run(" docker-compose stop ", shell=True)
        status = self.exec_cmd(" docker-compose rm -f")
        print("Starting Iagotchi")
        
        if not refresh:
            lima, iagotchi = self.checkContainers()
        else:
            lima = False
            iagotchi = False
        ct = False
        print(lima, iagotchi)
        if not lima or not iagotchi:
            #status = self.exec_cmd(" docker-compose up ")
            status = self.invoke_process_popen_poll_live(" docker-compose up ")
            #subprocess.run(" docker-compose up &", shell=True)
            lima, iagotchi = self.checkContainers()
            if not lima or not iagotchi:
                self.user_messages('Failed', message_type='critical')
                return
            elif lima and iagotchi:
                ct = True
            else:
                ct = False
        elif lima and iagotchi:
            ct = True
            #self.runChrome()
        if not ct:
            self.user_messages('Failed', message_type='critical')
            return
        else:
            self.runChrome()
           
            

    #def stopIagotchi(self):
        #print("Stopping Iagotchi")
        #subprocess.run("docker-compose stop &", shell=True)
        
    def stopIagotchi(self):
        print(f"Stopping: {self.current_bot}#{self.botname}")
        subprocess.run(" docker-compose stop ", shell=True)
        status = self.exec_cmd(" docker-compose rm -f")
        if not status:
            self.user_messages('Failed', message_type='critical')
        else:
            self.user_messages('Success', message_type='information')
     

    def trainIagotchi(self):
        self.what_run = "similarity-with-topics"
        self.saveOptions(dialog=False)
        print("Train Iagotchi")
        subprocess.run("docker-compose up &", shell=True)
        
    def trainIagotchi2(self):
        self.what_run = "similarity-without-topics"
        self.saveOptions(dialog=False)
        print("Train Iagotchi")
        status = self.invoke_process_popen_poll_live(" docker-compose up ", operation='train')
        if status == False:
            self.user_messages('Failed', message_type='critical')
        else:
            self.user_messages('Success', message_type='information')
            
        #subprocess.run("docker-compose up &", shell=True)
        
    def exec_cmd(self, cmd):
        
        try:
            #output = subprocess.check_output([cmd], stderr=subprocess.STDOUT, stdout=subprocess.PIPE, shell=True, universal_newlines=True)
            #popen = subprocess.Popen(cmd, shell=True, stdin=None, stdout=subprocess.PIPE, stderr=subprocess.PIPE, encoding='utf8')
            output = subprocess.check_output([cmd], stderr=subprocess.STDOUT, shell=True, universal_newlines=True)
            print("Output: \n{}\n".format(output))
            #(out, err) = popen.communicate()
            #print(out)
            #print(err)
            return True
        except subprocess.CalledProcessError as exc:
            print("Status : FAIL", exc.returncode, exc.output)
            return False
        else:
            print("Output: \n{}\n".format(output))
        
        
    def buildIagotchi(self):
        self.saveOptions(dialog=False)
        print("Install PureData")
        status = self.exec_cmd(" sh install_puredata.sh")
        if not status:
            self.user_messages('Failed', message_type='critical')
        print("Download Limaserver Image")
        #status = self.exec_cmd(" docker pull aymara/lima")
        #if not status:
        #    self.user_messages('Failed', message_type='critical')
        #    return
        print("Build Iagotchi")
        status = self.exec_cmd(" docker-compose build")
        if not status:
            self.user_messages('Failed', message_type='critical')
            return
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
        subprocess.run("pd puredata/IAGO_SOUND_PD/__IAGO_SOUND__.pd &", shell=True)

    def runConsole(self):
        print("Starting Console")
        subprocess.run("puredata/console/application.linux64/console &", shell=True)

        
    #def runMax(self):
        #print("Starting Max/Pd Patch")
        #status = self.exec_cmd("pd puredata/IAGO_SOUND_PD/__IAGO_SOUND__.pd &")
        #if not status:
            #self.user_messages('Failed', message_type='critical')
            #return

    #def runConsole(self):
        #print("Starting Console")
        #subprocess.run("puredata/console/application.linux64/console &", shell=True)

    def killAll(self, refresh=False):
        if not refresh:
            print("Killing Console")
            subprocess.run("killall console", shell=True)
            print("Killing Max Patch")
            subprocess.run("killall Iagotchi", shell=True)
        print("Killing Chrome")
        subprocess.run("killall \"Google Chrome\"", shell=True)
        print("Stopping Iagotchi")
        subprocess.run(" docker-compose stop", shell=True)
        #print("Killing Docker")
        #subprocess.run("killall Docker", shell=True)

if __name__ == "__main__":

    gui = iagotchiGui()
    gui.showGui()
    gui.exit()
    #sys.exit(app.exec_())
