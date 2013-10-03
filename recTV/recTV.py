#!/usr/bin/env python3
#-*- coding: utf-8 -*-
#
import sys, getopt, time, subprocess
from os import getenv, chdir, mkdir, getcwd, kill
from os.path import exists, isfile, isdir
from configparser import ConfigParser
from urllib.request import urlopen, URLError, quote

def getOpts(argv):
  hlps = ["""  -v  - видео-устройство
  -с  - канал из списка ['Ren', '5ch', 'Rus1', 'THT', 'CTC']
  -d  - папка хранения записей.
  -s  - кол-во секунд записи. Поумолчанию равно кол-ву секунд до конца
        текущего часа\n
  Опции для sms-оповещения.
  --smsi - опция sms-оповещения api_id - для зарегистрированного
           пользователя http://sms.ru/?panel=api.
  --smst - опция sms-оповещенияto - номер телефона
           (10 символов). sms отправляеься при возникновении ошибки во
           время выполнения команды записи.
  опции --smsi и --smst используюся одновременно!\n
  Опции для передачи файла по smb-протоколу:
  --smbh - smb-хост
  --smbd - smb-директория
  --smbu - smb-пользователь
  --smbp - smb-пароль
  опции --smb* используюся одновременно!\n""",
  'Используйте опцию -h , для получения справки']

  outopts = {
    'vdev': '/dev/video0',
    'nmtv': '',
    'nmch': '',
    'vsec': 0,
    'vdir': '',
    'smsi': '', 'smst': '', 'smbh': '','smbd': '', 'smbu': '','smbp': ''
    }

  if not(exists(outopts['vdev'])):
    print('ВНИМАНИЕ: Видео-устройство %s, используемое по умолчанию, не найдено!\n \
    Используйте опцию -v , для указания другого.'%outopts['vdev'],hlps[1])
    sys.exit()

  chtv = {"Ren":"25", "5ch":"39", "Rus1":"R1", "THT":"37", "CTC":"29"}
  try:
    opts, args = getopt.getopt(argv,"hv:c:d:s:",['smsi=','smst=','smbh=','smbd=','smbu=','smbp='])
    if (len(args) > 0):
      raise getopt.GetoptError('лишние аргументы')
  except getopt.GetoptError:
    print(hlps[1])
    sys.exit(2)
  for opt, arg in opts:
    if opt == '-h':
      print(hlps[0])
      sys.exit()
    elif opt in ('-v'):
      if exists(arg):
        outopts['vdev'] = arg
      else:
        print('устройство %s не найдено' %(arg))
        sys.exit()
    elif opt in ('-c'):
      try:
        outopts['nmch'] = chtv[arg]
        outopts['nmtv'] = arg
      except KeyError:
        print('канала %s нет в списке каналов для записи\n%s' \
        %(arg,hlps[1]))
        sys.exit()
    elif opt in ('-d'):
      if exists(arg) and isdir(arg):
        outopts['vdir'] = arg
      else:
        print('директория %s не существует' %(arg))
        sys.exit()
    elif opt in ('-s'):
      try:
        outopts['vsec'] = int(arg)
      except (ValueError, TypeError):
        print('ключ -s должен быть целым числом')
        sys.exit()
    elif opt in ('--smsi'):
      if len(arg)==36:
        outopts['smsi'] = arg
    elif opt in ('--smst'):
      if len(arg)==10:
        outopts['smst'] = arg
    elif opt in ('--smbh'):
      outopts['smbh'] = arg
    elif opt in ('--smbd'):
      outopts['smbd'] = arg
    elif opt in ('--smbu'):
      outopts['smbu'] = arg
    elif opt in ('--smbp'):
      outopts['smbp'] = arg
  return outopts


def readcfg():

  optscfg = {
  'vdev': '','adev': '','nmtv': '','nmch': '','vdir': '','vsec': 0,
  'smbh': '','smbd': '', 'smbu': '','smbp': '',
  'smsi': '', 'smst': ''
  }
  fn = "/".join((getenv('HOME'),'.rectv'))
  if isfile(fn):
    
    
    fcfg  =  ConfigParser()
    fcfg.read(fn)
    fcfgs = fcfg.sections()
    ermsg = "Структура файла %s некорректна"%fn
    ofc = {
      'main':{'vdev', 'adev', 'name_tv', 'channel', 'folder', 'seconds'},
      'smb':{'host', 'dir', 'user', 'pass'},
      'sms':{'api_id', 'ph_num'}
      }
    if set(fcfgs) == ofc.keys():
      chsecs = 0
      for isec in fcfgs:
        chsecs += 1 if ofc[isec] == set(fcfg.options(isec)) else 0
      if chsecs == len(ofc.keys()):
        optscfg['vdev']=fcfg.get('main','vdev')
        optscfg['adev']=fcfg.get('main','adev')
        optscfg['nmtv']=fcfg.get('main','name_tv')
        optscfg['nmch']=fcfg.get('main','channel')
        optscfg['vdir']=fcfg.get('main','folder')
        optscfg['vsec']=fcfg.get('main','seconds')
        optscfg['smbh']=fcfg.get('smb','host')
        optscfg['smbd']=fcfg.get('smb','dir')
        optscfg['smbu']=fcfg.get('smb','user')
        optscfg['smbp']=fcfg.get('smb','pass')
        optscfg['smsi']=fcfg.get('sms','api_id')
        optscfg['smst']=fcfg.get('sms','ph_num')
      else:
        print(ermsg)
        return optscfgz
    else:
      print(ermsg)
      return optscfgz
    
  else:
    ermsg = "Файл %s ненайден"%fn
    print(ermsg)
  return optscfg

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

