"""<module>
This module extracts documentation from python programs
"""
from types import *
import pdb
import ast
import re

import sys
sys.path.append("/me/code")

from PyHtmlGen.document import *

from common import *
from constants import *
import microdom

def extractSingleLineComment(byLine,idx):
    result = []
    firstSrcLine = None
#-    print byLine[idx]
#-    pdb.set_trace()
    
    while 1:
      line = byLine[idx].strip()
      if line[0:2]=="//":
        result.append(line[2:])
        idx+=1
      else:
        break
    
    while not line:
      idx+=1
      line = byLine[idx].strip()
    firstSrcLine = line
    return(idx-1," ".join(result),firstSrcLine)

def extractMultiLineComment(byLine,idx):
    result = []
    firstSrcLine = None
    while 1:
      try:
        line = byLine[idx].strip()
      except IndexError, e:
        idx = idx-1
        break
      idx+=1
      if line:
        cleaned = line
        if cleaned[0:3] == '/*?': cleaned = cleaned[3:] #- Strip off the start and typical commend block stuff
        cleaned = cleaned.replace("*/","")
        if cleaned and cleaned[0] == '*': cleaned = cleaned[1:]
        result.append(cleaned)          
        if line.find("*/") != -1:
          break
    
    line = byLine[idx].strip()
    while not line:
      idx+=1
      try:
        line = byLine[idx].strip()
      except IndexError, e:
        line=""
        break
      
    firstSrcLine = line

    return(idx-1," ".join(result),firstSrcLine)


def extractCodeDoc(byLine,idx):
  result = []
  nLines = len(byLine)
  while idx < nLines:
    line = byLine[idx]
    if line[0:4] == "//?]":
      break
    result.append(line)
    idx+=1

  result.insert(0,"<![CDATA[")
  result.append("]]>")
  return (idx,"\n".join(result),"")
    

def extractComments(text):
  """<fn>Pull the comments out of a Python file
     <arg name='text'>A single string containing python source code</arg>
     </fn>"""
  byLine = text.split("\n")
  num=0
  comments = []

  idx = 0
  while idx<len(byLine):
    line = byLine[idx]
    
    stripped = line.strip()
    #- TODO: search for strings and remove them
    if stripped:
      if stripped[0:4] == "//?[":
          (idx,comment,srcLine) = extractCodeDoc(byLine,idx)
          comments.append((idx,comment,srcLine))          
      elif stripped[0:3] == "//?":
          (idx,comment,srcLine) = extractSingleLineComment(byLine,idx)
          comments.append((idx,comment,srcLine))
      elif -1 != line.find("//?"):
          (srcLine,sep,comment) = line.partition("//?")
          comments.append((idx,comment,srcLine))
      elif line[0:3] == "/*?":
          (idx,comment,srcLine) = extractMultiLineComment(byLine,idx)
          comments.append((idx,comment,srcLine))          

    idx+=1

  return comments

def addLineAttr(match,lineNum):
  s = "<%s linenum='%d'" % (match.groups()[0],lineNum)
#-  print s
  return s

def addAttrClosure(attr,val):

  def fn(match):
    m = match.groups()
    if m[1].find(attr)==-1:  # Its not in there, so add it (if it is already defined we won't override)
      s = "<%s %s %s='%s'>" % (m[0],m[1],str(attr),str(val))
    else:
      s = "<%s %s>" % (m[0],m[1])
    return s

  return fn


#-
remacro = re.compile(r"\A\s*#define\s+(?P<name>[a-zA-Z_]+\w*)\s+(?P<value>\w+)")
renamespace = re.compile(r"\A\bnamespace\b\s*(?P<name>[a-zA-Z_]+\w*)")
reclass = re.compile(r"\A\bclass\b\s*(?P<name>[a-zA-Z_]+\w*)")
restruct = re.compile(r"\A\bstruct\b\s*(?P<name>[a-zA-Z_]+\w*)")
refn = re.compile(r"\A(?:\bvirtual\b|\bstatic\b)?\s*(?P<type>[\w<>,&*\s]*?)\s+(?P<name>\b[a-zA-Z_]\w*\b)\s*(?P<args>\(.*?\)\s*(?:\bconst\b)?)\s*(?P<semicolon>;+)?\s*")
rector = re.compile(r"\A(?P<name>\b[a-zA-Z_]\w*\b)\s*(?P<args>\(.*?\))\s*(?P<semicolon>;+)?\s*")
revardecl = re.compile(r"\A\s*(?P<type>[\w<>,&*\s]*?)\s+(?P<name>\b[a-zA-Z_]\w*\b)")
#reargdecl = re.compile(r"\A\s*(?P<type>[\w<>,&*\s]*?)\s+(?P<name>\b[a-zA-Z_]\w*\b)")
reargdecl = re.compile(r"\A\s*(?P<typequal>(?:(?:unsigned|signed|const|volatile|long|struct)\s)*)(?P<type>[\w<>,&*\s]*?)\s+(?P<name>\b[a-zA-Z_]\w*\b)")

