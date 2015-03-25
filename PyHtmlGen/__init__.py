"""
import gen 
import chunk 
import document 
import bar 
import layouttable 
import imagehtml 
import menu 
import form 
import template 
import htmldoc 
import json 
import js
"""

def Reload():
  print "reloading all submodules"
  reload(gen)
  reload(chunk)
  reload(document)
  reload(bar)
  reload(layouttable)
  reload(imagehtml)
  reload(menu)
  reload(form)
  reload(template)
  reload(htmldoc)
  reload(js)
  reload(json)

#__all__ = ["chunk","htmldoc","bar","layouttable","imagehtml","menu","form","template","js","json"]

#Reload()
