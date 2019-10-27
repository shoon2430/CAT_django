

const ID = document.querySelector("#userId")
const PASSWORD = document.querySelector("#userPassword")
const ERROR = document.querySelector("#errorText")

const loginCheck = () =>{
    if(ID.value === ""){
        alert("Please enter your ID");
        return false;
    }else if(PASSWORD.value === ""){
        alert("Please enter your PASSWORD");
        return false;
    }
    else
        return true;
}


const loginFalse = () =>{

    if(ERROR !== null){
        alert(ERROR.textContent);
    }
}

const init = ()=>{
    loginFalse();
}

init();