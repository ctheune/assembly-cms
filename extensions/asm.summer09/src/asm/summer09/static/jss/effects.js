// Copyright (c) 2005 Thomas Fuchs (http://script.aculo.us, http://mir.aculo.us)
// Contributors:
//  Justin Palmer (http://encytemedia.com/)
//  Mark Pilgrim (http://diveintomark.org/)
//  Martin Bialasinki
// 
// See scriptaculous.js for full license.  

// converts rgb() and #xxx to #xxxxxx format,  
// returns self (or first argument) if not convertable  
String.prototype.parseColor = function() {  
  var color = '#';  
  if(this.slice(0,4) == 'rgb(') {  
    var cols = this.slice(4,this.length-1).split(',');  
    var i=0; do { color += parseInt(cols[i]).toColorPart() } while (++i<3);  
  } else {  
    if(this.slice(0,1) == '#') {  
      if(this.length==4) for(var i=1;i<4;i++) color += (this.charAt(i) + this.charAt(i)).toLowerCase();  
      if(this.length==7) color = this.toLowerCase();  
    }  
  }  
  return(color.length==7 ? color : (arguments[0] || this));  
}

/*--------------------------------------------------------------------------*/

Element.collectTextNodes = function(element) {  
  return $A($(element).childNodes).collect( function(node) {
    return (node.nodeType==3 ? node.nodeValue : 
      (node.hasChildNodes() ? Element.collectTextNodes(node) : ''));
  }).flatten().join('');
}

Element.collectTextNodesIgnoreClass = function(element, className) {  
  return $A($(element).childNodes).collect( function(node) {
    return (node.nodeType==3 ? node.nodeValue : 
      ((node.hasChildNodes() && !Element.hasClassName(node,className)) ? 
        Element.collectTextNodesIgnoreClass(node, className) : ''));
  }).flatten().join('');
}

Element.setContentZoom = function(element, percent) {
  element = $(element);  
  Element.setStyle(element, {fontSize: (percent/100) + 'em'});   
  if(navigator.appVersion.indexOf('AppleWebKit')>0) window.scrollBy(0,0);
}

Element.getOpacity = function(element){  
  var opacity;
  if (opacity = Element.getStyle(element, 'opacity'))  
    return parseFloat(opacity);  
  if (opacity = (Element.getStyle(element, 'filter') || '').match(/alpha\(opacity=(.*)\)/))  
    if(opacity[1]) return parseFloat(opacity[1]) / 100;  
  return 1.0;  
}

Element.setOpacity = function(element, value){  
  element= $(element);  
  if (value == 1){
    Element.setStyle(element, { opacity: 
      (/Gecko/.test(navigator.userAgent) && !/Konqueror|Safari|KHTML/.test(navigator.userAgent)) ? 
      0.999999 : null });
    if(/MSIE/.test(navigator.userAgent))  
      Element.setStyle(element, {filter: Element.getStyle(element,'filter').replace(/alpha\([^\)]*\)/gi,'')});  
  } else {  
    if(value < 0.00001) value = 0;  
    Element.setStyle(element, {opacity: value});
    if(/MSIE/.test(navigator.userAgent))  
     Element.setStyle(element, 
       { filter: Element.getStyle(element,'filter').replace(/alpha\([^\)]*\)/gi,'') +
                 'alpha(opacity='+value*100+')' });  
  }
}  
 
Element.getInlineOpacity = function(element){  
  return $(element).style.opacity || '';
}  

Element.childrenWithClassName = function(element, className, findFirst) {
  var classNameRegExp = new RegExp("(^|\\s)" + className + "(\\s|$)");
  var results = $A($(element).getElementsByTagName('*'))[findFirst ? 'detect' : 'select']( function(c) { 
    return (c.className && c.className.match(classNameRegExp));
  });
  if(!results) results = [];
  return results;
}

Element.forceRerendering = function(element) {
  try {
    element = $(element);
    var n = document.createTextNode(' ');
    element.appendChild(n);
    element.removeChild(n);
  } catch(e) { }
};

/*--------------------------------------------------------------------------*/

Array.prototype.call = function() {
  var args = arguments;
  this.each(function(f){ f.apply(this, args) });
}

