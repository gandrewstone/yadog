from gen import *
from document import *
from chunk import *
from attribute import *
from imagehtml import *

import string

class Template(chunkBase):
  """Abstract base class defining the template"""
  def __init__(self):
    pass


  def apply(self,repeated):
    """Override this function to apply the template to the portion of the html that would be modified by the template.
       This function is called by the enclosing structure/class.
    """
    return repeated


class KidQualifierTemplate(Template):
  def __init__(self,qual,content):
    self.qualifier = qual
    self.content = content

  
  def apply(self,repeated):
    """Override this function to apply the template to the portion of the html that would be modified by the template.
       This function is called by the enclosing structure/class.
    """
    if isInstanceOf(repeated,chunkTag):
      repeated.attrs[self.qualifier[0]] = self.qualifier[1]
      
  def gen(self,doc):
    genDoc(doc,self.content)

class PyTemplate(Template):
  """?? This class allows Python template strings to be used as a template system.
  """
  def __init__(self, strOrFilename, dic=None):
    """?? Constructor
    <arg name='strOrFile'>The template string or a filename containing the template string</arg>
    """
    try:
      f = open(strOrFilename,"rb")
      s = f.read()
    except IOError, e:
      s = str(strOrFilename)

    self.template = string.Template(s)
    if dic is None: dic = {}
    self.mapping  = dic

  def gen(self,doc):
    s = self.template.substitute(self.mapping)
    genDoc(doc,s)


def Test():
  import gen
  test1 = PyTemplate("Let's try this: $key")
  test1.mapping["key"] = "value"
  gen.WriteFile("testtemplate.html",[test1])
