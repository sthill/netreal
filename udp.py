#!/usr/bin/env python

import paramiko,getpass,os,subprocess,conf, inspect
import time

# Vidyo routers login credentials  
user = conf.VIDYO_USER 
pwd = conf.VIDYO_PWD 

sshport = 2222

ssh1 = paramiko.SSHClient()
ssh1.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh1.connect("vidyorouter3.cern.ch", username=user, password=pwd, port=sshport, timeout=5)
t1, t2, t3 = ssh1.exec_command("nc -ul -w1 50000")
ssh2 = paramiko.SSHClient()
ssh2.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh2.connect("vidyorouter4.cern.ch", username=user, password=pwd, port=sshport, timeout=5)
ssh2.exec_command("echo -n 0 | nc -u -w1 vidyorouter3 50000")

time.sleep(1)
ssh1.close()
ssh2.close()

if t2.read().strip() != "0":
  print "Not working" 
