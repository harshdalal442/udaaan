var user_id = '';
var like_cnt = 2;
var query_cnt = 0;
var ask_3min = 1;
var mic_button_set = false;

var scroll_to_bottom = function() {
  $('#style-2').scrollTop($('#style-2')[0].scrollHeight);
};

try{
    var settings = {
        continuous:true, // Don't stop never because i have https connection
        onResult:function(text){
            console.log(text);
            if(text!="")
                $('#query').val(text);
            else{
                $("#submit-img").click();
                stopRecognition();
            }
        },
        onStart:function(){
            console.log("Dictation started by the user");
        },
        onEnd:function(){
        }
    };

    var artyom = new Artyom();
    var UserDictation = artyom.newDictation(settings);
    function startRecognition(){
      UserDictation.start();
    }

    function stopRecognition(){
      UserDictation.stop();
    }
    stopRecognition();
    console.log("NO ERROR");
    mic_button_set = true;
}
catch(err){
    console.log("This is a ERROR:", err);
}


function s4() {
return Math.floor((1 + Math.random()) * 0x10000)
  .toString(16)
  .substring(1);
}

function guid() {
  function s4() {
    return Math.floor((1 + Math.random()) * 0x10000)
      .toString(16)
      .substring(1);
  }
  return s4() + s4() + '-' + s4() + '-' + s4() + '-' +
    s4() + '-' + s4() + s4() + s4();
}

function setPcId(pcid){
    if((typeof pcid === 'undefined') || (pcid == null)){
        pc_id = guid();
        Cookies.set('pc_id', pc_id);
        $.ajax({
                url: "/chat/pc_id",
                type: "POST",
                data : {
                    pcid : pc_id,
                },
                success: function(data){
                }
        });
    }
    else{
        console.log("OLD PC");
    }
}

function returnTime(){
    var d = new Date();
    var hours = d.getHours().toString();
    var minutes = d.getMinutes().toString();
    var flagg = "AM";
    if(parseInt(hours) > 12){
        hours = hours - 12;
        flagg = "PM";
    }
    if(hours.length==1){
        hours = "0"+hours;
    }
    if(minutes.length==1){
        minutes = "0"+minutes;
    }

    var time = hours+":"+minutes+" "+flagg;
    return time;
}

function appendResponseServer(sentence, flag, url1, url2){
    sentence = sentence.replace("<p>","");sentence = sentence.replace("</p>","");
    sentence = sentence.replace("<strong>","<b>");sentence = sentence.replace("</strong>","</b>");
    sentence = sentence.replace("<em>","<i>");sentence = sentence.replace("</em>","</i>");
    var html =
    '<div class="row chatmessage">\
        <div class="col s1 l1" >\
           <img src="/static/engine/img/sbi.png"  class="circle"  width=28 class="chatbot_left_image">\
        </div>\
        <div class="col s10 m10">\
           <div class="chip chip2 chip_left" >\
              <span>'+sentence+'</span>\
           </div>\
        </div>';
    like_cnt++;
    if(flag == "true"){
    html+= '<div class="timestampl" >'+returnTime()+
           '<a class="right likebuttons">\
           <img src="/static/engine/img/thumbs-up1.png" id="like'+like_cnt+'"url_t="'+url1+'" width="16" class="responsive-img like-query"> <img src="/static/engine/img/thumbs-down1.png" id="disl'+like_cnt+'" url_t="'+url2+'" width="16" class="responsive-img dislike-query"></a>\
        </div>\
        ';
    }
    else{
    html += '<div class="timestampl" >\
            '+returnTime()+'\
        </div>\
    </div>\
    ';
    }
    $("#style-2").append(html);
}

function appendButtons(list){
    var string = '';
    for(var i=0;i<list.length;i++){
        string += '<button class="button2 button3 chipbutton">';
        string += list[i];
        string += '</button>';
    }
    var html = '\
    <div class="row chatmessage">\
        <div class="col s2 l2">\
        </div>\
        <div class="col s10 l10">\
           <div>'+
              string
           +'</div>\
        </div>\
    </div>\
    ';
    $("#style-2").append(html);
}
function appendResponseUser(sentence){
    sentence = sentence.replace("<p>","");sentence = sentence.replace("</p>","");
    var a_tag = '<a name="id'+query_cnt+'"/>';
    var html = a_tag +
    '<div class="row chatmessage">\
        <div class="col s3">\
        </div>\
        <div class="col s9">\
            <div class="chip chip2 right chip_right">\
                <span>'+sentence+'</span>\
            </div>\
        </div>\
        <div class="timestampr" >'+returnTime()+'</div>\
    </div>\
    ';
    $("#style-2").append(html);
    scroll_to_bottom();
}

