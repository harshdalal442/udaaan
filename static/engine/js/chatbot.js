$('body').append('<iframe id="allincall-chat-box" frameborder="0" style="display:none;"></iframe>');
$('body').append('<img id="allincall-popup" src="/static/engine/img/popup.png" style="position:fixed;cursor:pointer;right:20px;bottom:0;">');


$('#allincall-popup').click(function(e) {
  var current_src = $("#allincall-chat-box").attr("src");
  if((typeof current_src === 'undefined') || (current_src == null)){
    $("#allincall-chat-box").attr("src","/chat");
  }
  else{
    $("#allincall-chat-box").show();
  }
  $('#allincall-popup').hide();
  $("#allincall-chat-box").slideDown("slow");
});