res = [remacro,renamespace,reclass,restruct,refn,rector,revardecl]

reKeys = ['name','value','type','args']

#- This pattern matches an xml opener tag with an arbitrary number of attributes and returns
#- the tag as the first group and all attributes and values as a string in the second
xmlpat = re.compile(r"""<\s*(\w+)((?:\s+\w+\s*=\s*['"][^'"]*['"])*)\w*\s*>""")

#- pat.match("<foo>").groups()
#- pat.match("< foo >").groups()
#- pat.match("<foo >").groups()
#- pat.match("< foo>").groups()
#- pat.match("<foo bar='1'>").groups()
#- pat.match("""<foo bar='1' zerg="2">""").groups()

def fixupComments(comments):
  ret = []
  pat = re.compile("<(\w+)")

  for (linenum,comment,srcline) in comments:  # If the comment begins with a ?, then replace it with the generic xml tag
      if srcline:
        for r in res:
          t = r.search(srcline)
          if t:
            matches = t.groupdict()
            for key in reKeys:
              if matches.has_key(key):
                comment = re.sub(xmlpat,addAttrClosure(key,matches[key]),comment)

      comment = re.sub(pat,lambda x,y=linenum: addLineAttr(x,y),comment)
      comment = comment.replace("&","&amp;")
      ret.append(comment)
  return ret


def comments2MicroDom(comments,filename):
  """<fn>Convert a list of (line number,comment) to an xml doc</fn>"""
  
  xml = "<%s name='%s' language='c++'>" % (TagFile,filename) + "\n".join(comments)+"</%s>" % TagFile
  try:
    dom = microdom.parseString(xml)
  except microdom.ExpatError,e:
    print "File: %s: XML ERROR!" % filename, str(e)
    try:
      print "Clause: %s" % comments[e.lineno-1]
    except:
      pass
    pdb.set_trace()
    
  return dom


def regularize(node):
  """? This function ensures that the tree is complete and regular.  For example it breaks descriptions into brief and desc tags.
  """
  if microdom.isInstanceOf(node,microdom.MicroDom):
    if node.tag_ in [TagCtor,TagMethod,TagFunction]:
      # Add the "decl" tag
      t = microdom.MicroDom({"tag_":TagDecl},None,node.name + node.args)
      node.addChild(t)

      # Supplement the args tags
      args = node.args
      args = args.replace("(","").replace(")","") # remove leading and trailing paren
      arglst = args.split(',')
      for arg in arglst:
        if arg!="void":
          (typequal,atype,aname) = reargdecl.match(arg).groups()

          argdefs = node.filterByAttr({AttrName:aname})
          if not argdefs:
            t = microdom.MicroDom({"tag_":TagParam,AttrType:typequal + atype,AttrName:aname},None,None)
            node.addChild(t)
          for t in argdefs:
            t.addAttr(AttrType,typequal + atype)
      

    for c in node.children_:
      regularize(c)

  return node

def extractXml(prjPfx, filename):
  

  f = open(filename,"rb")
  text = f.read()

  #- pdb.set_trace()
  comments = extractComments(text)

  comments = fixupComments(comments)

  if filename.startswith(prjPfx):
    filename = filename[len(prjPfx):]   

  xml = comments2MicroDom(comments,filename)
  regularize(xml)
  

  print "Extracted XML:\n", xml.write()  
  return xml

def Test():
  pdb.set_trace()
  xml = extractXml("/me/hw/arduino/arduino-m5451-current-driver/latest/apps/lightuino_lib_dev/lightuino.h")
  #- xml = extractXml("microdom.py")



if __name__ == "__main__":
    Test()

#</module>
