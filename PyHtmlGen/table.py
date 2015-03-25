import pdb

from chunk import *

def FillGrid(x,y):
  ret = []
  for xi in range(0,x):
    ret.append(y * [chunkRecurse()])
  return ret
    

class ChunkTable(ChunkTag):
  def __init__(self,numCol,numRow,colwidth=None,rowwidth=None,myId=None,cellspace=None,border=None,ExtraAttrStr=None):
    ChunkTag.__init__(self,"table")
    self.id     = myId
    self.idx    = FillGrid(numCol,numRow)
    self.numRow = numRow
    self.numCol = numCol

    if border is None:
      if debugShowTableEdges:
        border = 1
      else:
        border = 0
    
    [rowwidth,cellspace,border] = FixupLen([(rowwidth,centPercent),(cellspace,0),(border,0)])
    
    if colwidth:
      colwidth                  = FixupLen([(x,None) for x in colwidth])

    #self.table = chunkTag("table",None,[('cellspace',cellspace),('border',border),('width',rowwidth)],myId=self.id)
    self.setAttrs([('cellspace',cellspace),('border',border),('width',rowwidth)])
    
    if colwidth is None:
      body = self
    else:
      cw = chunkBuffer()
      for len in colwidth:
        cw.append(chunkStr("<col width='%s' />" % len))

      self.infix = cw
      body = chunkTag('tbody')
      cw.append(body)
      
    self.render = chunkBuffer()
    self.rows = []
    self.cols = []
    for r in range(0,numRow):
      row = chunkTag('tr')
      cols = chunkBuffer()
      for c in range(0,numCol):
        col = chunkTag("td")
        item = chunkRecurse()
        col.set(item)
        self.idx[c][r] = item
        cols.append(col)
        self.cols.append(col)
        
      row.set(cols)
      self.rows.append(row)
      self.render.append(row)

    body.infix = self.render
    

#  def gen(self,doc):
#    return self.table.gen(doc)

#  def __str__(self):
#    return str(self.table)

  def rowGroup(self,start,end,attrs=None,styles=None,myId=None):
    """ Allows rows to be grouped and returns the grouping object.
        start and end are slice indexes, based not on the table, but on the table including all prior groupings
    """
    pullOut = self.render.buf[start:end]
    grp = Chunk(pullOut,attrs,styles,myId)
    self.render.buf[start:end] = [grp]
    return grp    

  def row(self,y):
    """Returns the containing <tr></tr>, so you can modify style or Id"""
    return self.rows[y]

  def cell(self,x,y):
    """Returns the container <td></td>.  To set the contents, use [x][y] or item, and then 'set' the returned object: e.g. tab.idx[0][0].set(Chunk("contents"))"""
    return self.cols[(y*self.numCol) + x]

  def item(self,x,y):
    "Returns the contents, same as [][]"
    return self.idx[x][y]

  def __getitem__(self,idx):
    "Items are stored in x,y format (ie specify column first, then row)"
    return self.idx[idx]



class Grid(ChunkTable):
  """Fixed size table"""
  def __init__(self,numCol,numRow,colwidth=None,rowwidth=None,myid=None,cellspace=None,border=None,ExtraAttrStr=None):
    ChunkTable.__init__(self,numCol,numRow,colwidth,rowwidth,myid,cellspace,border,ExtraAttrStr)

  def RowBackground(self,head=None,body=None):
    self.lineBkgCol = (head,body)
    pos = 0
    if head:
       self.rows[pos].styles['background'] = head
       pos += 1
   
    cnt = 0
    blen = len(body)
    for r in self.rows[pos:]:
      self.rows[pos].styles['background'] = body[cnt % blen]
      pos+=1
      cnt+=1

  def RowAttrs(self,head=None,body=None):
    """?? Set attributes associated with each row.
    <param name="head">Attribute dictionary to apply to the table header</param>
    <param name="body">List of attribute dictionaries to apply to the table rows sequentially</param>
    """
    self.lineBkgCol = (head,body)
    pos = 0
    if head:
       self.rows[pos].setAttrs(head)
       pos += 1
   
    cnt = 0
    blen = len(body)
    for r in self.rows[pos:]:
      self.rows[pos].setAttrs(body[cnt % blen])
      pos+=1
      cnt+=1

  def RowStyles(self,head=None,body=None):
    self.lineBkgCol = (head,body)
    pos = 0
    if head:
       self.rows[pos].setStyles(head)
       pos += 1
   
    cnt = 0
    blen = len(body)
    for r in self.rows[pos:]:
      self.rows[pos].setStyles(body[cnt % blen])
      pos+=1
      cnt+=1
    


def GridFromList(header,body,hidden=[],colwidth=None,rowwidth=None,myid=None,cellspace=None,border=None,ExtraAttrStr=None):
  """Create a table from lists
  @param header A list of elements corresponding to the table header
  @param body A list of list of elements.  Each inner list is a single row in the table
  @param hidden A list of (name,list of elements) [same format as the body except the row is a (name, list) pair] that correspond to hidden rows (for use with javascript)
  """
  hasHeader = 0
  if header:
    numCol = len(header)
    hasHeader = 1
  elif body and body[0]:
    numCol = len(body[0])
  else:
    numCol = len(hidden)

  g = Grid(numCol,len(body)+hasHeader+len(hidden),colwidth=colwidth,rowwidth=rowwidth,myid=myid,cellspace=cellspace,border=border,ExtraAttrStr=ExtraAttrStr)
  
  y = 0
  if header:
    x = 0
    for h in header:
      g.idx[x][y].set(h)
      x +=1
    y += 1

  for row in body:
    x = 0
    for field in row:
      if field is None:
        g.cell(x,y).clear()  # If a None is explicitly passed, then do not have the <td/> -- this allows other cells to span...
      else: g.idx[x][y].set(field)

      x += 1
    y += 1

  for hiddenRow in hidden:
    if hiddenRow:
      (name,row) = hiddenRow
      x = 0
      rowHdr = g.row(y)
      rowHdr.styles['display'] = 'none'
      if type(name) is StringType:
        rowHdr.id = name
      else:
        TODO()
      for field in row:
        g.idx[x][y].set(field)
        x += 1
      y += 1

  return g


def Test():
  import pdb
  g = GridFromList(["First","Last"],[["Andrew", "Stone"],["Jane","Doe"],["joe","doe"]])
  g.RowBackground(Color(200,80,255),[Color(200,200,200),Color(240,240,240)])
#  pdb.set_trace()


  ct = ChunkTable(2,2,colwidth=["20%","80%"])
  ct[0][0].set("00")
  ct[0][1].set("01")
  ct[1][0].set("10")
  ct[1][1].set("11")

  ct1 = ChunkTable(2,2)
  ct1[0][0].set("00")
  ct1[0][1].set("01")
  ct1[1][0].set("10")
  ct1[1][1].set("11")
 
  ct2 = ["no header", GridFromList(None,[["Andrew", "Stone"],["Jane","Doe"],["joe","doe"]])]
  ct2[1].RowBackground(None,[Color(200,200,200),Color(240,240,240)])

  WriteFile('testtable.html',[g,ct,ct1,ct2,ChunkStr("The End")])

