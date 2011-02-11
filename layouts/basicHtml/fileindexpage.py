"""<module>
This module generates an html page based on some class
"""
import pdb

import sys
sys.path.append("/me/code")


from PyHtmlGen.gen import *
from PyHtmlGen.document import *
from PyHtmlGen.htmldoc import *
from PyHtmlGen.bar import *
# from layoutstyle import *
from PyHtmlGen.layouttable import *
from PyHtmlGen.table import *
from PyHtmlGen.imagehtml import *
from PyHtmlGen.menu import *
from PyHtmlGen.layouthtml import *
from PyHtmlGen.form import *
from PyHtmlGen.attribute import *
from PyHtmlGen.json import *
from PyHtmlGen.cssclass import *

from common import *
from htmlcommon import *
from constants import *

def genClasses(cllist):
  header = ["Class","Section","File"]
  body = []
  for obj in cllist:
    body.append([obj2link(obj),parentLink(TagSection),parentLink(TagFile)])

  grid = GridFromList(header, body )
  grid.RowBackground(Color(250,250,100),[Color(200,200,200),Color(240,240,240)])
  return grid


def generate(objs,cfg):
  return(None,None)
  mv = genFiles(objs)

  hdr = VSplit([resize(2,"Class Directory")])
  ctr = HSplit([BR,mv])
  content = HeaderFooter(hdr, None,ctr)
  sidebarContent=""
  page = Sidebar(length(17,"%"), sidebarContent, content)

  fname = obj2file(obj)
  WriteFile("html"+os.sep+fname,page,HtmlSkel())
 
  return (fname,page)

#</module>
