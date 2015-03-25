from types import *
import random

BorderStyles = ["none","hidden","dotted","dashed","solid","double","groove","ridge","inset","outset"]

BorderStyleDesc = [ "No border. This value forces the computed value of 'border-width' to be '0'.",
    "Same as 'none', except in terms of border conflict resolution for table elements.",
    "The border is a series of dots.",
    "The border is a series of short line segments.",
    "The border is a single line segment.",
    "The border is two solid lines. The sum of the two lines and the space between them equals the value of 'border-width'.",
    "The border looks as though it were carved into the canvas.",
    "The opposite of 'grove': the border looks as though it were coming out of the canvas.",
    "The border makes the entire box look as though it were embedded in the canvas.",
    "The opposite of 'inset': the border makes the entire box look as though it were coming out of the canvas."
 ]

def SetBorder(item,thickness,color,style="solid"):
  """Adds a border attribute to a chunk
  @param item       The object of type ChunkBase that you want affected
  @param thickness  Width of border (if just a number, pixels are assumed)
  @param color      The border's color
  """
  if type(thickness) is IntType: thickness = "%spx" % thickness
  return item.setAttrs("border", "%s %s %s" % (width,style,color))
  

def locSize(x,y):
  return location(None,None,None,None,x,y)

def locLen(x):
  return location(None,None,None,None,x,None)

def NoLoc():
  return location(None,None,None,None,None,None)

def SetHeight(amt,item):
  """Sets the height of a chunk"""
  return(item.setAttrs("height",amt))

def SetWidth(amt,item):
  """Sets the width of a chunk"""
  return(item.setAttrs("width",amt))


class length:
  "The Length of something -- expressed either as a percent of the whole (the default), or as a number of pixels"
  def __init__(self,amt,units="%"):
    assert(type(amt) == type(0))
    self.amt = amt
    self.units = units

  def __str__(self):
    return "%d%s" % (self.amt,self.units)

  def inverse(self):
    global scrnSize
    if self.units == "%":
      therest = 100-self.amt
    else:
      therest = scrnSize[0] - self.amt
    
    ret = length(therest, self.units)
    return ret


class location:
  def __init__(self,xref,yref,x,y,width, height, z = 0):
    self.ref  = (xref,yref)
    self.pos  = (x,y,z)
    self.size = (width,height)

  def setStyle(self,dict):
    if self.ref[0]: dict[self.ref[0]] = self.pos[0]
    if self.ref[1]: dict[self.ref[1]] = self.pos[1]
    if self.pos[2]: dict["z-index"]   = self.pos[2]
    if self.size[0]: dict["width"]    = self.size[0]
    if self.size[1]: dict["height"]   = self.size[1]
    

  def __str__(self):
    if self.ref[0]:
      return " %s:%s ; %s:%s ; width:%s ; height:%s ; z-index:%s" % (self.ref[0],self.pos[0], self.ref[1],self.pos[1], self.size[0],self.size[1], self.pos[2])
    elif self.size[0] and self.size[1]:
      return " width:%s; height:%s" % (self.size[0],self.size[1])
    elif self.size[0]:
      return " width:%s " % (self.size[0])
    else: return ""


class Color:
  def __init__(self,red,green,blue,opacity=255):

    # FOR PUBLIC ACCESS
    self.red     = red
    self.green   = green
    self.blue    = blue
    self.opacity = opacity

  def __getitem__(self,idx):
    if   idx == 0: return self.red
    elif idx == 1: return self.green
    elif idx == 2: return self.blue
    elif idx == 3: return self.opacity
    else: assert(0)

  def Randomize(self):
    self.red = random.randint(0,128)
    self.green = random.randint(0,128)
    self.blue = random.randint(0,128)
    self.opacity = 255
    return self

  def __str__(self):
    if self.opacity==0:
      return "transparent"
    else:
      return "rgb(%d,%d,%d)" % (self.red, self.green, self.blue)




# Constant, common lengths
centPercent = length(100)  # 100 percent
half        = length(50)

# for the xref and yref in the location class
top    = "top"
bottom = "bottom"
left   = "left"
right  = "right"

relative = 0
absolute = 1

# RefCvt = ("top", "bottom", "left", "right")
PosCvt = ("relative","absolute")
