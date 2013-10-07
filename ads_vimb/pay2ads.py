#!/usr/bin/env python3
# -*- coding: utf-8 -*- 

import sys,xlrd,fdb,time
from os import chdir, getenv
from configparser import ConfigParser


def readcfg(cfn):
  

def readCompany(fn):
  bookC = xlrd.open_workbook(fn)
  shC = bookC.sheet_by_index(0)
  icCompId = 1
  icCompName = 2
  company = {}
  for irow in range(0, shC.nrows-1):
    company[shC.cell_value(irow,icCompName)] = \
      shC.cell_value(irow,icCompId)
  return company


def readPay(fn,bok):

  def dictAdd(idict,k,v):
    try:
      idict[k] += v
    except KeyError:
      idict[k] = v
    return idict

  bookP = xlrd.open_workbook(fn)
  shP = bookP.sheet_by_index(0)
  icDate = 0
  icDoc = 1
  icComDog = 4
  icSum = 9
  irSum = 9
  payments = []
  erPayments = []
  ipay = ()
  DocIdInDB = set()
  sql="select DOC_NUM from PAID where PAID_DATE between '{0}' and '{1}' and DEST={2};"
  lstDocIdInDB = sel2ads(sql.format(\
    dmy2ymd(shP.cell_value(irSum,icDate)), \
    dmy2ymd(shP.cell_value(shP.nrows-2,icDate)),bok))
  DocIdInDB = {i[0] for i in lstDocIdInDB}
  del lstDocIdInDB
  print(DocIdInDB)
  sqlInsPaid = "insert into PAID(PAID_ID,PAID_DATE,COMPANY_ID,PAID_SUM,\
    DOC_NUM,PAID_NAME,ITS_ID,DEST,DOGOVOR_ID) values \
    (GEN_ID(GEN_PAID_ID,1),'{0}',{1},{2},'{3}','{4}',{5},{6},{7})"
  iDocIdCount = {}
  for irow in range(irSum, shP.nrows-1):
    idtp,iComDog,idog,ixk,iperror,isump,iPaNm = "",[],[],"",0,0,''
    idtp = dmy2ymd(shP.cell_value(irow,icDate))
    iComDog = shP.cell_value(irow,icComDog).split("\n")
    idog = iComDog[1].replace("Договор №","").strip().rstrip("г.").split(" от ")
    iDoc = shP.cell_value(irow,icDoc).split("\n")
    iDocId = iDoc[0][-30:-22] if iDoc[0][-8] == ' ' else iDoc[0][-31:-23]
    dictAdd(iDocIdCount,iDocId,1)
    iDocId += str('%02i' % iDocIdCount[iDocId])
    if not(iDocId in DocIdInDB):
      iPaNm = iDoc[1].split(' от ')[0].strip() if bok == 1 else iDoc[1].split('согласно')[0].strip()
      ixcn = iComDog[0].strip()
      try:
        ixck = company[ixcn]
      except KeyError:
        ixck = 0
      isump = shP.cell_value(irow,icSum)
      sql = "select COMPANY.COMPANY_ID,DOGOVOR.DOGOVOR_ID from COMPANY,DOGOVOR \
          where COMPANY.COMPANY_ID=DOGOVOR.COMPANY_ID \
          and COMPANY.CODE='{0}' \
          and DOGOVOR.DOGOVOR_NUM='{1}' \
          and DOGOVOR.DOGOVOR_DATE='{2}'"
      if (len(idog)==2 and ixck != 0):
        sql = sql.format(ixck,idog[0],idog[1])
        resFind = sel2ads(sql)
      else:
        iperror = 1
      if (resFind and iperror == 0):
        icid,idid = resFind[0]
        ipay = (idtp,icid,isump,iDocId,iPaNm,5,bok,idid)
        cur.execute(sqlInsPaid.format(*ipay))
        payments.append(ipay)
      else:
        iperror = 2
      if iperror > 0:
        erPayments.append((idtp,ixck,iComDog[:2],isump,iDocId,bok,iperror,))
    else:
      continue
  lst2file(erPayments,"in/out/erPpay2ads_%s_%s.txt"%(ndtm, bok))
  return payments

def dmy2ymd(indt):
  return ".".join((indt[6:],indt[3:5],indt[:2]))

def ins2db(data):
  pass

def lst2file(inPays, fn):
  f = open(fn, 'w')
  for i in inPays:
    f.write(str(i) + "\n")
  cl = len(inPays)
  f.write(str(cl))
  f.close()
  print("В файл: {0} записано {1} строк".format(fn,cl))

def printPay(inPays):
  for i in inPays:
    print(i)
  print("Всего строк: ",len(inPays))

def sel2ads(isql):
  try:
    cur.execute(isql)
    res = []
    for row in cur:
      res.append(row)
  except fdb.fbcore.DatabaseError:
    print(isql)
    res.append(())
  else:
    return res


if __name__ == "__main__":
  if len(sys.argv) > 2:
    sys.stderr.write("Используйте: python %s имя_катклога" % sys.argv[0])
    raise SystemExit(1)
  chdir("/home/storm/Python/workRen/pay2ads")
  con = fdb.connect(host='host',database='base',user='user',
                    password='pass',role='ADM',charset='WIN1251')
  cur = con.cursor()
  sql = ""
  ndtm = time.strftime("%Y%m%d-%H%M",time.localtime())
  company = readCompany("in/agents.xls")
  print(len(company))
  payments = readPay("in/bank.xls",1) + readPay("in/kassa.xls",2)
  lst2file(payments,"in/out/pays1c_%s.txt"%ndtm)
  del company
  con.commit()
  con.close()
