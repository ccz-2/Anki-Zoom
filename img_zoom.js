//Anki Zoom v1.2

var instance
var element
var disabled


$(document).ready(function() {
  $("head").wrap(`<style>
    .canvas {
      position: absolute;
      width:100%;
      height:100%;
    }
    body:focus {
      outline: none;
    }
    body: {
      width: 100vw;
      height: 100vh;
      overflow: hidden;
    }
    </style>`)
});
    //$("#qa").wrap("<div class='canvas'></div>")


    function enableImgZoom() {
      applyZoom();
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

    };

    function applyZoom() {
      element = document.querySelector('#qa')
      instance = panzoom(element, {
        minZoom: 1,
        bounds: true,
        boundsPadding: 1
      });
    }

    function disableImgZoom() {
      disabled = true;
      if (instance != null) {
        instance.pause();
      }
    }



