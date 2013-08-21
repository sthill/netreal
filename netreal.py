#!/usr/bin/env python

import paramiko
import os 
import conf
import inspect
import sys
import socket
import time

import logging 
import loggingSMTP

# Hosts login credentials  
user = conf.SSH_USER 
pwd = conf.SSH_PWD 

# SSH port  
sshport = conf.SSH_PORT 

# TCP and UDP ports
tcports = conf.TCP_PORTS
udports = conf.UDP_PORTS

# Mail details
mailserver = conf.MAIL_SERVER
mailfrom = conf.MAIL_FROM
mailto = conf.MAIL_TO
mailsubject = conf.MAIL_SUBJECT

# Logging
logging.getLogger("paramiko").setLevel(logging.CRITICAL)

log = logging.getLogger()
log.setLevel(logging.DEBUG)
log_format = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')

mh = loggingSMTP.BufferingSMTPHandler(mailserver, mailfrom, mailto, mailsubject,5000)
mh.setLevel(logging.CRITICAL)
mh.setFormatter(log_format)
log.addHandler(mh)

ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
ch.setFormatter(log_format)
log.addHandler(ch)

def test_ssh(host):
  """ Test ssh connection """
  try:
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(host[0], username=user, password=pwd, port=sshport, timeout=5)
    ssh.close
    response = 0
  except:
    log.error("SSH connection error or not open to " + host[1] + " (" + host[0] + ")")
    response = 1
  return response

def test_net(host,port,type):
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
      log.critical("Cannot connect to " + host[1] + " (" + host[0] + ") on TCP port: " + str(port))
    else:
      if errno != 107:
        pass
      else:
        log.critical("Cannot connect to " + host[1] + " (" + host[0] + ") on TCP port: " + str(port))

  s.close

def test_udp(host,port):
  """ Check if udp packet was received.
      Connects through ssh, opens a udp server and
      waits for a packet.
  """

  err = 0
  ssh = paramiko.SSHClient()
  ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
  ssh.connect(host[0], username=user, password=pwd, port=sshport, timeout=5)
  t1, t2, t3 = ssh.exec_command("nc -ul -w1 " + str(port))
 
  netest(host,port,"udp")

  time.sleep(5)
  ssh.close()
  
  if t2.read().strip() != "0":
    log.error("Cannot connect to " + host[1] + " (" + host[0] + ") on UDP port: " + str(port))
    err = 1

  return err

if __name__ == "__main__":

  # Find the right path for files (win or unix)
  path = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
  if os.name == 'nt':
    path += "\\"
  else:
    path += "/" 
  lr = [tuple(line.strip().split(':')) for line in (x for x in open(path + "hosts.txt", 'r') if not x.startswith('#'))]
  
  log.info('Testing TCP Ports...')
  for host in lr:
    for port in tcports:
      test_net(host,port,"tcp")
  
  log.info('Checking Hosts SSH Connectivity...')
  lr[:] = [host for host in lr if not test_ssh(host)]
  
  log.info('Testing UDP Ports...')
  for host in lr:
    err = 0
    for port in udports:
      err += test_udp(host,port)
    if err > 2:
      log.critical(host[1] + " (" + host[0] + ") has UDP ports closed")

  log.info('Done')
  # Send mail with log
  mh.flush()
  logging.shutdown()
