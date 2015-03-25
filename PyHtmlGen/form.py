from types import *

from gen import *
from chunk import *
from document import *

class Form(chunkTag):

  def __init__(self,action, contents,myId=None):
    chunkTag.__init__(self,"form",myId=myId)
    self.attrs['method'] = 'POST'
    self.attrs['enctype'] = 'multipart/form-data'
    self.attrs['action'] = action

    self.infix = contents

#  def gen(self,doc):
#    #pre = "<form %s>" % self.attrStr()
#    suf = "</form>"
#    self.genOpenTag(doc,"form")
#    genDoc(doc,[self.contents,suf])


FileInput = "file"
TextInput = "text"
#TextAreaInput  = "TEXTAREA"

ButtonInput = "button"
CheckboxInput = "checkbox"
ButtonSubmit = "submit"

class Input(ChunkTag):
  """Creates any html 'Input' style widget"""
  def __init__(self,typ,name,value=None):
    chunkTag.__init__(self,"input")
    self.attrs['type'] = typ
    self.attrs['name'] = name
    if value is not None:
      self.attrs['value'] = value
    else:
      self.attrs['value'] = name

#  def gen(self,doc):
#    for m in self.modules: doc.AddModule(m)
#    self.genOpenTag(doc)

  def SetDisabled(self,tf=True):
    """Make this input grayed out and not useable"""
    attr = 'disabled'
    if tf:
      self.setAttrs(attr, attr)
    else:
      if self.attrs.has_key(attr):
        del self.attrs[attr]
    return self

class TextArea(Input):
  """Creates block text entry"""
  def __init__(self,name,contents="",cols=80,rows=25):
    Input.__init__(self,None,name,None)
    self.tag[0] = "textarea"  # override the tag specced in the Input base class
    self.setAttrs({"rows":rows,"cols":cols})
    self.infix = " "  # Force html 1.0
        


class InputButton(Input):
  """Creates a button"""
  def __init__(self,name,default=None):
    if default is None: default = ""
    else: default = str(default)
    Input.__init__(self,ButtonInput,name,default)

  
class InputText(Input):
  """Creates a textbox"""
  def __init__(self,name,default=None):
    if default is None: default = ""
    else: default = str(default)
    Input.__init__(self,TextInput,name,default)

class InputCheck(Input):
  """Creates a checkbox"""

  def __init__(self,name,default=None):
    Input.__init__(self,CheckboxInput,name)
    if type(default) == StringType:
      if default[0] in ["t","T"]:
        self.attrs['checked'] = ""
    else:
      if default: self.attrs['checked'] = ""

class Select(chunkTag):
  """Creates a Combo-box"""

  def __init__(self,name,items, attrs=None, styles=None, myId=None, optionAttrs={},optionStyles=None):
    self.items = []
    self.itemDict = {}
    if type(items) is DictType:
      items = items.items()
      items.sort()    
 
    for i in items:
      iname = None
      if type(i) is TupleType or type(i) is ListType:
        ct = ChunkTag("option", i[1],{"value":i[0]}.update(optionAttrs),optionStyles)
        if len(i) > 2 and (i[2] == True or i[2] == "selected"):
          ct.setAttrs("selected","selected")
        iname = i[0]
      elif isInstanceOf(i, ChunkBase):
        ct = i
      else:
        ct = ChunkTag("option", str(i),{"value":str(i)})
        iname = str(i)
      if ct:
        self.items.append(ct)
        if iname: self.itemDict[iname] = ct 

    chunkTag.__init__(self,"select",self.items,{'name':name},None,myId)

    

  def SetNumRowsToShow(self,rows): 
    self.setAttr('size', rows)
    return self

  def SetMultiple(self,tf = True): 
    attr = 'multiple'
    if tf:
      self.setAttrs(attr, attr)
    else:
      if self.attrs.has_key(attr):
        del self.attrs[attr]
    return self
  
  def SetDisabled(self,tf=True):
    attr = 'disabled'
    if tf:
      self.setAttrs(attr, attr)
    else:
      if self.attrs.has_key(attr):
        del self.attrs[attr]
    return self



def Test():
  import htmldoc
  doc = htmldoc.HtmlSkel()

  f1 = Form("/formhandler",["Simple form",Input(ButtonSubmit,"button","press me"),"file:",Input(FileInput,"upload"),"Text:",Input(TextInput,"words"), Select("sel",["a","b","c"]),Select("sel2",[("a",ChunkTag("big","A"),True),"b","c"]),Select("sel2",{"a":ChunkTag("big","A"),"b":"b","c":"c"}),
Select("sel2",[ChunkTag("option","A")])  ])

  all = chunkBuffer([f1])

  all.gen(doc)
                     
  print str(doc)

  file = open('formtest.html','w')
  file.write(str(doc))
  file.close
  
