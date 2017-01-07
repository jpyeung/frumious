
Number.prototype.mod = function(n) { return ((this%n)+n)%n; }

var toolOrder = [];
var subToolOrder = [];
function frameLoad() {
  $('#docframe').contents().find('body').css('margin', '12pt').css('background','#f6f6f6');

  $('#docframe').contents().find('a').each(function() {
    // make links to external domains open in a new window
    if ($(this).attr('href').indexOf('http') == 0) {
      $(this).attr('target', '_blank');
    }
    // add icon to new window links
    if ($(this).attr('target') == '_blank') {
      $(this).css('background', 'url(data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAoAAAAKCAYAAACNMs+9AAAAVklEQVR4Xn3PgQkAMQhDUXfqTu7kTtkpd5RA8AInfArtQ2iRXFWT2QedAfttj2FsPIOE1eCOlEuoWWjgzYaB/IkeGOrxXhqB+uA9Bfcm0lAZuh+YIeAD+cAqSz4kCMUAAAAASUVORK5CYII=) center right no-repeat');
      $(this).css('padding-right', '13px');
    }
  });

  var pageName = $('#docframe')[0].contentWindow
    .location.href.replace(/.*\/|\.[^.]*$/g, '');

  // capture tool order
  if (pageName == 'menu') {
    var tools = $('#docframe').contents().find('a.tool:not([target])');
    for (var i = 0; i < tools.length; i++) {
      toolOrder[i] = tools[i].href.replace(/.*\/|\.[^.]*$/g, '');
    }
    return;  // the rest of the function only applies to tool pages
  }
  if (pageName == 'gridpuzzle') {
    var tools = $('#docframe').contents().find('a:not([target])');
    for (var i = 0; i < tools.length; i++) {
      subToolOrder[i] = tools[i].href.replace(/.*\/|\.[^.]*$/g, '');
    }
  }

  chooseTool(pageName);

  // find previous and next tools
  var prevTool = '&laquo; prev';
  var nextTool = 'next &raquo;';
  var tlen = toolOrder.length;
  for (var i = 0; i < tlen; i++) {
    if (toolOrder[i] == pageName && tlen > 1) {
      prevTool = '<a href="' + toolOrder[(i-1).mod(tlen)] + '.html">&laquo; prev</a>';
      nextTool = '<a href="' + toolOrder[(i+1).mod(tlen)] + '.html">next &raquo;</a>';
    }
  }
  var subMenu = '';
  tlen = subToolOrder.length;
  for (var i = 0; i < tlen; i++) {
    if (subToolOrder[i] == pageName && tlen > 1) {
      prevTool = '<a href="' + subToolOrder[(i-1).mod(tlen)] + '.html">&laquo; prev</a>';
      nextTool = '<a href="' + subToolOrder[(i+1).mod(tlen)] + '.html">next &raquo;</a>';
      subMenu = ' / <a href="gridpuzzle.html" style="font-weight:bold">Grid Puzzles</a>';
    }
  }

  // add menu links at top and bottom
  var menuStr = '<br>'
    + '<div style="position:fixed;left:0;right:0;top:0;padding:10pt 12pt;background:#f6f6f6;z-index:2;font-size:1.2em">'
    + '<div style="float:left">' + prevTool + '</div>'
    + '<div style="float:right">' + nextTool + '</div>'
    + '<div style="margin:0 auto;text-align:center"><a href="menu.html" style="font-weight:bold">Tool Menu</a>' + subMenu + '</div>'
    + '</div>';
  $('#docframe').contents().find('body').prepend(menuStr).append('<br>');

  // add "try it" buttons to examples
  $('#docframe').contents().find('.example').each(function() {
    // escape characters for embedding in javascript string
    var text = $(this).html().replace(/([\\"''"])/g, "\\$1").replace(/\n/g,"\\n");
    // create DOM element just to decode html entities like &gt;
    var tmpElt = document.createElement('div');
    tmpElt.innerHTML = text;
    text = tmpElt.childNodes[0].nodeValue;
    text = "$('#inputbox')[0].value = '" + text + "'; if (!running) { start(); }";
    $(this).before($('<button>try it</button>').css({
      'float': 'right', 'position': 'relative', 'z-index': '1' })
      .click(new Function(text)));
  });
  updateButtonState();  // disable try buttons if running
}


