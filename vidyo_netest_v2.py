#!/usr/bin/env python

import paramiko,os,conf, inspect
from mail_handler import cernMail

import sys
import socket
import time

messages = []
# Vidyo routers login credentials  
user = conf.VIDYO_USER 
pwd = conf.VIDYO_PWD 
  
sshport = 2222

def ssh(host):
  try:
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(host[0], username=user, password=pwd, port=sshport, timeout=5)
    ssh.close
    response = 0
  except:
    messages.append("SSH connection error or not open to " + host[1] + " (" + host[0] + ")")
    response = 1
  return response

def netest(host,port,type):
  # type => ["tcp" or "udp"]
  if type == "udp":
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
  else:
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
  s.settimeout(5)
  try:
    if type == "udp":
      s.sendto("0", (host[0], port))
      recv, svr = s.recvfrom(255)
      s.shutdown(2)
    else:
      s.connect((host[0], port))
      s.shutdown(2)
  except Exception, e:
    try:
      errno, errtxt = e
    except ValueError:
      messages.append("Cannot connect to " + host[0] + " on port: " + str(port))
    else:
      if errno != 107:
        messages.append("Cannot connect to " + host[0] + " on port: " + str(port))

  s.close

def udp(host,port):
    ssh1 = paramiko.SSHClient()
    ssh1.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh1.connect(host[0], username=user, password=pwd, port=sshport, timeout=5)
    t1, t2, t3 = ssh1.exec_command("nc -ul -w1 " + str(port))
   
    netest(host[0],port,"udp")
 
    time.sleep(1)
    ssh1.close()
    
    if t2.read().strip() != "0":
      messages.append("Cannot connect to " + host[0] + " on port: " + str(port))
    
if __name__ == "__main__":

  path = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
  if os.name == 'nt':
    path += "\\"
  else:
    path += "/" 
  lr = [tuple(line.strip().split(':')) for line in (x for x in open(path + "routers.txt", 'r') if not x.startswith('#'))]
  
  print "Testing TCP Ports From Routers..."
  for host in lr:
    netest(host,17990,"tcp")
    netest(host,17991,"tcp")
    netest(host,17992,"tcp")
  
  print "Checking Routers SSH Connectivity..."
  lr[:] = [host for host in lr if not ssh(host)]
  
  print "Testing UDP Ports From Routers..."
  for host in lr:
    udp(host,50000)

  if messages:
    body = "\n".join(messages)
    print body
    #fr0m = "service-avc-operation@cern.ch"
    #to = ["service-avc-operation@cern.ch"]
    #sub = "[Vidyo] Problem(s) with Vidyo Routers Connectivity"
    #m = cernMail(fr0m, to, sub, body)
    #m.send()
    
  print "Done"
