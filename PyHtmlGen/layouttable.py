from gen import *
from chunk import *
from document import *
from attribute import *
from table import *

# Deprecated
chunkTable = ChunkTable


GridSplit = ChunkTable

class HSplit(ChunkTable):
  def __init__(self,splitContentList=None,colWidths=None):
    if splitContentList is None:  # Default split is 2
      splitContentList = ["",""]
    self.nSplits = len(splitContentList)
    ChunkTable.__init__(self,1,self.nSplits,colWidths)
    
    idx = 0
    for c in splitContentList:
      self.item(0,idx).set(c)
      idx += 1
                   
  def setTop(self,obj):
    self.item(0,0).set(obj)

  def setBottom(self,obj):
    self.item(0,self.nSplits-1).set(obj)


class HeaderFooter:
  def __init__(self,header=True,footer=True,center=True):
    (wantsHeader,header) = TFO(header,"")
    (wantsCenter,center) = TFO(center,"")
    (wantsFooter,footer) = TFO(footer,"")

    # You have to select a center and one or more of header and footer
    assert(wantsCenter) # the center option is there just in case he passes an object to BE the center.
    assert(wantsHeader or wantsFooter)
    
    tablen = wantsHeader + wantsCenter + wantsFooter
    
    self.table = chunkTable(1,tablen)

    if wantsHeader:
      self.header = self.table[0][0]
      self.center = self.table[0][1]
      if wantsFooter: self.footer = self.table[0][2]
      else:           self.footer = chunkNoShow()
    elif wantsFooter:
      self.center = self.table[0][0]
      self.footer = self.table[0][1]

    self.header.set(header)
    self.center.set(center)
    self.footer.set(footer)


  def header(self,obj):
    self.header.set(obj)

  def footer(self,obj):
    self.footer.set(obj)

  def set(self,obj):
    "Sets the center"
    self.center.set(obj)

  def gen(self,doc):
    self.table.gen(doc)

  def __str__(self):
    return str(self.table)


class VSplit(ChunkTable):
  def __init__(self,splitContentList=None,colWidths=None,myId=None):
    if splitContentList is None:  # Default split is 2
      splitContentList = ["",""]
    self.nSplits = len(splitContentList)
    ChunkTable.__init__(self,self.nSplits,1,colWidths,myId=myId)
    
    idx = 0
    for c in splitContentList:
      self.item(idx,0).set(c)
      idx += 1
                   
  def setLeft(self,obj):
    self.item(0,0).set(obj)

  def setRight(self,obj):
    self.item(self.nSplits-1,0).set(obj)

      
class Sidebar(VSplit):
  def __init__(self,sideWidth,sidebar="",center=""):
    sideWidth = FixupLen([(sideWidth,10)])[0]
    VSplit.__init__(self,[sidebar,center],[sideWidth])

  def sidebar(self,obj):
    self.item(0,0).set(obj)
    
  def set(self,obj):
    self.item(1,0).set(obj)


  

def Test():

  tt = ChunkTable(2,2)

  tt.idx[0][0].set("00")
  tt.idx[1][0].set("10")
  tt.idx[0][1].set("01")
  tt.idx[1][1].set("11")

  hf = HeaderFooter("Header","Footer")
  hf.set("Center")

  sb = Sidebar(25)

  sb.sidebar("Sidebar")
  sb.set("Center")

  sb1 = Sidebar(80,"sidebar","center")

  hsplit = HSplit(["Top","Bottom"])

  result = "%s\n%s\n%s\n%s\n%s\n" % (tt,hf,sb,sb1,hsplit)

  print result


  file = open('testlayouttable.html','w')
  file.write(result)
  file.close
 
  return tt

  
