#!/usr/bin/env python

import paramiko,getpass,os,subprocess,conf, inspect
from mail_handler import cernMail

messages = []

def ping(host):
  if os.name == 'nt':
    process = subprocess.Popen("ping -n 1 "+host[0],stdout=subprocess.PIPE)
    process.wait()
    response = process.returncode
  else:
    response = os.system("ping -c 1 " + host[0] + " > /dev/null")   
  if response != 0:
    messages.append(host[1] + " (" + host[0] + ") is not reachable!")
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
      ssh.connect(host[0], username=user, password=pwd, port=sshport, timeout=5)
      for line in lr:
        t1, t2, t3 = ssh.exec_command("nc -z " + line[0] + " 17990; echo $?")
        if int(t2.read().strip()) != 0:  
          messages.append("From " + host[1] + " (" + host[0] + ") port 17990 is closed in " + line[1] + " (" + line[0] + ")")
      for line in lp:
        t1, t2, t3 = ssh.exec_command("nc -z " + line[0] + " 17991; echo $?")
        if int(t2.read().strip()) != 0:
          messages.append("From " + host[1] + " (" + host[0] + ") port 17991 is closed in " + line[1] + " (" + line[0] + ")")
    except:
      messages.append("SSH connection error or not open to " + host[1] + " (" + host[0] + ")")

if __name__ == "__main__":
  path = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
  if os.name == 'nt':
    path += "\\"
  else:
    path += "/" 
  lr = [tuple(line.strip().split(':')) for line in (x for x in open(path + "routers.txt", 'r') if not x.startswith('#'))]
  lp = [tuple(line.strip().split(':')) for line in (x for x in open(path + "portals.txt", 'r') if not x.startswith('#'))]
  print "Checking Routers Connectivity..."
  lr[:] = [host for host in lr if not ping(host)]
  lp[:] = [host for host in lp if not ping(host)]
  main(lr,lp)
  if messages:
    body = "\n".join(messages)
    fr0m = "service-avc-operation@cern.ch"
    to = ["service-avc-operation@cern.ch"]
    sub = "[Vidyo] Problem(s) with Vidyo Routers Connectivity"
    m = cernMail(fr0m, to, sub, body)
    m.send()
    
  print "Done"
