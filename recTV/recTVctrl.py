#!/usr/bin/env python3
#-*- coding: utf-8 -*-
#
import time
from datetime import time as dtime
from subprocess import getoutput
from urllib.request import urlopen, URLError, quote
def main():

  cdtm = time.localtime()
  #tm_year,tm_mon,tm_mday,tm_hour,tm_min,tm_sec,tm_wday,tm_yday,tm_isdst
  cdt = time.strftime("%Y%m%d",cdtm)
  tmf =  time.strftime("%H00",cdtm)
  smbu = 'user1'
  smbp = '1'
  smstxt = 'srv:'
  chs = {
          '5ch':['rec5','rec5ch',dtime(8,0),dtime(1,0)],
          'Ren':['recren','recRen',dtime(6,0),dtime(4,0)]
          #'Rus1':['rectv','recRus1',dtime(8,0),dtime(21,0)]
        }
  for ch in chs.keys():
    tmnt = time.localtime()
    tmn = dtime(tmnt[3],tmnt[4])
    if ((chs[ch][2]<tmn<chs[ch][3]) or (chs[ch][2]==chs[ch][3]) or \
    ((chs[ch][2]>chs[ch][3])and((dtime(0,0)<tmn< chs[ch][3])or\
    chs[ch][2]<tmn<dtime(23,59,59)))):
      idnm1 = '%s'%chs[ch][1]
      ifn='%s_%s_%02i/%s_%s/%s_%s_%s.avi'%(chs[ch][1],cdtm[0],cdtm[1],chs[ch][1],cdt,chs[ch][1],cdt,tmf)
      #print(ifn)
      fsz = getSizeFileBySMB(chs[ch][0],chs[ch][1],smbu,smbp,ifn)
      if (fsz < 9961472):
        smstxt += "\n rec%s fail:%.1f"%(ch,fsz/1024**2)
  print(smstxt)
  if len(smstxt)>5:
    sendSmsRu('xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx','yyyyyyyyyy',smstxt)

def sendSmsRu(api_id,to,txt):
  
  url="http://sms.ru/sms/send?api_id=%s&to=%s&text=%s&partner_id=3805" \
  %(api_id, to, quote(txt))
  http_timeout = 10
  try:
    res=urlopen(url,timeout=http_timeout)
  except URLError as errstr:
    print("smssend[debug]: %s" %(errstr))
  
  service_result=res.read().splitlines()
  
  if service_result is not None and int(service_result[0]) == 100:
    print("smssend[debug]: Message send ok. ID: %s" %(service_result[1]))
  
  if service_result is not None and int(service_result[0]) != 100:
    print('''smssend[debug]: Unable send sms message to %s when service \
    has returned code: %s '''%(to,servicecodes[int(service_result[0])]))

def getSizeFileBySMB(ismbh,ismbd,ismbu,ismbp,ifnm):
  
  cmd = '%'.join(("smbclient //%s/%s -U %s"%(ismbh,ismbd,ismbu),"%s -c 'ls %s'"%(ismbp,ifnm)))
  print(cmd)
  res = 8
  smbRes = getoutput(cmd).split('\n')
  #print("smbRes: %s"%smbRes)
  if len(smbRes) == 4 and not(smbRes[1]=='') and smbRes[2]=='':
    res = int(smbRes[1].split()[2])
  if len(smbRes) == 5 and not(smbRes[2]=='') and smbRes[3]=='':
    try:
      res = int(smbRes[2].split()[1])
    except ValueError:
      res = int(smbRes[2].split()[2])
  elif len(smbRes) == 2 and smbRes[1][:22] == 'NT_STATUS_NO_SUCH_FILE':
    res =  6  # 6 - '110', 100 - host поднят, 10 - smb-сервер поднят, 0 - файл не найден
  elif len(smbRes) == 1:
    if smbRes[0][-23:]== 'NT_STATUS_LOGON_FAILURE':
      res =  7  # '111'- неудачная авторизация
    if smbRes[0][-29:-1]=='Error NT_STATUS_UNSUCCESSFUL':
      res = 0  # '000' - host не доступен
  return(res)

if __name__ == "__main__":
  main()

