import pdb
from types import *

from gen import *
from attr import *

from document import *
#import htmldoc

class ChunkBase:
  def __init__(self):
    ChunkBase.clear(self)

  def clear(self):
    self.styles = {}
    self.attrs  = {}
    self.cssClass  = None
    self.id     = None  # If id remains None, then the style will be inline; otherwise it will be put in the style sheet
    self.forceId = False
    self.modules = set()

  def getId(self):
    """? Get this chunk's id.  This function will return this chunk's id, generating one if necessary"""
    self.forceId = True
    if self.id is None:
      self.id = GenUniqueId("i")
    return self.id

  def setModules(self,mods):
    if type(mods) is not ListType: mods = [mods]

    for m in mods:
      self.modules.add(m)
    return self

  def setAttrs(self,k,v=None):
    """Set the attributes of this xml tag
       @param k key string or dictionary of key/value pairs
       @param v value string (if k is a string) or None
       @return self, so you can use this inline (i.e. foo(NewObj().setAttrs(...).setStyles(...).setClass(...)))
    """
    if k is None: return self
    elif type(k) is DictType:
      self.attrs.update(k)
    elif type(k) is ListType:
      for (key,val) in k:
        self.attrs[str(key)] = val
    else:
      self.attrs[str(k)] = v
    return self

  def setActive(self,over=None,out=None,clickk=None):
    """Set the "active" (onMouse-- over, out and OnClick) attributes of this chunk"""
    if over:
      self.setAttrs("onMouseover",over)
    if out:
      self.setAttrs("onMouseout",out)
    if clickk:
      self.setAttrs("onClick",clickk)
    return self

  def setClass(self,cssclass):
    """Set the CSS class of this entity
       @param cssclass String or ChunkClass object
       @return self, so you can use this inline (i.e. foo(NewObj().setAttrs(...).setStyles(...).setClass(...)))
    """
    self.cssClass = cssclass
    return self

  def setStyles(self,k,v=None):
    """Set the styles of this xml tag
       @param k key string or dictionary of key/value pairs
       @param v value string (if k is a string) or None
       @return self, so you can use this inline (i.e. foo(NewObj().setAttrs(...).setStyles(...).setClass(...)))
    """
    if k is None: return self
    if type(k) is DictType:
      self.styles.update(k)
    if type(k) is ListType:
      for (key,val) in k:
        self.styles[str(key)] = val
    else:
      self.styles[str(k)] = v
    return self

  def setLoc(self,loc):
    loc.setStyle(self.styles)

  def styleStr(self):
    if len(self.styles) == 0: return ""
    s = ""
    for (name,val) in self.styles.items():
      if val is not None:
        s += "%s:%s; " % (name,val)
    return s

  def attrStr(self):
    """Return all of the attributes as a single string ready to be put into html"""
    if len(self.attrs) == 0: return ""
    s = ""
    for (name,val) in self.attrs.items():
      val = self.attrFixup(name,val)
      s += ' %s="%s"' % (name,val)
    return s

  def attrFixup(self,name,val):
    """Fix common mistakes when specifying well known attributes, and make defaults explicit"""
    if name in ['width','height']:  # Convert an integer into a pixel count
      if type(val) is type(int):
        return "%dpx" % val
    return str(val)


chunkBase = ChunkBase



class chunkCnxn:
  "Usually chunks generate their strings in place -- that is, where they actually are in the heirarchy.  This chunk indicates that the string should be placed somewhere else in the heirarchy.  For example, this is used to put content up in a main window when a menu item is clicked"
  def __init__(self,cnxn,item=None):
    self.item = item
    self.cnxn = cnxn
  
  def set(self,obj):
    self.item = obj

  def connect(self):
    "Used internally during page generation to put the content in the right spot for generation of a particular file"
    self.cnxn.set(item)
  
  def item(self):
    if self.item: return self.item.item()
    return self
  
  def __str__(self):
    assert(0)
    
  

class chunkNoShow:
  "Used to fill various variables, so I do not have to be doing if var is not None: blah.  But the str() display fn should never be called"
  def __init__(self):
    pass
  def set(self,obj):
    pass
  
  def item(self):
    return self

  def gen(self,doc):
    assert(0)
  
  def __str__(self):
    assert(0)


