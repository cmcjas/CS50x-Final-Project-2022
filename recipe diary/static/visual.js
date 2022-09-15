// create audio visualisation using built-in canvas function - courtesy of youtuber Franks laboratory's tutorial video: https://www.youtube.com/c/Frankslaboratory
const container = document.getElementById('container');
const canvas = document.getElementById('canvasA');
// set canvas size to fit the page size
canvas.width = window.innerWidth;
canvas.height = window.innerHeight;
// initialising canvas elements
const ctx = canvas.getContext('2d');
ctx.lineWidth = 6;
ctx.globalCompositeOperation = 'destination-over';
const audioCtx = new (window.AudioContext)();
let audioSrc;
let analyser;

play();
function play(){
    // display canvas for the current active playing song, otherwise no canvas
    let track = $("#playlist .current").index();
    $("#player")[0].src = $("#playlist li a")[track];
    $("#player")[0].load();

    // initialising visual elements
    audioSrc = audioCtx.createMediaElementSource($("#player")[0]);
    analyser = audioCtx.createAnalyser();
    audioSrc.connect(analyser);
    analyser.connect(audioCtx.destination);
    analyser.fftSize = 64;
    const bufferLength = analyser.frequencyBinCount;
    const dataArray = new Uint8Array(bufferLength);
    const barWidth = (canvas.width/2)/bufferLength;
    let barHeight;
    let x;

    // create canvas animation using visual elements above
    function animate(){
        x = 0;
        ctx.clearRect(0, 0, canvas.width, canvas.height);
        analyser.getByteFrequencyData(dataArray);
        drawVisualiser(bufferLength, x, barWidth, barHeight, dataArray);
        drawVisualiser2(bufferLength, x, barWidth, barHeight, dataArray);
        drawVisualiser3(bufferLength, x, barWidth, barHeight, dataArray);
        requestAnimationFrame(animate);
    }
    animate();
}

// draw an animated spiral circular shape
function drawVisualiser(bufferLength, x, barWidth, barHeight, dataArray){
    for (let i = 0; i < bufferLength; i++){
        barHeight = dataArray[i] * 1.2;
        ctx.save();
        ctx.translate(canvas.width/1.6, canvas.height/1.7);
        ctx.rotate(-(i * Math.PI * 2 / (bufferLength/2)) );
        const hue = i * 8;
        ctx.fillStyle = 'hsl(' + hue + ', 100%, ' + barHeight/2 + '%)';
        ctx.strokeStyle = 'hsl(' + hue + ',100%,' + barHeight/3 + '%)';
        ctx.fillRect(0, 0, (barWidth * i)/1.2, (barHeight)/1.1);
        ctx.beginPath();
        ctx.moveTo(0, 0);
        ctx.lineTo(0, barHeight);
        ctx.arc(0, barHeight * 4, barHeight / 2, 0, Math.PI * i);
        ctx.stroke();
        x += barWidth;
        ctx.restore();
    }

    // draw an animated spikey circular shape
    for (let j = 0; j < bufferLength; j++){
        barHeight = dataArray[j]/10;
        ctx.save();
        ctx.translate(canvas.width/6, canvas.height/2);
        ctx.rotate(j + Math.PI*(barHeight/40));
        const hue = j * 3;
        ctx.fillStyle = 'hsl(' + hue + ', 100%, 50%)';
        ctx.fillRect(0, 0, (barWidth * j)/2, barHeight);
        x += barWidth;
        ctx.restore();
    }
}

// draw two animated bar charts
function drawVisualiser2(bufferLength, x, barWidth, barHeight, dataArray){
    for(let i = 0; i < bufferLength; i++){
        barHeight = dataArray[i] * 1.5;
        const red = i * barHeight/14;
        const green = i * 4;
        const blue = barHeight;
        ctx.fillStyle = 'rgb(' + red + ',' + green + ',' + blue + ')';
        ctx.fillRect(x, canvas.height - barHeight, barWidth, barHeight);
        x += barWidth;
    }

    for(let j = 0; j < bufferLength; j++){
        barHeight = dataArray[j] * 2.5;
        const red = j * barHeight/10;
        const green = 0;
        const blue = 0;
        ctx.fillStyle = 'rgb(' + red + ',' + green + ',' + blue + ')';
        ctx.fillRect((x - 1200) - barHeight/4, 0, barWidth, barHeight);
        x += barWidth;
    }
}

// render a color changing background
function drawVisualiser3(bufferLength, x, barWidth, barHeight, dataArray){

    for(let i = 0; i < bufferLength; i++){
        barHeight = dataArray[i];
        ctx.rotate(i * Math.PI * 2 / (bufferLength/2) );
        const hue = i * 8;
        ctx.fillStyle = 'hsl(' + hue  + ', 100%, ' + barHeight/2.7 + 90 + '%, 0.5)';
        ctx.fillRect(0, 0, canvas.width, canvas.height);
        x += barWidth;
    }
}



