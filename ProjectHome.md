This project generates documentation from source code.  It differs from its peers in that it defines an XML markup language that can be embedded into comments in the source code for annotation.  This "base" markup can be used in ANY source code language without any customization of YaDoG, so YaDoG can always be used (albeit with a little extra pain).

Additionally, "output" generators can be written to parse this XML rather than the source language, making them easier to write.

YaDoG provides context-sensitive "shortcut" notation parsers for common languages like C and Python that convert source files in these languages to the "base" XML markup.  This means that the "base" XML markup is rarely explicitly used in the source code of supported languages, but it is still there if you are doing something very fancy.

This bi-level architecture makes YaDoG extremely flexible, and makes additional output generators easy to write.