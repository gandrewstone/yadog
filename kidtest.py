import kid
#kid.enable_import() # path="/path/to/kid/templates") ext=".html"


def Test():
  template = kid.Template(file="simpletemplate.xml")
  print str(template)

  template = kid.Template(source='<p>$foo</p>', foo='Hello World!')
  print template.serialize()

  out = {'section': u'<span onClick="ReplaceChildrenWithUri(\'center\',\'section_classes.html\')" onMouseout="this.setAttribute(\'style\',\'\');" onMouseover="this.setAttribute(\'style\',\'color:Blue;\');">classes</span>', 'ClassFile': u'<span onClick="ReplaceChildrenWithUri(\'center\',\'file_lightuino.h.html\')" onMouseout="this.setAttribute(\'style\',\'\');" onMouseover="this.setAttribute(\'style\',\'color:Blue;\');">/me/hw/arduino/arduino-m5451-current-driver/latest/apps/lightuino_lib_dev/applet/lightuino.h</span>', 'subSection': ["hi"], 'className': u'Lightuinop'}
  template = kid.Template(file="yadogskin/classdetails.xml",**out)
  print str(template)
