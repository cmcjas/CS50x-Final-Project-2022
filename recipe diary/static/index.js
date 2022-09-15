// By default, when the recipe page is loaded, only the recipe section is shown, and the audio section is hided unless icon is clicked
$(".mp3page").hide();
$('.bi-menu-down').addClass("current");

// By default, when the home page is loaded, only the weather section is shown, and the rest are hided unless the corresponding icon is clicked
$(".profile").hide();
$('#planpage').hide();
$('.bi-cloud-fog2-fill').addClass("current");
$('.weathertemp').hide();
$('#search').hide();
$('#searchlist').hide();
$('.bar').hide();

// Allow appropraite auto page scrolling for create and edit pages when user clicks add/del of an element such as ingredients, methods etc.
function scroll(s){
    $('html,body').animate({
    scrollTop: $(s).offset().top},
    'slow');
}

// Only appropirate elements are shown on the recipe page when the corresponding icon is clicked
function menu(){
    $('.bi i').removeClass("current");
    $('.bi-menu-down').addClass("current")
    $(".mp3page").hide();
    $(".recipepage").show()
}

function playmp3(){
    $('.bi i').removeClass("current");
    $('.bi-music-note-list').addClass("current")
    $(".mp3page").show();
    $(".recipepage").hide()
}

// Only appropirate elements are shown on the home page when the corresponding icon is clicked
function plan(){
    $('.backimage img').hide();
    $('.weathertemp').hide();
    $('.weather').hide();
    $('#planpage').show();
    $('.weapic img').hide();
    $('.bi-egg-fried').removeClass("current");
    $('#search').hide()
    $('#searchlist').hide();
    $('.genre i').removeClass("current");
    $('.bi-cloud-fog2-fill').removeClass("current");
    $('.profile').hide();
    $('.bi-book-half').addClass("current");
    $('.bi-person-lines-fill').removeClass("current");
    $('.bar').hide();
}

function backhome(){
    $('.backimage img').hide();
    $('.weathertemp').show();
    $('#planpage').hide();
    $('.weapic img').show();
    $('.bi-egg-fried').removeClass("current");
    $('#search').hide()
    $('#searchlist').hide();
    $('.genre i').removeClass("current");
    $('.bi-book-half').removeClass("current");
    $('.profile').hide();
    $('.bi-cloud-fog2-fill').addClass("current");
    $('.bi-person-lines-fill').removeClass("current");
    $('.bar').hide();
}

function people(){
    $('#search').show();
    $('#searchlist').show();
    $('.backimage img').hide();
    $('.weathertemp').hide();
    $('.weather').hide();
    $('#planpage').hide();
    $('.weapic img').hide();
    $('.bi-egg-fried').removeClass("current");
    $('.genre i').removeClass("current");
    $('.bi-cloud-fog2-fill').removeClass("current");
    $('.profile').hide();
    $('.bi-book-half').removeClass("current");
    $('.bi-person-lines-fill').addClass("current");
    $('.bar').hide();
}

function food(){
    $('.bi-person-lines-fill').removeClass("current");
    $('.bi-cloud-fog2-fill').removeClass("current");
    $('.bi-book-half').removeClass("current");
    $('.weathertemp').hide();
    $('.weather').hide();
    $('.weapic img').hide();
    $('#planpage').hide();
    $('#search').hide()
    $('#searchlist').hide();
    $('.bar').show();
    $('.bi-egg-fried').addClass("current")
    let dir = "<img src='/static/img/kitchen.jpg'></img>"
    $(".profile").show();
    $('.backimage img').hide();
    $('.backimage').append(dir);
}

// codes that control the audio playlist on recipe page
audioPlayer();
function audioPlayer(){
    let track = 0;
    // set selected track as current and highlight it via css
    $("#player")[0].src = $("#playlist li a")[0];
    $("#playlist li")[0].className = "current";
    $("#playlist li a").click(function(e){
        e.preventDefault();
        $("#player")[0].src = this;
        $("#player")[0].play();
        $("#playlist li").removeClass("current");
        $(this).parent().parent().addClass("current");
        // if shuffle is enabled, apply shuffle function to playlist otherwise keep playlist as normal
        if (shuff === true){
            shuffle();
        }else{
            orderplay(); 
        }
    });
    // keep playlist as normal after current song ended
    orderplay();
    return;
}

