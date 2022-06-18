var serverTime = new Date();
if (!!window.EventSource) {
  var source = new EventSource('/stream');
  source.onmessage = function(e) {
    if (e.data.startsWith("##TimeOffset")) {
      offs = parseInt(e.data.substring(12))
      serverTime = new Date(serverTime.getTime() + offs*1000*60*60*24)
    } else if (e.data.startsWith("##Active Members")) {
      $('#footright').text(e.data.substring(2));
    } else if (e.data.startsWith("##Timer")) {
      timerbar(e.data.substring(7))
    }
  }
}
function updateTime() {
  /// Increment serverTime by 1 second and update the html for '#time'
  serverTime = new Date(serverTime.getTime() + 1000);
  $('#footleft').html(serverTime.toLocaleString());
}
$(document).ready(function(){
    updateTime();
    setInterval(updateTime, 1000);
});

tbti = 0;
cti = 0;
tto=0
function timerbar(ti) {
  tbti = ti-1;
  $("#timerbar").css("width","100%")
  cti = tbti
  if (tto != 0) {
    clearTimeout(tto)
  }
  tto = setTimeout(updbar,100)
}

function updbar() {
  cti -= .1;
  console.log(cti)
  $("#timerbar").css("width",(100/tbti*cti) + "%")
  if (cti > 0) {
    tto = setTimeout(updbar,100)
  }
}