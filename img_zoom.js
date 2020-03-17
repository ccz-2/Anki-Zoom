//Anki Zoom v1.2

//var timer;
//$("body").on('DOMSubtreeModified', '#qa', function() {
//  clearTimeout(timer);
//  timer = setTimeout(function(){
//    applyImgZoom();
//  }, 50); //prevents overzealous updates, since selector grabs multiple events per card change
//});
var instance
function enableImgZoom() {
  $(document).ready(function() {
    $("head").wrap(`<style>
      .canvas {
        position: absolute;
        width:100%;
        height:100%;
      }
      </style>`)
    $("#qa").wrap("<div class='canvas'></div>")

    var element = document.querySelector('.canvas')
    instance = panzoom(element);

    var rmbDown = false;
    instance.pause();

    $(document).keydown(function(event){
        if (event.keyCode == 18){ //alt
          instance.resume();
        }
      });
    $(document).keyup(function(event){
        if (event.keyCode == 18){ //alt
          instance.pause();
        }
      });
    document.addEventListener('mousedown', function(event){
       if (event.button == 2 && !rmbDown){ //RMB
        rmbDown = true;
        instance.resume();
        new_event = new MouseEvent(event.type, event)
        new_event.repeat = true;
        element.dispatchEvent(new_event);
      }
    });
    document.addEventListener('mouseup', function(event){
     if (event.button == 2){
      rmbDown = false;
      if (!event.altKey){
        instance.pause()
      }}
    });
  });
};

function disableImgZoom() {
  if (instance != null) {
    instance.dispose();
  }
}



