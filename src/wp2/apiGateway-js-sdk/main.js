var apigClient = apigClientFactory.newClient({});
console.log(1)

// $(".login100-form-btn").click(function() {
//     // event.stopPropagation();
//     // event.stopImmediatePropagation();

// });

function PostData() {
    console.log(2)
    passcode = $('.input100').val();
    console.log(passcode)  // outputs a message to the web console
    var body = {
        "message": {
            "passcode": passcode
            }
        };
       
        
    apigClient.rootPost({}, body, {})
        .then(function(result){
            console.log(result);
            var body = result.data.body;
            var res = body['valid'];
            var name = body['name'];

            // hardcode 
            // var res = "valid";
            // var name = "Jeffrey";

            console.log(res);
            if (res == "valid") {
                sessionStorage.setItem("visitorName", name);
                
                window.open("./success.html", "_self")
            } else if (res == "not valid") {
                alert("Permission denied!");
            }
        }).catch(function(result){
            console.log("failed");
        });

    return false;
}