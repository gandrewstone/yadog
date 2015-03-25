from gen import *
from chunk import *
from document import *
from attribute import *
from template import *

import pdb
import copy
from types import *

#class MenuItem:
#  def __init__(self, text, whenclicked):

# Send a list of items, this wraps it in code that will change the foreground color when the mouse goees over it.
# the list of items is either just the item or (item,onclickaction)
def activeHighlightItems(items,onCol,offCol):
  result = []
  if type(items[0]) == type(()):
    #print "PAIR", items[0][1]
    result = [ active(Span(x[0]),setAttr("style","color: %s" % onCol),setAttr("style","color: %s" % offCol), [x[1]] ) for x in items]
  else:    
    result = [ active(Span(x),setAttr("style","color: %s" % onCol),setAttr("style","color: %s" % offCol) ) for x in items]
  print result
  return result

def activeStyleItemsSpan(items,onStyle,offStyle,func=setAttr):
  result = []
  if type(items[0]) == type(()):
    #print "PAIR", items[0][1]
    result = [ active(Span(x[0]),func("style",onStyle),func("style",offStyle), [x[1]] ) for x in items]    
  else:
    result = [ active(Span(x),func("style",onStyle),func("style",offStyle) ) for x in items]
  print result
  return result

def activeStyleItems(items,onStyle,offStyle,func=setAttr):
  result = []
  for i in items:
    if type(i) == type(()): 
      shown = i[0]
      lnk = [i[1]]
    else:
      shown = i
      lnk = None

    if isInstanceOf(i,ChunkBase): wrapper = shown
    else: wrapper = Span(shown)

    result.append(active(wrapper,func("style",onStyle),func("style",offStyle), lnk ))

  #print result
  return result




class VerticalList(Block):
  def __init__(self, items,selAttr=None,myId="VerticalList"):
    Block.__init__(self,myId,None,None,"relative")
    self.suppressBody = true # Turn off the Block's automatic div creation because we have another block
    self.sel = selAttr
    self.lst = chunkBuffer()
    self.menu = chunkTag(["div","ul"],self.lst,('id',self.id))
    for i in items:  #(text, item) in items:
      if type(i) is TupleType:  # Allow either (text,item) or just text
        text = i[0]
        item = i[1]
      else:
        text = i
        item = None
      tg = chunkTag("li",text)
      if isInstanceOf(text,Template):
        text.apply(tg)
      self.lst.append(tg)
      if type(item) == type([]):
        self.lst.append(VerticalList(item,copy.deepcopy(self.sel)))
        

    if self.sel:
      print "selAttr ", self.sel
      tmp = self.lst[0]
      print self.lst[0]
      self.lst[0] = copy.deepcopy(self.sel)
      self.lst[0].setrec(tmp)  # For now, put the selection on the first item
      

  def gen(self,doc):
    Block.gen(self,doc)
    genDoc(doc, self.menu)
 

class VerticalMenu(Block):
  def __init__(self, items,selAttr=None,submenufn=None,itemfn=None,myId="VerticalMenu",depth=0 ):
    Block.__init__(self,myId,None,None,"relative")
    self.submenufn = submenufn if submenufn else lambda x,y: y
    self.itemfn = itemfn if itemfn else lambda x,y: y
    self.suppressBody = True # Turn off the Block's automatic div creation because we have another block
    self.sel = selAttr
    self.lst = chunkBuffer()
    self.menu = chunkTag(["div"],self.lst)
    self.menu.id = self.id
    for i in items:  #(text, item) in items:
      if type(i) is TupleType:  # Allow either (text,item) or just text
        text = i[0]
        item = i[1]
      else:
        text = i
        item = None

      tg = self.itemfn(depth,text) #chunkTag("center",text)
      if isInstanceOf(text,Template):
        text.apply(tg)
      self.lst.append(tg)
      if type(item) == type([]):
        v = VerticalMenu(item,copy.deepcopy(self.sel),self.submenufn,self.itemfn,myId+text,depth+1)
        self.lst.append(self.submenufn(depth, v))
        

    if self.sel:
      print "selAttr ", self.sel
      tmp = self.lst[0]
      print self.lst[0]
      self.lst[0] = copy.deepcopy(self.sel)
      self.lst[0].setrec(tmp)  # For now, put the selection on the first item

  def item(self,idx):
    "Return the nth menu item"
    return self.lst[idx]      

  def gen(self,doc):
    # Push any attributes and styles set on me to the first generated block, because suppressBody is true
    self.menu.attrs.update(self.attrs)
    self.menu.styles.update(self.styles)
    Block.gen(self,doc)
    genDoc(doc, self.menu)
 
       