function appendRecommendationsList(list){
    if(list.length > 0){
        var html =
        '<div class="row chatmessage">\
            <div class="col s2">\
               <img src="/static/engine/img/sbi.png" width="28"  class="circle" class="chatbot_left_image" >\
            </div>\
            <div class="col s9 l9">\
               <div class="button-group button-group2" style="margin-top:4px;">\
               ';

        for(var i=0;i<list.length;i++){
            html += '<div class="button recommendation_style chiprecommendation">'+list[i]+'</div>';
        }
        html += '</div>';

        html += '</div>\
            <div class="timestampl">'+returnTime()+'</div>\
         </div>\
        ';
        $("#style-2").append(html);
    }
}

function setUUID(uuid){
    if((typeof uuid === 'undefined') || (uuid == null)){
        user_id = guid();
        console.log("NEW USER", user_id);
        Cookies.set('uuid', user_id);

        $.ajax({
                url: "/chat/updateuser",
                type: "POST",
                data : {
                    user_id : user_id
                },
                success: function(data){
                      console.log(data);
                      response = data["response"]
                      recommended_queries = data["recommended_queries"]
                      is_typable = data["is_typable"]

                      if(!((typeof response === 'undefined') || (response == null))){
                        disableOrEnableInput(is_typable, response);
                        console.log(data["response"]);
                        list = splitByDollar(data["response"]);
                        console.log(list);
                        if(!((typeof data["is_answer"] === 'undefined') || (data["is_answer"] == null))){
                            console.log(data["is_answer"], "CHECK THIS ")
                            for(var i=0;i<list.length;i++){
                                if(i==list.length-1)
                                    appendResponseServer(list[i], data["is_answer"], data["upvote_link"], data["downvote_link"]);
                                else
                                    appendResponseServer(list[i], false, "", "");
                            }
                        }
                        else{
                             for(var i=0;i<list.length;i++){
                                appendResponseServer(list[i], false, "", "");
                             }

                        }
                      }
                      if(!((typeof recommended_queries === 'undefined') || (recommended_queries == null))){
                        console.log("GOES IN IF STATMENT")
                        appendRecommendationsList(recommended_queries);
                      }
                }
        });
    }
    else{
        user_id = uuid;
        console.log("OLD USER");
    }
}

$(document).ready(function() {
    $("#navig").css("background-color","#FFF");

    var uuid = Cookies.get('uuid_t');
    var pcid = Cookies.get('pc_id');

    setPcId(pcid);
    setUUID(uuid);

    if(mic_button_set){
        $("#submit").append('<img id="submit-mic" onclick="startRecognition()" src="/chat/static/engine/img/mic.png" width=28 class="responsive-img">');
        $("#submit-img").css({'display':'none'});
    }
    else
        $("#submit-img").attr('src','/static/engine/img/send1.png');
});

function convertStrongToBold(sentence){
    if(!((typeof sentence === 'undefined') || (sentence == null))){
        sentence = sentence.replace("<strong>","<b>");
        sentence = sentence.replace("</strong>","</b>");
    }
    return sentence;
}

function removeWhiteSpaces(sentence){
    if(!((typeof sentence === 'undefined') || (sentence == null))){
        sentence = sentence.replace(" ","");
    }
    return sentence;
}

function enableInput(query){
    $("#query").removeAttr('disabled');
    if(!((typeof query === 'undefined') || (query == null))){
        query = removePTag(query);
        $("#query").attr("placeholder","You can type your query here");
    }
}

function disableInput(){
    $('#query').val("");
    $('#query').attr('placeholder','Please select an option from the above choices');
    $("#query").attr('disabled','disabled');
}

function disableOrEnableInput(is_typable, query){
    if(!((typeof is_typable === 'undefined') || (is_typable == null))){
        if(!((typeof query === 'undefined') || (query == null))){
            if(is_typable == "false"){
                disableInput();
            }
            else if(is_typable == "true"){
                enableInput(query);
            }
        }
    }
}

function removePTag(sentence){
    if(!((typeof sentence === 'undefined') || (sentence == null))){
        sentence = sentence.replace("<p>","");
        sentence = sentence.replace("</p>","");
    }
    return sentence;
}

