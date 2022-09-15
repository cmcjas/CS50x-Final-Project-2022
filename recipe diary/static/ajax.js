// handle the removal of recipes & playlist for the frontend, while ajax handle the backend plus sql
function rm(i, j, m){
  $.ajax({
    url:"/delete1",
    type:"POST",
    data:{"data1":i, "data2": j},
  });

  let num = $(m).parent().index();
  $("#playlist li")[num].remove();


}

function rm2(i, j, m){
  let listbtn = document.querySelectorAll('.listbtn2');
  let listitem = document.querySelectorAll('.listitem');

  $.ajax({
    url:"/delete2",
    type:"POST",
    data:{"data1":i, "data2": j},
  });

  // remove recipes from user's own recipe section
  let num = $(m).parent().parent().index();
  $(".profile")[num - 1].remove();

  // remove recipes from the recipe search section 
  var pkey = $(listbtn[num-1]).data('pkey');

  for (var i = 0; i < existing.length; i++) {
    if (pkey === existing[i].key) {
      $(listitem[i]).remove();
    }
  }
}

// move playlist upward & downward for the frontend, while ajax handle the backend plus sql
function asc(pos){
  var index = $(pos).parent().index();
  var a = $('#playlist li')[index - 1];
  var b = $('#playlist li')[index];
  var filename = $('#playlist li a')[index].textContent;

  if (index != 0){
    $.ajax({
      url:"/asc",
      type:"POST",
      data:{"name":filename},
    });
    a.parentNode.insertBefore(b, a);
  }
}

function dsc(pos){
  var index = $(pos).parent().index();
  var a = $('#playlist li')[index + 1];
  var b = $('#playlist li')[index];
  var filename = $('#playlist li a')[index].textContent;

  if (index != ($('#playlist li').length)){
    $.ajax({
      url:"/dec",
      type:"POST",
      data:{"name":filename},
    });
    b.parentNode.insertBefore(a, b);
  }
}

// upload mp3 files to flask via ajax
$(document).ready(function(){
  $('#fileUP').change(function(event){
      if($('#myFile1').val()){
          event.preventDefault();

        // create an animate upload progress bar to inform the user if the mp3 file is being uploaded or not
        $('#fileUP').ajaxSubmit({
          beforeSubmit:function(){
            $('.ttext').text("Wait...");
            $('.progress-bar').width('50%');
          },
          uploadProgress: function(event, position, total, percentageComplete)
          {
              $('.progress-bar').animate({
                  width: percentageComplete + '%'
              }, {
                  duration: 1000
              });
          },
          success:function(data){
            $('.ttext').text("Done");
          },
          resetForm: true
        });
      }  
  });
});

// handle the assigning of songs to playlist for the frontend, while the above function handle the backend
function up(file) {
  var file_data = file.files;

  for (var i = 0; i < file_data.length; i++){
    // make sure mp3 file names are secured similar to python's werkzeug.utils for the frontend
    var n = file.files[i];
    var name = n.name.replace(/\.[^/.]+$/, "");
    var safe1 = name.replace(/[^a-z0-9-.&]/gi, '_');
    var safe2 = safe1.replace(/_{2,}/gi, '_');
    var safe3 = safe2.replace(/[^a-z0-9-.]$/gi,'');
    var safename = safe3.replace(/&/gi, '');

    let subdir = "<button class='btn btn-light' onclick='asc(this)'><i class='bi-arrow-up-circle-fill'></i></button><button class='btn btn-light'\
    onclick='dsc(this)'><i class='bi-arrow-down-circle-fill'></i></button><button class='btn btn-light' name='"+ safename +"' \
    value='static/upload_data/music_"+ num +"/" + safename + ".mp3' onclick='rm(this.name, this.value, this);'>\
    <i class='bi-file-earmark-excel-fill'></i></button></li>";
    let player = "<li><div><a class='li' href='/static/upload_data/music_"+ num +"/" + safename + ".mp3'>" + safename +"</a></div>" + subdir;
    $('#playlist .list').append(player);
    
    $("#playlist li a").click(function(e){
      e.preventDefault();
      $("#player")[0].src = this;
        $("#player")[0].play();
        $("#playlist li").removeClass("current");
        $(this).parent().parent().addClass("current");
        if (shuff === true){
            shuffle();
        }else{
            orderplay(); 
        }
    });
  }
}

