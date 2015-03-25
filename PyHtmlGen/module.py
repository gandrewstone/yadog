

class Module:
  def __init__(self,name,marker,lst):
    """? Create a new module
    <arg name='name'>The unique name of the module (so duplicate inclusions are eliminated)</arg>
    <arg name='marker'>Where to place this module</arg>
    <arg name='lst'>a list of strings and markers that constitutes the content of the module</arg>    
    """
    self.name = name
    self.marker = marker
    self.lst = lst

  def __hash__(self):
    return self.name.__hash__()

  def __getitem__(self,key):
    if key==0: return self.name
    if key==1: return self.marker
    if key==2: return self.lst
    raise IndexError(key)

  def __str__(self):
    if self.marker:
      return "%s at %s" % (self.name, str(self.marker.name))
    else:
      return self.name
