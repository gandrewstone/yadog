import pdb
import re
from chunk import *


LIT = "lit"
REP = "rep"

def lhtml2html(obj, phtml,rdic):
    ret = ""
    print "cvt", phtml, "\n", rdic, "\n\n"
    if type(phtml[0]) != type(()):
      pdb.set_trace()
        
    for (typ,content) in phtml: # Grab each phrase & split them into the phrase type and content.
      print "On", typ, content, rdic, "\n"
      if typ == REP:       # If its a replacement
        (tag,body) = content    # split replacement into the tag & the body
        try:
          print "TAG:", tag
          data = rdic[tag]      # See if the tag exists, if not replace with ""
          print "DAta:", data
              
          if type(data) == type({}): # We have a more complicated replacement to do:
            dict = data
            print "Body: ", body
            if type(body) == type([]) and len(body) > 1:
              print "Recurse"
              data = lhtml2html(obj,body,dict)  # if body not found, we have a complicated xlation
            else:
              try:
                if type(body) == type([]): body = body[0]
                data = dict[body[1]]   # If tag exists, look for a translation of the body
              except KeyError:
                data = dict[""] # or use the default

            
      #    if type(body) == type([]):  # if the body is a single literal, then convert it to a string for lookup
      #        if len(body) == 1 and body[0][0] == LIT:
      #          body = body[0][1] # this must be a string, so the else in the next clause will be what is executed
                
                                 

        except KeyError:
          data = ""  # if conversion not found, assume not in use

        if type(data) == type(lambda x:1):  # if its a fn, then execute it
          data = data(obj,body[1])

        if type(data) == type([]):  # if the body is a single literal, then convert it to a string for lookup
            data = lhtml2html(obj,data,rdic)
 
        print "DATA: ", data
        if data is not None:
          ret += str(data)
        
      elif typ == LIT:
        ret += content
        
      else:
        ret += "\nERROR: phrase type not understood: (%s,%s)\n" % (typ,content)
    return ret
  


class LayoutHtmlTemplate(chunkBase):
  """
  LayoutHtmlPage is an abstract superclass for pages that are described by what I call a layouthtml document. A layouthtml document is a html document that has content tags instead of actual content (for example "{TITLE}{/TITLE}" instead of "My Home Page").

  Layouthtml is very similar to, but the the flip side of XML and style sheets.  In fact it is possible to implement this using XML/XSL...
  Essentially XML/XSL is content centric -- you have content, and then use the style sheet to decide how to display the content.
  Layouthtml is display centric -- you describe how the display should look, and then insert available content.
  
  """

  def __init__(self,fileOrString):
    chunkBase.__init__(self)
    self.vdic  = {} # variables (things defined IN the page) dictionary 
    self.doc   = Doc()     
#    try:
    if 1:
        self.phtml = self.parseLayoutHtmlFile(fileOrString)
#    except:
#        self.phtml = self.parseLayoutHtmlStr(fileOrString)
    
  def cvt(self,rdic):
    return lhtml2html(self, self.phtml,rdic)

  def parseLayoutHtmlFile(self,filename):
    f = open(filename)
    text = f.read()
    f.close()
    return self.parseLayoutHtmlStr(text)

  def parseLayoutHtmlStrOld(self,text):
#    print text
    tagOpen = re.compile(r"\{(?!/)(?P<tag>[^}]+)\}(.*?)\{/(?P=tag)\}",re.DOTALL)
    all = tagOpen.finditer(text)

    ret = []
    curloc = 0
    
    for m in all:
      if curloc<m.start():
        ret.append( (LIT,text[curloc:m.start()]  ) ) # put in the preceding literal
      curloc = m.end()
