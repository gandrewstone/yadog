from types import *

from document import *
from htmldoc import *
from chunk import ChunkBase

noGaps = """body, table, tr, td, h1, h2, p, hr
{
margin: 0 0 0 0;
padding: 0 0 0 0;
border-spacing: 0 0;
}
"""

class CssClass(ChunkBase):
  """This represents a CSS class"""
  def __init__(self,name,style=None,parent=None,othernames=None):
    ChunkBase.__init__(self)
    self.id = name
    if othernames == None: self.othernames = []
    else: self.othernames = othernames

    if style:
      self.styles = style
    if parent: self.cssClass = parent
    
  def gen(self,doc):
    if doc.scratchPad.has_key(self.id): return # Only generate once per document
    doc.scratchPad[self.id] = True
    for m in self.modules: doc.AddModule(m)
 
    if self.cssClass and type(self.cssClass) is not StringType: self.cssClass.gen(doc)

    styleStr = self.styleStr()
    if len(styleStr)>0:  # no point to put an entry in CSS if there is nothing in this class
        doc.Insert("%s {%s}\n" % (self.getClassHierarchy(), styleStr), doc.style, Before)

  def getClassHierarchy(self):
    prefix = ""
    parent = self.cssClass
    if parent: 
      if type(parent) is StringType: prefix = parent
      else: prefix = parent.getClassHierarchy()
    name = "%s.%s" % (prefix,self.id)  
    ret = self.othernames + [name]
    return ",".join(ret)

  def __str__(self):
    return str(self.id)

#cleanAnchor = "a.z,a.z:link,a.z:visited,a.z:active,a.z:hover {text-decoration: none; outline:none; color: black;}"

#anchorCssClass = CssClass("a",CssRootClass)

cleanAnchor = CssClass("z",{"text-decoration": "none", "outline":"none", "color": "black"},"a",othernames=["a.z:link","a.z:visited","a.z:active","a.z:hover"])