/*--------------------------------------------------------------------------*/

var Effect = {
  tagifyText: function(element) {
    var tagifyStyle = 'position:relative';
    if(/MSIE/.test(navigator.userAgent)) tagifyStyle += ';zoom:1';
    element = $(element);
    $A(element.childNodes).each( function(child) {
      if(child.nodeType==3) {
        child.nodeValue.toArray().each( function(character) {
          element.insertBefore(
            Builder.node('span',{style: tagifyStyle},
              character == ' ' ? String.fromCharCode(160) : character), 
              child);
        });
        Element.remove(child);
      }
    });
  },
  multiple: function(element, effect) {
    var elements;
    if(((typeof element == 'object') || 
        (typeof element == 'function')) && 
       (element.length))
      elements = element;
    else
      elements = $(element).childNodes;
      
    var options = Object.extend({
      speed: 0.1,
      delay: 0.0
    }, arguments[2] || {});
    var masterDelay = options.delay;

    $A(elements).each( function(element, index) {
      new effect(element, Object.extend(options, { delay: index * options.speed + masterDelay }));
    });
  },
  PAIRS: {
    'slide':  ['SlideDown','SlideUp'],
    'blind':  ['BlindDown','BlindUp'],
    'appear': ['Appear','Fade']
  },
  toggle: function(element, effect) {
    element = $(element);
    effect = (effect || 'appear').toLowerCase();
    var options = Object.extend({
      queue: { position:'end', scope:(element.id || 'global'), limit: 1 }
    }, arguments[2] || {});
    Effect[element.visible() ? 
      Effect.PAIRS[effect][1] : Effect.PAIRS[effect][0]](element, options);
  }
};

var Effect2 = Effect; // deprecated

/* ------------- transitions ------------- */

Effect.Transitions = {}

Effect.Transitions.linear = function(pos) {
  return pos;
}
Effect.Transitions.sinoidal = function(pos) {
  return (-Math.cos(pos*Math.PI)/2) + 0.5;
}
Effect.Transitions.reverse  = function(pos) {
  return 1-pos;
}
Effect.Transitions.flicker = function(pos) {
  return ((-Math.cos(pos*Math.PI)/4) + 0.75) + Math.random()/4;
}
Effect.Transitions.wobble = function(pos) {
  return (-Math.cos(pos*Math.PI*(9*pos))/2) + 0.5;
}
Effect.Transitions.pulse = function(pos) {
  return (Math.floor(pos*10) % 2 == 0 ? 
    (pos*10-Math.floor(pos*10)) : 1-(pos*10-Math.floor(pos*10)));
}
Effect.Transitions.none = function(pos) {
  return 0;
}
Effect.Transitions.full = function(pos) {
  return 1;
}

/* ------------- core effects ------------- */

Effect.ScopedQueue = Class.create();
Object.extend(Object.extend(Effect.ScopedQueue.prototype, Enumerable), {
  initialize: function() {
    this.effects  = [];
    this.interval = null;
  },
  _each: function(iterator) {
    this.effects._each(iterator);
  },
  add: function(effect) {
    var timestamp = new Date().getTime();
    
    var position = (typeof effect.options.queue == 'string') ? 
      effect.options.queue : effect.options.queue.position;
    
    switch(position) {
      case 'front':
        // move unstarted effects after this effect  
        this.effects.findAll(function(e){ return e.state=='idle' }).each( function(e) {
            e.startOn  += effect.finishOn;
            e.finishOn += effect.finishOn;
          });
        break;
      case 'end':
        // start effect after last queued effect has finished
        timestamp = this.effects.pluck('finishOn').max() || timestamp;
        break;
    }
    
    effect.startOn  += timestamp;
    effect.finishOn += timestamp;

    if(!effect.options.queue.limit || (this.effects.length < effect.options.queue.limit))
      this.effects.push(effect);
    
    if(!this.interval) 
      this.interval = setInterval(this.loop.bind(this), 40);
  },
  remove: function(effect) {
    this.effects = this.effects.reject(function(e) { return e==effect });
    if(this.effects.length == 0) {
      clearInterval(this.interval);
      this.interval = null;
    }
  },
  loop: function() {
    var timePos = new Date().getTime();
    this.effects.invoke('loop', timePos);
  }
});

