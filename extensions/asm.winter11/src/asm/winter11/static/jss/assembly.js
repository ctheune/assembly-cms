
// ASSEMBLY-overlay
$(document).ready(function(){
    
});

//$(function() {
//// find wrap		
//	$("#live.wrap #livestream").overlay({
//
//		expose: {
//			opacity: 0.9,
//			color: '#000'   
//		},
//		
//		// load iframe
//		onLoad: function() {
//			var wrap = this.getContent().find("div.contentWrap");
//			wrap.load(this.getTrigger().attr("href"));
//		},
//	
//		onClose: function() {
//			var wrap = this.getContent().find("div.contentWrap");
//			wrap2.unload(); 
//		} 
//	});	
//});

$(document).ready(function(){
    
});

$(function() {
   // if the function argument is given to overlay,
   // it is assumed to be the onBeforeLoad event listener
   $("#livestream").overlay({
        mask: 'black',
        onBeforeLoad: function() {
            // grab wrapper element inside content
            var wrap = this.getOverlay().find(".wrap");
            // load the page specified in the trigger
            wrap.load(this.getTrigger().attr("href"));
        }
    });
});


// Rotate News
$(function() { 
    var rotateDelay = 20000; //milliseconds 
    var rotateTabs=true;     
    var $tabItems = $('.tabs a').click(function(){ //clicking a tab should cancel the rotate 
        rotateTabs=false; 
    }); 
    var tabs = $("div.tabs").tabs('.newsitem', {api:true, current: 'active'}); //create the tabs and return the api 
    function doRotateTabs(){ //recursive function 
        if (rotateTabs) { 
            setTimeout(function(){ 
                if (!rotateTabs) return; 
                if(tabs.getIndex() == $tabItems.length-1){ //last tab. restart on first tab 
                    tabs.click(0); 
                } 
                else { 
                    tabs.next(); 
                } 
                doRotateTabs(); 
            }, rotateDelay); 
        } 
    } 
    doRotateTabs(); 
}); 

// Count-down
var target;
function startClock() {
    target = document.getElementById('clock').getAttribute('alt');
    setTimeout('updateClock()',3000);
}

function updateClock() {
  var now = new Date();
  var diff = Math.floor((target-now)/1000);
  if (diff < 0) { diff=0; }
  document.getElementById('clock_days').innerHTML=Math.floor(diff/86400);
  diff = diff % 86400;
  document.getElementById('clock_hours').innerHTML=Math.floor(diff/3600);
  diff = diff % 3600;
  document.getElementById('clock_minutes').innerHTML=Math.floor(diff/60);
  if (diff > 0) { setTimeout('updateClock()', 60000); }
}