class chunkRecurse:
  """A class that simply holds a chunk item.  Used as a place holder because the contained item can be modified."""
  def __init__(self,item=None):
    self.rec = item

  def set(self,obj):
    self.rec = obj

  def item(self):
    if self.rec: return self.rec.item()
    return self

  def gen(self,doc):
    if self.rec: genDoc(doc,self.rec)
    
  def genJsonDom(self):
    return genJsonDom(self.rec)

  def __str__(self):
    if self.rec: return str(self.rec)
    else: return ""
  

class ChunkStr:
  "This is a piece of the buffer that is a string"
  ctype = "chunkStr"
  def __init__(self,s=None):
    self.ctype = chunkStr.ctype
    if s==None: self.str = ""
    else: self.str = s

  def item(self):
    return self   

  def gen(self,doc):
    genDoc(doc,[self.str])
    
  def __str__(self):
    if self.str==None: return ""
    return self.str

chunkStr = ChunkStr

class ChunkTag(ChunkBase):
  "This is a piece of the buffer that has a prefix, center (infix), and postfix.  The center can be set l8r"
  ctype = "chunkTag"
  def __init__(self,tag, infix = None,attrs=None,styles=None,myId=None):
    """ Initialization
        @param tag  A string or a list of strings (use the list to efficiently jam in a set of nested tags -- only the outermost gets the attributes and styles).
        @param infix Tag contents/children, or list of children
        @param attrs HTML attributes
        @param styles HTML styles
        @param myId id=blah attr
    """
    ChunkBase.__init__(self)
    self.id = myId
    for (k,v) in PairIterator(attrs):
      self.attrs[k] = v
    for (k,v) in PairIterator(styles):
      self.styles[k] = v

    self.ctype   = chunkTag.ctype
    if type(tag) is StringType:
      self.tag = [tag]
    else:
      self.tag  = tag

    self.infix = infix
#    if infix == None: self.infix = ""
#    else:             self.infix = infix

  def clear(self):
    """Blows away this tag.  Removing a tag is useful because you can create a big standard object (like a table) and then remove the parts you don't want (use clear())
    """
    ChunkBase.clear(self)
    self.infix = None
    self.tag   = None

  def inject(self,something):
    """Stick some other object in the parent-child hierarchy, so we now get parent-something-child.
       @param something a function that takes the child and will generate the stuff to be inserted
    """
    self.infix = something(self.infix)    

  def setBkg(self,imgcol):
    """?? Sets a background image or color within this block
    """
    if type(imgcol) == type(""):
      self.styles["background-image"] = "url('%s')" % bkimg
    else:
      self.styles["background-color"] = imgcol

  def set(self, obj):
    self.infix = obj

  def setrec(self,obj):
    if self.infix:
      self.infix.setrec(obj)
    else:
      self.infix = obj

  def item(self):
    if self.infix: return self.infix.item()
    return self

  def genTags(self,doc):

    # If tag is None, then don't generate anything -- used to blow away a tag.
    # Removing a tag is useful because you can create a big standard object (like a table) and then remove the parts you don't want (use clear())
    if self.tag is None: return (None,None)

    styleStr = self.styleStr()

    if self.id is not None:  # if there is an Id, put the styles in the stylesheet
      if len(styleStr)>0:  # no point to put an entry in CSS if there are no styles
        doc.Insert("#%s {%s}\n" % (self.id, styleStr), doc.style, Before) 
      styleStr = r' id="%s"' % self.id
    else:  # Put the style inline
      if len(styleStr)>0:
        styleStr = ' style="%s"' % styleStr

