#!/usr/bin/env python

import paramiko
import os 
import conf
import inspect
import sys
import socket
import time

import logging 
logging.getLogger("paramiko").setLevel(logging.CRITICAL)
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

from mail_handler import cernMail

# Messages buffer
messages = []

# Hosts login credentials  
user = conf.SSH_USER 
pwd = conf.SSH_PWD 

# SSH port  
sshport = conf.SSH_PORT 

def ssh(host):
  """ Test ssh connection """
  try:
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(host[0], username=user, password=pwd, port=sshport, timeout=5)
    ssh.close
    response = 0
  except:
    logging.error("SSH connection error or not open to " + host[1] + " (" + host[0] + ")")
    response = 1
  return response

def netest(host,port,type):
  """ Test port connectivity 
      type => ["tcp" or "udp"] 
  """
  
  if type == "udp":
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
  else:
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
  s.settimeout(5)
  
  try:
    if type == "udp":
      s.sendto("0", (host[0], port))
    else:
      s.connect((host[0], port))
      s.shutdown(2)
  except Exception, e:
    try:
      errno, errtxt = e
    except ValueError:
      messages.append("Cannot connect to " + host[1] + " (" + host[0] + ") on TCP port: " + str(port))
    else:
      if errno != 107:
        pass
      else:
        messages.append("Cannot connect to " + host[1] + " (" + host[0] + ") on TCP port: " + str(port))

  s.close

def udp(host,port):
  """ Check if udp packet was received.
      Connects through ssh, opens a udp server and
      waits for a packet.
  """

  ssh = paramiko.SSHClient()
  ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
  ssh.connect(host[0], username=user, password=pwd, port=sshport, timeout=5)
  t1, t2, t3 = ssh.exec_command("nc -ul -w1 " + str(port))
 
  netest(host,port,"udp")

  time.sleep(5)
  ssh.close()
  
  if t2.read().strip() != "0":
    messages.append("Cannot connect to " + host[1] + " (" + host[0] + ") on UDP port: " + str(port))
    
if __name__ == "__main__":

  # Find the right path for files (win or unix)
  path = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
  if os.name == 'nt':
    path += "\\"
  else:
    path += "/" 
  lr = [tuple(line.strip().split(':')) for line in (x for x in open(path + "hosts.txt", 'r') if not x.startswith('#'))]
  
  logging.info('Testing TCP Ports...')
  for host in lr:
    for port in conf.TCP_PORTS:
      netest(host,port,"tcp")
  
  logging.info('Checking Hosts SSH Connectivity...')
  lr[:] = [host for host in lr if not ssh(host)]
  
  logging.info('Testing UDP Ports...')
  for host in lr:
    for port in conf.UDP_PORTS:
      udp(host,port)

  if messages:
    body = "\n".join(messages)
    logging.info(body)
    #fr0m = "service-avc-operation@cern.ch"
    #to = ["service-avc-operation@cern.ch"]
    #sub = "[Vidyo] Problem(s) with Vidyo Routers Connectivity"
    #m = cernMail(fr0m, to, sub, body)
    #m.send()
    
  logging.info('Done')