// function to take playlist index into an array and randomise it via algorithm() function
function shuffle(){
    var trackOrder = [];
    var shuffOrder = [];
    var p = -1;

    // assign playlist index into array
    for(var i = 0; i < $("#playlist li").length; i++){
        trackOrder.push(i);
    }
    // store newly randomised index into array and pass it to shuffle playing function
    shuffOrder = algorithm(trackOrder);

    shuffplay(shuffOrder, p);
    return;
}


function shuffplay(array, pos){

    if(pos === array.length - 1){
        $("#playlist li").removeClass("current");
        $("#playlist li")[array[pos]].className = "current";

        $("#player")[0].src = $("#playlist li a")[array[pos]];
        $("#player")[0].play();

        shuffle();
    }
    else{
        $("#player")[0].addEventListener("ended", function(){
            pos++;
    
            $("#playlist li").removeClass("current");
            $("#playlist li")[array[pos]].className = "current";
        
            $("#player")[0].src = $("#playlist li a")[array[pos]];
            $("#player")[0].play();
    
            shuffplay(array, pos);    
        });
    }
    return;
}

// By default, bool false is set for shuffle, when shuffle button is clicked, shuffle will enable or disable depending on the exisitng bool value for shuffle.
var shuff = false;
function enableShuffle(){

    // if shuffle is already on, set bool false for shuffle and disable it by telling playlist to act normal after shuffle button is clicked
    if(shuff === false){
        $("#hi").text("Shuffle ON");
        shuff = true;
        shuffle();
    }
    else {
        $("#hi").text("Shuffle OFF");
        shuff = false;
        orderplay();
    }
    return;
}

// a simple randomised algorithm that take an array of index numbers and return a different randomised version of it each time
function algorithm(array){
    // using js Math function for randomising
    for(let i = array.length - 1; i > 0; i--){
        let j = Math.floor(Math.random() * (i + 1));
        let temp = array[i];
        array[i] = array[j];
        array[j] = temp;
    }
    return array;
}

// telling the playlist to play songs in a normal way which is to play them in order, if it reaches the end of the playlist, set track to zero and restart the playlist
function orderplay(){
    let track = $("#playlist .current").index();

    $("#player")[0].addEventListener("ended", function(){
        track++;

        if(track == $("#playlist li").length){
            track = 0; 
        }
        $("#playlist li").removeClass("current");
        $("#playlist li")[track].className = "current";
        $("#player")[0].src = $("#playlist li a")[track];
        $("#player")[0].play();   
        // telling the playlist to continue through all the tracks after the current song is ended via recursion
        orderplay()
    });
    return;
}

// asking the playlist to play the next songs in the playlist, unaffect by shuffle though
function next(){
    let next = 0;
    let pos = $("#playlist .current").index();

    if(shuff === true){
        if (pos == $("#playlist li").length - 1){
            next = 0;
        }
        else{
            next = pos + 1;
        }
    
        $("#playlist li").removeClass("current");
        $("#playlist li")[next].className = "current"
    
        $("#player")[0].src = $("#playlist li a")[next];
        $("#player")[0].play(); 

        shuffle();
    }
    else{
        if (pos == $("#playlist li").length - 1){
            next = 0;
        }
        else{
            next = pos + 1;
        }
    
        $("#playlist li").removeClass("current");
        $("#playlist li")[next].className = "current"
    
        $("#player")[0].src = $("#playlist li a")[next];
        $("#player")[0].play(); 
    
        orderplay();

    }
    return;
}

// asking the playlist to play the previous songs in the playlist, unaffect by shuffle though
function prev(){
    let prev = 0;
    let pos = $("#playlist .current").index();

    if(shuff === true){
        if(pos == 0){
            prev = $("#playlist li").length - 1; 
        }
        else{
            prev = pos - 1;
        }
    
        $("#playlist li").removeClass("current");
        $("#playlist li")[prev].className = "current"
    
        $("#player")[0].src = $("#playlist li a")[prev];
        $("#player")[0].play();
    
        shuffle();
    }
    else{
        if(pos == 0){
            prev = $("#playlist li").length - 1; 
        }
        else{
            prev = pos - 1;
        }
    
        $("#playlist li").removeClass("current");
        $("#playlist li")[prev].className = "current"
    
        $("#player")[0].src = $("#playlist li a")[prev];
        $("#player")[0].play();
        orderplay();
    }
    return;
}

// disable download functionality while a youtube->mp3 conversion is underway
function noEmptySubmit(form) {
    var controls = form.elements;

    $("#text").text("Download In Progress...Please Wait.");
    document.getElementById("download").disabled = true;

    // pass only non-emptied url fields for submition
    for (var i = 0; i < controls.length; i++) {
        controls[i].disabled = controls[i].value == ''; 
    } 

}















