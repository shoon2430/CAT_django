SignUp_ID = document.querySelector("#userId")
SignUp_PASSWORD = document.querySelector("#userPassword")
SignUp_NAME = document.querySelector("#userName")
SignUp_PHONE = document.querySelector("#phone")


const signUpCheck = () =>{
    //전화번호 정규식
    var regExp = /^\d{3}-\d{3,4}-\d{4}$/;

    if(SignUp_ID.value === ""){
        alert("Please enter your ID");
        return false;
    }else if(SignUp_PASSWORD.value === ""){
        alert("Please enter your PASSWORD");
        return false;
    }else if(SignUp_NAME.value === ""){
        alert("Please enter your NAME");
        return false;
    }else if(SignUp_PHONE.value === ""){
        alert("Please enter your PHONE");
        return false;
    }else if(regExp.test(SignUp_PHONE.value)){
        alert("Is not valid your Phone number");
        return false;
    }

    else
        return true;
}


const init = () => {

}


