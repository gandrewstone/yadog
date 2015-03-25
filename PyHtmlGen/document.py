from types import *
import pdb
#import dbg
#from GasTypes import *
#from token import *

class Recurse(Exception):
  def __init__(self,item):
    Exception.__init__(self)
    self.item = item

class Marker:
    ctype = "Marker"
    def __init__(self,name):
      self.name = name

    def __str__(self):
      return ""  # Return nothing so the markers are not output as text in the document

    def __repr__(self):
      return "<PyHtmlGen.document.Marker instance %s>" % self.name

Start = Marker("Start")
End   = Marker("End")

After   = 0
Before  = 1
Replace = 2



class Doc:
  "A generated document"
  ctype = "document.Doc"
  def __init__(self,name=None):
    self.doc = [Start,End]
    self.markers = {Start.name:0,End.name:1}
    self.markerByName = {Start.name:Start,End.name:End}
    self.markerIndex = 0
    self.subdocIndex = 0
    self.parent = None
    self.anonMarker = "mark "
    self.xforms     = []
    self.scratchPad = {}   # Any thing can store arbitrary data here for lookup during subsequent processing


  def SubDocFactory(self):
    "Derived classes should overload this so the the subdoc can be derived classes too"
    return Doc()

  def SubDoc(self):
    ret = self.SubDocFactory()
    ret.parent = self
    self.subdocIndex += 1
    ret.anonMarker = "s%d %s" % (self.subdocIndex, self.anonMarker)
    return ret
    
  def AddXform(self,typeOrPredicate, func):
    """Add a transformation function that is applied to all objects of type 'entity'.
       For example, this can be used to implement internationalization (i18n), by surrounding all
       text with a call to a server-side transformation function.
       
       @param typeOrPredicate A type or obj.__class__ to test equality or instance respectively, or a function that evaluates to True if the transformation should be applied
       @param func return a transformed object when complete, or raise Recurse(obj) to recurse
    """
    self.xforms.append((typeOrPredicate,func))

  def xform(self,s):
    """ Internal function that implements the installed transformations """
    while 1: 
     try:
      for (tp,f) in self.xforms:
        if type(tp) is FunctionType: 
          if tp(s): s = f(s); break
        elif isInstanceOf(s, tp): s = f(s); break
        elif tp is type(s): s = f(s); break
      break     
     except Recurse, r:
      s = r.item
    return s
 
  def genDoc(self,lst):
    if type(lst) != type([]): lst = [lst]  # change into canonical form

    for item in lst:
      if type(item) == type(lst): # handle recursive lists
        self.genDoc(item)
      else:
        item = self.xform(item)  # User-installed transforms can override default generation
        if type(item) is InstanceType:
          if "gen" in dir(item):
            item.gen(self)
          elif "__str__" in dir(item):
            print "WARNING: __str__ function depreciated in favor of gen in object: ", item, "\n"
            assert(0)
            #self.Insert([chunkStr(str(item))],self.body,Before)
          else:
            raise AttributeError, "Obj: %s has neither a gen or __str__ function, so it cannot be converted into html." % item
        elif item is not None:  # A "simple" item just gets converted to a string and then output
          #self.Insert([chunkStr(str(item))],self.body,Before)
          self.Insert([str(item)],self.body,Before)
    

# Private
  def Marker2Index(self,marker):
    if type(marker) in StringTypes:  # Accept strings or markers
      name = marker
      marker = self.markerByName[name]    
    else:    
      name = marker.name      

    if not self.markers.has_key(name):
      if self.parent is None:
        # raise KeyError, "Marker does not exist in the document"
        self.markers[name] = 0
      else:
        return self.parent.Marker2Index(marker)
      
    oldidx = self.markers[name]
    idx = oldidx
    while idx < len(self.doc):
      if self.doc[idx] == marker:
        self.markers[name] = idx
        return (self,idx)
      idx += 1
    assert(not "Marker should have been found, because it is in our dictionary")
    """ # Can only happen if you can delete chunks of the doc
    idx = oldidx
    while idx > 0:
      idx -= 1
      if self.doc[idx] == Marker:
        return idx
    """
    

# Public

  def Insert(self,tokenOrList,marker,whence=Before):
    if type(tokenOrList) == type([]):
      toks = tokenOrList
    else:
      toks = [tokenOrList]
      
    (d,idx) = self.Marker2Index(marker)
    if whence == Replace:
      del d.markers[marker]
      del d.doc[idx]
    elif whence == After:
      idx += 1

    d.doc[idx:idx] = toks

