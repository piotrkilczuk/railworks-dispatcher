"function"!=typeof Object.create&&(Object.create=function(c){function d(){}d.prototype=c;return new d});
!function(c){var d=c.snack={},g=0,k=Object.prototype.toString,b=[].indexOf,a=[].push;d.extend=function(){if(1==arguments.length)return d.extend(d,arguments[0]);for(var h=arguments[0],a,f=1,b=arguments.length;f<b;f++)for(a in arguments[f])h[a]=arguments[f][a];return h};d.extend({v:"1.2.3",bind:function(h,e,f){f=f||[];return function(){a.apply(f,arguments);return h.apply(e,f)}},punch:function(h,a,f,b){var c=h[a];h[a]=b?function(){c.apply(h,arguments);return f.apply(h,arguments)}:function(){var a=[].slice.call(arguments,
0);a.unshift(d.bind(c,h));return f.apply(h,a)}},create:function(a,e){var b=Object.create(a);if(!e)return b;for(var c in e)e.hasOwnProperty(c)&&(a[c]&&"function"==typeof e[c]?d.punch(b,c,e[c]):b[c]=e[c]);return b},id:function(){return++g},each:function(a,e,b){if(void 0===a.length){for(var c in a)a.hasOwnProperty(c)&&e.call(b,a[c],c,a);return a}c=0;for(var g=a.length;c<g;c++)e.call(b,a[c],c,a);return a},parseJSON:function(a){if("string"==typeof a){a=a.replace(/^\s+|\s+$/g,"");if(!/^[\],:{}\s]*$/.test(a.replace(/\\(?:["\\\/bfnrt]|u[0-9a-fA-F]{4})/g,
"@").replace(/"[^"\\\n\r]*"|true|false|null|-?\d+(?:\.\d*)?(?:[eE][+\-]?\d+)?/g,"]").replace(/(?:^|:|,)(?:\s*\[)+/g,"")))throw"Invalid JSON";var b=c.JSON;return b&&b.parse?b.parse(a):(new Function("return "+a))()}},isArray:function(a){return a instanceof Array||"[object Array]"==k.call(a)},indexOf:b?function(a,c){return b.call(c,a)}:function(a,c){for(var b=0,g=c.length;b<g;b++)if(c[b]===a)return b;return-1}})}(window);
!function(c,d){var g={},k;c.wrap=function(b,a){"string"==typeof b&&(b=k(b,a));b.length||(b=[b]);for(var h=Object.create(g),e=0,f=b.length;e<f;e++)h[e]=b[e];h.length=f;h.id=c.id();return h};c.extend(c.wrap,{define:function(b,a){if("string"!=typeof b)for(var h in b)c.wrap.define(h,b[h]);else g[b]=a},defineEngine:function(c){k=c}});c.wrap.defineEngine(function(c,a){"string"==typeof a&&(a=d.querySelector(a));return(a||d).querySelectorAll(c)})}(snack,document);
!function(c,d,g){function k(){try{m.doScroll("left")}catch(a){setTimeout(k,50);return}b("poll")}function b(a){if("readystatechange"!=a.type||"complete"==g.readyState)("load"==a.type?d:g)[h](e+a.type,b,!1),!f&&(f=!0)&&c.each(n,function(a){a.apply(g)})}var a=g.addEventListener?"addEventListener":"attachEvent",h=g.addEventListener?"removeEventListener":"detachEvent",e=g.addEventListener?"":"on",f=!1,l=!0,m=g.documentElement,n=[];c.extend({stopPropagation:function(a){a.stopPropagation?a.stopPropagation():
a.cancelBubble=!0},preventDefault:function(a){a.preventDefault?a.preventDefault():a.returnValue=!1}});c.listener=function(b,f){b.delegate&&(b.capture=!0,_handler=f,f=function(a){for(var h=a.target||a.srcElement,e="string"==typeof b.delegate?c.wrap(b.delegate,b.node):b.delegate(b.node);h&&-1==c.indexOf(h,e);)h=h.parentNode;h&&h!==this&&h!==g&&_handler.call(h,a,h)});b.context&&(f=c.bind(f,b.context));var l={attach:function(){b.node[a](e+b.event,f,b.capture)},detach:function(){b.node[h](e+b.event,f,
b.capture)},fire:function(){f.apply(b.node,arguments)}};l.attach();return l};c.ready=function(a){f?a.apply(g):n.push(a)};if(g.createEventObject&&m.doScroll){try{l=!d.frameElement}catch(p){}l&&k()}g[a](e+"DOMContentLoaded",b,!1);g[a](e+"readystatechange",b,!1);d[a](e+"load",b,!1)}(snack,window,document);
!function(c){c.publisher=function(d){var g={};d=d||{};c.extend(d,{subscribe:function(d,b,a){var h={fn:b,ctxt:a||{}};g[d]||(g[d]=[]);a={attach:function(){g[d].push(h)},detach:function(){g[d].splice(c.indexOf(b,g[d]),1)}};a.attach();return a},publish:function(d,b){if(!g[d])return!1;c.each(g[d],function(a){a.fn.apply(a.ctxt,b||[])});return g[d].length}});return d};c.publisher(c)}(snack);
!function(c,d,g){function k(){}c.JSONP=function(a,b){var e="jsonp"+c.id(),f=g.createElement("script"),d=!1;c.JSONP[e]=function(a){d=!1;delete c.JSONP[e];b(a)};"object"==typeof a.data&&(a.data=c.toQueryString(a.data));var m={send:function(){d=!0;f.src=a.url+"?"+a.key+"=snack.JSONP."+e+"&"+a.data;g.getElementsByTagName("head")[0].appendChild(f)},cancel:function(){d&&f.parentNode&&f.parentNode.removeChild(f);d=!1;c.JSONP[e]=function(){delete c.JSONP[e]}}};!1!==a.now&&m.send();return m};c.toQueryString=
function(a,b){var e=[];c.each(a,function(a,d){b&&(d=b+"["+d+"]");var g;if(c.isArray(a)){var k={};c.each(a,function(a,b){k[b]=a});g=c.toQueryString(k,d)}else"object"==typeof a?g=c.toQueryString(a,d):g=d+"="+encodeURIComponent(a);null!==a&&e.push(g)});return e.join("&")};var b=function(){var a=function(){return new XMLHttpRequest},b=function(){return new ActiveXObject("MSXML2.XMLHTTP")},c=function(){return new ActiveXObject("Microsoft.XMLHTTP")};try{return a(),a}catch(f){try{return b(),b}catch(d){return c(),
c}}}();c.request=function(a,h){if(!(this instanceof c.request))return new c.request(a,h);this.options=c.extend({},this.options,a);this.callback=h;this.xhr=new b;this.headers=this.options.headers;!1!==this.options.now&&this.send()};c.request.prototype={options:{exception:k,url:"",data:"",method:"get",now:!0,headers:{"X-Requested-With":"XMLHttpRequest",Accept:"text/javascript, text/html, application/xml, text/xml, */*"},async:!0,emulation:!0,urlEncoded:!0,encoding:"utf-8"},onStateChange:function(){var a=
this.xhr;if(4==a.readyState&&this.running){this.running=!1;this.status=0;try{var b=a.status;this.status=1223==b?204:b}catch(c){}a.onreadystatechange=k;this.callback.apply(this,200<=this.status&&300>this.status?[!1,this.xhr.responseText||"",this.xhr.responseXML]:[this.status])}},setHeader:function(a,b){this.headers[a]=b;return this},getHeader:function(a){try{return this.xhr.getResponseHeader(a)}catch(b){return null}},send:function(){var a=this.options;if(this.running)return this;this.running=!0;var b=
a.data||"",e=String(a.url),f=a.method.toLowerCase();"string"!=typeof b&&(b=c.toQueryString(b));a.emulation&&0>c.indexOf(f,["get","post"])&&(f="_method="+f,b=b?f+"&"+b:f,f="post");a.urlEncoded&&-1<c.indexOf(f,["post","put"])&&(this.headers["Content-type"]="application/x-www-form-urlencoded"+(a.encoding?"; charset="+a.encoding:""));e||(e=g.location.pathname);var d=e.lastIndexOf("/");-1<d&&-1<(d=e.indexOf("#"))&&(e=e.substr(0,d));b&&"get"==f&&(e+=(-1<e.indexOf("?")?"&":"?")+b,b=null);d=this.xhr;d.open(f.toUpperCase(),
e,open.async,a.user,a.password);a.user&&"withCredentials"in d&&(d.withCredentials=!0);d.onreadystatechange=c.bind(this.onStateChange,this);for(var k in this.headers)try{d.setRequestHeader(k,this.headers[k])}catch(n){a.exception.apply(this,[k,this.headers[k]])}d.send(b);a.async||this.onStateChange();return this},cancel:function(){if(!this.running)return this;this.running=!1;var a=this.xhr;a.abort();a.onreadystatechange=k;this.xhr=new b;return this}}}(snack,window,document);
!function(c,d){function g(b,a,d,e){(d=b.data(d))&&c.each(d,function(c){c[a].apply(b,e)});return b}function k(b){return b.replace(/\s+/g," ").replace(/^\s+|\s+$/g,"")}c.wrap.define({data:function(){var b={};return function(a,c){var d=b[this.id];d||(d=b[this.id]={});return void 0===c?d[a]:d[a]=c}}(),each:function(b,a){return c.each(this,b,a)},addClass:function(b){return this.each(function(a){-1<k(a.className).indexOf(b)||(a.className=k(a.className+" "+b))})},removeClass:function(b){return this.each(function(a){a.className=
a.className.replace(new RegExp("(^|\\s)"+b+"(?:\\s|$)"),"$1")})},attach:function(b,a,d){var e=b.split("."),f=[];e[1]&&(f=this.data(e[1])||[]);this.each(function(b){b={node:b,event:e[0]};d&&(b.delegate=d);f.push(c.listener(b,a))});e[1]&&this.data(e[1],f);return this},detach:function(b){g(this,"detach",b,null,!0);this.data(b,null);return this},fire:function(b,a){return g(this,"fire",b,a)},delegate:function(b,a,c){return this.attach(b,c,a)}})}(snack,document);function handleClick(){1<this.classList.length?snack.wrap(this).removeClass("collapsed"):snack.wrap(this).addClass("collapsed")}snack.wrap("article").each(function(c,d){snack.listener({node:c,event:"click"},handleClick)});