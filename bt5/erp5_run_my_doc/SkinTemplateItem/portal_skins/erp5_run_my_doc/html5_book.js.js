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
            <value> <string>http_cache</string> </value>
        </item>
        <item>
            <key> <string>__name__</string> </key>
            <value> <string>html5_book.js</string> </value>
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

/*\n
Copyright (c) 2011 Nexedi SARL and Contributors. All Rights Reserved.\n
\n
This program is Free Software; you can redistribute it and/or\n
modify it under the terms of the GNU General Public License\n
as published by the Free Software Foundation; either version 2\n
of the License, or (at your option) any later version.\n
\n
This program is distributed in the hope that it will be useful,\n
but WITHOUT ANY WARRANTY; without even the implied warranty of\n
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the\n
GNU General Public License for more details.\n
\n
You should have received a copy of the GNU General Public License\n
along with this program; if not, write to the Free Software\n
Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.\n
*/\n
var textContent, testPageHTML, body;\n
\n
function isUrl(s) {\n
  var regexp = /(ftp|http|https):\\/\\/(\\w+:{0,1}\\w*@)?(\\S+)(:[0-9]+)?(\\/|\\/([\\w#!:.?+=&%@!\\-\\/]))?/\n
  return regexp.test(s);\n
}\n
\n
function cleanForPrince(){\n
  var temp = $(\'iframe\', parent.document).contents().children().clone();\n
  $(\'script\', temp).remove();\n
  $(\'style, meta:not([name=author])\', temp).remove();\n
  $(\'head\', temp).prepend($(\'<meta>\').attr(\'http-equiv\',\'content-type\').attr(\'content\', \'text/html; charset=utf-8\'));\n
  var images = $(\'img\', temp);\n
  n = images.length;\n
  for(var i = 0; i < n; i++){\n
    var img = images.eq(i);\n
    var src = img.attr(\'src\').split(\'?format\')[0].split(\'/\');\n
    var extension = img.attr(\'type\');\n
    if(extension == undefined)\n
      extension = "png";\n
    else\n
      extension = extension.split(\'/\')[1].split(\'+\')[0];\n
    img.attr(\'src\',src[src.length - 1] + \'.\' + extension);\n
  }\n
  var text = temp.html();\n
  var result = "", tagName = "", c = "", chr = "";\n
  var n = text.length;\n
  if (text == null) {\n
    return false;\n
    }\n
  var tag = false, tagNameParsing = false;\n
  for(var i = 0; i < n; i++){\n
    chr = text[i];\n
    c = chr.toLowerCase();\n
    if(c == \'<\' && tag == false){\n
      tag = true;\n
      tagNameParsing = true;\n
    }\n
    else if(tag){\n
      if(c == \' \')\n
        tagNameParsing = false;\n
      else if(c == \'>\'){\n
        tagNameParsing = false;\n
        tag = false;\n
        if(tagName == \'img\')\n
          result += \'/\';\n
        tagName = \'\';\n
      }\n
      else if(tagNameParsing){\n
        if(c == \'i\' && tagName == \'\')\n
          tagName += c;\n
        else if(c == \'m\' && tagName == \'i\')\n
          tagName += c;\n
        else if(c == \'g\' && tagName == \'im\')\n
          tagName += c;\n
      }\n
    }\n
    result += chr;\n
  }\n
  $(\'textarea[name=field_book_text_content]\', parent.document).val(\'<html>\\n\' + result + \'\\n</html>\');\n
  return false;\n
}\n
\n
function changeTag(element, tag){\n
  var tag = $(\'<\' + tag + \'>\').html(element.html());\n
  element.after(tag);\n
  element.remove();\n
  return tag;\n
}\n
\n
function parseList(text){\n
  return text.replace("[","").replace("]","").replace(/\'/g,"").replace(/,/g,", ");\n
}\n
\n
function generateTblContent(title, id, className){\n
  return $(\'<li>\').addClass(className).append($(\'<a>\').attr(\'href\',\'#\' + id).text(title));\n
}\n
\n
function generateToCLine(){\n
  return generateTblContent("Table of Contents", \'toc-h-1\', \'frontmatter\');\n
}\n
\n
function generateFMLine(title, id){\n
  return generateTblContent(title, \'frontmatter-h-\' + id, \'frontmatter\');\n
}\n
\n
function generateEMLine(title, id){\n
  return generateTblContent(title, \'endmatter-h-\' + id, \'endmatter\');\n
}\n
\n
function generatePartLine(title, id){\n
  return generateTblContent(title,\'part-h-\' + id, \'part\');\n
}\n
\n
function addLinksToChapters(chapterContainer, id){\n
  var chapters = chapterContainer.children();\n
  var n = chapters.length;\n
  for(var i = 0; i < n; i++){\n
    var chap = chapters.eq(i);\n
    chap.addClass(\'chapter\');\n
    $(\'a\', chap).attr(\'href\', \'#chapter-h-\' + id + \'-\' + (i+1));\n
  }\n
  return chapterContainer;\n
}\n
\n
function addToC(txt){\n
  // Add to table of Contents\n
  var ul = $(\'<ul>\').addClass(\'toc\');\n
  var beginning = true;\n
  var counter = 1,  partCounter = 1;\n
  $(\'body\').prepend($(\'<div>\').addClass(\'toc\').attr(\'id\',\'toc-h-1\').append(ul));\n
  ul.html(txt);\n
  ul.append(generateToCLine());\n
  var headers = $(\'h1\', ul);\n
  var n = headers.length;\n
  for(var i = 0; i < n; i++){\n
    var hdr = headers.eq(i);\n
    var j = hdr.index() + 1;\n
    var chapterList = ul.children().eq(j)[0];\n
    if(chapterList == undefined || chapterList.tagName.toUpperCase() == "UL"){\n
      beginning = false;\n
      ul.append(generatePartLine(hdr.text(), partCounter).append(addLinksToChapters($(chapterList), partCounter)));\n
      partCounter++;\n
      counter = 1;\n
    }\n
    else{\n
      if(beginning)\n
        ul.append(generateFMLine(hdr.text(), counter));\n
      else\n
        ul.append(generateEMLine(hdr.text(), counter));\n
      counter++;\n
    }\n
  }\n
  $(\'> h1\', ul).remove();\n
}\n
\n
function fetchTextInfo(hasToC, txt){\n
  $.get(\'TestPage_getDetail\', function(details, status, xhr){\n
    details = details.split(\'\\n\');\n
    var title = details[0], shortTitle = details[1], description = details[2], authors = parseList(details[3]);\n
    var year = details[4].split(\'/\')[0];\n
    var titleObj = $(\'title\');\n
    if(titleObj.length > 0)\n
      titleObj.text(title);\n
    else\n
      $(\'head\').append($(\'<title>\').text(title));\n
    $(\'head\').prepend($(\'<meta>\').attr(\'name\',\'author\').attr(\'content\', authors));\n
    titleObj = $(\'<h1>\').text(title);\n
    var subtitle = $(\'<h2>\').text(description);\n
    var edition = $(\'<h3>\').text(shortTitle);\n
\n
    //Add Table of Contents\n
    if(hasToC)\n
      addToC(txt);\n
    //Add imprint\n
    $(\'body\').prepend($(\'<div>\').addClass(\'imprint\').append($(\'<p>\').text("Copyright \\u00A9 " + year + \' \' + authors)));\n
    //Add Title Page\n
    $(\'body\').prepend($(\'<div>\').addClass(\'titlepage\').append(titleObj.clone().addClass(\'no-toc\')).append(subtitle.clone().addClass(\'no-toc\')).append(edition.clone().addClass(\'no-toc\')).append($(\'<p>\').addClass(\'no-toc\').text(authors)));\n
    //Add Front Cover\n
    $(\'body\').prepend($(\'<div>\').addClass(\'frontcover\').append($(\'<img>\').attr(\'src\',\'canvas?format=\')).append(titleObj).append(subtitle).append(edition));\n
    if(hasToC)\n
      cleanForPrince();\n
  });\n
}\n
\n
function convertChapter(link, container, first, isChapter, chapterCounter, partCounter){\n
  $(function() {\n
    //Getting the html content\n
    $.get(link, function(data, textStatus, jqXHR){\n
      var chapterContainer = $(\'<div>\').addClass(\'chapter\').attr(\'id\', \'chapter-h-\' + partCounter + \'-\' + chapterCounter).html(data);\n
      link = link.replace("index_html?format=html","");\n
      $(\'test\', chapterContainer).remove();\n
      var sections = $(\'section\', chapterContainer);\n
      $(\'base,meta,link,title\', chapterContainer).remove();\n
      changeTag($(\'footer\', chapterContainer), \'p\');\n
      var n = sections.length;\n
      for(var i = 0; i < n; i++){\n
        element = changeTag(sections.eq(i), \'div\');\n
        var images = $(\'> img, details > img\', element);\n
        var otherImages = $(\'img:not(> img, details > img)\', element);\n
        var p = images.length;\n
        for(var j = 0; j < p; j++){\n
          var img = images[j];\n
          var div = $(\'<div>\');\n
          var caption = $(\'<p>\').addClass(\'caption\');\n
          if(isUrl($(img).attr(\'src\')) == false) {\n
           $(img).attr(\'src\', link + $(img).attr(\'src\'));\n
          }\n
          $(img).before(div);\n
          var imgToAppend = $(img);\n
          var imgWidth = $(img).attr(\'width\');\n
          if( imgWidth == undefined || imgWidth == \'\')\n
            imgToAppend.attr(\'width\',\'90%\');\n
          div.addClass(\'figure\').append(caption).append($(\'<p>\').addClass(\'art\').append(imgToAppend));\n
          caption.text($(img).attr(\'title\'));\n
        }\n
        var p = otherImages.length;\n
        for(var j = 0; j < p; j++){\n
          var img = otherImages[j];\n
          if((/^http/).test($(img).attr(\'src\')) == false) {\n
           $(img).attr(\'src\', link + $(img).attr(\'src\'));\n
          }\n
        }\n
        if(first && i == 0)\n
          element.attr(\'style\',\'counter-reset: page 1;\');\n
        else if(i != 0){\n
          var headers = $(\':header\', element);\n
          var j = 0, p = headers.length;\n
          for(j = 0; j < p; j++){\n
            var hdr = headers[j];\n
            changeTag($(hdr), \'H\' + (parseInt(hdr.tagName.split(\'H\')[1]) + 1));\n
          }\n
        }\n
        var details = $(\'details\', element);\n
        details.before(details.html());\n
        details.remove();\n
        element.addClass(\'section\');\n
      }\n
      //Why using this instead of load? because using load causes errors when the images are loaded, and the process won\'t reach the end in certain cases\n
      //Moreover, since we load also descriptions, it\'s better to do it this way so that the user doesn\'t see the trick\n
      chapterContainer.append($(\'div.section\', chapterContainer));\n
      \n
      $(\'test\', chapterContainer).remove();\n
      //If it\'s a chapter and not the introduction or an appendix for instance\n
      if(isChapter){\n
        container.append(chapterContainer);\n
        cleanForPrince();\n
      }\n
      else\n
        container.append(chapterContainer.children());\n
      if(container[0].tagName.toUpperCase() == \'BODY\'){\n
        fetchTextInfo(false, \'\');\n
      }\n
    });\n
  });\n
}\n
\n
function convertBook(linkToBook, container){\n
  $(function() {\n
    //Getting the html content\n
    $.get(linkToBook, function(data, textStatus, jqXHR){\n
      linkToBook = linkToBook.replace(\'index_html?format=html\',\'\');\n
      var tocContainer = $(\'<div>\').html(data);\n
      var sections = tocContainer.children();\n
      body = $(\'<body>\');\n
      var firstSection = true, firstChapter = true;\n
      var n = sections.length;\n
      var partCounter = 0, matterCounter = 1;\n
      var partContainer = $(\'<div>\');\n
      for(var i = 0; i < n; i++){\n
        var section = sections.eq(i);\n
        var isPart = section[0].tagName.toUpperCase() == \'UL\';\n
        //If it\'s a list tag, it\'s a part (containing several chapters)\n
        if(isPart){\n
          var chapterTitles = $(\'> li\', section);\n
          var p = chapterTitles.length;\n
          for(var j = 0; j < p; j++){\n
            var newChapter = $(\'<div>\').addClass(\'chapter\').attr(\'id\',\'chapter-h-\' + partCounter + \'-\' + (j+1));\n
            partContainer.append(newChapter);\n
            convertChapter($(\'> a\', chapterTitles.eq(j)).attr(\'href\') + \'/index_html?format=html\', newChapter, false, false);\n
          }\n
          body.append(partContainer);\n
          firstChapter = false;\n
          matterCounter = 1;\n
        }\n
        else{\n
          var link = $(\'> a\', section);\n
          //If there is a link, then it\'s a frontmatter (or endmatter) like an introduction else it\'s the title of a part\n
          if(link.length == 1){\n
            var newMatter = $(\'<div>\');\n
            if(firstChapter){\n
              newMatter.addClass(\'frontmatter\').attr("id","frontmatter-h-" + matterCounter);\n
              if(firstSection)\n
                newMatter.attr(\'style\',\'counter-reset: page 1;\');\n
            }\n
            else\n
              newMatter.addClass(\'endmatter\').attr("id","endmatter-h-" + matterCounter);\n
            body.append(newMatter);\n
            matterCounter++;\n
            convertChapter(link.attr(\'href\') + \'/index_html?format=html\', newMatter, false, false);\n
          }\n
          else{\n
            partCounter++;\n
            partContainer = $(\'<div>\').addClass(\'part\').attr(\'id\',\'part-h-\' + partCounter).append(section.clone());\n
          }\n
        firstSection = false;\n
        }\n
      }\n
      $(\'body\').append(body.children());\n
      fetchTextInfo(true, data);\n
    });\n
  });\n
}\n


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
