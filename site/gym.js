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
function gymserver() {  
  if (!!window.EventSource) {
    var gymsource = new EventSource('/stream');
    gymsource.onmessage = function(e) {
      if (e.data.startsWith("##Timeset")) {
        stime = e.data.substring(9)
        serverTime = Date.parse(stime)
      } else if (e.data.startsWith("##Active Members")) {
        $('#footright').text(e.data.substring(2));
      } else if (e.data.startsWith("##Timer")) {
        timerbar(e.data.substring(7))
      } else if (e.data == "##Refresh") {
        location.reload(true);
      }
    }
    gymsource.onerror = function(e) {
      setTimeout(function() {
        $('#footright').text("Server Disconnected");
        gymsource.close()
        gymserver()
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

function tobr(val) {
  try {
    return val.replace(/[\r\n]+/g,"<br>") + "&nbsp;"
  } catch (e) {
    return "&nbsp;"
  }
}

function showad(nn) {
  $(".adv").css("opacity",0)
  $("#adv"+nn).css("opacity",1)
  $("#adv"+nn).html(tobr($("#ad"+nn).val()))
  $("#ad"+ nn + ",#adv" + nn).css("color",$("#ad" + nn + "col").val())
  textFit(document.getElementsByClassName('adv'), {maxFontSize: 600,multiLine: true})
}

var keycard = ""
var clearcardp
function clearcard() {
  keycard = ""
}

$(document).keypress(function(e) {
  if ("0123456789".includes(e.key)) {
    keycard += e.key
    if (clearcardp) {
      clearTimeout(clearcardp)
    }
    clearcardp = setTimeout(clearcard,1000)
  } else {
    if (e.code = 13 && keycard != "") {
      $(document).trigger("cardswiped",[keycard])
    } else {
      clearcard()
    }
  }
})

$(document).ready(function(){
    gymserver()
    updateTime();
    setInterval(updateTime, 1000);   
    $(".adv").each(function() {
      $(this).html(tobr($(this).text()))
      $(this).css("opacity",0)
    } )
    textFit(document.getElementsByClassName('adv'), {maxFontSize: 600,multiLine: true})

  if (location.search.includes("door")) {
    $(document).on("cardswiped", function(e,cardno) {
          $.ajax("/swipe", {
            data : {"card": cardno, "door": true},
            type : 'POST',
            success: function(response) {
                
            },
            error: function(xhr, ajaxOptions, thrownError) {
                
            }
          })           
      }
    );
  }  

});