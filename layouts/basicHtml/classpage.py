"""? <module>
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


def genMemVars(obj):
  lst =  obj.getElementsByTagName(TagField) + obj.getElementsByTagName(TagVariable)
  header = ["Member Variable","Documentation"]
  body = []
  for mv in lst:
    body.append([mv.name,str(mv.children_[0])])
  grid = GridFromList(header, body )
  grid.RowBackground(Color(250,250,100),[Color(200,200,200),Color(240,240,240)])
  return grid

def genMethods(obj):
  lst =  obj.getElementsByTagName(TagFunction) + obj.getElementsByTagName(TagMethod)
  header = ["Methods","Args","Documentation"]
  body = []
  for m in lst:
    args = m.getElementsByTagName(TagParam)
    args = [a.name for a in args]
    body.append([m.name,",".join(args),str(m.children_[0])])
  grid = GridFromList(header, body )
  grid.RowBackground(Color(250,250,100),[Color(200,200,200),Color(240,240,240)])
  return grid



def generate(obj,cfg):

  mv = genMemVars(obj)
  m = genMethods(obj)

  # Figure out the upwards links
  fileobj = obj.findParent(TagFile)
  if fileobj: f = ["File: ", obj2link(fileobj[0])]
  else: f = ""
  
  sectionobj  = obj.findParent("section")
  if sectionobj: s = ["Section: ",obj2link(sectionobj[0])]
  else: s= ""

  hdr = VSplit([resize(2,obj.name),f,s])
  ctr = HSplit([BR,mv,BR,m])
  content = HeaderFooter(hdr, None,ctr)
  sidebarContent=""
  page = Sidebar(length(17,"%"), sidebarContent, content)

  fname = obj2file(obj)
  WriteFile("html"+os.sep+fname,page,HtmlSkel())
 
  return (fname,page)

#?</module>
