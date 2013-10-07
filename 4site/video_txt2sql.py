#!/usr/bin/env python3

import sys
import time

if len(sys.argv) != 3:
  sys.stderr.write("Используйте: python %s имя_файла номер_группы" % sys.argv[0])
  raise SystemExit(1)

fntxt = sys.argv[1]
vgid = sys.argv[2]

fsql = open(fntxt[:fntxt.rfind('.')]+".sql", 'w')
fsql.write("INSERT INTO `photo_info` (`SectionID`, `MediaType`, `VideoID`, `Name`, `Title`, `Description`, `FileName`, `Source`, `CreateDate`, `IsVisible`, `InSlideShow`, `Hit`, `Voice`, `Mark`) VALUES\n")
ftxt = open(fntxt,'r')
curtm = time.strftime("%Y-%m-%d %H:%M:%S")
#lenftxt = len(ftxt)
for line in ftxt:
  iln = line.split("^")
  if len(iln) == 2:
    fsql.write("(" + vgid + ", 'video', '" + iln[0] + "', '" + 
      iln[1][:-1] + "', '" + iln[1][:-1] + "', NULL, 'http://i.ytimg.com/vi/" + iln[0] + "/0.jpg', 'YouTube', '" + curtm + "', 1, 0, 0, 0, 0),\n")
fsql.close()
ftxt.close()
#for line in open(fn, 'r'):
