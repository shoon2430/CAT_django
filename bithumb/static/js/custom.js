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

const START = document.querySelector("#startBtn");
const STOP = document.querySelector("#stopBtn");
const USER_ID = document.querySelector("#userId");
const USER_NAME = document.querySelector("#userName");

const SEETING_BOX =  document.querySelector("#programSetting");
const SETTING = document.querySelector("#settingBtn");

const mddSelect = document.querySelector("#mddSelect");
const hprSelect = document.querySelector("#hprSelect");

const ticker_name = document.querySelector("#tickerName");
const price = document.querySelector("#price");
const up_down = document.querySelector("#updown");
const mdd = document.querySelector("#mdd");
const hpr = document.querySelector("#hpr");
const loaders = document.querySelectorAll(".loader");
const dataList = document.querySelectorAll(".dataList");

const tradeReal = document.querySelector("#realTradingBtn");
const tradeTest = document.querySelector("#testTradingBtn");

const BV = document.querySelector("#BV");
const BB = document.querySelector("#BB");
const ST = document.querySelector("#ST");

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

    let type = ""
    if(BV.checked == true) type = "BV"
    if(BB.checked == true) type = "BB"
    if(ST.checked == true) type = "ST"

    const sendData =  { 'userId'   : USER_ID.value,
                        'userName' : USER_NAME.value,
                        'ticker'   : TICKER.value == "" ? 'BTC' : TICKER.value,
                        'kind'     : tradeTest.checked ? "TEST" : "REAL",
                        'type'     : type
                        };

    console.log(sendData);

    setStating();

    $.ajax({
        url: '/cat/start',
        data: sendData,
        method: 'POST',
        dataType: 'json',
        success: function(data) {
        console.log('trade START!!');
        }
    });
}


const stopClick = () =>{
    console.log("stopClick!!");
    const sendData =  { 'userId': USER_ID.value,
                        'userName': USER_ID.value,
                        'kind'     : tradeTest.checked ? "TEST" : "REAL"
                        };

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

const getBacktastResult = (obj) =>{

    const TYPE = obj.id.substr(0,3).toUpperCase();
    console.log(TYPE);
    let loader = "";
    let Info = "";

    const sendData = {
        'ticker' : TICKER.value,
        'selectType': TYPE,
        'dateType': obj.value
    }

    loader = TYPE == "MDD" ?  document.querySelector("#mdd_loader") :  document.querySelector("#hpr_loader") ;
    Info = TYPE == "MDD" ?  document.querySelector("#mddInfo") :  document.querySelector("#hprInfo") ;

    $.ajax({
         url:'backTest',
            data: sendData,
            method:'POST',
            dataType:'json',
            success:function(data) {
                console.log(data);

                if(TYPE == 'MDD')
                    mdd.value = data['bt'];
                else if(TYPE == 'HPR')
                    hpr.value = data['bt'];

            },beforeSend:function(){
                loader.classList.remove('hide');
                Info.classList.add('hide');
            }
            ,complete:function(){
                loader.classList.add('hide');
                Info.classList.remove('hide');
            },
            error:function(request,status,error){
                alert("code:"+request.status+"\n"+"message:"+request.responseText+"\n"+"error:"+error);
            }
            ,timeout:100000

    })
}


const TEST = document.querySelector("#testBtn");

const testing = () =>{
    console.log("testBtn CLICKS~");

    let type = ""
    if(BV.checked == true) type = "BV"
    if(BB.checked == true) type = "BB"
    if(ST.checked == true) type = "ST"

    const sendData =  { 'userId'   : USER_ID.value,
                        'userName' : USER_NAME.value,
                        'ticker'   : TICKER.value == "" ? 'BTC' : TICKER.value,
                        'kind'     : tradeTest.checked ? "TEST" : "REAL",
                        'type'     : type
                        };

    $.ajax({
        url:'test',
        data : sendData,
        method: 'POST',
        dataType: 'json',
        success: function(data) {
            console.log('TEST POST!!');
        },
        error:function(request,status,error){
            alert("code:"+request.status+"\n"+"message:"+request.responseText+"\n"+"error:"+error);
        }
    });
}

const buttonManageMent = function(){
    START.addEventListener("click",function(){startClick()});
    STOP.addEventListener("click",function(){stopClick()});
    SETTING.addEventListener("click",function(){settingClick()});
    TICKER.addEventListener("change",function(){tickerChange()});
    mddSelect.addEventListener("change",function(){getBacktastResult(this)});
    hprSelect.addEventListener("change",function(){getBacktastResult(this)});
    //테스트용
    TEST.addEventListener("click",function(){testing()});

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

    tradeTest.checked = true;
    BV.checked =true;

    if(myStatus.value === 'N'){
        setNomal();
    }else if(myStatus.value === 'Y'){
        setStating();
    }
    buttonManageMent();

    //실제 사용시 가림
    //TEST.style.display = 'none'

//    $("#startDay").datepicker({
//        uiLibrary: 'bootstrap4'
//    });
//
//    $("#endDay").datepicker({
//        uiLibrary: 'bootstrap4'
//    });

})