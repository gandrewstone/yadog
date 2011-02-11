"""?
<desc>This module extracts documentation from text files</desc>
"""
from types import *
import pdb
import ast
import re

import sys
sys.path.append("/me/code")

from PyHtmlGen.document import *

from common import *
import microdom

from constants import *
      

def extractXml(prjPfx, filename):
  
  print "Parsing %s" % filename
  f = open(filename,"rb")
  text = f.read()

  if filename.startswith(prjPfx):
    filename = filename[len(prjPfx):]   

  xmltxt = "<%s name='%s' language='text'>" % (TagFile,filename) + text + "</%s>" % TagFile

  try:
    xml = microdom.parseString(xmltxt)
  except microdom.ExpatError,e:
    print "XML ERROR!", str(e)
    print str(xml)
    pdb.set_trace()
    
  return xml


def Test():
  xml = extractXml("readme.txt")
  #- xml = extractXml("microdom.py")

if __name__ == "__main__":
    Test()