var token = '';
var running = false;
var tool = '';
var serverReady = true;
var historyLog = {};

var reqTimeout;
var updateTimeout;
var xmlHttp;
var UPDATE_PERIOD = 500;
var TIMEOUT_PERIOD = 10000;

var toolNames = {
  '': 'no tool selected',
  'caesarshift': 'caesar shift',
  'fillapix': 'fill-a-pix',
  'paintbynumbers': 'paint by numbers'
};

function createXMLHttpRequest() {
  try { return new XMLHttpRequest(); } catch(e) {}
  try { return new ActiveXObject('Msxml2.XMLHTTP'); } catch (e) {}
  try { return new ActiveXObject('Microsoft.XMLHTTP'); } catch(e) {}
  alert("Sorry, these tools don't work in your browser. Please try a recent version of Chrome or Firefox.");
  return null;
}
function setServerReady(val) {
  serverReady = val;
  updateButtonState();
}
function updateButtonState() {
  $('#startbutton')[0].disabled = !serverReady || (tool == '' && !running);
  $('#docframe').contents().find('button')
    .each(function() { $(this)[0].disabled = running || !serverReady; });
}
function setRunning(val) {
  running = val;
  if (running) {
    $('#startbutton').html('Stop');
    $('#progress').html('-');
    $('#copybutton').hide();
  } else {
    $('#startbutton').html('Start');
    $('#progress').html('');
    if ($('#output').html().split(/<br>/gi).length > 4) {
      $('#copybutton').show();
    }
    histKey = $('#history option:last-child').val();
    if (historyLog[histKey] && historyLog[histKey][1] == '')
      historyLog[histKey][1] = $('#output').html();
  }
  updateButtonState();
}
function startStop() {
  if (running) { stop(); }
  else { start(); }
}
function connTimeout() {
  xmlHttp.abort();
  setServerReady(true);
  $('#progress').html('trying to reach server...');
  update();
}
function start() {
  var input = $('#inputbox')[0].value;
  if (tool == '') {
    $('#output').html('Please select a tool.');
    $('#copybutton').hide();
    return;
  }
  if (input == '') {
    $('#output').html('Please enter some input text.');
    $('#copybutton').hide();
    return;
  }
  setServerReady(false);
  xmlHttp = createXMLHttpRequest();
  xmlHttp.onreadystatechange = function() {
    if (xmlHttp.readyState != 4 || xmlHttp.status != 200) { return; }
    clearTimeout(reqTimeout);
    token = xmlHttp.responseText;
    if (token.charAt(0) == 'E' || token.charAt(0) == 'S') {  // error
      $('#output').html(token.replace('\n', '<br>'));
    } else {
      setRunning(true);
      $('#output').html('running ' + tool + '<br>');
      updateTimeout = setTimeout(update, UPDATE_PERIOD);
    }
    setServerReady(true);
  };
  reqTimeout = setTimeout(connTimeout, TIMEOUT_PERIOD);
  xmlHttp.open('post', 'localhost:5000/q?tool=' + tool, true);
  xmlHttp.send(input);
  addHistory();
}
function stop() {
  setServerReady(false);
  clearTimeout(updateTimeout);
  clearTimeout(reqTimeout);
  xmlHttp = createXMLHttpRequest();
  xmlHttp.onreadystatechange = function() {
    if (xmlHttp.readyState != 4 || xmlHttp.status != 200) { return; }
    clearTimeout(reqTimeout);
    setRunning(false);
    setServerReady(true);
  };
  reqTimeout = setTimeout(connTimeout, TIMEOUT_PERIOD);
  xmlHttp.open('post', 'q?stop', true);
  xmlHttp.send(token);
}
function makeProgress() {
  var old_str = $('#progress').html();
  var new_str;
  if (old_str == '-') { new_str = '\\'; }
  else if (old_str == '\\') { new_str = '|'; }
  else if (old_str == '|') { new_str = '/'; }
  else { new_str = '-'; }
  $('#progress').html(new_str);
}
function update() {
  xmlHttp = createXMLHttpRequest();
  xmlHttp.onreadystatechange = function() {
    if (xmlHttp.readyState != 4 || xmlHttp.status != 200) { return; }
    clearTimeout(reqTimeout);
    var lines = xmlHttp.responseText.split('\n');
    $('#output').append(lines.slice(1).join('&nbsp;<br>').replace(/ /g,'&nbsp;'));
    if (lines[0] == 'running') {
      makeProgress();
      updateTimeout = setTimeout(update, UPDATE_PERIOD);
    } else {
      setRunning(false);
    }
  };
  reqTimeout = setTimeout(connTimeout, TIMEOUT_PERIOD);
  xmlHttp.open('post', 'q?update', true);
  xmlHttp.send(token);
}
function addHistory() {
  var histEntry = document.createElement('option');
  var time = new Date().toLocaleTimeString().split(' ')[0];
  histEntry.text = time + ' ' + $('#curtool').html() + ' ' + $('#inputbox')[0].value.length;
  var histKey = tool + ' ' + new Date().getTime();
  historyLog[histKey] = [$('#inputbox')[0].value, ''];
  histEntry.value = histKey;
  $('#history')[0].options.add(histEntry);
  $('#history')[0].selectedIndex = $('#history')[0].length - 1;
  $('#history')[0].disabled = false;
}
function getHistory() {
  histKey = $('#history')[0].options[$('#history')[0].selectedIndex].value;
  $('#inputbox')[0].value = historyLog[histKey][0];
  chooseTool(histKey.split(' ')[0]);
  $('#docframe').attr('src', tool + '.html');
  if (!running) $('#output').html(historyLog[histKey][1]);
}
function chooseTool(toolName) {
  tool = toolName;
  $('#curtool').html(toolName in toolNames ? toolNames[toolName] : toolName);
  updateButtonState();
}
function doCopy() {
  var text = $('#output').html();
  text = text.replace(/&nbsp;/g, ' ').replace(/&amp;/g, '&');
  text = text.replace(/&lt;/g, '<').replace(/&gt;/g, '>');
  text = text.replace(/ *<br>/gi, '\n');
  var lines = text.split('\n');
  lines.splice(0,3);  // remove first 3 lines (status text)
  $('#inputbox')[0].value = lines.join('\n');
}

