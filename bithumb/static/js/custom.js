
const tickerTable = document.querySelector("#ticker_table");
const tickersName = document.querySelectorAll(".ticker_name ");
const tickersPrice = document.querySelectorAll(".ticker_price");
const tickersFiveAvg = document.querySelectorAll(".ticker_fiveAvg");
const tickersState = document.querySelectorAll(".ticker_state");
const TICKER = document.querySelector("#ticker");

const ONE_SECONDE = 1000

const ANIMATION = document.querySelector("#animation");
const ICON = document.querySelector("#animaionIcon");
const TEXT = document.querySelector("#animaionText");

const START_DAY = document.querySelector("#startDay");
const END_DAY = document.querySelector("#endDay");


const START = document.querySelector("#startBtn");
const STOP = document.querySelector("#stopBtn");
const USER_ID = document.querySelector("#userId")
const USER_NAME = document.querySelector("#userName")


const SEETING_BOX =  document.querySelector("#programSetting");
const SETTING = document.querySelector("#settingBtn");

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


    const sendData =  { 'userId'   : USER_ID.value,
                        'userName' : USER_NAME.value,
                        'ticker'   : TICKER.value == "" ? 'BTC' : TICKER.value,
                        'startDay' : START_DAY.value,
                        'endDay'   : END_DAY.value
                        };

    setStating();

    $.ajax({
        url: '/cat/start',
        data: sendData,
        method: 'POST',
        dataType: 'json',
        success: function(data) {
        console.log('trade END!!');
        console.log('MAX : '+data.max);
        }
    });
}


const stopClick = () =>{
    const sendData =  { 'userId': USER_ID.value,
                        'userName': USER_ID.value};

    console.log("stopClick!!");

    ANIMATION.children[1].innerText = "ENDING";
    ANIMATION.children[2].innerText = "Please Wait...";

    $.ajax({
        url: '/cat/stop',
        data: sendData,
        method: 'POST',
        dataType: 'json',
        async: false,
        success: function(data) {
            console.log(data);
            setNomal();

        },
        error:function(request,status,error){
            alert("code:"+request.status+"\n"+"message:"+request.responseText+"\n"+"error:"+error);
             }
    });
}

const settingClick = () =>{
    console.log("settingClick");

    if(SEETING_BOX.style.display === "none"){
        SEETING_BOX.style.display = 'block'

        offset = $("#programSetting").offset();
        $('html, body').animate({scrollTop : offset.top});
    }else{
        SEETING_BOX.style.display = 'none'
    }
}

const tickerChange = () =>{
    console.log("tickerChange");

    if(TICKER.value == ""){
        TICKER.classList.remove('setDark');
    }else{
        TICKER.classList.add('setDark');

        const ticker_name = document.querySelector("#tickerName");
        const price = document.querySelector("#price");
        const up_down = document.querySelector("#updown");
        const mdd = document.querySelector("#mdd");
        const hpr = document.querySelector("#hpr");
        const loaders = document.querySelectorAll(".loader");
        const dataList = document.querySelectorAll(".dataList");

        $.ajax({
            url:'tickerInfo',
            data:{'ticker':TICKER.value},
            method:'POST',
            dataType:'json',
            success:function(data) {
                console.log(data);
                ticker_name.value = data.tickerName+"("+data.tickerKName+")";
                price.value = data.nowPrice;
                up_down.value = data.upDown;
                mdd.value = data.MDD;
                hpr.value = data.HPR;

            },beforeSend:function(){
                TICKER.disabled = true
                TICKER.style.background = '#343a40';

                for(let idx=0; idx< dataList.length; idx++){
                    dataList[idx].classList.add('hide');
                }

                for(let idx=0; idx< loaders.length; idx++){
                    loaders[idx].classList.remove('hide');
                }

            }
            ,complete:function(){
                TICKER.disabled = false
                TICKER.style.background = "";

                for(let idx=0; idx< dataList.length; idx++){
                    dataList[idx].classList.remove('hide');
                }

                for(let idx=0; idx< loaders.length; idx++){
                    loaders[idx].classList.add('hide');
                }
            },
            error:function(request,status,error){
                alert("code:"+request.status+"\n"+"message:"+request.responseText+"\n"+"error:"+error);
            }
            ,timeout:100000

        });
    }
}

const buttonManageMent = function(){
    START.addEventListener("click",()=>startClick());
    STOP.addEventListener("click",()=>stopClick());
    SETTING.addEventListener("click",()=>settingClick());
    TICKER.addEventListener("change",()=>tickerChange());
}



const setNomal = ()=>{
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

const setStating = ()=>{
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
}

const setEnding = ()=>{
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

$(function() {
    console.log("coustomJS~");
    const myStatus = document.querySelector("#userStatus")

    if(myStatus.value === 'N'){
        setNomal();
    }else if(myStatus.value === 'Y'){
        setStating();
    }



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