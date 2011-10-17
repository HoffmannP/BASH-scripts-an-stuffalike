/*
#content_wrapper > .content > .main_content > .box_columns .clear_fix > .column_02 >
	* box_title
	* bloc_grey_lowlight_wrapper
	* box_article doc_page

*/
var keepCSS = new Array("reset", "base", "common", "doc");

/*
Node.prototype.setAnAttribute = function(a,v){this.setAttribute(a,v);return this;}
document.getElementsByTagName("body")[0].appendChild(
    document
		.createElement("script")
		.setAnAttribute("src", "file:///home/ber/bin/clearPages.js")
		.setAnAttribute("type", "text/javascript")
);
body
  .clearLevel("#content_wrapper")
  .clearLevel(".content")
  .clearLevel(".main_content")
  .clearLevel(".box_columns")
  .clearLevel(".column_02");
*/

String.prototype.sub = function(begin, end) {
	if (end === null) { end = this.length);          }
	if (begin <  0)   { begin = this.length + begin; }
	if (end <= 0)     { end = this.length + end;     }
	if (begin < 1)    { begin = end - 1/begin;       }
	if (end < 1)      { end = begin + 1/end;         }
	return this.substring(begin, end);
}
Node.prototype.checkAttr = function(attr, value) {
	return  this.hasAttributes(attr) && (this.getAttribute(attr) == value);
}
Node.prototype.checkClass = function(value){
	if (!this.hasAttribute || !this.hasAttribute("class")) {
		return false;
	}
	return this.getAttribute("class").split(" ").in(value); 
}
Node.prototype.checkId    = function(value){return this.checkAttr("id",    value);}
Node.prototype.check      = function(value) {
	if (!(this instanceof Node)) {
		return false;
	}
	switch (value[0]) {
	case ".": 
		return this.checkClass(value.substr(1));
 	case "#":
		return this.checkId(value.substr(1));
	case "[":
		value = value.sub(1, -1).split("=");
		if (value.length == 1) {
			return this.hasAttribute(value[0]);
		}
		switch (value[0].sub(-1)) {
		case "~":
			return (this.hasAttribute(value[0].sub(0, -1)) && 
                    this.getAttribute(value[0].sub(0, -1)).split(" ").in(value[1]));
		case "|":
			return (this.hasAttribute(value[0].sub(0, -1)) && (
				this.getAttribute(value[0].sub(0, -1)) == value[1] ||
				this.getAttribute(value[0].sub(0, -1)).sub(0, value[1].length+1)
					== value[1] + "-"
			    )
                   );
		default:
			return (this.hasAttribute(value[0]) &&
					this.getAttribute(value[0]).indexOf(value[1]) != -1);
		}
	default:
		return this.nodeName == value.toUpperCase();
	}
}
Node.prototype.mcheck = function() {
} 
Node.prototype.iterateChilds = function(onAll, arguments) {
	var child = this.firstChild, next;
	if (!(arguments instanceof Array)) {
		arguments = [arguments];
	}
	while (child) {
		next = child.nextSibling;
		onAll.apply(child, arguments);
		child = next;
	}
	return this;
}
Node.prototype.remove = function() {
	this.parentNode.removeChild(this);
}
Node.prototype.deleteIf = function(check, against) {
	if (!check.apply(this, [against])) {
		this.remove();
	}
}
Array.prototype.in = function(ele) {
	for (var i=0; i<this.length; i++) {
		if (this[i] == ele) {
			return true;
		}
	}
	return false;
}
Node.prototype.filename = function() {
	if ((this.nodeType != 1) || (this.nodeName != "LINK")) {
		return false;
	}
	var uri = this.getAttribute("href").split("/");
	return uri[uri.length-1].split(".")[0];
}
var clearCSS = function (keepCSS) {
	var css = document.getElementsByTagName("link");
	for (var i=0; i < css.length; i++) {
		var fn = css[i].filename();
		if (keepCSS.in(css[i].filename())) {
			css[i].remove();
		}
	}
}
var body = document.getElementsByTagName("body")[0];
Node.prototype.clearLevel = function(attr) {
	this.iterateChilds(
		Node.prototype.deleteIf,
		[
			Node.prototype.check,
			attr
		]
	);
	return this.firstChild;
}
var clearBody = function () {
	document.getElementsByTagName("body")[0]
		.clearLevel("#content_wrapper")
		.clearLevel(".content")
		.clearLevel(".main_content")
		.clearLevel(".box_columns clear_fix")
		.clearLevel(".column_02");
}
function clear() {
	clearCSS(keepCSS);
	clearBody();
}
