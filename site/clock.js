var serverTime = new Date();
if (!!window.EventSource) {
  var source = new EventSource('/stream');
  source.onmessage = function(e) {
    if (e.data.startsWith("##TimeOffset")) {
      offs = parseInt(e.data.substring(12))
      serverTime = new Date(serverTime.getTime() + offs*1000*60*60*24)
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
