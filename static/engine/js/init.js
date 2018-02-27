var user_id = '';
var btn_cnt = 0;
var like_cnt = 2;
var query_cnt = 0;
var first_time = 1;
var recc_cnt = 0;


var scroll_to_bottom = function() {
  //$("#show").animate({ scrollTop: $('#show').prop("scrollHeight")}, 1000);
  $("#show").scrollTop($("#show")[0].scrollHeight);
};

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

function splitByDollar(sentence){
    list = sentence.split("$$");
    return list;
}


function setPcId(pcid){
    if((typeof pcid === 'undefined') || (pcid == null)){
        pc_id = guid();
        Cookies.set('pc_id', pc_id);
        $.ajax({
                url: "/pc_id",
                type: "POST",
                data : {
                    pcid : pc_id,
                },
                success: function(data){

                    console.log("SETTED");
                }
        });
    }
}

function setUUID(uuid){
    if((typeof uuid === 'undefined') || (uuid == null)){
        user_id = guid();
        Cookies.set('uuid', user_id);

        var random_user_name = "abcde" + Math.floor((1 + Math.random()) * 0x10000).toString(16).substring(1);

        $.ajax({
                url: "/updateuser",
                type: "POST",
                data : {
                    username : random_user_name,
                    user_id : user_id
                },
                success: function(data){

                    console.log("SETTED");
                    hideAndShowStuff();
                    $.ajax({
                        url: "/query/",
                        type: "POST",
                        data: {
                            message: "pos",
                            user_id: user_id,
                            channel: "web",
                        },
                        success: function(data){
                            console.log(data);
                            appendServerChat(data);
                            $("#search-box").show();
                            $("#search-load").hide();
                            scroll_to_bottom();
                            $("#query").focus();
                            query_cnt++;
                        }
                    });
                }
        });
    }
    else{
        user_id = uuid;
    }
}

