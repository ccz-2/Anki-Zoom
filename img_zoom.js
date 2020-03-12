//Anki Zoom v1.2
var timer;
$("body").on('DOMSubtreeModified', '#qa', function() {
  clearTimeout(timer);
  timer = setTimeout(function(){
    applyImgZoom();
  }, 50); //prevents overzealous updates, since selector grabs multiple events per card change
});

var imgZoomEnabled = true;
function applyImgZoom() {
  $('#qa img').each(function() {
    var instance = $(this).data('xzoom');
    if (!!instance) { //if already exists, skip
      return
    }
    src = $(this).attr("src");
    $(this).attr("xoriginal", src)
    var instance = $(this).xzoom({
        zoomWidth: Number.MAX_SAFE_INTEGER,
        zoomHeight: Number.MAX_SAFE_INTEGER,
        position: 'inside',
        defaultScale: 2,
        lens: "#ffffff",
        smoothZoomMove: 3,
        smoothScale: 6,
        lensCollision: true,
        hover: true,
    });
    instance.eventunbind();
    $(this).click(event, function() {
        var instance = $(this).data('xzoom');
        if ($('*').hasClass('xzoom-source')){
            instance.eventunbind()
            instance.closezoom()
        } else if (imgZoomEnabled){
            instance.eventdefault()
            instance.openzoom(event)
        }
    });
  });
};

function enableImgZoom() {
  console.log('enabled')
  imgZoomEnabled = true;
};

function disableImgZoom() {
  imgZoomEnabled = false;
};

function stopAllZoom() {
    $('.xzoom-source').remove();
};



$('head').append(`
<style>
/* Compatibility styles for frameworks like bootstrap, foundation e.t.c */
.xzoom-source img, .xzoom-preview img, .xzoom-lens img {
  display: block;
  max-width: none;
  max-height: none;
  margin: 0px;
  width: auto;
  height: auto;
  -webkit-transition: none;
  -moz-transition: none;
  -o-transition: none;
  transition: none;
}
/* --------------- */

/* xZoom Styles below */
.xzoom-container { 
  display: inline-block;
}

.xzoom-thumbs {
  text-align: center;
  margin-bottom: 10px;
}

.xzoom, .xzoom2, .xzoom3, .xzoom4, .xzoom5 { 
  -webkit-box-shadow: 0px 0px 5px 0px rgba(74,169,210,1);
  -moz-box-shadow: 0px 0px 5px 0px rgba(74,169,210,1);
  box-shadow: 0px 0px 5px 0px rgba(74,169,210,1);
}

/* Thumbs */
.xzoom-gallery, .xzoom-gallery2, .xzoom-gallery3, .xzoom-gallery4, .xzoom-gallery5 {
  border: 1px solid #cecece;
  margin-left: 5px;
  margin-bottom: 10px;
}

.xzoom-source, .xzoom-hidden {
  display: block;
  position: static;
  float: none;
  clear: both;
}

/* Everything out of border is hidden */
.xzoom-hidden {
  overflow: hidden;
}

/* Preview */
.xzoom-preview {
  border: 1px solid #888;
  background: rgba(0,0,0,0);
  box-shadow: -0px -0px 15px rgba(74,169,210,1);
}

/* Lens */
.xzoom-lens {
  border: 1px solid #555;
  box-shadow: -0px -0px 10px rgba(0,0,0,0.50);
  cursor: crosshair;
}

/* Loading */
.xzoom-loading {
  background-position: center center;
  background-repeat: no-repeat;
  border-radius: 100%;
  opacity: .7;
  background: url(../images/xloading.gif);
  width: 48px;
  height: 48px;
}

/* Additional class that applied to thumb when it is active */
.xactive {
  -webkit-box-shadow: 0px 0px 3px 0px rgba(74,169,210,1);
  -moz-box-shadow: 0px 0px 3px 0px rgba(74,169,210,1);
  box-shadow: 0px 0px 3px 0px rgba(74,169,210,1); 
  border: 1px solid #4aaad2;
}

/* Caption */
.xzoom-caption {
  position: absolute;
  bottom: -43px;
  left: 0;
  background: #000;
  width: 100%;
  text-align: left;
}

.xzoom-caption span {
  color: #fff;
  font-family: Arial, sans-serif;
  display: block;
  font-size: 0.75em;
  font-weight: bold;
  padding: 10px;
}
</style>`);