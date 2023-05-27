tbti = 0;
cti = 0;
tto=0
function timerbar(ti) {
  if (tto != 0) {
    clearTimeout(tto)
  }
  if (ti != 0) {
    tbti = ti-1;
    $("#timerbar").show().css("width","100%")
    cti = tbti    
    tto = setTimeout(updbar,100)
  } else {
    $("#timerbar").hide().css("width","0%")
  }
}

function updbar() {
  cti -= .1;
  $("#timerbar").css("width",(100/tbti*cti) + "%")
  if (cti > 0) {
    tto = setTimeout(updbar,100)
  }
}

var serverTime = 0;
function startserver() {  
  if (!!window.EventSource) {
    var gymsource = new EventSource('/stream');
    gymsource.onmessage = function(e) {
      if (e.data.startsWith("##Timeset")) {
        stime = e.data.substring(9)
        serverTime = Date.parse(stime)
      } else if (e.data.startsWith("##Active Members")) {
        console.log(e.data)
        $('#footright').text(e.data.substring(2));
      } else if (e.data.startsWith("##Timer")) {
        timerbar(e.data.substring(7))
      }
    }
    gymsource.onerror = function(e) {
      setTimeout(function() {
        $('#footright').text("Server Disconnected");
        gymsource.close()
        startserver()
      },2000)
    }
  }
}

function updateTime() {
  if (serverTime > 0) {
    serverTime += 1000;
    ndate = new Date(serverTime)
    $('#footleft').html(ndate.toString().replace(/ GMT.*/,""));
  }
}
$(document).ready(function(){
    startserver()
    updateTime();
    setInterval(updateTime, 1000);
});