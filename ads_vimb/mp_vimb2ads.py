#!/usr/bin/python3
#-*- coding: cp1251 -*-

"""
2013/03/28 14:18:08
2013/04/02 13:15:24
2013/04/03 16:07:45
"""

import xlrd
from configparser import ConfigParser

def date2int(indt):
  dtlst = indt.split('.')
  dtstr = dtlst[-1] + dtlst[-2] + dtlst[-3]
  return dtstr

def dt1moredt2(indt1, indt2):
  if date2int(indt1) > date2int(indt2):
    return True
  else:
    return False

def readxls(fn):

  colt = 3  # colt - column of time
  cold = 0  # cold - column of date
  colsp = 4 # cols - column of name video
  rowb = 8  # rowd - begin number for row
  endsnamesh = [' Б', ' б']
  outtds = []
  outbed = ['','']  # bed - list['data_begin','data_end']
  outvc = 0
  counttime = 0    #
  tms = []    # list of time tms['hh:mm', ... 'hh:mm']
  dts = []    # list of date and idSpot. tds = [['dd.mm.yyy',ts], ... ['dd.mm.yyy',ts]]
              # tms[i] - tds[i]

  book = xlrd.open_workbook(fn)
  count_shs = book.sheet_names().index('Лист1') + 1
  xlssheets = []
  for i in range(count_shs):
    xlssheets.append(book.sheet_by_index(i))
    print(xlssheets[i].name)  

  #print(sh.name, sh.nrows, sh.ncols)
  #print(rowb, rowe)

  for sh in xlssheets:
    bonus = True if sh.cell_value(colx = 2, rowx = 5)[-2:] in endsnamesh else False
    rowe = sh.nrows - 21  # rowe - end number for row
    tvct = rowe - rowb
    outvc += tvct   # outvc -  VixodCount
    tdtb = str(sh.cell_value(colx = cold, rowx = rowb))
    tdte = str(sh.cell_value(colx = cold, rowx = rowe))
    print(sh.name, bonus, tdtb, tdte)
    if sh.name == xlssheets[0].name:
      outbed[0] = tdtb
      outbed[1] = tdte
    else:
      outbed[0] = tdtb if dt1moredt2(outbed[0], tdtb) else outbed[0]
      outbed[1] = tdte if dt1moredt2(tdte, outbed[1]) else outbed[1]

    for rx in range(rowb, rowe):
      outd = str(sh.cell_value(colx = cold, rowx = rx))
      outt = str(sh.cell_value(colx = colt, rowx = rx))
      nmv = str(sh.cell_value(colx = colsp, rowx = rx))
      idv = nmv[:nmv.index('_')]
      if bonus:
        idv += 'b'

      try:
        indx = tms.index(outt)
      except ValueError:
        tms.append(outt)
        dts.append([])
        indx = len(tms) - 1
      dts[indx].append(outd + " " + idv)

  ctm = len(tms)
  if ctm == len(dts):
    for i in range(ctm):
      outtds.append([tms[i],dts[i]])

  outtds.sort()
  return outtds, outbed, outvc

def tds2dict(intds,inspots):
  dblpl = {}
  ib = 0
  for b in intds:
    tm = b[0]
    ib += 1
    dblpl['Block'+str(ib)] = {'BlockID':0, 'Time':tm + ':00','PlanCount':0}
    ip = 0
    for p in b[1]:
      dt,idv = p.split()
      ip += 1
      dblpl['Plan' + str(ib) + '_' + str(ip)] = {'SpotID':inspots[idv], 'Date':dt}
      dblpl['Block' + str(ib)]['PlanCount'] = ip
  return dblpl

def unionimp(fn1, fn2):
  f1 = open(fn1, 'a')
  f2 = open(fn2, 'r')
  f1.writelines(f2)
  f2.close()
  f1.close()

def xls2imp(fx, fi, fo1, fo2):
  mpimp = ConfigParser()
  mpimp.read(fi)
  mpimpSections = mpimp.sections()
  
  spots = {}
  countsp = 1
  for isec in mpimpSections:
    if (isec == 'Object' + str(countsp)) and ('Spot' + str(countsp) in mpimpSections):
      if mpimp.get('Spot'  + str(countsp), 'Bonus') == '1':
        spots[mpimp.get('Object' + str(countsp), 'Name').split('_')[0] + 'b'] = mpimp.get('Spot' + str(countsp), 'ID')
      else:
        spots[mpimp.get('Object' + str(countsp), 'Name').split('_')[0]] = mpimp.get('Spot' + str(countsp), 'ID')
      countsp += 1

  print(spots)

  xlsdata = readxls(fx)
  print(xlsdata[])
  
  mpimp.set('MP', 'BeginDate', xlsdata[1][0])
  mpimp.set('MP', 'EndDate', xlsdata[1][1])
  mpimp.set('MP', 'BlockCount', str(len(xlsdata[0])))
  f = open(fo1,'w')
  mpimp.write(f)
  f.close()

  mpdct = ConfigParser()
  mpdct.read_dict(tds2dict(xlsdata[0], spots))
  f = open(fo2,'w')
  mpdct.write(f)
  f.close()
  unionimp(fo1,fo2)


xls2imp('mp.xls', 'mp.imp', 'mp.imp', 'mpo2.imp')
#uninoimp("mpn.imp", "mpbp.imp")