$('#query').keypress(function (e) {
 var key = e.which;
 if(key == 13)  // the enter key code
 {
  $('#submit-img').click();
  return false;
 }
});

function splitByDollar(sentence){
    list = sentence.split("$$");
    return list;
}

function appendServerChat(data){
    if(!((typeof data["response"] === 'undefined') || (data["response"] == null)))
        disableOrEnableInput(data["is_typable"], data["response"]);
    else
        disableOrEnableInput(data["is_typable"], "");
    if(!((typeof data["response"] === 'undefined') || (data["response"] == null))){
                        list = splitByDollar(data["response"]);
                        if(!((typeof data["is_answer"] === 'undefined') || (data["is_answer"] == null))){
                            console.log(data["is_answer"], "CHECK THIS ")
                            for(var i=0;i<list.length;i++){
                                if(i==list.length-1)
                                    appendResponseServer(list[i], data["is_answer"], data["upvote_link"], data["downvote_link"]);
                                else
                                    appendResponseServer(list[i], false, "", "");
                            }
                        }
                        else{
                             for(var i=0;i<list.length;i++){
                                appendResponseServer(list[i], false, "", "");
                             }

                        }
                      }
    if(!((typeof data["choices"] === 'undefined') || (data["choices"] == null)))
        appendButtons(data["choices"]);
    if(!((typeof data["recommended_queries"] === 'undefined') || (data["recommended_queries"] == null)))
        appendRecommendationsList(data["recommended_queries"]);
    if(mic_button_set){
        $("#submit-mic").show();
        $("#submit-img").hide();
    }
    else
        $("#submit-img").attr('src','/static/engine/img/send1.png');
}

function ajaxCallToIndex(sentence, clicked){
    $.ajax({
        url: "/chat/query/",
        type: "POST",
        data: {
            message: sentence,
            user_id: user_id,
            channel: "web",
            language: "eng",
            clicked: clicked,
        },
        success: function(data){
            console.log(user_id, sentence)
            console.log(data);
            appendServerChat(data);
            $("#query").focus();
            console.log("SCROLLING TO ", "id"+query_cnt);
            scroll_to_bottom();
            query_cnt++;
        },
        error: function (jqXHR, exception) {
             appendResponseServer("SIA is under maintenance, Please try again after some time. Sorry for your inconvenience.", false, "", "");
             disableOrEnableInput("true","");
             scroll_to_bottom();
        },
    });
}

$("#submit-img").click(function(){
    if(($.trim($('#query').val()) != '') && ($("#query").val()).length<300){
        var sentence = $("#query").val();
        sentence = $($.parseHTML(sentence)).text();
        if (sentence.length == 0) {      // error!
          $("#query").val("");
          return;
        }
        $("#query").val("");
        appendResponseUser(sentence);
        ajaxCallToIndex(sentence,"0");
    }
    else{
        Materialize.toast("Please enter a valid query", 2000);
    }
});

$('body').on('click','.like-query', function(){
    var clicked = $(this).attr('clicked');
    if(!((typeof clicked === 'undefined') || (clicked == null))){
        if(clicked != "true"){
            var id = this.id;
            var id = id.substring(4);
            $("#like"+id).attr("src","/static/engine/img/thumbs-down-filled.png");
            $("#disl"+id).attr("src","/static/engine/img/thumbs-down1.png");
            $("#disl"+id).removeAttr("clicked");
            var url = $(this).attr('url_t');
            var final_url = "/chat"+url;
            //$(this).removeAttr('url_t');
            if(!((typeof url === 'undefined') || (url == null))){
                $(this).attr('clicked','true');
                $.ajax({
                    url: final_url,
                    type: "GET",
                    success: function(data){
                    }
                });
            }
        }
    }
    else{
        var id = this.id;
        var id = id.substring(4);
        $("#like"+id).attr("src","/static/engine/img/thumbs-down-filled.png");
        $("#disl"+id).attr("src","/static/engine/img/thumbs-down1.png");
        $("#disl"+id).removeAttr("clicked");
        var url = $(this).attr('url_t');
        //$(this).removeAttr('url_t');
        var final_url = "/chat"+url;
        if(!((typeof url === 'undefined') || (url == null))){
            $(this).attr("clicked","true");
            $.ajax({
                url: final_url,
                type: "GET",
                success: function(data){
                }
            });
        }
    }
});

