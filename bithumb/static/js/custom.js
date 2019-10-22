
const tickerTable = document.querySelector("#ticker_table");
const tickersName = document.querySelectorAll(".ticker_name ");
const tickersPrice = document.querySelectorAll(".ticker_price");
const tickersFiveAvg = document.querySelectorAll(".ticker_fiveAvg");
const tickersState = document.querySelectorAll(".ticker_state");
const ONE_SECONDE = 1000

const ANIMATION = document.querySelector("#animation");
const ICON = document.querySelector("#animaionIcon");
const TEXT = document.querySelector("#animaionText");

const START_DAY = document.querySelector("#startDay");
const END_DAY = document.querySelector("#endDay");


const START = document.querySelector("#startBtn");
const STOP = document.querySelector("#stopBtn");


const changeTickersPrice = (resultData) => {
    idx = 0;
    resultData.map((ticker) => {
        if(tickersName[idx].innerText === ticker[0]){
            tickersPrice[idx].innerText = ticker[1]
        }
        idx++;
    })
}

const changeTickersState = (resultData) => {
    idx = 0;
    /*
        resultData[0] name
        resultData[1] 5일평균가격
        resultData[2] 상/하락장
    */
    resultData.map((resultData) => {
        if(tickersName[idx].innerText === resultData[0]){
            tickersFiveAvg[idx].innerText = resultData[1]
            tickersState[idx].innerText = resultData[2]
            if(resultData[2] === '상승장'){
               tickersFiveAvg[idx].classList.add('text-primary')
               tickersState[idx].classList.add('text-primary')
            }else{
               tickersFiveAvg[idx].classList.add('text-danger')
               tickersState[idx].classList.add('text-danger')
            }
        }
        idx++;
    })
}

const getRealTimeTickersPrice = () => {
    $.ajax({
        url: '/cat/price',
        method: 'GET',
        dataType: 'json',
        success: function(data) {
        //console.log('getRealTimeTickersPrice');
        console.log(data);
        changeTickersPrice(data);
        }
    });
   setTimeout(getRealTimeTickersPrice, ONE_SECONDE*10);
}

const getUpDownData = () =>{
     $.ajax({
        url: '/cat/updown',
        method: 'GET',
        dataType: 'json',
        success: function(data) {
        changeTickersState(data)
        }
    });
    setTimeout(getRealTimeTickersPrice, ONE_SECONDE*60);
}




const startClick = () =>{
    console.log("startClick!!");

    const sendData =  { userId   : 'shoon2430',
                        userName : '정승훈',
                        startDay : START_DAY.value,
                        endDay   : END_DAY.value
                        };

    ANIMATION.classList.remove('animation_div_stop');
    ICON.classList.remove('loader-icon_stop');
    TEXT.classList.remove('loader-text_stop');

    ANIMATION.classList.add('animation_div');
    ICON.classList.add('loader-icon');
    TEXT.classList.add('loader-text');
    START.style.display = "none";
    STOP.style.display = "block";
    ANIMATION.children[1].innerText = "TRADING";
    ANIMATION.children[2].innerText = "Making Money...";


    $.ajax({
        url: '/cat/trade/start',
        data: sendData,
        method: 'POST',
        dataType: 'json',
        success: function(data) {
        console.log('trade END!!');
        console.log('MAX : '+data.max);
            ANIMATION.classList.remove('animation_div');
            ICON.classList.remove('loader-icon');
            TEXT.classList.remove('loader-text');

            ANIMATION.classList.add('animation_div_stop');
            ICON.classList.add('loader-icon_stop');
            TEXT.classList.add('loader-text_stop');
            START.style.display = "block";
            STOP.style.display = "none";
            ANIMATION.children[1].innerText = "TRADE";
            ANIMATION.children[2].innerText = "Do Nothing...";
        }
    });
}


const stopClick = () =>{
    const sendData =  {userId: 'shoon2430', userName: '정승훈'};

    console.log("stopClick!!");

    $.ajax({
        url: '/cat/trade/stop',
        data: sendData,
        method: 'POST',
        dataType: 'json',
        async: false,
        success: function(data) {
            console.log(data);
             ANIMATION.children[1].innerText = "ENDING";
             ANIMATION.children[2].innerText = "Please Wait...";
        },
        error:function(request,status,error){
            alert("code:"+request.status+"\n"+"message:"+request.responseText+"\n"+"error:"+error);
             }
    });
}


const buttonManageMent = function(){
    START.addEventListener("click",()=>startClick());
    STOP.addEventListener("click",()=>stopClick());
}




$(function() {
    console.log("coustomJS~");

    ANIMATION.classList.add('animation_div_stop');
    ICON.classList.add('loader-icon_stop');
    TEXT.classList.add('loader-text_stop');
    START.style.display = "block";
    STOP.style.display = "none";
    ANIMATION.children[2].innerText = "Do Nothing...";

    buttonManageMent();

    $("#startDay").datepicker({
        uiLibrary: 'bootstrap4'
    });

    $("#endDay").datepicker({
        uiLibrary: 'bootstrap4'
    });

    //getRealTimeTickersPrice();
    //getUpDownData();

})