#   Code to check for an obj in the doc, if you find that something is not being converted.
#    for tok in toks:
#      if type(tok) is InstanceType:
#        assert(not tok.ctype == "chunkTag")
           
  # After creating a marker, you must insert it using the above fn
  def NewMarker(self,Name=None):
    if not Name:
      Name = self.anonMarker + str(self.markerIndex)
    if self.markers.has_key(Name):
      raise KeyError, "Attempted to create a new marker with the same name as an existing marker"
    self.markers[Name]=0
    marker = Marker(Name)
    self.markerByName[Name] = marker
    return marker


  def __str__(self):
    ret = "".join([str(tok) for tok in self.doc])
    return ret

#    ret = ""
#    for tok in self.doc:
#      ret += str(tok)
#    return ret

class DocSections(Doc):
  """This looks like a document but it actually just keeps a dictionary of markers and associated data.  Unlike a dict, there is no sequential positioning for all the markers.  This is useful when generating sub-documents and then merging them all into a single doc."""
  ctype = "document.Doc"
  def __init__(self,name=None):
    Doc.__init__(self,name=name)
    self.sections = {}
    self.markers = {}
    self.markerByName = {}
    self.markerIndex = 0
    self.subdocIndex = 0
    self.parent = None
    self.anonMarker = "mark "
    self.scratchPad = {}   # Any thing can store arbitrary data here for lookup during subsequent processing

  def update(self,doc):
    for (k,v) in self.sections.items():
      doc.Insert(v[0] + v[1],k.name,Before)

  def getSection(self,marker):
    t = self.sections[marker]
    return (t[0] + t[1])

  def SubDocFactory(self):
    "Derived classes should overload this so the the subdoc can be derived classes too"
    return DocSections()    

  def __getattr__(self,name):
    "The assumption here is that a member variable defining a section is being accessed"
    if self.markerByName.has_key(name): return self.markerByName[name]
    else: return self.NewMarker(name)

# Public

  def Insert(self,tokenOrList,marker,whence=Before):
    if type(tokenOrList) == type([]):
      toks = tokenOrList
    else:
      toks = [tokenOrList]
    
    d = self

    if not d.sections.has_key(marker):
      d.sections[marker] = [[],[]]

    if whence == Replace or whence == After:
        d.sections[marker][1][0:0] = toks  # put it in the beginning of the "after" list
    else:
        d.sections[marker][0] += toks  # put it in the end of the "before" list
                 
  # After creating a marker, you must insert it using the above fn
  def NewMarker(self,Name=None):
    if not Name:
      Name = self.anonMarker + str(self.markerIndex)
    if self.markers.has_key(Name):
      raise KeyError, "Attempted to create a new marker with the same name as an existing marker"
    self.markers[Name]=0
    m = Marker(Name)
    self.sections[m] = [[],[]]
    self.markerByName[Name] = m
    return m


  def __str__(self):
    ret = "".join([str(tok) for tok in self.doc])
    return ret




        
        
def S(s):
  return s

def Test():
  import regress

  regress.PushComponent("document")
  regress.PushComponent("Doc")

  d = Doc()

  regress.UnitTest("emptyDoc",str(d) == "")

  regress.PushComponent("insert")
  regress.UnitTest("b4 Start",d.Insert([S("1")],Start,Before) is None)
  regress.UnitTest("b4 Start 2",d.Insert([S("2")],Start,Before) is None)
  regress.UnitTest("af Start",d.Insert([S("4")],Start,After) is None)
  regress.UnitTest("af Start 2",d.Insert([S("3")],Start,After) is None)

  regress.UnitTest("b4 End",d.Insert([S("5")],End,Before) is None)
  regress.UnitTest("b4 End 2",d.Insert([S("6")],End,Before) is None)
  regress.UnitTest("af End",d.Insert([S("8")],End,After) is None)
  regress.UnitTest("af End 2",d.Insert([S("7")],End,After) is None)

  regress.UnitTest("ordering",str(d)=="12345678")

  print str(d)

  d = Doc()
  t = d.NewMarker()
  d.Insert(t,End,Before)

  d1 = d.SubDoc()
  d1.Insert(d1.NewMarker(),Start,After)
  d1.Insert(["hi"],Start,After)
  d1.Insert(["The end"],t,After)
  d.Insert([d1,"there"],Start,After)

  print str(d)
  

  regress.PopComponent()
 
  regress.PopComponent()
  regress.PopComponent()
