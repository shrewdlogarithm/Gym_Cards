var width = 1280;    
var height = 0;     
var streaming = false;
var video = null;
var canvas = null;

function startup() {
  video = document.getElementById('video');
  canvas = document.createElement("CANVAS")

  navigator.mediaDevices.getUserMedia(
    {
      video: {width: {exact: 1280}, height: {exact: 720}}
    }
  )
  .then(function(stream) {
    video.srcObject = stream;
    video.play();
  })
  .catch(function(err) {
    console.log("An error occurred: " + err);
  });

  video.addEventListener('canplay', function(ev){
    if (!streaming) {
      height = video.videoHeight / (video.videoWidth/width);
      if (isNaN(height)) {
        height = width / (4/3);
      }
      video.setAttribute('width', width);
      video.setAttribute('height', height);
      canvas.setAttribute('width', width);
      canvas.setAttribute('height', height);
      streaming = true;
    }
  }, false);

}

function takepicture(memno) {
  var context = canvas.getContext('2d');
  if (width && height) {
    canvas.width = video.height;
    canvas.height = video.width;
    context.translate(canvas.width * 0.5, canvas.height * 0.5);
    context.rotate(Math.PI/180*90);
    context.translate(-video.width * 0.5, -video.height * 0.5);
    context.drawImage(video, 0,0,width,height);      
    var data = canvas.toDataURL('image/png');
  }
  imagedata = canvas.toDataURL()
  $.ajax({
    type: "POST",
    url: "/savepic",
    data: { 
        memno: memno,
        image: imagedata
    }
  }).done(function(o) {
    console.log('saved'); 
  });
}

window.addEventListener('load', startup, false);