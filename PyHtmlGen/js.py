import os.path
import os

from document import *
from module import *

def moduledir():
  return os.path.dirname(os.path.abspath(__file__))


hidden = Marker("hidden")

# Modules: ( name, marker, [ (marker,[insert before marker,...] ), (marker,...), ...] )

jsm = Marker("js")

# Modules: ( name, marker, [ (marker,[insert before marker,...] ), (marker,...), ...] )

jsModule = Module("js",jsm,[("head",["<script language='JavaScript'> /* <![CDATA[ */\n",jsm,"//]]>\n</script>\n"]) ])

AnOlderToggleShowImpl = """
function toggleShow(itemId){
    var ctnt = document.getElementById(itemId);
    curStyle = ctnt.getAttribute("style");
    if (curStyle == 'display: none;') {
      ctnt.setAttribute("style",ctnt.getAttribute("origstyle"));
}
    else {
      ctnt.setAttribute("origstyle",ctnt.getAttribute("style"));
      ctnt.setAttribute("style","display: none;");
}
    }
"""

showHideModule = Module("showhide",hidden, [("js",["""function toggleShow(itemId) {
    var ctnt = document.getElementById(itemId);

    if ((ctnt.style.display == "none") || (ctnt.style.display == "")) {
      if (ctnt.getAttribute("actualdisplay"))
        ctnt.style.display = ctnt.getAttribute("actualdisplay");
      else
        ctnt.style.display = "block";
    }
    else {
      ctnt.setAttribute("actualdisplay",ctnt.style.display);
      ctnt.style.display = "none";
    }

  } 


  function SwapContent(contentId, toId, hideId){
    var ctnt = document.getElementById(contentId);
    var hide = document.getElementById(hideId) ;
    var tgt  = document.getElementById(toId);

    kids = tgt.childNodes;
 
    for (var i = 0; i < kids.length; i++) {
      hide.appendChild(kids[i]);
      }
    tgt.appendChild(ctnt);
    }

function MoveContent(contentId,toId){
var ctnt = document.getElementById(contentId);
var tgt  = document.getElementById(toId);
tgt.appendChild(ctnt);
}

function CopyContent(contentId,toId,remExisting){
var ctnt = document.getElementById(contentId);
var tgt  = document.getElementById(toId);
var copy = ctnt.cloneNode(true);
copy.removeAttribute('id');
if (remExisting) while( tgt.hasChildNodes() ) { tgt.removeChild( tgt.lastChild ); }
tgt.appendChild(copy);
}
"""] ), 
                                      ("style",["#hidden { display:none }\n"]),("body",["<div id='hidden'>",hidden,"</div>"])  ])

#                                      ("style",["#hidden { position:absolute; bottom:0px ; right:0px ; height:1px ; width:1px ; z-index:-10000 ; overflow:hidden; clip:auto }\n"]),("body",["<div id='hidden'>",hidden,"</div>"])  ])

delayLoadModule = Module("delayLoad",None,[("js",[""" 
  function delayLoadImg(imId,href){
    var img = document.getElementById(imId);
    img.src = href;
    }
"""])])


faderModule = Module("delayLoad",None,[("js",[file(moduledir() + os.sep + "fader.js","r").read()])])



""" Example use of styleRow
<tr>
<td>
<div onClick="styleRow(this,'background-color:red')">
New
</div>
</td>
</tr>
"""

styleRowModule = Module("styleRow",None,[("js",["""
  function styleRow(elemInRow,newStyle){
    var row = elemInRow;

    while ((row != document)&&(row.tagName != "TR")) { row = row.parentNode; }
    if (row != document) row.setAttribute('style', newStyle);
}
"""])])



newRowModule = Module("newRow",None,[("js",["""
function newRow(anyElemInTable,budId){
    var table  = anyElemInTable;
    while ((table != document)&&(table.tagName != "TABLE")) { table = table.parentNode; }
    if (table != document) {
      var copy = document.getElementById(budId).cloneNode(true);
      copy.removeAttribute('id');
      table.appendChild(copy);
  }
}
"""])])


""" Example use of makeEditable: note I have to removeAttribute('onClick'), or when you click to edit it will make another.
<form>
<table><tr>
            <td onClick="this.removeAttribute('onClick'); makeEditable(this,'textbox1')">
New Hampshire
        </td>
      </tr>
    </table>
    <input  id='textbox1' name="Start" type="text" value="Start" />
  </form>
"""
makeEditableModule = Module("makeEditable",None,[("js",[r"""
function makeEditable(elem,editBoxBudId, newId){
  var newEditBox = document.getElementById(editBoxBudId).cloneNode(true);
  var data = elem.firstChild.data;
  var i=0;
  while ((data[i] == ' ')||(data[i] == '\n')) i++;  /* Wipe preceding whitespace */
  data = data.substring(i,data.length);
  newEditBox.setAttribute('value',data);
  if (newId != "") newEditBox.setAttribute('id',newId);
  newEditBox.setAttribute('name',newId);
  elem.replaceChild(newEditBox, elem.firstChild);
  newEditBox.focus();
}

"""])])


#    styleRow(anyElemInTable,'background-color:blue')
