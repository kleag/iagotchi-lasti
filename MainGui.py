import sys, subprocess,json,socket
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
        self.btnIagoConfig = QPushButton("Open config.json")
        self.btnGitPull = QPushButton("Update (git pull)")
        self.btnMax = QPushButton("Start Max patch")
        self.btnConsole = QPushButton("Start Processing Console")
        self.btnKill = QPushButton("Stop everything (killall)")
        
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

        grid.addWidget(self.btnDocker,0,0)
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
        grid.addWidget(self.btnIagoConfig,15,0)
        grid.addWidget(self.btnGitPull,16,0)
        grid.addWidget(self.btnBuild,17,0)
        grid.addWidget(self.btnTrain,18,0)
        grid.addWidget(self.btnTrain2,19,0)
        grid.addWidget(self.btnKill,20,0)
        
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
        
    def printOptions(self):
        print("Options")
        print("    BOTNAME "+self.botname)
        print("    WHAT_RUN "+self.what_run)
        print("    IP "+self.ipAddress)
        
    def runDocker(self):
        print("Starting Docker")
        subprocess.run("open -a Docker &", shell=True)
        
    def runChrome(self):
        print("Starting Chrome")
        #subprocess.run(["open", "-a", "Google Chrome", "http://localhost:8088", "&"], shell=True)
        subprocess.run("open -a \"Google Chrome\" http://localhost:8088 &", shell=True)
        
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
        
    def buildIagotchi(self):
        self.saveOptions()
        print("Build Iagotchi")
        subprocess.run("sudo docker-compose build &", shell=True)
        
    def confDocker(self):
        print("opening Docker Config")
        subprocess.run("open docker-compose.yml &", shell=True)
        
    def confIago(self):
        print("opening Iagotchi Config")
        subprocess.run("open data/config.json &", shell=True)
        
    def gitPull(self):
        print("updating Iagotchi")
        subprocess.run("git pull &", shell=True)
        
    def runMax(self):
        print("Starting Max Patch")
        subprocess.run("open ../patch/Iagotchi.app &", shell=True)

    def runConsole(self):
        print("Starting Console")
        subprocess.run("open ../patch/console.app &", shell=True)

    def killAll(self):
        print("Killing Console")
        subprocess.run("killall console", shell=True)
        print("Killing Max Patch")
        subprocess.run("killall Iagotchi", shell=True)
        print("Killing Chrome")
        subprocess.run("killall \"Google Chrome\"", shell=True)
        print("Stopping Iagotchi")
        subprocess.run("docker-compose stop", shell=True)
        print("Killing Docker")
        subprocess.run("killall Docker", shell=True)

if __name__ == "__main__":

    gui = iagotchiGui()
    gui.showGui()
    gui.exit()
    #sys.exit(app.exec_())