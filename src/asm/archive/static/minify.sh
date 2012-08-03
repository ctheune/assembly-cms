#!/bin/sh

YUI_JAR=/usr/share/yui-compressor/yui-compressor.jar
java -Xss51200k -jar "$YUI_JAR" -o css/style-min.css css/style.css
cat css/reset.css css/960.css css/text.css css/style-min.css > allstyles-min.css

java -Xss51200k -jar "$YUI_JAR" -o js/archive-min.js js/archive.js
cat js/jquery-1.6.2.min.js js/html5placeholder-1.01.jquery.min.js js/archive-min.js > allscripts-min.js
