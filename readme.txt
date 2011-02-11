<section name="home">

YaDoG is a documentation generator.

Why YaDoG as opposed to another generator?

1. YaDoG proceeds in 2 phases: it converts files to a simple XML format and then converts that XML into your documentation (html for example).  This makes it easy to write your own output generator.  It can even be written in a complete separate script/language.

2. Search!  Documentation REQUIRES search, but existing documentation generators have poor search capabilities.  YaDoG offers a client side search engine.

3. Languages! YaDoG supports the languages I care about instead of just one language, and you can add simple XML-tag support for other languages trivially.

4. Definable markup.  YaDoG specifies XML markup so any file can be "documented" using XML, even if YaDoG does not understand the file's contents (outside of the XML tags).  Language-specific modules provide "shortcuts" that automatically insert XML based on language constructs and expand shorthand notations.  For example: in Python the following two snippets are equivalent:

#? <fn name="myFunc"> 
# <brief>The MyFunc Function</brief>
# <desc> This function does what it does and does it well.</desc>
# <arg name="param">The parameter to the function</arg>
# </fn>
def myFunc(param):
  pass

def myFunc(param):
  """?? The MyFunc Function.  This function does what it does and does it well.
     <arg name="param">The parameter to the function</arg>
  """
  pass

The Python markup parser module interpretes the double question-mark (that is "??") to mean expand shorthand.  The shorthand notation uses the first sentence as the brief description, and subsequent sentences as full description.  Within shorthand notation, however you can always drop back and define something (like an argument) the XML way.

The Python markup parser is also smart enough to automatically discover and add the function name "myFunc", and to generate the surrounding "fn" XML block.

</section>