class HorizList(chunkBuffer):
  def __init__(self, items,selAttr=None, separator = None,myId=None):
    chunkBuffer.__init__(self)
    self.id  = myId
    self.sel = selAttr
    count = 0
    for i in items:  #(text, item) in items:
      if type(i) is TupleType:  # Allow either (text,item) or just text
        text = i[0]
        item = i[1]
      else:
        text = i
        item = None

      if separator is not None and count>0: self.append(separator)
      self.append(text)
      if type(item) == type([]): #TODO, add a popup drop down menu
        pass
      count += 1
    

# class HorizTable:


  

def Test():
            
  vdef = VerticalList([('Home',None),('Art',None),('Code',[('C/C++',None),('Python',None)]),('Woodworking',None) ],color(Color(255,0,100),bold(None)),  )

  vdef1 = VerticalList([(x,None) for x in activeHighlightItems(['Home','Art','Code','Woodworking' ], Color(255,0,200), Color(50,50,50) )]  )

  v3 = VerticalMenu([('Home',None),('Art',None),('Code',[('C/C++',None),('Python',None)]),('Woodworking',None) ],None,lambda depth,x: resize(-1,x)  )


  v4 = VerticalMenu([('Home',None),('Art',None),('Code',[('C/C++',None),('Python',None)]),('Woodworking',None) ],None,lambda depth,x: resize(-1,italic(x))  )

  ah = lambda x: activeHighlightItems(x,Color(255,0,200), Color(50,50,50))
  i = ah(['Home','Art','Code','C/C++','Python','PyHtmlGen','Woodworking'])
  v5 = VerticalMenu([(i[0],None),(i[1],None),(i[2],[(i[3],None),(i[4],[(i[5],None)])]),(i[6],None) ],None,lambda depth,x: resize(-1,italic(x))  )

  ah = lambda x: activeStyleItems(x,"color:rgb(0,255,0); font-weight: bold; text-transform: uppercase;", "color:rgb(0,0,0)")
  i = ah(['Home','Art','Code','C/C++','Python','PyHtmlGen','Woodworking'])
  v6 = VerticalMenu([(i[0],None),(i[1],None),(i[2],[(i[3],None),(i[4],[(i[5],None)])]),(i[6],None) ],None,lambda depth,x: resize(-1,italic(x))  )

  ah = lambda x: activeStyleItems(x,"color:rgb(0,255,0); font-size: 150%; ", "")
  i = ah(['Home','Art','Code','C/C++','Python','PyHtmlGen','Woodworking'])
  v7 = VerticalMenu([(i[0],None),(i[1],None),(i[2],[(i[3],None),(i[4],[(i[5],None)])]),(i[6],None) ],None,lambda depth,x: resize(-1,italic(x))  )

  # I can add a link by specifying an "onclick" action for each item
  ah = lambda x: activeStyleItems([(y,jsLink("testmenuregress.html")) for y in x],"color:rgb(0,0,255); padding: 5px; border: solid; border-width: thin; width: 95%", "")
  i = ah(['Home','Art','Code','C/C++','Python','PyHtmlGen','Woodworking'])
  v8 = VerticalMenu([(i[0],None),(i[1],None),(i[2],[(i[3],None),(i[4],[(i[5],None)])]),(i[6],None) ],None,lambda depth,x: resize(-1,italic(x))  )

  # I can add a link using an anchor
  ah = lambda x: activeStyleItems([anchor("testmenuregress.html",y) for y in x] ,"background:rgb(50,50,50); color:white;", "")
  i = ah(['Home','Art','Code','C/C++','Python','PyHtmlGen','Woodworking'])
  v9 = VerticalMenu([(i[0],"{url home}"),(i[1],None),(i[2],[(i[3],None),(i[4],[(i[5],None)])]),(i[6],None) ],None,lambda depth,x: resize(-1,italic(x))  )


  hdef2 = HorizList(
                     [(x,None) for x in activeHighlightItems(['Home', 'Art', 'Code', 'Woodworking' ],
                                                             Color(255,0,200),
                                                             Color(50,50,50) )],color(Color(255,0,100),bold(None))
                     )
   
#  hdef2 = HorizList(color(Color(255,0,100),bold(None)),[(x,None) for x in ['Home','Art','Code','Woodworking' ]] )

  mall = ChunkBuffer([vdef,vdef1,v3,hdef2,v4,v5,v6,v7,v8,v9])

  doc = HtmlSkel()
  mall.gen(doc)
  doc.Insert([chunkStr(BR+BR+"\n\n\n")],doc.body,Before)

  print str(doc)
  file = open('testmenuregress.html','w')
  file.write(str(doc))
  file.close
  