Effect.Queues = {
  instances: $H(),
  get: function(queueName) {
    if(typeof queueName != 'string') return queueName;
    
    if(!this.instances[queueName])
      this.instances[queueName] = new Effect.ScopedQueue();
      
    return this.instances[queueName];
  }
}
Effect.Queue = Effect.Queues.get('global');

Effect.DefaultOptions = {
  transition: Effect.Transitions.sinoidal,
  duration:   1.0,   // seconds
  fps:        25.0,  // max. 25fps due to Effect.Queue implementation
  sync:       false, // true for combining
  from:       0.0,
  to:         1.0,
  delay:      0.0,
  queue:      'parallel'
}

Effect.Base = function() {};
Effect.Base.prototype = {
  position: null,
  start: function(options) {
    this.options      = Object.extend(Object.extend({},Effect.DefaultOptions), options || {});
    this.currentFrame = 0;
    this.state        = 'idle';
    this.startOn      = this.options.delay*1000;
    this.finishOn     = this.startOn + (this.options.duration*1000);
    this.event('beforeStart');
    if(!this.options.sync)
      Effect.Queues.get(typeof this.options.queue == 'string' ? 
        'global' : this.options.queue.scope).add(this);
  },
  loop: function(timePos) {
    if(timePos >= this.startOn) {
      if(timePos >= this.finishOn) {
        this.render(1.0);
        this.cancel();
        this.event('beforeFinish');
        if(this.finish) this.finish(); 
        this.event('afterFinish');
        return;  
      }
      var pos   = (timePos - this.startOn) / (this.finishOn - this.startOn);
      var frame = Math.round(pos * this.options.fps * this.options.duration);
      if(frame > this.currentFrame) {
        this.render(pos);
        this.currentFrame = frame;
      }
    }
  },
  render: function(pos) {
    if(this.state == 'idle') {
      this.state = 'running';
      this.event('beforeSetup');
      if(this.setup) this.setup();
      this.event('afterSetup');
    }
    if(this.state == 'running') {
      if(this.options.transition) pos = this.options.transition(pos);
      pos *= (this.options.to-this.options.from);
      pos += this.options.from;
      this.position = pos;
      this.event('beforeUpdate');
      if(this.update) this.update(pos);
      this.event('afterUpdate');
    }
  },
  cancel: function() {
    if(!this.options.sync)
      Effect.Queues.get(typeof this.options.queue == 'string' ? 
        'global' : this.options.queue.scope).remove(this);
    this.state = 'finished';
  },
  event: function(eventName) {
    if(this.options[eventName + 'Internal']) this.options[eventName + 'Internal'](this);
    if(this.options[eventName]) this.options[eventName](this);
  },
  inspect: function() {
    return '#<Effect:' + $H(this).inspect() + ',options:' + $H(this.options).inspect() + '>';
  }
}

Effect.Parallel = Class.create();
Object.extend(Object.extend(Effect.Parallel.prototype, Effect.Base.prototype), {
  initialize: function(effects) {
    this.effects = effects || [];
    this.start(arguments[1]);
  },
  update: function(position) {
    this.effects.invoke('render', position);
  },
  finish: function(position) {
    this.effects.each( function(effect) {
      effect.render(1.0);
      effect.cancel();
      effect.event('beforeFinish');
      if(effect.finish) effect.finish(position);
      effect.event('afterFinish');
    });
  }
});

Effect.Opacity = Class.create();
Object.extend(Object.extend(Effect.Opacity.prototype, Effect.Base.prototype), {
  initialize: function(element) {
    this.element = $(element);
    // make this work on IE on elements without 'layout'
    if(/MSIE/.test(navigator.userAgent) && (!this.element.hasLayout))
      this.element.setStyle({zoom: 1});
    var options = Object.extend({
      from: this.element.getOpacity() || 0.0,
      to:   1.0
    }, arguments[1] || {});
    this.start(options);
  },
  update: function(position) {
    this.element.setOpacity(position);
  }
});

