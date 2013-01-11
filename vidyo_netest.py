#!/usr/bin/env python

import paramiko,getpass,os,subprocess,conf
from mail_handler import cernMail

messages = []

def ping(host):
  if os.name == 'nt':
    process = subprocess.Popen("ping -n 1 "+host,stdout=subprocess.PIPE)
    process.wait()
    response = process.returncode
  else:
    response = os.system("ping -c 1 " + host +" > /dev/null")   
  if response != 0:
    messages.append(host + ' is not reachable!')
  return response

def main(lr,lp):

  # Vidyo routers login credentials  
  user = conf.VIDYO_USER 
  pwd = conf.VIDYO_PWD 
  
  sshport = 2222
  
  print "Testing Ports..."
  for host in lr:
    try:
      ssh = paramiko.SSHClient()
      ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
      ssh.connect(host, username=user, password=pwd, port=sshport, timeout=5)
      for line in lr:
        t1, t2, t3 = ssh.exec_command("nc -z " + line + " 17990; echo $?")
        if int(t2.read().strip()) != 0:  
          messages.append("From "+host+" port 17990 is closed in " + line)
      for line in lp:
        t1, t2, t3 = ssh.exec_command("nc -z " + line + " 17991; echo $?")
        if int(t2.read().strip()) != 0:
          messages.append("From "+host+" port 17991 is closed in " + line)
    except:
      messages.append("SSH connection error or not open to "+host)

if __name__ == "__main__":
  lr = [line.strip() for line in (x for x in open("routers", 'r') if not x.startswith('#'))]
  lp = [line.strip() for line in (x for x in open("portals", 'r') if not x.startswith('#'))]
  print "Checking Routers Connectivity..."
  lr[:] = [host for host in lr if not ping(host)]
  lp[:] = [host for host in lp if not ping(host)]
  main(lr,lp)
  if messages:
    body = "\n".join(messages)
    fr0m = "service-avc-operation@cern.ch"
    to = ["bruno.bompastor@cern.ch"]
    sub = "Problem(s) with Vidyo Routers Connectivity"
    m = cernMail(fr0m, to, sub, body)
    m.send()
    
  print "Done"