// remembering each user's likes preference via ajax and database interaction
var pp = [];
var existing = [];

function like_clicked() {
    let icon3 = document.querySelectorAll(".icon");
    let cb3 = document.querySelectorAll(".cbtn2");
    let lis = document.querySelectorAll(".listbtn2");
    
    // create an arrray that store key info for all existing recipes which will be used to compare against each user's likes preference array
    for (var i = 0; i < cb3.length; i++) {
        existing.push({
            key: $(cb3[i]).data('title') + "_" + $(cb3[i]).data('author'),
        });
    }

    // create an arrray that store key info for user's own existing recipes which will be used to reflect like counts for the frontend effect
    for (var j = 0; j < lis.length; j++) {
        pp.push($(lis[j]).data('pkey'));
    }

    // apply remembered likes preferences array which is extracted from python codes on page load
    for (var m = 0; m < existing.length; m++) {
        for(var n = 0; n < key_list.length; n++) {
            if ((key_list[n] === existing[m].key)) {
                $(icon3[m]).replaceWith("<div class='icon'><i class='bi-hand-thumbs-up-fill'></i></div>");
                $(cb3[m]).attr("onclick", "delike(this, value, name)");
            }
        }
    }
}

function like(t, a) {
  pos= $(t).parent().index();
  let lik = document.querySelectorAll(".lik");
  let likk = document.querySelectorAll(".lik2");
  let icon = document.querySelectorAll(".icon");
  let cb = document.querySelectorAll(".cbtn2");
  var name = $(cb[pos]).data("author");
  var no = parseFloat(lik[pos].innerHTML) + 1;

 // frontend effect: when user likes his/her own recipes, the like counts will immediately reflect on user's own recipe page
  for (var i = 0; i < pp.length; i++) {
      if (pp[i] === (a + "_" + name)){
          var noo = parseFloat(likk[i].innerHTML) + 1;
          $(likk[i]).replaceWith("<div class='lik2'>"+ noo + "</div>");
      }
  }

  // when user clicks the default like button, the button switches to active state and will execute delike if it's clicked again
  var dir = "<div class='lik'>"+ no + "</div>";
  var dir2 = "<div class='icon'><i class='bi-hand-thumbs-up-fill'></i></div>";
  $(lik[pos]).replaceWith(dir);
  $(icon[pos]).replaceWith(dir2);
  $(cb[pos]).attr("onclick", "delike(this, value)");
  
  // storing likes preference to the backend plus sql
  $.ajax({
      url:"/like",
      type:"POST",
      data:{"data":a, "data2":name, "key":a + "_" + name},
  });
}

function delike(tt, aa) {
  poss= $(tt).parent().index();
  let lik2 = document.querySelectorAll(".lik");
  let likk2 = document.querySelectorAll(".lik2");
  let icon2 = document.querySelectorAll(".icon");
  let cb2 = document.querySelectorAll(".cbtn2");
  var name2 = $(cb2[poss]).data("author");
  var no2 = parseFloat(lik2[poss].innerHTML) -1;

  // frontend effect: when user de-likes his/her own recipes, the like counts will immediately reflect on user's own recipe page
  for (var i = 0; i < pp.length; i++) {
      if (pp[i] === (aa + "_" + name2)){
          var noo2 = parseFloat(likk2[i].innerHTML) - 1;
          $(likk2[i]).replaceWith("<div class='lik2'>"+ noo2 + "</div>");
      }
  }

  // when user clicks the active like button, the button switches to default state and delike the recipe, but it will execute like if it's clicked again
  var dir3 = "<div class='lik'>" + no2 + "</div>";
  var dir4 = "<div class='icon'><i class='bi-hand-thumbs-up'></i></div>";
  $(lik2[poss]).replaceWith(dir3);
  $(icon2[poss]).replaceWith(dir4);
  $(cb2[poss]).attr("onclick", "like(this, value)");
  
  // storing likes preference to the backend plus sql
  $.ajax({
      url:"/delike",
      type:"POST",
      data:{"data":aa, "data2":name2, "key":aa + "_" + name2},
  });
}
