"""?? This file is the engine that converts the xml to html
"""
import pdb
import os

from common import *

import microdom

#? <section name="Helper Functions">

def genTagDict(xml):
  """?? Converts a <ref>microdom</ref> tree into a dictionary of key: tag names, value: list of objects
  """
  tags = {}
  for node in xml.walk():
    if isInstanceOf(node,microdom.MicroDom):
      lst = tags.get(node.tag_,None)
      if lst is None:
        lst = []
        tags[node.tag_] = lst          
      lst.append(node)
  return tags

generEnv = globals()

def importAndRun(modul,cmdlst):
  try:
    print "Running module %s" % modul
    exec "import %s" % modul in generEnv
    for (c,locals) in cmdlst:
      (filename,html) = eval (c,generEnv,locals)
      #print "Generated %s" % filename
  except ImportError, e:
    print "Missing module: %s" % modul
    print "Exception: %s" % str(e)

#? </section>

def gen(direc,xml,cfg):
  """?? Generate html from microdom.
  <arg name='direc'>Unused</arg>
  <arg name='xml'>The root of the microdom tree</arg>
  <arg name='cfg'>Configuration dictionary</arg>

  <desc>
  This function drives the generation of the html documentation given a microdom tree.  This tree is generally (but not necessarily) created by parsing source code.  The html generation is customized through the cfg object.  Here is an example of this object:
  Example configuration:
  <html><pre>
  cfg={"project":{'name':'YaDoG: Yet Another Documentation Generator','version':'0.0.1.0','date':"Oct 29,2009",'author':"G. Andrew Stone",'homepage':None},
     "sections":["section","file","class","fn","var"],
     "html":
       {
       "dir":"layouts/basicJson",
       "skin":"yadogskin",
       "pageimplementers": {"class":"jsclasspage","file":"jsfilepage"},
       "indeximplementers": { "search":"jssearch","idx":"jsindex","class":"jsclassindexpage","file":"jsfileindexpage"},
       "quicklists": {"History":"jsqhist","Sections":"jsqsec","Classes":"jsqclass","Files":"jsqfile"},
       "misc": { "home":"jshomepage"}
       }
     }
  </pre></html>
  </desc>
  """
  htmlcfg = cfg["html"]
  tagDict = genTagDict(xml)
  print "TAGS:",tagDict.keys()

  # Add the layout path to the environment so we can load the modules
  if htmlcfg.has_key("dir"):
    print "PATH: ", htmlcfg["dir"]
    exec "import sys; sys.path.append('%s')\n" % htmlcfg["dir"] in generEnv

  # Generate the top level page
  for (k,v) in htmlcfg["misc"].items():
    print "Generating %s using module %s" % (k,v)
    importAndRun(v,[("%s.generate(obj,cfg,td)" % v,{"obj":xml,"cfg":cfg,"td":tagDict})])
    

  # Generate the lowest level pages
  for sect in cfg["sections"]:
    # Look up the page implementation for this section
    pi = htmlcfg["pageimplementers"].get(sect,None)
    if pi:
      importAndRun(pi,[("%s.generate(obj,cfg)" % pi,{"obj":obj,"cfg":cfg}) for obj in tagDict[sect]])
      # Pull it in
      #exec "import %s" % pi in generEnv
      # And run it over every object in the section
      #for obj in tagDict[sect]:
      #  (filename,html) = eval("%s.generate(obj,cfg)" % pi,generEnv,{"obj":obj,"cfg":cfg})
    pi = htmlcfg["indeximplementers"].get(sect,None)
    if pi:
      # Pull it in
      #exec "import %s" % pi in generEnv
      # And run it
      #(filename,html) = eval("%s.generate(obj,cfg)" % pi,generEnv,{"obj":tagDict[sect],"cfg":cfg})
      importAndRun(pi,[("%s.generate(obj,cfg)" % pi,{"obj":tagDict[sect],"cfg":cfg})])

  for nav in cfg["html"]["nav"]:
    name = nav[0]
    pi = nav[1]
    if len(nav) > 2:
      args = nav[2]
    else:
      args = None
    importAndRun(pi,[("%s.generate(obj,cfg,args,tagDict)" % pi,{"obj":xml,"cfg":cfg,"args":args,"tagDict":tagDict})])

  if 0:
   pi = htmlcfg["indeximplementers"].get("idx",None)
   if pi:
    importAndRun(pi,[("%s.generate(obj,cfg)" % pi,{"obj":xml,"cfg":cfg})])
   pi = htmlcfg["indeximplementers"].get("search",None)
   if pi:
    importAndRun(pi,[("%s.generate(obj,cfg)" % pi,{"obj":xml,"cfg":cfg})])
