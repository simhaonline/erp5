<?xml version="1.0"?>
<ZopeData>
  <record id="1" aka="AAAAAAAAAAE=">
    <pickle>
      <global name="DTMLDocument" module="OFS.DTMLDocument"/>
    </pickle>
    <pickle>
      <dictionary>
        <item>
            <key> <string>_Cacheable__manager_id</string> </key>
            <value> <string>root_http_skin_cache</string> </value>
        </item>
        <item>
            <key> <string>__name__</string> </key>
            <value> <string>tabber-cookie.js</string> </value>
        </item>
        <item>
            <key> <string>_vars</string> </key>
            <value>
              <dictionary/>
            </value>
        </item>
        <item>
            <key> <string>globals</string> </key>
            <value>
              <dictionary/>
            </value>
        </item>
        <item>
            <key> <string>raw</string> </key>
            <value> <string encoding="cdata"><![CDATA[

/* Optional: Temporarily hide the "tabber" class so it does not "flash"\n
   on the page as plain HTML. After tabber runs, the class is changed\n
   to "tabberlive" and it will appear. */\n
\n
document.write(\'<style type="text/css">.tabber{display:none;}<\\/style>\');\n
\n
/*==================================================\n
  Set the tabber options (must do this before including tabber.js)\n
  ==================================================*/\n
var tabberOptions = {\n
\n
  \'cookie\':"tabber", /* Name to use for the cookie */\n
\n
  \'onLoad\': function(argsObj)\n
  {\n
    var t = argsObj.tabber;\n
    var i;\n
\n
    /* Optional: Add the id of the tabber to the cookie name to allow\n
       for multiple tabber interfaces on the site.  If you have\n
       multiple tabber interfaces (even on different pages) I suggest\n
       setting a unique id on each one, to avoid having the cookie set\n
       the wrong tab.\n
    */\n
    if (t.id) {\n
      t.cookie = t.id + t.cookie;\n
    }\n
\n
    /* If a cookie was previously set, restore the active tab */\n
    i = parseInt(getCookie(t.cookie));\n
    if (isNaN(i)) { return; }\n
    t.tabShow(i);\n
  },\n
\n
  \'onClick\':function(argsObj)\n
  {\n
    var c = argsObj.tabber.cookie;\n
    var i = argsObj.index;\n
    setCookie(c, i);\n
  }\n
};\n
\n
/*==================================================\n
  Cookie functions\n
  ==================================================*/\n
function setCookie(name, value, expires, path, domain, secure) {\n
    document.cookie= name + "=" + escape(value) +\n
        ((expires) ? "; expires=" + expires.toGMTString() : "") +\n
        ((path) ? "; path=" + path : "") +\n
        ((domain) ? "; domain=" + domain : "") +\n
        ((secure) ? "; secure" : "");\n
}\n
\n
function getCookie(name) {\n
    var dc = document.cookie;\n
    var prefix = name + "=";\n
    var begin = dc.indexOf("; " + prefix);\n
    if (begin == -1) {\n
        begin = dc.indexOf(prefix);\n
        if (begin != 0) return null;\n
    } else {\n
        begin += 2;\n
    }\n
    var end = document.cookie.indexOf(";", begin);\n
    if (end == -1) {\n
        end = dc.length;\n
    }\n
    return unescape(dc.substring(begin + prefix.length, end));\n
}\n
function deleteCookie(name, path, domain) {\n
    if (getCookie(name)) {\n
        document.cookie = name + "=" +\n
            ((path) ? "; path=" + path : "") +\n
            ((domain) ? "; domain=" + domain : "") +\n
            "; expires=Thu, 01-Jan-70 00:00:01 GMT";\n
    }\n
}

]]></string> </value>
        </item>
        <item>
            <key> <string>title</string> </key>
            <value> <string></string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
