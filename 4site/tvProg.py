#!/usr/bin/env python3

import xlrd
import sys
from datetime import date, time, timedelta

if len(sys.argv) != 2:
  sys.stderr.write("Используйте: python %s файл1.xls" % sys.argv[0])
  raise SystemExit(1)
fnxls = sys.argv[1]

def readxls(fn):
  book = xlrd.open_workbook(fn)
  sh = book.sheet_by_index(0)
  weekDay = {'Понедельник', 'Вторник', 'Среда', 'Четверг', 'Пятница', 'Суббота', 'Воскресенье'}
  tm0 = time(0,0)
  tms = time(5,0) 
  outData = []
  print("cols: ", sh.ncols)
  
  def getAge(icv):
    if icv.find(' ') > 0:
      return icv.split()[0]
    else:
      return icv.split("+")[0]

  def getIprog(inRow,intm,indt):
    if len(intm) == 5 and len(intm.split(":")) == 2:
      itm = time(int(intm[:2]), int(intm[3:]))
      if 0 <= itm.hour < 5:
        indt += delta
      ipn = sh.cell_value(inRow, 1)
      iag = getAge(sh.cell_value(inRow,2))
      #print(itm, indt)
      outData.append([iag, "-".join(["%4d" %indt.year, "%02d" %indt.month, "%02d" %indt.day])+" "+":".join(["%02d" %itm.hour, "%02d" %itm.minute, "%02d" %itm.second]), ipn])

  if sh.ncols == 3:
    idt = ""
    for iRow in range(sh.nrows):
      itm = ""
      ipr = ""
      iag = ""
      iou = []
      delta = timedelta(days=1)
      iRowTypes = str(sh.cell_type(iRow, 0)) + str(sh.cell_type(iRow, 1)) + str(sh.cell_type(iRow, 2))
      if iRowTypes == "010":
        iRowDt = sh.cell_value(iRow, 1).split()
        if (len(iRowDt[0]) == 8) and (iRowDt[1] in weekDay) and (len(iRowDt[0].split(".")) == 3):
          liDt = iRowDt[0].split(".")
          idt = date(int("20" + liDt[2]),int(liDt[1]),int(liDt[0]))
          print("Date: ", idt)
      elif (iRowTypes == "111") and (sh.cell_value(iRow, 0) != 'Начало'):
        ittm = sh.cell_value(iRow, 0)
        getIprog(iRow,ittm,idt)
      elif (iRowTypes == "311") and (sh.cell_value(iRow, 0) != 'Начало'):
        ittm = (xlrd.xldate_as_tuple(sh.cell_value(iRow,0), book.datemode))
        getIprog(iRow,ittm,idt)
  return outData

def tosql(inTP):
  fsql = open("out/"+fnxls[:fnxls.rfind('.')]+".sql", 'w')
  fsql.write("INSERT INTO `tv_program`(`AgeBracketID`, `ShowTime`, \
`Name`) VALUES \n")
  for i in inTP:
    fsql.write("('" + "', '".join(i) + "'),\n")
  fsql.close()

tosql(readxls("in/"+fnxls))
