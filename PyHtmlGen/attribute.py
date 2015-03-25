import random
import pdb

from htmldoc import *
from types import *
from attr import *
from chunk import *
from js import *
import imagehtml


def jsAnchor(jsFn,item):
  # http://blog.reindel.com/2006/08/11/a-hrefjavascriptvoid0-avoid-the-void/
  #return chunkTag('a', item,('href',"javascript:%s" % jsFn))
  return chunkTag('a',item,{'href':"#",'onclick':"%s;return false;" % str(jsFn)})

def anchor(html,item):
  return chunkTag("a", item,('href',html))

def bold(item):
  return chunkTag("strong", item)

def center(item):
  return chunkTag("center", item)

def img(name,myId=None):
  return chunkTag("img", None,('src',name),None,myId)

def color(col,item):
  if type(col) is TupleType:
    colStr = 'rgb(%d,%d,%d)' % (col[0], col[1], col[2])
  elif type(col) is StringType:
    colStr = col
  else:
    colStr = 'rgb(%d,%d,%d)' % (col.red, col.green, col.blue)

  return chunkTag("span", item,None,('color', colStr))

def bkcolor(col,item):
  if type(col) is TupleType:
    colStr = 'rgb(%d,%d,%d)' % (col[0], col[1], col[2])
  elif type(col) is StringType:
    colStr = col
  else:
    colStr = 'rgb(%d,%d,%d)' % (col.red, col.green, col.blue)

  return chunkTag("div", item,None,('background', colStr))



def italic(item):
  """Italicises a section of text"""
  return chunkTag("span", item,None,('font-style', 'italic'))

def underline(item):
  """Underlines a section of text"""
  return chunkTag("span", item, None, ('text-decoration','underline'))

def active(item,over=None,out=None,clickk=None):
  #  pdb.set_trace()
  if over:
    jsAction("onMouseover",over,item)
  if out:
    jsAction("onMouseout",out,item)
  if clickk:
    jsAction("onClick",clickk,item)
  return item

def action(item,actionName,act):
  #  pdb.set_trace()
  jsAction(actionName,act,item)
  return item

def hide(item):
  """Places the item in a hidden area of the html page
  @param item A ChunkBase-derivation that you want on the page but hidden
  @returns An object that should be included in the page
  """
  return AddHidden(item)

def hideHere(item):
  """Makes a hidden area of the page in this location
  @param item A ChunkBase-derivation that you want on the page but hidden
  @returns An object that should be included in the page
  """
  return Chunk(item,None,{"display":"none"})




#  if click:
#    click = " onClick=\"%s\"" % click
#  else: click = ""
#  return chunkTag("""<span onMouseover="%s" onMouseout="%s"%s> """ % (over,out,click), "</span>",item)

def setAttr(attr,val,domNode='this'):
  """An action that removes an attribute from the current (by default) node"""
  return "%s.setAttribute('%s','%s');" % (domNode,attr,val)

def remAttr(attr,domNode='this'):
  """An action that removes an attribute from the current (by default) node"""
  return "%s.removeAttribute('%s');" % (domNode,attr)

def setparentattr(attr,val):
  return "this.parentNode.setAttribute('%s','%s');" % (attr,val)

def actionHighlight(elem,col,duration):
  """Returns javascript to highlight the elem or elemId passed as elem as color col"""
  try:
    elemId = elem.id
  except:
    elemId = elem  
  return "highlight('%s','%s',%s)" % (str(elemId),str(col),duration)

def actionNormallight(elem):
  """Returns javascript to un-highlight the elem or elemId passed as elem as color col"""
  try:
    elemId = elem.id
  except:
    elemId = elem
  return "normallight('%s')" % str(elemId)


def resize(amt,item):
  """Change the size of an item (ie. <big> or <small>).  Use positive amt to get bigger, negative amt to get smaller"""
  if amt > 0:
    return chunkTag(amt * ["big"], item)
  if amt < 0:
    return chunkTag((-1*amt) * ["small"], item)
  else:
    assert(0)
    return item

def jsLink(href):
  return "parent.location='%s'" % href


class jsAction(chunkBuffer):
  def __init__(self,trigger,ActLst=None,content=None):
    chunkBuffer.__init__(self,ActLst)
    self.trigger = trigger
    self.content = content

    # Install this action as an attribute of the content for onclick, onmouseover, etc
    if not self.trigger == 'anchor':
      self.content.attrs[trigger] = self
      

  def gen(self,doc):
    jsd = doc.SubDoc()
    chunkBuffer.gen(self,jsd)