Effect.Move = Class.create();
Object.extend(Object.extend(Effect.Move.prototype, Effect.Base.prototype), {
  initialize: function(element) {
    this.element = $(element);
    var options = Object.extend({
      x:    0,
      y:    0,
      mode: 'relative'
    }, arguments[1] || {});
    this.start(options);
  },
  setup: function() {
    // Bug in Opera: Opera returns the "real" position of a static element or
    // relative element that does not have top/left explicitly set.
    // ==> Always set top and left for position relative elements in your stylesheets 
    // (to 0 if you do not need them) 
    this.element.makePositioned();
    this.originalLeft = parseFloat(this.element.getStyle('left') || '0');
    this.originalTop  = parseFloat(this.element.getStyle('top')  || '0');
    if(this.options.mode == 'absolute') {
      // absolute movement, so we need to calc deltaX and deltaY
      this.options.x = this.options.x - this.originalLeft;
      this.options.y = this.options.y - this.originalTop;
    }
  },
  update: function(position) {
    this.element.setStyle({
      left: this.options.x  * position + this.originalLeft + 'px',
      top:  this.options.y  * position + this.originalTop  + 'px'
    });
  }
});

// for backwards compatibility
Effect.MoveBy = function(element, toTop, toLeft) {
  return new Effect.Move(element, 
    Object.extend({ x: toLeft, y: toTop }, arguments[3] || {}));
};

Effect.Scale = Class.create();
Object.extend(Object.extend(Effect.Scale.prototype, Effect.Base.prototype), {
  initialize: function(element, percent) {
    this.element = $(element)
    var options = Object.extend({
      scaleX: true,
      scaleY: true,
      scaleContent: true,
      scaleFromCenter: false,
      scaleMode: 'box',        // 'box' or 'contents' or {} with provided values
      scaleFrom: 100.0,
      scaleTo:   percent
    }, arguments[2] || {});
    this.start(options);
  },
  setup: function() {
    this.restoreAfterFinish = this.options.restoreAfterFinish || false;
    this.elementPositioning = this.element.getStyle('position');
    
    this.originalStyle = {};
    ['top','left','width','height','fontSize'].each( function(k) {
      this.originalStyle[k] = this.element.style[k];
    }.bind(this));
      
    this.originalTop  = this.element.offsetTop;
    this.originalLeft = this.element.offsetLeft;
    
    var fontSize = this.element.getStyle('font-size') || '100%';
    ['em','px','%'].each( function(fontSizeType) {
      if(fontSize.indexOf(fontSizeType)>0) {
        this.fontSize     = parseFloat(fontSize);
        this.fontSizeType = fontSizeType;
      }
    }.bind(this));
    
    this.factor = (this.options.scaleTo - this.options.scaleFrom)/100;
    
    this.dims = null;
    if(this.options.scaleMode=='box')
      this.dims = [this.element.offsetHeight, this.element.offsetWidth];
    if(/^content/.test(this.options.scaleMode))
      this.dims = [this.element.scrollHeight, this.element.scrollWidth];
    if(!this.dims)
      this.dims = [this.options.scaleMode.originalHeight,
                   this.options.scaleMode.originalWidth];
  },
  update: function(position) {
    var currentScale = (this.options.scaleFrom/100.0) + (this.factor * position);
    if(this.options.scaleContent && this.fontSize)
      this.element.setStyle({fontSize: this.fontSize * currentScale + this.fontSizeType });
    this.setDimensions(this.dims[0] * currentScale, this.dims[1] * currentScale);
  },
  finish: function(position) {
    if (this.restoreAfterFinish) this.element.setStyle(this.originalStyle);
  },
  setDimensions: function(height, width) {
    var d = {};
    if(this.options.scaleX) d.width = width + 'px';
    if(this.options.scaleY) d.height = height + 'px';
    if(this.options.scaleFromCenter) {
      var topd  = (height - this.dims[0])/2;
      var leftd = (width  - this.dims[1])/2;
      if(this.elementPositioning == 'absolute') {
        if(this.options.scaleY) d.top = this.originalTop-topd + 'px';
        if(this.options.scaleX) d.left = this.originalLeft-leftd + 'px';
      } else {
        if(this.options.scaleY) d.top = -topd + 'px';
        if(this.options.scaleX) d.left = -leftd + 'px';
      }
    }
    this.element.setStyle(d);
  }
});

