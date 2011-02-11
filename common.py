from types import *
import inspect

def isInstanceOf(obj,objType):
  """? <fn>Is the object an instance (or derived from) of the class objType)</fn>"""
  if type(obj) is InstanceType and objType in inspect.getmro(obj.__class__): return True
  if type(obj) is objType: return True
  return False