#    pdb.set_trace()    
    if self.trigger == 'anchor':
      # (auto added in HtmlSkel subdoc)      jsd.Insert(jsd.NewMarker("body"),Start,After)
      bod = jsAnchor(jsd,self.content)
    else:
      bod = jsd

    genDoc(doc,bod)
#    doc.Insert(bod,doc.body,Before)
      
      


class AddHidden:
  def __init__(self,item):
    self.item = item

  def gen(self,doc):
    doc.AddModule(jsModule,LocationBoth)
    doc.AddModule(showHideModule,LocationBoth)
    tmp = doc.body
    doc.body = doc.showhide
    genDoc(doc,self.item)
    doc.body = tmp
 
class AllowHighlighting():
   def gen(self,doc):
     doc.AddModule(jsModule)
     doc.AddModule(faderModule)
 

class MakeCollapsible():
  """Connect a button to collapse & expand a chunk.  This class should replace the button in the document, and the pane be placed independently whereever it is needed, by calling self.getPanel()"""
  def __init__(self,button,panel,action=None,initiallyShown=False):
    self.panel = Chunkify(panel,"collapsible")
    self.button = Chunkify(button)
    self.action = action if action is not None else "onClick"     
    self.button.setAttrs(self.action,"toggleShow('%s')" % self.panel.id)
    if not initiallyShown:
      if self.panel.styles.has_key("display"):  # If it already has a display style, store it as an attribute for use when shown (see the javascript)
        self.panel.setAttrs("actualdisplay", self.panel.styles["display"])
      self.panel.setStyles("display","none")

  def getPanel(self):
    return self.panel

  def gen(self,doc):
    doc.AddModule(jsModule,LocationBoth)
    doc.AddModule(showHideModule)
    genDoc(doc,self.button)

class MakeEditable(ChunkBase):
  """Transform text into an editable form input"""
  def __init__(self,item,bud,newId="",action=None):
    """Constructor
       @param item The piece of data (ChunkBase, string or number)  you want to be editable
       @param bud  A ChunkBase that is the prototype for the edit functionality (this DOM will be copied into the right place when the user clicks to edit)
       @param newId What should the ID of the new edit box be?
       @param action What event should trigger this to become editable?  Default is "onClick" 
    """
    chunkBase.__init__(self)
    self.bud = bud
    self.action = action if action is not None else "onClick"      
    self.item = item
    self.newId = newId

  def gen(self,doc):
    doc.AddModule(jsModule)
    doc.AddModule(makeEditableModule)
    if not type(self.item) is InstanceType:  # Put a div around it so I can set attributes
      self.item = Chunk(self.item)
    budid = self.bud if type(self.bud) is StringType else self.bud.id

    # Make the inner item get the attributes and styles of this MakeEditable
    self.item.attrs.update(self.attrs)
    self.item.styles.update(self.styles)
    assert(not (self.id and self.item.id))  # if both have an Id, we are in trouble because there's just one div
    if not self.item.id: 
      self.item.id = self.id
      self.item.forceId = self.forceId

    self.item.setAttrs(self.action,"this.removeAttribute('%s'); makeEditable(this,'%s','%s')" % (self.action,budid,self.newId))
    genDoc(doc,self.item)
 
  def __str__(self):
    pdb.set_trace()

class NewRow(chunkBase):
  """This class partners with GridFromList to allow you to dynamically add another row into a table.
     The new row will be a copy of the row labeled by the second parameter.  I call this row a "bud" because
     new rows grow from it.  For example:

     GridFromList([NewRow(Input(ButtonInput,"New"),"rowBud"),"Name","Address"],  # Header row
                  [ # A normal row
                    [Input(CheckboxInput,"Selected.${person.name}","${person.name}"),"${person.name}", "${person.value}"]], 
                    # The "bud"
                    [('rowBud',["",InputText("NewUser").setStyles("width","99%"),InputText("NewAddress").setStyles("width","99%")])]
)
  """
  def __init__(self,item,bud,action=None):
    chunkBase.__init__(self)
    self.bud = bud
    self.action = action if action is not None else "onClick"      
    self.item = item

  def gen(self,doc):
    doc.AddModule(jsModule)
    doc.AddModule(newRowModule)
    if not type(self.item) is InstanceType:  # Put a div around it so I can set attributes
      self.item = Chunk(self.item)
    budid = self.bud if type(self.bud) is StringType else self.bud.id
    self.item.setAttrs(self.action,"newRow(this,'%s')" % budid)
    genDoc(doc,self.item)
 
  def __str__(self):
    pdb.set_trace()


                