Effect.Highlight = Class.create();
Object.extend(Object.extend(Effect.Highlight.prototype, Effect.Base.prototype), {
  initialize: function(element) {
    this.element = $(element);
    var options = Object.extend({ startcolor: '#ffff99' }, arguments[1] || {});
    this.start(options);
  },
  setup: function() {
    // Prevent executing on elements not in the layout flow
    if(this.element.getStyle('display')=='none') { this.cancel(); return; }
    // Disable background image during the effect
    this.oldStyle = {
      backgroundImage: this.element.getStyle('background-image') };
    this.element.setStyle({backgroundImage: 'none'});
    if(!this.options.endcolor)
      this.options.endcolor = this.element.getStyle('background-color').parseColor('#ffffff');
    if(!this.options.restorecolor)
      this.options.restorecolor = this.element.getStyle('background-color');
    // init color calculations
    this._base  = $R(0,2).map(function(i){ return parseInt(this.options.startcolor.slice(i*2+1,i*2+3),16) }.bind(this));
    this._delta = $R(0,2).map(function(i){ return parseInt(this.options.endcolor.slice(i*2+1,i*2+3),16)-this._base[i] }.bind(this));
  },
  update: function(position) {
    this.element.setStyle({backgroundColor: $R(0,2).inject('#',function(m,v,i){
      return m+(Math.round(this._base[i]+(this._delta[i]*position)).toColorPart()); }.bind(this)) });
  },
  finish: function() {
    this.element.setStyle(Object.extend(this.oldStyle, {
      backgroundColor: this.options.restorecolor
    }));
  }
});

Effect.ScrollTo = Class.create();
Object.extend(Object.extend(Effect.ScrollTo.prototype, Effect.Base.prototype), {
  initialize: function(element) {
    this.element = $(element);
    this.start(arguments[1] || {});
  },
  setup: function() {
    Position.prepare();
    var offsets = Position.cumulativeOffset(this.element);
    if(this.options.offset) offsets[1] += this.options.offset;
    var max = window.innerHeight ? 
      window.height - window.innerHeight :
      document.body.scrollHeight - 
        (document.documentElement.clientHeight ? 
          document.documentElement.clientHeight : document.body.clientHeight);
    this.scrollStart = Position.deltaY;
    this.delta = (offsets[1] > max ? max : offsets[1]) - this.scrollStart;
  },
  update: function(position) {
    Position.prepare();
    window.scrollTo(Position.deltaX, 
      this.scrollStart + (position*this.delta));
  }
});

/* ------------- combination effects ------------- */

Effect.BlindUp = function(element) {
  element = $(element);
  element.makeClipping();
  return new Effect.Scale(element, 0, 
    Object.extend({ scaleContent: false, 
      scaleX: false, 
      restoreAfterFinish: true,
      afterFinishInternal: function(effect) {
        effect.element.hide();
        effect.element.undoClipping();
      } 
    }, arguments[1] || {})
  );
}

Effect.BlindDown = function(element) {
  element = $(element);
  var elementDimensions = element.getDimensions();
  return new Effect.Scale(element, 100, 
    Object.extend({ scaleContent: false, 
      scaleX: false,
      scaleFrom: 0,
      scaleMode: {originalHeight: elementDimensions.height, originalWidth: elementDimensions.width},
      restoreAfterFinish: true,
      afterSetup: function(effect) {
        effect.element.makeClipping();
        effect.element.setStyle({height: '0px'});
        effect.element.show(); 
      },  
      afterFinishInternal: function(effect) {
        effect.element.undoClipping();
      }
    }, arguments[1] || {})
  );
}



Element.Methods.visualEffect = function(element, effect, options) {
  s = effect.gsub(/_/, '-').camelize();
  effect_class = s.charAt(0).toUpperCase() + s.substring(1);
  new Effect[effect_class](element, options);
  return $(element);
};

Element.addMethods();