$(function() {
  setRunning(false);
  var urlparam = window.location.search.substring(1);
  chooseTool(urlparam);
  if (urlparam) { $('#docframe').attr('src', tool + '.html'); }

  $('#inputbox').resize(function() {
    $('#output_div').css('top', $('#inputbox').height() + 60 + 'px');
  });
});




/*
 * jQuery resize event - v1.1 - 3/14/2010
 * http://benalman.com/projects/jquery-resize-plugin/
 * 
 * Copyright (c) 2010 "Cowboy" Ben Alman
 * Dual licensed under the MIT and GPL licenses.
 * http://benalman.com/about/license/
 */
(function($,h,c){var a=$([]),e=$.resize=$.extend($.resize,{}),i,k="setTimeout",j="resize",d=j+"-special-event",b="delay",f="throttleWindow";e[b]=250;e[f]=true;$.event.special[j]={setup:function(){if(!e[f]&&this[k]){return false}var l=$(this);a=a.add(l);$.data(this,d,{w:l.width(),h:l.height()});if(a.length===1){g()}},teardown:function(){if(!e[f]&&this[k]){return false}var l=$(this);a=a.not(l);l.removeData(d);if(!a.length){clearTimeout(i)}},add:function(l){if(!e[f]&&this[k]){return false}var n;function m(s,o,p){var q=$(this),r=$.data(this,d);r.w=o!==c?o:q.width();r.h=p!==c?p:q.height();n.apply(this,arguments)}if($.isFunction(l)){n=l;return m}else{n=l.handler;l.handler=m}}};function g(){i=h[k](function(){a.each(function(){var n=$(this),m=n.width(),l=n.height(),o=$.data(this,d);if(m!==o.w||l!==o.h){n.trigger(j,[o.w=m,o.h=l])}});g()},e[b])}})(jQuery,this);