def startRec(opts):
  optsD = 

  opts['vdev'] = optsD['vdev'] if opts['vdev'] == '' else opts['vdev']
  opts['nmtv'] = optsD['nmtv'] if opts['nmtv'] == '' else opts['nmtv']
  opts['vdir'] = optsD['vdir'] if opts['vdir'] == '' else opts['vdir']
  ermsg = 'rec%s'%(opts['nmtv'])
  for pid in  list(set([p.split()[1] for p in subprocess.getoutput('lsof %s'%opts['vdev']).split('\n')[1:]])):
    kill(int(pid),9)

  if (len(subprocess.getoutput('lsof %s'%(opts['vdev'])).split('\n')) > 1):
    ermsg += " : vdev is bisy"
  if opts['nmch'] == '':
    opts['nmch'] = optsD['nmch']
  elif (subprocess.call('v4lctl -c %s setchannel %s'%(opts['vdev'],opts['nmch']), shell=True) > 0):
    ermsg += " : can't set channel"

  print("opts : ",opts)

  if (" : " in ermsg):
    print('ermsg: ',ermsg)
    sendSmsRu(opts['msid'],opts['msto'],ermsg)
    sys.exit()

  chdir(opts['vdir'])
  if not(isdir(opts['vdir']+'/.rec%s.log.d'%opts['nmtv'])):
    mkdir('.rec%s.log.d'%opts['nmtv'])

  cmdRec = """ffmpeg -y -f video4linux2 -i %s -f alsa -ac 2 -i hw:1 \
  -vf "drawtext=fontfile=/usr/share/fonts/TTF/DejaVuSans-Bold.ttf: \
  text='%s\ ': timecode='%s\:00': r=25: x=(w-tw)/2: y=h-(2*lh): \
  fontcolor=white: box=1: boxcolor=0x00000000@1" -strict -2 -map 0:0 \
  -map 1:0 -r 25 -c:v libxvid -b:v 2000k -s 768x576 -acodec mp3 -ar 44100 \
  -ab 128k -to %s %s.avi 2> .rec%s.log.d/%s.log"""

  ctm = time.localtime()
  cdts = time.strftime("%Y-%m-%d",ctm)
  ctms = time.strftime("%H\:%M\:%S",ctm)
  dts = time.strftime("%Y%m%d",ctm)
  tms = time.strftime("%H%M",ctm)
  fn = 'rec%s_%s'%(opts['nmtv'],"_".join((dts,tms)))
  vrd = 'rec%s_%s_%s'%(opts['nmtv'],ctm[0],time.strftime("%m",ctm))+'/'+fn[:-5]
  if not(isdir(vrd)):
    print(subprocess.getoutput('mkdir -p %s'%vrd))

  fnv = vrd+'/'+fn
  opts['vsec'] = 60*(59-ctm.tm_min)+58-time.localtime().tm_sec if opts['vsec'] == 0 else opts['vsec']
  cmdRec = cmdRec %(opts['vdev'],cdts,ctms,opts['vsec'],fnv,opts['nmtv'],fn)
  print(cmdRec)

  exs = subprocess.call(cmdRec, shell=True)
  if exs==0:
    print('rec%s success'%opts['nmtv'])
    if (opts['smbh'] and opts['smbd'] and (opts['smbu'] and opts['smbp'])):
      smbcmd = '%'.join(("smbclient //%s/%s -U %s"%(opts['smbh'],\
               opts['smbd'],opts['smbu']),"%s -c 'put %s'"%(opts['smbp'],fnv+'.avi')))
      print(smbcmd)
      subprocess.call(smbcmd, shell=True)
    else:
      print('Файл %s не был передан по smb-протоколу! Используйте опцию -h , для получения справки'%fn)
  else:
    if (opts['smsi'] and opts['smst']):
      sendSmsRu(opts['smsi'],opts['smst'],"rectv: %s > %s"%(fn,exs))


if __name__ == "__main__":

  startRec(getOpts(sys.argv[1:]))
  sys.exit()