$(document).ready(function() {
    //ajaxCallToCancel();
    $("#navig").css("background-color","#FFF");

    var dateObj = new Date();
    var month = (dateObj.getUTCMonth() + 1).toString(); //months from 1-12
    var day = dateObj.getUTCDate().toString();
    var year = dateObj.getUTCFullYear().toString();

    console.log(month, day, year);
    if(day.length==1){
        day = "0"+day;
    }
    if(month.length==1){
        month = "0"+month;
    }
    var from_date = day+"/"+(parseInt(month)-1).toString()+"/"+year;
    var to_date = day+"/"+month+"/"+year;
    $("#from-data").val(from_date);
    $("#to-data").val(to_date);
    $("#submit-analytics").click();
    $('.modal').modal();

    var uuid = Cookies.get('uuid_t');
    var pcid = Cookies.get('pc_id');

    setPcId(pcid);
    setUUID(uuid);
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

function appendUserChat(sentence){
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

    var str = '<div class="click-button" style="width:100%;overflow:auto;"><div class="chip chip2 white-text" style="line-height:27px;max-width:80%;background-color:#0094E0;float:right;box-shadow: 1px 1px 1px grey;">';
    str += sentence;
    //str += '<p style="color:white;font-size:8px;position:relative;right:0;">16:07AM</p> ';
    str += '</div></div>';
    $("#show").append(str);
    scroll_to_bottom();
}

function enableInput(query){
    console.log("GOES TO ENABLE", query);
    $("#query").removeAttr('disabled');
    $("#query").css('background-color','white');
    if(!((typeof query === 'undefined') || (query == null))){
        query = removePTag(query);
        $("#query").attr("placeholder","You can type your query here");
    }
}

function disableInput(){
    $('#query').val("");
    $('#query').attr('placeholder','Please select an option from the above choices');
    $("#query").css('background-color','#fafafa');
    $("#query").attr('disabled','disabled');
}

function disableOrEnableInput(is_typable, query){
    if(!((typeof is_typable === 'undefined') || (is_typable == null))){
        if(!((typeof query === 'undefined') || (query == null))){
            if(is_typable == "false"){
                disableInput();
            }
            else if(is_typable == "true"){
                console.log(query, "Query is");
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

function appendSentenceToLeft(sentence, list, flag){
    console.log(sentence, "AAAAAAAAAA");
    if(!((typeof sentence === 'undefined') || (sentence == null))){

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

        sentence = removePTag(sentence);
        var str = '<div class="click-button" style="width:100%;"><div class="left-align chip chip2 black-text" style="line-height:27px;max-width:80%;background-color:#eee;border:1px solid rgb(239, 239, 239);box-shadow: 1px 1px 1px grey;">';
        str += sentence;
        //str += '<p style="color:grey;font-size:8px;position:relative;right:0;">16:07 AM</p>';
        str += '</div></div>';
        $('#show').append(str);
        appendRecommendations(list);
        if(flag == true)
            $("#show").append('<hr>');
    }
}

function returnChipsInput(){
    recc_cnt++;
    var str = '\
        <div class="click-button">\
                  <div class="recc'+recc_cnt+' hoverable chip chipinitial" style="background-color:#E12523;margin-left:4%;">\
                     <a>\
                        <span class="white-text text-lighten-1">\
                           What are the documents required for Home Loan?\
                        </span>\
                     </a>\
                  </div>\
               </div>\
               <div class="click-button">\
                  <div class="recc'+recc_cnt+' hoverable chip chipinitial" style="background-color:#E12523;margin-left:4%;">\
                     <a>\
                        <span class="white-text text-lighten-1">\
                           What is the interest rate for Home Loan?\
                        </span>\
                     </a>\
                  </div>\
               </div>\
               <div class="click-button">\
                  <div class="recc'+recc_cnt+' hoverable chip chipinitial" style="background-color:#E12523;margin-left:4%;">\
                     <a>\
                        <span class="white-text text-lighten-1">\
                           Apply for Home Loan\
                        </span>\
                     </a>\
                  </div>\
               </div>\
               <div class="click-button">\
                  <div class="recc'+recc_cnt+' hoverable chip chipinitial" style="background-color:#E12523;margin-left:4%;">\
                     <a>\
                        <span class="white-text text-lighten-1">\
                           When is my next EMI due?\
                        </span>\
                     </a>\
                  </div>\
               </div>\
    ';
    return str;
}

function appendChipsInput(sentence){
    if(!((typeof sentence === 'undefined') || (sentence == null))){
        sentence = removePTag(sentence);
        var str = '<div class="click-button" style="width:100%;"><div class="left-align chip grey white-text">';
        str += sentence;
        str += '</div></div>';
        $('#show').append(str);
        $("#show").append(returnChipsInput());
        $("#show").append('<hr>');
    }
}

$('#feedback-text').on('input',function(e){
    if($.trim($('#feedback-text').val()) != ''){
        $("#feedback-submit").show();
        $("#feedback-cancel").show();
    }
    else{
        $("#feedback-submit").hide();
        $("#feedback-cancel").show();
    }
});

$('body').on('click','#feedback-submit',function(){
     if($.trim($('#feedback-text').val()) != ''){
        $.ajax({
            url: "/overallfeedback",
            type: "POST",
            data: {
              "feedback": $("#feedback-text").val(),
              "user_id": user_id
            },
            success: function(response) {
              $("#feedback-text").val("");
              Materialize.toast('Your feedback has been submitted successfully!', 2000);
            },
            error: function(xhr, textstatus, errorthrown) {
              //Materialize.toast('Error in submitting feedback.', 2000);
            }
        });
    }
    else{
        Materialize.toast('Feedback is empty', 2000);
    }
});

function appendChoices(list){
    if(!((typeof list === 'undefined') || (list == null))){
        $("#show").append('<div class="click-button" style="width:100%;"><div style="margin-left:2% !important;" id="recommendation'+query_cnt+'"></div></div>');
        for(var i=0;i<list.length;i++){
            if(i==0){
                var str = '<a><div class="btn'+query_cnt+' chip chipbutton button4" style="background-color:#ffffff;margin:auto;border:1px solid #1e88e5;border-radius:5px;font-size:95%;color:#1e88e5;text-align:center;margin-right:3px;margin-bottom:2px;">';
                str += list[i];
                //str += '<i class="material-icons" style="background-color:#E12523">chevron_right</i>';
                str += '</div></a>';
                $("#recommendation"+query_cnt).append(str);
            }
            else{
                var str = '<a><div class="btn'+query_cnt+' chip chipbutton button4" style="background-color:#ffffff;margin:auto;border:1px solid #1e88e5;border-radius:5px;font-size:95%;color:#1e88e5;text-align:center;margin-right:3px;margin-bottom:2px;">';
                str += list[i];
                //str += '<i class="material-icons" style="background-color:#E12523">chevron_right</i>';
                str += '</div></a>';
                $("#recommendation"+query_cnt).append(str);
            }
        }
    }
}

$('#query').keypress(function (e) {
 var key = e.which;
 if(key == 13)  // the enter key code
 {
  if($('#remove_select').length && $('#query').val().length>0)
    $('#remove_select').remove();
  $('#submit').click();
  return false;
 }
});

function appendRecommendations(list){
    if(!((typeof list === 'undefined') || (list == null))){
        //$("#show").append('<div class="click-button" style="width:100%;"><div id="recommendation'+query_cnt+'"></div></div>');
        for(var i=0;i<list.length;i++){
            var str = '<div class="hovera"><div style="margin-left: 4%;background-color: #d32f2f;" class="hoverable chip chipbutton white-text text-lighten-1">';
            str += list[i];
            str += '<i class="material-icons">chevron_right</i>';
            str += '</div></div>';
            //$("#recommendation"+query_cnt).append(str);
        }
    }
}

function appendDataForm(data_form){
    if(!((typeof data_form === 'undefined') || (data_form == null))){
        console.log("DATAFORM IS:", data_form)
        $("#query").val(data_form);
    }
}

$('body').on('change', '.datepicker', function(){

    //console.log("aaaabbbbbb");

     $('#query').val($('#date').val());

     $('#query').focus();

})

function appendDate(){
    var html = '<div id="remove_select">\
    <div class="row chatmessage">\
        <div class="col s2 l2">\
        </div>\
        <div class="col s6 l6 offset-l6 offset-s6">\
           <div>'+
              '<input id="date" type="text" class="datepicker" placeholder="Select DOB">'
           +'</div>\
        </div>\
    </div></div>\
    ';
    $('#show').append(html);
  $('.datepicker').pickadate({
    selectMonths: true, // Creates a dropdown to control month
    selectYears: 115, // Creates a dropdown of 15 years to control year,
    today: 'Today',
    clear: 'Clear',
    close: 'Ok',
    format: 'dd/mm/yyyy',
    focus: true,
    maxDate: "0",
    closeOnSelect: false // Close upon selecting a date,
  });

}

$('body').on('change', '.dropdown_select', function(){
    //$(this).css({'background-color':'#1e88e5'});
    //$(this).css({'color':'white'});
    //removeDropdownPropertyBut($(this));
    //console.log($(this).attr('class'));
    var sentence = $(this).val();
    //sentence = $($.parseHTML(sentence)).val();
    if (sentence.length == 0) {      // error!
      return;
    }
    //appendResponseUser($(this).val());
    //ajaxCallToIndex($(this).val(),"1");
    //console.log("aaaaaaaaaaaaaaaaaaa", ($(this).val()));
    $('#query').val ( ($(this).val()));
    $('#query').focus();
});

function appendDropdown(list){
    var string = '<div id="remove_select"><select class="dropdown_select"><option value="" disabled selected>Choose your option</option>';
    for(var i=0;i<list.length;i++){
        string += '<option value="'+ list[i] +'">' + list[i] + '</option>';
    }
    string += '</select>';
    var html = '\
    <div class="row chatmessage">\
        <div class="col s2 l2">\
        </div>\
        <div class="col s6 l6 offset-s6 offset-l6">\
           <div>'+
              string
           +'</div>\
        </div>\
    </div></div>\
    ';
    //console.log(html, "aaaaaaaaaaaaaaaaaaaaaaaaaa");

    $("#show").append(html);
    $('select').material_select();
    enableInput($('#query').val());
}

function appendFile(){
    var html = '<div id="remove_select">\
    <div class="row chatmessage">\
        <div class="col s2 l2">\
        </div>\
        <div class="col s6 l6 offset-l6 offset-s6">\
           <div>'+
              '<div class="file-field input-field">\
      <div class="btn">\
        <span>File</span>\
        <input id="file_input" type="file">\
      </div>\
      <div class="file-path-wrapper">\
        <input class="file-path validate" type="text">\
      </div>\
    </div>'
           +'</div>\
        </div>\
    </div></div>\
    ';
    $('#show').append(html);
    enableInput($('#query').val());
}

$('body').on('change', '#file_input', function(){
    console.log("aaaaaaaaaaaaa");
    $('#query').val($('#file_input').val().substr(12));
    $('#query').focus();
});

function appendServerChat(data){
    console.log(data);
    if(!((typeof data["question_asked"] === 'undefined') || (data["question_asked"] == null)))
        disableOrEnableInput(data["is_typable"], data["question_asked"]);
    else
        disableOrEnableInput(data["is_typable"], "");
    if(!((typeof data["question_asked"] === 'undefined') || (data["question_asked"] == null))){
        list = splitByDollar(data["question_asked"]);
        console.log(list,"AAAAAAAAAAAAAAAAA");
        for(var i=0;i<list.length;i++){
            appendSentenceToLeft(list[i], data["recommended_queries"], false);
        }
    }
    //appendSentenceToLeft(data["sentence"], data["recommended_queries"], true);
    if(!(typeof data["sentence"]==='undefined')){
    list = splitByDollar(data["sentence"]);
        console.log(list,"AAAAAAAAAAAAAAAAA");
        for(var i=0;i<list.length;i++){
            appendSentenceToLeft(list[i], data["recommended_queries"], false);
        }}
    appendSentenceToLeft(data["answer"],[],false);
    if(data["is_clickable"]=="true" && !data["is_dropdown"] && !data["is_file"])appendChoices(data["choices"]);
    appendChipsInput(data["change_this_later"]);
    appendDataForm(data["data_form"]);
    if(data["is_date"])	{appendDate();console.log("aaaaaaaaaaaaaaaaaaaaa");}
    if(data["is_dropdown"])	{appendDropdown(data["choices"]);}
    if(data["is_file"])	{appendFile();}
}

function appendServerChat2(data){
    console.log(data);
    if(!((typeof data["question_asked"] === 'undefined') || (data["question_asked"] == null)))
        disableOrEnableInput(data["is_typable"], data["question_asked"]);
    else
        disableOrEnableInput(data["is_typable"], "");
    if(!((typeof data["question_asked"] === 'undefined') || (data["question_asked"] == null))){
        list = splitByDollar(data["question_asked"]);
        for(var i=0;i<list.length;i++){
            appendSentenceToLeft(list[i], data["recommended_queries"], false);
        }
    }
    appendSentenceToLeft(data["sentence"], data["recommended_queries"], true);
    appendSentenceToLeft(data["answer"],[],false);
    appendChoices(data["choices"]);
    appendChipsInput(data["change_this_later"]);
    appendDataForm(data["data_form"]);
}
function ajaxCallToIndex(sentence){
    $.ajax({
        url: "/query/",
        type: "POST",
        data: {
            message: sentence,
            user_id: user_id,
            channel: "web",
        },
        success: function(data){
            console.log(data);
            appendServerChat(data);
            $("#search-box").show();
            $("#search-load").hide();
            scroll_to_bottom();
            $("#query").focus();
            query_cnt++;
        }
    });
}

function ajaxCallToCancel(){
    $.ajax({
        url: "/cancelbutton/",
        type: "POST",
        data: {
            user_id: user_id,
        },
        success: function(data){
            console.log("SUCC");
            $("#help-div").show();
        }
    });
}

function hideAndShowStuff(){
    $("#help-div").hide();
    $("#search-box").hide();
    $("#search-load").show();
    $("#r1").show();
    $("#r3").show();
    if(first_time == 1){
        first_time = 0;
        $("#show").append('<hr>');
    }
}

$("#submit").click(function(){
    if($('#remove_select').length && $('#query').val().length>0)
        $('#remove_select').remove();
    if(($.trim($('#query').val()) != '') && ($("#query").val()).length<300){
        console.log("CLICKED");
        hideAndShowStuff();
        var sentence = $("#query").val();
        $("#query").val("");
        appendUserChat(sentence);
        ajaxCallToIndex(sentence);
    }
    else{
        Materialize.toast("Please enter a valid query", 2000);
    }
});

$('body').on('click','.chipbutton', function(){
    hideAndShowStuff();
    removeClickableProperty($(this));
    appendUserChat($(this).clone().children().remove().end().text());
    ajaxCallToIndex($(this).clone().children().remove().end().text());
});

function removeClickableProperty(ctx){
    var classList = $(ctx).attr('class').split(/\s+/);
    $.each(classList, function(index, item) {
        if (item.substring(0,4) === 'recc') {
            var value = parseInt(item.substring(4));
            for(var i=1;i<=value;i++){
                console.log(".recc"+i);
                $(".recc"+i).removeClass("chipinitial");
                $(".recc"+i).removeClass("hoverable");
                $('.recc'+i).css( 'cursor', 'default' );
            }
        }
        if (item.substring(0,3) === 'btn') {
            console.log(item);
            var value = parseInt(item.substring(3));
            console.log(value);
            for(var i=0;i<=value;i++){
                console.log(".recc"+i);
                $(".btn"+i).removeClass("chipbutton");
                $(".btn"+i).removeClass("hoverable");
                $('.btn'+i).css( 'cursor', 'default' );
            }
        }
    });
}

$('body').on('click','.chipinitial', function(){
    hideAndShowStuff();
    removeClickableProperty($(this));
    appendUserChat($(this).text());
    ajaxCallToIndex($(this).text());
});

function giveStr(){
    str = '\
    <div id="help-div">\
            <h5>\
              Welcome to <b style="color:#E12523">EasyChat</b>.\
            </h5>\
            <p class="grey-text text-darken-1">\
              Please type your query at the bottom of the page.\
            </p>\
            <p id="text-help-queries" class="grey-text text-darken-1">\
            I can help you with queries like:\
          </p>\
            <div id="cards">\
               <div class="click-button">\
                  <div class="hovera">\
                    <div class="hoverable chip chipinitial" style="background-color:#E12523;margin-left:14px;">\
                        <span class="white-text text-lighten-1">\
                            What are the documents required for Home Loan?\
                        </span>\
                    </div>\
                  </div>\
               </div>\
               <div class="click-button">\
                   <div class="hovera">\
                    <div class="hoverable chip chipinitial" style="background-color:#E12523;margin-left:14px;">\
                     <a>\
                         <span class="white-text text-lighten-1">\
                            What is the interest rate for Home Loan?\
                        </span>\
                     </a>\
                  </div>\
                   </div>\
               </div>\
               <div class="click-button">\
                   <div class="hovera">\
                    <div class="hoverable chip chipinitial" style="background-color:#E12523;margin-left:14px;">\
                     <a>\
                         <span class="white-text text-lighten-1">\
                           Apply for Home Loan\
                        </span>\
                     </a>\
                  </div>\
                  </div>\
               </div>\
               <div class="click-button">\
                   <div class="hovera">\
                    <div class="hoverable chip chipinitial" style="background-color:#E12523;margin-left:14px;">\
                     <a>\
                         <span class="white-text text-lighten-1">\
                           When is my next EMI due?\
                        </span>\
                     </a>\
                  </div>\
                  </div>\
               </div>\
            </div>\
          </div>\
    ';
    return str;
}

function startOver(){
    console.log("LOG1");
    //$("#show").html(giveStr());
    //first_time = 1;
    $("#show").html("");
    enableInput("");
    $.ajax({
        url: "/cancelbutton/",
        type: "POST",
        data: {
            user_id: user_id,
        },
        success: function(data){
            //console.log("SUCC");
                    $.ajax({
                        url: "/query/",
                        type: "POST",
                        data: {
                            message: "pos",
                            user_id: user_id,
                            channel: "web",
                        },
                        success: function(data){
                            console.log(data,"GGGGGGGGGGGGGGGGGGGGGG");
                            $("#help-div").hide();
                            appendServerChat(data);

                            scroll_to_bottom();
                            $("#query").focus();
                            query_cnt++;
                        }
                    });
        }
    });
    //$("#r1").hide();
    //$("#r3").hide();
    $("#query").val("");

}

function cancelButton(){
    $("#show").append("<hr>");
    enableInput("");
    ajaxCallToCancel();
    //asdasdsadsa
}

$('body').on('click','.chiprecc', function(){
    var id = this.id;
    id = parseInt(id.substring(1));
    console.log(id);
    if(id==1)
        startOver();
    else if(id==2)
        cancelButton();
    else
        overAllFeedback();
});


var settings = {
    continuous:true, // Don't stop never because i have https connection
    onResult:function(text){
        console.log(text);
        if(text!="")
            $('#query').val(text);
        else{
            $("#submit").click();
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

$('body').on('click','#logo-container', function(){
     $("#query").focus();
});

$('#query').on('input',function(e){
    var value = $("#query").val();
    if($.trim($('#query').val()) == ''){
        $("#mic").show();
        $("#submit").hide();
    }
    else{
        $("#submit").show();
        $("#mic").hide();
    }
});


var settings = {
    continuous:true, // Don't stop never because i have https connection
    onResult:function(text){
        console.log(text);
        if(text!="")
            $('#query').val(text);
        else{
            $("#submit").click();
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