#      print m.groups(), m.group(2)
      tag = m.group(1)
      body = m.group(2)
      recurse = self.parseLayoutHtmlStr(body)
      if tag[0] == "$": # its a variable
        self.vdic[tag] = recurse
      ret.append( (REP, (tag,recurse)) )

    if curloc<len(text):
      ret.append( (LIT,text[curloc:]  ) ) # put in the final literal

    return ret


  """
  {def foo}This Content saved in dictionary under 'foo'{/def foo} 
  {mark bar /} <-- Marker called 'bar' created
  {mark yar}This Content saved in dictionary under 'yar',marker called 'yar' created.{/emark yar}

  """

  def parseLayoutHtmlStr(self,text):
    if not text: return ""
    #   print text
    
    tagOpen = re.compile(r"(\{\s*mark\s+([^\/}\s]+)\s*\/\})|(\{\s*mark\s+(?P<tag>[^\/}\s]+)\s*\}(.*?)\{\s*\/\s*mark\s+(?P=tag)\})|(\{\s*def\s+(?P<tagd>[^\/}\s]+)\s*\}(.*?)\{\s*\/\s*def\s+(?P=tagd)\})",re.DOTALL)
    
    #    tagOpen = re.compile(r"\{(?!/)(?P<tag>[^}]+)\}(.*?)\{/(?P=tag)\}",re.DOTALL)
    all = tagOpen.finditer(text)

    ret = []
    curloc = 0
    
    for m in all:
      print m
      if curloc<m.start():
        self.doc.Insert(text[curloc:m.start()],End,Before) # put in the preceding literal
      curloc = m.end()
      if m.group(0):
        tagtype = 1  # just a marker
        tag = m.group(1)
        body = None
      elif m.group(2):
        tagtype = 2  # a marker & def
        tag = m.group(3)
        body = m.group(4)
      else:
        tagtype = 3  # just a def
        tag  = m.group(5)
        body = m.group(6)
        

      # NOTE: this function must be rewritten to use recursive docs -- not self.doc.
      recurse = self.parseLayoutHtmlStr(body)
      if body:   # its a variable
        self.vdic[tag] = recurse
      # In theory, the recurive chunk will be put into vdic as the default replacement for the tag.
      # Now, if the user doesn't override, then this chunk will become part of the document.
      
        
      if tagtype != 3:
        self.doc.Insert(self.doc.NewMarker(tag),End,Before)

    if curloc<len(text):
      self.doc.Insert(text[curloc:],End,Before) # put in the final literal

    return ret


class LayoutHtmlPage(Doc):
  def __init__(self,template,dict):
    Doc.__init__(self)
    self.template = template
    self.dict     = dict

    # Note, need to find all markers in the template and set them, especially:
    # self.head, self.style, and self.body

  def gen(self,doc):
    s = self.template.cvt(self.dict)
    doc.Insert([s],End,Before)
    
    


def Test():

  r = re.compile(r"(\{\s*mark\s+([^\/}\s]+)\s*\/\})|(\{\s*mark\s+(?P<tag>[^\/}\s]+)\s*\}(.*?)\{\s*\/\s*mark\s+(?P=tag)\})|(\{\s*def\s+(?P<tagd>[^\/}\s]+)\s*\}(.*?)\{\s*\/\s*def\s+(?P=tagd)\})",re.DOTALL)  #   (?!/)(?P<tag>[^}]+)\}(.*?)\{/(?P=tag)\}",re.DOTALL)
# emark\s([^}]+\})

  text = "{mark body/} { mark body1 /} {mark mkvar1}{/mark mkvar1} { mark mkvar2 }ANYTHING{ mark mkvar3 }ANYTHING ELSE {/mark mkvar3} MORE STUFF {/mark mkvar2} {def d1}INSIDE{/def d1}{ def d1 }INSIDE{ / def d1}"
  # { mark body2 }"

  all = r.findall(text)

  
  repl = {
    "title": "LayoutHtml Trial Page",
    "menubar": {
      "item1": "file",
      "item2": lambda self,body: body + "edit",
      "item3":"view",
      "item4":"help"
      },
      
    "sidebar" : "New%sOpen%s" % (BR,BR)
    }

  lp = LayoutHtmlTemplate("layoutpagetest1.html")
  
#  lp.init(lp.parseLayoutHtmlFile("layoutpagetest1.html"),repl)

  c = lp.cvt(repl)

  f = open("tmp.html","w")
  f.write(c)
  f.close()
  
  print c
  return c
 
