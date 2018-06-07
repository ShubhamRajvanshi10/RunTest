#!/usr/bin/env python
import os, sys, time
import logging, threading

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
def ResetNDCServer(ControllerName):
	if(ControllerName == "work"):
		cmd = '/etc/init.d/ndc restart'
		logger.info("Running cmd -> " + cmd)
		NDCRestart = os.popen(cmd).read()
		logger.info("restart output --> " + NDCRestart)
		time.sleep(60)
	else:
		cmd = '/etc/init.d/ndc_{0} restart'.format(ControllerName)
		logger.info("Running cmd -> " + cmd)
		NDCRestart = os.popen(cmd).read()
		logger.info("restart output --> " + NDCRestart)
		time.sleep(60)
	return
def CheckCon(ControllerName, ServerIP, StatusFile):
	while(True):
		if(ControllerName == "work"):
                	cmd = '/etc/init.d/ndc show | grep "NDC port =" | cut -d "=" -f2 | cut -d " " -f2'
                	NDCPort = os.popen(cmd).read()
                	NDCPort = NDCPort.strip('\n')
                	CheckConnection = 'netstat -natp | grep -w {0} | grep {1} | wc -l'.format(NDCPort,ServerIP)
                	TotalConnection = os.popen(CheckConnection).read()
                	logger.info("    TotalNumber of connections are ->" + TotalConnection)
			time.sleep(300)
        	else:
                	cmd = '/etc/init.d/ndc_{0} show | grep "NDC port =" | cut -d "=" -f2 | cut -d " " -f2'.format(ControllerName)
                	NDCPort = os.popen(cmd).read()
                	NDCPort = NDCPort.strip('\n')
                	CheckConnection = 'netstat -natp | grep -w {0} | grep {1} | wc -l'.format(NDCPort,ServerIP)
                	TotalConnection = os.popen(CheckConnection).read()
                	logger.info("    TotalNumber of connections are ->" + TotalConnection)
			time.sleep(300)
	return
def CheckTest(ControllerName):
	#cmd = "/home/cavisson/{}/bin/nsu_show_netstorm | cut -d ' ' -f1 | tr '\n' '+' | cut -d '+' -f2".format(ControllerName)
	cmd = '/home/cavisson/{0}/bin/nsu_show_all_netstorm | grep "{1}" | cut -d "|" -f4'.format(ControllerName,ControllerName)
	output = os.popen(cmd).read()
	return output

def RunTest(TestCommand,StatusFile):
	cmd = TestCommand
	output = os.popen(cmd).read()
	logger.info("Going to run Command --> " + cmd)
	logger.info(output)
	return

def ResetServer(ResetIIS, ControllerName, ServerIP):
	if(ResetIIS == 1):
		TRFlag = CheckTest(ControllerName)
		try:
			TestRun = int(TRFlag)
			logger.debug("    TR running -> {}".format(TestRun))
		except ValueError:
			logger.info("<----Going to ResetIIS---->")
			Reset_IIS = '/home/cavisson/{0}/bin/nsu_server_admin -s {1} -i -c "iisreset"'.format(ControllerName,ServerIP)
			Reset_IIS_Output = os.popen(Reset_IIS).read()
			logger.debug("Cmd -> {}".format(Reset_IIS))
			logger.debug(Reset_IIS_Output)
			time.sleep(60)
	return

def PreTestFunction(ServerIP,ControllerName,Project,SubProject,ScenarioName,EnableND,ConnectToNDC,TestRunCount,ResetIIS,StatusFile,ResetNDC):
	count=0
        Set_ND = '/home/cavisson/{0}/bin/nsu_server_admin -s {1} -i -c "setx COR_ENABLE_PROFILING {2} -m"'.format(ControllerName,ServerIP,EnableND)
        ConnectNDC = '/home/cavisson/{0}/bin/nsu_server_admin -s {1} -i -c "setx CONNECT_TO_NDC {2} -m"'.format(ControllerName,ServerIP,ConnectToNDC)
        Set_ND_OutPut = os.popen(Set_ND).read()
        ConnectNDC_OutPut = os.popen(ConnectNDC).read()
	'''if(ResetIIS == 1):
		TRFlag = CheckTest(ControllerName)
		try:
			TestRun = int(TRFlag)
			logger.debug("    TR running -> {}".format(TestRun))
		except ValueError:
			logger.info("<----Going to ResetIIS---->")
			Reset_IIS = '/home/cavisson/{0}/bin/nsu_server_admin -s {1} -i -c "iisreset"'.format(ControllerName,ServerIP)
			Reset_IIS_Output = os.popen(Reset_IIS).read()
			logger.debug("Cmd -> {}".format(Reset_IIS))
			logger.debug(Reset_IIS_Output)'''
	cmd = "/home/cavisson/{0}/bin/nsu_start_test -n {1}/{2}/{3} -S gui".format(ControllerName,Project,SubProject,ScenarioName)
        while(count < TestRunCount):
                Status = CheckTest(ControllerName)
                try:
                        TestRun = int(Status)
			logger.debug("    TR running -> {}".format(TestRun)) 
                        time.sleep(600)
                except ValueError:
			ResetServer(ResetIIS, ControllerName, ServerIP)
			if(ResetNDC == 1):
				ResetNDCServer(ControllerName)
			RunTest(cmd,StatusFile)
                        time.sleep(60)
                	count = count + 1

	return

def main():
	Date = 'date +"%Y%m%d%H%M"'
	Date_OP = Set_ND_OutPut = os.popen(Date).read().rstrip('\n')
	StatusFile = "Status_{}.log".format(Date_OP)
	#logger = logging.getLogger(__name__)
	#logger.setLevel(logging.INFO)
	handler = logging.FileHandler(StatusFile)
	handler.setLevel(logging.INFO)
	formatter = logging.Formatter('%(asctime)s|%(name)s|%(levelname)s|%(message)s')
	handler.setFormatter(formatter)
	logger.addHandler(handler)
	logger.info("Going to start the main function")
	ThreadFlag = True
	#ConThread = threading.Thread(name = 'ConnThread', target=CheckCon)
	#ConThread.setDaemon(True)
	with open("PerfCases.txt", "r") as IF:
                for line in IF:
			if "#" in line:
				pass
			else:
				Details = line.split("|")
				ServerIP = Details[0]
				ControllerName = Details[1]
				Project = Details[2]
				SubProject = Details[3]
				ScenarioName = Details[4]
				EnableND = Details[5]
				ConnectToNDC = Details[6]
				TestRunCount = int(Details[7])
				ResetIIS = int(Details[8])
				ResetNDC = int(Details[9])
				if (ThreadFlag == True):
					ConThread = threading.Thread(name = 'ConnThread', target=CheckCon, args=(ControllerName, ServerIP, StatusFile))
        				ConThread.setDaemon(True)
					ConThread.start()
					ThreadFlag = False
				CheckCMON = "/home/cavisson/{0}/bin/nsu_server_admin -s {1} -i -c 'echo Hello'".format(ControllerName,ServerIP)
				CheckCMON_OutPut = os.popen(CheckCMON).read()
				if "Hello" in CheckCMON_OutPut:
					PreTestFunction(ServerIP,ControllerName,Project,SubProject,ScenarioName,EnableND,ConnectToNDC,TestRunCount,ResetIIS,StatusFile,ResetNDC)
				else:
					logger.info("NotAble to run NSU_SERVER_ADMIN on {} server".format(ServerIP))
			
	return
main()	
