
const tickerTable = document.querySelector("#ticker_table");
const tickersName = document.querySelectorAll(".ticker_name ");
const tickersPrice = document.querySelectorAll(".ticker_price");
const tickersFiveAvg = document.querySelectorAll(".ticker_fiveAvg");
const tickersState = document.querySelectorAll(".ticker_state");
const ONE_SECONDE = 1000

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


$(function() {

    getRealTimeTickersPrice();
    getUpDownData();

})