#    if len(styleStr)>0: # No point for an ID if there are no styles
#      if doc is not None and self.id is not None:  # if there is an Id, put the styles in the stylesheet
#        doc.Insert("#%s {%s}\n" % (self.id, styleStr), doc.style, Before) 
#        styleStr = "id='%s'" % self.id
#      else:  # Put the style inline
#        styleStr = "style='%s'" % styleStr

    classStr=""
    if self.cssClass: 
      classStr = ' class="%s"' % str(self.cssClass)
      self.cssClass.gen(doc)

    prefix = []
    postfix = []
    num = 0
    for t in self.tag:
      num += 1
      if num == 1: prefix.append("<%s%s%s%s>" % (t,self.attrStr(),styleStr,classStr))  # Only the first tag gets attrs and styles
      else: prefix.append("<%s>" % t)
      postfix.append("</%s>" % t)

    postfix.reverse()
    
    return (prefix,postfix)    

  def genOpenTag(self,doc,finisher=" /",tag=None):
    if not tag: tag = self.tag

    if tag is not None:  # If tag is None, then don't generate anything -- used to blow away a tag during some modifications
      styleStr = self.styleStr()

      if self.id is not None:  # if there is an Id, put the styles in the stylesheet
        if len(styleStr)>0:  # no point to put an entry in CSS if there are no styles
          doc.Insert("#%s {%s}\n" % (self.id, styleStr), doc.style, Before) 
        styleStr = " id='%s'" % self.id
      else:  # Put the style inline
        if len(styleStr)>0:
          styleStr = " style='%s'" % styleStr

      classStr=""
      if self.cssClass: 
        classStr = ' class="%s"' % str(self.cssClass)
        self.cssClass.gen(doc)

      genDoc(doc,["<%s%s%s%s%s>" % (tag[0],self.attrStr(),styleStr,classStr,finisher)])


  def gen(self,doc):
    for m in self.modules: doc.AddModule(m)

    if self.infix is None and self.tag is not None and len(self.tag)==1: # create a pre-closed tag
      self.genOpenTag(doc)
    else:
      (prefix, postfix) = self.genTags(doc)
      genDoc(doc,[prefix, self.infix, postfix])

  def __str__(self):
#     assert(0)  # This is screwed up due to circular ref betw chunk and htmldoc
     d = DocSections()  # Create a dummy doc to put out-of-band generated stuff into
     (prefix, postfix) = self.genTags(d)
     if self.infix:
      return "".join(prefix) + str(self.infix) + "".join(postfix)
     else:
       return "".join(prefix) + "".join(postfix)

  def genJsonDom(self):
    children  = genJsonDom(self.infix)    
    attrs     = {}
    styleStr  = self.styleStr()

    for (k,v) in self.attrs.items():
      attrs[k] = str(v)

    if styleStr:
      attrs["style"]=styleStr

    prev = None
    for t in self.tag:
      if prev==None: 
        prev = ret = {"tag":str(t), "attrs": attrs, 'children': children}
      else: 
        prev['children'] = {"tag":str(self.tag),"attrs":None}

    return ret


chunkTag = ChunkTag

class Chunk(ChunkTag):
  def __init__(self, contents,attrs=None,styles=None,myId=None):
    ChunkTag.__init__(self,"div",contents,attrs,styles,myId)
    if myId: self.forceId = True # If he specified an id, its a good bet it should definately be overwritten

class Span(chunkTag):
  """?? Creates a 'span' tag.
  This class implements a span object tag.  A span is like a div but it does not break the line.
  <see> <ref>Chunk</ref> </see>
  """
  def __init__(self,contents=None,attrs=None,styles=None,myId=None,loc=None):
    """?? Create a span object.
    <arg name='contents'> The inside of the tag. A string, list, or chunkBase derived class.</arg>
    <arg name='loc'> The location. See <ref>location</ref></arg>
    """
    ChunkTag.__init__(self,"span",contents,attrs,styles,myId)
    if myId: self.forceId = True # If he specified an id, its a good bet it should definately be overwritten
    self.loc      = loc

    if debugShowTableEdges:
      self.styles["border-style"] = "dotted"

  def setLoc(self,loc):
    assert(0) # Deprecated
    self.loc = loc
      
  def oldgen(self,doc):
    for m in self.modules: doc.AddModule(m)

    sty = self.styleStr() + strChk(self.loc)

    if sty is not "":
      if self.id:
        doc.Insert("#%s { %s }\n" % (self.id, sty),doc.style,Before)
        sty = Kv('id',self.id)
      else:
        sty = Kv('style',sty)
      

    doc.Insert(["<span %s %s>" % (sty,self.attrStr())],doc.body,Before)
    if self.contents:
      genDoc(doc, self.contents)
    doc.Insert(["</span>"],doc.body,Before)