$('body').on('click','.dislike-query', function(){
    var clicked = $(this).attr('clicked');
    if(!((typeof clicked === 'undefined') || (clicked == null))){
        if(clicked != "true"){
            var id = this.id;
            var id = id.substring(4);
            $("#disl"+id).attr("src","/static/engine/img/thumbs-up-filled.png");
            $("#like"+id).attr("src","/static/engine/img/thumbs-up1.png");
            $("#like"+id).removeAttr("clicked");
            var url = $(this).attr('url_t');
            //$(this).removeAttr('url_t');
            var final_url = "/chat"+url;
            if(!((typeof url === 'undefined') || (url == null))){
                $(this).attr("clicked","true");
                $.ajax({
                    url: final_url,
                    type: "GET",
                    success: function(data){
                    }
                });
            }
        }
    }
    else{
        var id = this.id;
        var id = id.substring(4);
        $("#disl"+id).attr("src","/static/engine/img/thumbs-up-filled.png");
        $("#like"+id).attr("src","/static/engine/img/thumbs-up1.png");
        $("#like"+id).removeAttr("clicked");
        var url = $(this).attr('url_t');
        //$(this).removeAttr('url_t');
        var final_url = "/chat"+url;
        if(!((typeof url === 'undefined') || (url == null))){
            $(this).attr('clicked','true');
            $.ajax({
                url: final_url,
                type: "GET",
                success: function(data){
                }
            });
        }
    }
});

$('body').on('click','#restart-button', function(){
    $(".chatmessage").remove();
    enableInput("");
    $.ajax({
        url: "cancelbutton/",
        type: "POST",
        data: {
            user_id: user_id,
        },
        success: function(data){
            response = data["response"]
            recommended_queries = data["recommended_queries"]
            is_typable = data["is_typable"]

            if(!((typeof response === 'undefined') || (response == null))){
              disableOrEnableInput(is_typable, response);
              list = splitByDollar(data["response"]);
              for(var i=0;i<list.length;i++){
                 appendResponseServer(list[i], false, "", "");
              }
            }
            if(!((typeof recommended_queries === 'undefined') || (recommended_queries == null))){
              appendRecommendationsList(recommended_queries);
            }
        }
    });
    $("#query").val("");
    if(mic_button_set){
        $("#submit-mic").show();
        $("#submit-img").hide();
    }
    else
        $("#submit-img").attr('src','/static/engine/img/send1.png');
});

$('body').on('click','.chiprecommendation', function(){
    var isDisabled = $('#query').prop('disabled');
    if(!isDisabled){
        removeClickablePropertyRec($(this));
        $(this).css({'background-color':'#eeeeee'});
        var sentence = $(this).text();
        sentence = $($.parseHTML(sentence)).text();
        if (sentence.length == 0) {      // error!
          return;
        }
        appendResponseUser($(this).text());
        ajaxCallToIndex($(this).text(),"1");
    }
});

$('body').on('click','#close-chatbot', function(){
   $('#allincall-chat-box', window.parent.document).hide();
   $('#allincall-popup', window.parent.document).show();
});

$('body').on('click','.chipbutton', function(){
    $(this).css({'background-color':'#1e88e5'});
    $(this).css({'color':'white'});
    removeClickablePropertyBut($(this));
    var sentence = $(this).text();
    sentence = $($.parseHTML(sentence)).text();
    if (sentence.length == 0) {      // error!
      return;
    }
    appendResponseUser($(this).text());
    ajaxCallToIndex($(this).text(),"1");
});

function removeClickablePropertyRec(ctx){
   $(ctx).parent().children().removeClass("chiprecommendation");
   $(ctx).parent().removeClass("button-group2");
   $(ctx).parent().children().css({'cursor' :"default"});
}

function removeClickablePropertyBut(ctx){
   $(ctx).parent().children().removeClass("chipbutton");
   $(ctx).parent().children().removeClass("button3");
   $(ctx).parent().children().css({'cursor' :"default"});
}

$('body').on('click','#logo-container', function(){
     $("#query").focus();
});

$('#query').on('input',function(e){
    var value = $("#query").val();
    if($.trim($('#query').val()) == ''){
        if(mic_button_set){
            $("#submit-mic").show();
            $("#submit-img").hide();
        }
        else
            $("#submit-img").attr('src','/static/engine/img/send1.png');
    }
    else{
        $("#submit-mic").hide();
        $("#submit-img").show();
        $("#submit-img").attr('src','/static/engine/img/send2.png');
    }
});