deadcode = r"""
class LinkShow:
  def __init__(self,item,target):
    self.item = item
    self.target = target

  def gen(self,doc):
    doc.Insert(["MoveContent('%s','%s')" % (self.item.id, self.target.id)],doc.body,Before)

    
class LinkHide:
  def __init__(self,item):
    self.item = item
  
  def gen(self,doc):
    doc.Insert(["MoveContent('%s','hidden')" % self.item.id],doc.body,Before)
"""    

class LinkSwap:
  def __init__(self,item,target):
    self.item = item
    self.target = target
    
  def gen(self,doc):
   doc.AddModule(jsModule)
   doc.AddModule(showHideModule)
   doc.Insert(["SwapContent('%s','%s','hidden')" % (self.item.id,self.target.id)],doc.body,Before)
     

  def __str__(self):
    return "SwapContent('%s','%s','hidden')" % (self.item.id,self.target.id)
    pdb.set_trace()

class DomCopy:
  def __init__(self,item,target,rem=True):
    self.item = item
    self.target = target
    self.remExisting = rem
    
  def gen(self,doc):
   doc.AddModule(jsModule)
   doc.AddModule(showHideModule)
   doc.Insert([self.__str__()],doc.body,Before)
     

  def __str__(self):
    if type(self.target) is StringType:
      tgtId = self.target
    else: tgtId = self.target.id

    if type(self.item) is StringType:
      itemId = self.item
    else: itemId = self.item.id

    return "CopyContent('%s','%s',%s)" % (itemId,tgtId,'true' if self.remExisting else 'false')


class LinkDelayLoad:
  def __init__(self,item,image):
    self.item  = item
    self.image = image

  def gen(self,doc):
    doc.AddModule(jsModule)
    doc.AddModule(delayLoadModule)
    self.image.save()  # In a delayed load, the image is never "generated" (ie gen() called), so we have to ensure that the image is output
    doc.Insert(["delayLoadImg('%s','%s');" % (self.item.id, self.image.name)],doc.body,Before)


# Attributes that apply themselves to Chunks

def BackImage(item, image,repeat="xy",stretch=None,fixed=False):
  sd = {}
  repeatXlat = {"xy": "repeat", "x":"repeat-x", "y":"repeat-y","":"no-repeat"}

  if stretch:
    if stretch[0]: sd["width"] = stretch[0]
    if stretch[1]: sd["height"] = stretch[1]
    sd['position'] = 'relative'
    sd['left'] = '0px'
    sd['top'] = '0px'
    sd['z-index'] = 0

  if fixed:
    sd["background-attachment"] = "fixed"

  if repeat:
    sd["background-repeat"] = repeatXlat.get(repeat,repeat)
  
  sd["background-image"] = "url('%s')" % imagehtml.ImagePathFixup(image) 

  return item.setStyles(sd)


def Test():
  import gen
  import document
  import table
  import form

  textbud = form.InputText("state","")
  textbud.setAttrs("style","width:100%")
  textbud.id = 'inpState'
 
  d = []

  grid = table.GridFromList([NewRow(form.Input(form.ButtonInput,"New"),"rowBud"), "Name","Email", "State"],[["","Andrew", "g.andrew.stone@gmail.com", MakeEditable("New Hampshire",textbud,'stateEntry','OnClick')]],[('rowBud',["",form.InputText("name","").setAttrs("style","width:100%"), form.InputText("email","").setAttrs("style","width:100%"), MakeEditable("mked",textbud,'stateEntry','OnClick')])])


  f = form.Form("formhandler",[grid,hide(textbud)])

  d.append(f)
 
  c = Chunk("content<br/>" * 10, myId="hiTest")
  b1 = Chunk("Red Highlight")
  b2 = Chunk("Blue Highlight")
  b3 = Chunk("Back to Default")
  action(b1,"onClick",actionHighlight("hiTest","#FF8040",5000))
  action(b2,"onClick",actionHighlight("hiTest","steelblue",10000))
  action(b3,"onClick",actionNormallight("hiTest"))
  
  d.append([b1,b2,b3,c])
  d.append(AllowHighlighting())

  gen.WriteFile("testattribute.html",d)