class chunkBuffer(chunkBase):
  "This is a list of chunks that can either be chunkStrs or chunkBuffers"
  def __init__(self,lst=None):
    chunkBase.__init__(self)
    if lst is None:
      self.buf = []
    else: self.buf = lst

  def append(self,obj):
    self.buf.append(obj)

  def set(self,obj):
    self.buf.append(obj)

  def clear(self):
    self.buf = []
    
  def item(self,idx=None):
    if idx is None: return self
    else: return self.buf[idx]

  def gen(self,doc):
    for m in self.modules: doc.AddModule(m)
    # If attributes or styles were added then we have to make a div, otherwise we can skip it
    if len(self.attrs) or len(self.styles):
      styleStr = self.styleStr()
      if not styleStr == "":
        if self.id is not None:  # if there is an Id, put the styles in the stylesheet
          doc.Insert("#%s {%s}\n" % (self.id, styleStr), doc.style, Before) 
          styleStr = "id='%s'" % self.id
        else:  # Put the style inline
          styleStr = "style='%s'" % styleStr
      genDoc(doc,["<div %s %s>" % (self.attrStr(),styleStr),self.buf,"</div>"])
    else:
      genDoc(doc,self.buf)

  def genJsonDom(self):
    return genJsonDom(self.buf)


  def __getitem__(self,idx):
    return self.buf[idx]

  def __setitem__(self,idx,item):
    self.buf[idx] = item
    return self.buf[idx]

  def __str__(self):
    ret = ""
    for c in self.buf:
      ret += (str(c))

    return ret
    
ChunkBuffer = chunkBuffer

class Place(ChunkBase):
  def __init__(self,loc=None,myId=None):
    ChunkBase.__init__(self)
    self.id = myId if myId else GenUniqueId("Place")
    self.contents = None
    self.loc = loc
    
  def gen(self,doc):
    for m in self.modules: doc.AddModule(m)
    if self.loc: loc = self.loc
    else:        loc = ""
    
    s = "#%s { position:relative ;%s}\n" % (self.id, loc)

    doc.Insert([s],doc.style,Before)

    doc.Insert(["<div %s>" % Kv('id',self.id)],doc.body,Before)
    if self.contents:
      genDoc(doc, self.contents)
    doc.Insert(["</div>"],doc.body,Before)
   

class Block(chunkBase):
  def __init__(self,IdPfx, loc, contents=None, posStyle="absolute", overflow="auto", bkcol="transparent",bkimg=None):
    chunkBase.__init__(self)
    if not IdPfx: IdPfx = "Block"
    self.id       = GenUniqueId(IdPfx)
    self.loc      = loc
    self.suppressBody = false  # Derived classes should set this to true if they will create the body
    assert(posStyle in ['inherit','static','fixed','absolute','relative'])
    assert(overflow in ['inherit','visible','auto','hidden','scroll'])

    if debugShowTableEdges:
      self.styles["border"] = "1px solid %s" % Color(0,0,0).Randomize()
    else:
      self.styles["border"] = "0px none"
      
#      self.styles["border-style"] = "dashed"
#      self.styles["border"] = 2
  
    self.styles["position"] = posStyle
    self.styles["overflow"] = overflow
    self.styles["background-color"] = bkcol
    if bkimg:
      self.styles["background-image"] = "url('%s')" % bkimg
      
    self.content = contents

  def setBkg(self,imgcol):
    if type(imgcol) == type(""):
      self.styles["background-image"] = "url('%s')" % bkimg
    else:
      self.styles["background-color"] = imgcol

  def SetScrollBars(self,on=1):
    if on:
      self.styles["overflow"] = "scroll"
    else:
      self.styles["overflow"] = "hidden"

  def setLoc(self,loc):
    self.loc = loc

  def set(self,item):
    self.content = item
      
  def gen(self,doc):
    for m in self.modules: doc.AddModule(m)
    # If overflow is hidden, make sure that the clipping area is set. Set it to the entire block, if it wasn't explicitly specified.
    if self.styles["overflow"] == "hidden":
      noOvr(self.styles,[("clip","auto")])
          
    if not self.suppressBody:
      doc.Insert([chunkStr("#%s { %s %s }\n" % (self.id, self.styleStr(),strChk(self.loc)))],doc.style,Before)    
      doc.Insert(["<div %s %s>" % (Kv('id',self.id),self.attrStr())],doc.body,Before)
      if self.content:
        genDoc(doc, self.content)
      doc.Insert(["</div>"],doc.body,Before)




def Chunkify(item,idPfx=None,kind=None):
  """Turn this item into a derivation of ChunkBase, if and only if it is not already one.
  @param item  The item you want converted
  @parem idPfx Set to the string id if you want to force the item to have and ID
  @param kind  Set to a function that generates a ChunkBase derivation (contained item is first parameter) if you don't want DIV wrapped around the item.
  @returns The new item 
  """
  if isInstanceOf(item,ChunkBase): c = item
  elif kind is None: 
    if type(item) is ListType:
      c = ChunkBuffer(item)
    else:
      c = Chunk(item)
  else: c = kind(item)

  if c.id is None: 
    c.id = genUniqueId(idPfx)
    c.forceId = True
  return c

