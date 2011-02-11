"""<module>
This module generates an html page based on some file
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

def genVars(obj):
  lst =  obj.getElementsByTagName(TagVariable)
  header = ["Global Variables","Documentation"]
  body = []
  for v in lst:
    if not v.findParent(TagClass): # Skip all variables that are actually defined in a class not at the top level
      body.append([v.name,str(v.children_[0])])
  grid = GridFromList(header, body )
  grid.RowBackground(Color(250,250,100),[Color(200,200,200),Color(240,240,240)])
  return grid

def genFns(obj):
  lst =  obj.getElementsByTagName(TagFunction)
  header = ["Global Functions","Args","Documentation"]
  body = []
  for m in lst:
    if m.findParent(TagClass): continue  # Skip all functions that are actually defined in a class not at the top level  
    args = m.getElementsByTagName(TagParam)
    args = [a.name for a in args]
    docstr = m.get(TagDoc,"")
    if not docstr:
      try:
          docstr = m.children_[0]
      except IndexError:
          pass
    body.append([m.name,",".join(args),str(docstr)])
  grid = GridFromList(header, body )
  grid.RowBackground(Color(250,250,100),[Color(200,200,200),Color(240,240,240)])
  return grid

def genClasses(obj):
  lst =  obj.getElementsByTagName(TagClass)
  header = ["Classes","Documentation"]
  body = []
  for m in lst:
    args = m.getElementsByTagName(TagParam)
    args = [a.name for a in args]
    body.append([obj2link(m),str(m.children_[0])])
  grid = GridFromList(header, body )
  grid.RowBackground(Color(250,250,100),[Color(200,200,200),Color(240,240,240)])
  return grid



def generate(obj,cfg):
  try:
    mv = genVars(obj)
    m =  genFns(obj)
    c =  genClasses(obj)

    # Figure out the upwards links  
    sectionobj  = obj.findParent("section")
    if sectionobj: s = ["Section: ",obj2link(sectionobj[0])]
    else: s= ""

    hdr = VSplit([resize(2,obj.name),s])
    ctr = HSplit([BR,mv,BR,m,BR,c])
    content = HeaderFooter(hdr, None,ctr)
    sidebarContent=""
    page = Sidebar(length(17,"%"), sidebarContent, content)

    fname = obj2file(obj)
    WriteFile("html"+os.sep+fname,page,HtmlSkel())
  except Exception, e:
    print e
    pdb.set_trace()
 
  return (fname,page)

#</module>
