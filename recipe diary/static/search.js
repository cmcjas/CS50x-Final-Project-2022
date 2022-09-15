// codes for the sharing page search function, 
// get all relevant elements
const searchInput = document.querySelector("[data-search]");
const searchInputt = document.querySelector("[data-search2]");
let p = document.querySelectorAll(".listbtn");
let c = document.querySelectorAll(".cbtn");
let c2 = document.querySelectorAll(".cbtn2");
let m = document.querySelectorAll(".msgsubmit");
let img = document.querySelectorAll(".img");
let t = document.querySelectorAll(".typebtn");
var ele = document.getElementById("ele");

// hide multiple elements initially, unless user input matches
$(p).hide();
$(img).hide();
$(c).hide();
$(c2).hide();
$(m).hide();

// listen for user input and matches existing data by each input letters or selected type of food
searchInput.addEventListener("input", (e) => {
    $(m).hide();

    var v = e.target.value.toLowerCase();
    var value = ele.options[ele.selectedIndex].text.toLowerCase();

    for(var i = 0; i < p.length; i++) {
        var v2 = p[i].value.toLowerCase();
        var v3 = t[i].value.toLowerCase();
        
        const isVisible = v2.includes(v);
        const isVisible2 = v3.includes(value)

         // if type none is selected, no filtering aplly and show all recipes
        if (value === 'none'){
            slogic1(isVisible, !isVisible, p[i], img[i], c[i], c2[i], p, img, c, c2,'','','','', v);
        }
        else{
            slogic1(isVisible && isVisible2, !isVisible || !isVisible2, p[i], img[i], c[i], c2[i], p, img, c, c2,'','','','', v);
        }
    }
});

// search codes for the user recipe page search function
// get all relevant elements
const searchInput2 = document.querySelector("[current-search]");
let p2 = document.querySelectorAll(".listbtn2");
let img2 = document.querySelectorAll(".img2");
let t2 = document.querySelectorAll(".typebtn2");
let r = document.querySelectorAll(".rmbtn");
let ed = document.querySelectorAll(".ebtn");
var ele2 = document.getElementById("ele2");

// listen for user input and matches existing data by each input letters or selected type of food
searchInput2.addEventListener("input", (E) => {
    var vv = E.target.value.toLowerCase();
    var value2 = ele2.options[ele2.selectedIndex].text.toLowerCase();

    for(var i = 0; i < p2.length; i++) {
        var vv2 = p2[i].value.toLowerCase();
        var vv3 = t2[i].value.toLowerCase();
        
        const isVisiblee = vv2.includes(vv);
        const isVisible3 =  vv3.includes(value2);

        // if type none is selected, no filtering aplly and show all recipes
        if (value2 === 'none'){
            if (isVisiblee){
                $(p2[i]).show();
                $(img2[i]).show();
                $(r[i]).show();
                $(ed[i]).show();
            }
            else {
                $(p2[i]).hide();
                $(img2[i]).hide();
                $(r[i]).hide();
                $(ed[i]).hide();
            }
        }
        else {
            slogic1(isVisiblee && isVisible3, !isVisiblee || !isVisible3, p2[i], img2[i],'','', p2, img2,'','', r[i], ed[i], r, ed, vv);
        }
    }
});

// empty recipes display upon selecting type of food
function empty(i,j,mm,n){
    i.hide();
    j.hide();
    mm.hide();
    n.hide();
}

// make sure relevant elements are shown dynamically as users type in and search for recipes
function slogic1(s, d, x, y, z, z0, x1, y1, z1, z01, xx, yy, xx1, yy1, last){
    if (s){
        $(x).show();
        $(y).show();
        $(z).show();
        $(z0).show();
        $(xx).show();
        $(yy).show();
    }
    else if(d){
        $(x).hide();
        $(y).hide();
        $(z).hide();
        $(z0).hide();
        $(xx).hide();
        $(yy).hide();
    }
    if (last.length === 0){
        $(x1).hide();
        $(y1).hide();
        $(z1).hide();
        $(z01).hide();
        $(xx1).hide();
        $(yy1).hide();
    }
}

// show message input field
function msg(n){
    var pos = $(n).parent().index();
    $(m[pos]).show();
}
// remove message input field
function can(nn){
    var poss = $(nn).parent().parent().parent().parent().index();
    $(m[poss]).hide();
}