def FixupLen(listOfLens):
  "Takes a list of (One of {None,length,int}, and default value which is an int or length) and converts this into a list of items of type length.  The conversion alg is what you'd expect: type length is unchanged, int -> length as a %, None -> default value (as a length if it isn't) "
  ret = []
  for (x,default) in listOfLens:
    if x is None:
      x = default
      
    if type(x) == type(0):
      x = length(x)
      
    ret.append(x)
    
  return ret
      

def genDoc(doc,lst):
  return doc.genDoc(lst)

def genJsonDom(item):
  if type(item) is ListType:
    if len(item):
      return [genJsonDom(x) for x in item]
    else: return None
  if type(item) is StringType:
    return item
  if item is None: return None
  if type(item) is InstanceType:
    if "genJsonDom" in dir(item):
      return item.genJsonDom()
  pdb.set_trace()
  raise TypeError

  


def unused1():
  if type(lst) != type([]): lst = [lst]  # change into canonical form

  for item in lst:
    if type(item) == type(lst): # handle recursive lists
      genDoc(doc,item)
    elif type(item) is InstanceType:
      if "gen" in dir(item):
        item.gen(doc)
      elif "__str__" in dir(item):
        print "WARNING: __str__ function depreciated in favor of gen in object: ", item, "\n"
        doc.Insert([chunkStr(str(item))],doc.body,Before)
      else:
        raise AttributeError, "Obj: %s has neither a gen or __str__ function, so it cannot be converted into html." % item        
    elif item is not None:  # A "simple" item just gets converted to a string and then output
      doc.Insert([chunkStr(str(item))],doc.body,Before)
      
      
  


  """
  for item in lst:
    try:
      if type(item) == type(lst): # handle recursive lists
        genDoc(doc,item)
      else:
        item.gen(doc)
    except AttributeError,arg:  # if it doesn't have gen function then try to turn it into a string & put in the default location, the body
      print "EXCEPTION:", arg
      if item is not None:
        doc.Insert([chunkStr(str(item))],doc.body,Before)
  """ 




def Test():
  import js
  from htmldoc import HtmlSkel

  doc = HtmlSkel()

  b1 = Block(None,location(top,left,length(5),length(10),length(20),length(30),1),10*((5*"contents ") + BR),"fixed","scroll","red","images/clear.png")
  b1.gen(doc)

  genDoc(doc,["foo",1,ChunkTag("center","foo"),Chunk(chunkStr("bar")).setClass(ChunkClass("testclass").setStyles("background","red")),chunkBuffer([chunkStr("<div>"),"</div>","center"])  ])

  doc1 = HtmlSkel()
  doc1.AddModule(js.jsModule)
  doc1.AddModule(js.showHideModule)
  print "\n\n", str(doc), str(doc1)

  file = open('testchunk.html','w')
  file.write(str(doc))
  file.close

  
#  class Block(chunkBase):
#  def __init__(self,loc, posStyle, overflow="clip", bkcol="transparent",bkimg=None, contents=None):
#  class location:
#  def __init__(xref,yref,x,y,len, wid, z = 0):


"""
class Delimiter(chunkBase):
  def __init__(self, loc, contents=None):
    chunkBase.__init__(self)
    self.id       = GenUniqueId("Delimiter")
    self.setLoc(loc)
    self.content  = contents

  def set(self,item):
    self.content = item
      
  def gen(self,doc):
    # If overflow is hidden, make sure that the clipping area is set. Set it to the entire block, if it wasn't explicitly specified.
    if self.styles.has_key("overflow") and self.styles["overflow"] == "hidden":
      noOvr(self.styles,[("clip","auto")])
          
    doc.Insert(["#%s { %s }\n" % (self.id, self.styleStr())],doc.style,Before)    
    doc.Insert(["<div id=%s>" % self.id],doc.body,Before)
    if self.content:
      genDoc(doc, self.content)
    doc.Insert(["</div>"],doc.body,Before)

def FullHeight(contents):
  return Delimiter(locSize("auto",centPercent))
def FullWidth(contents):
  return Delimiter(locSize(centPercent,"auto"))
def FullSize(contents):
  return Delimiter(locSize(centPercent,centPercent))
"""
