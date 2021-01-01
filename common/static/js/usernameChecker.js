$( document ).ready(function() {
    $('#id_username').keyup(function() {
        $.ajax({  
            type: "GET",  
            url: check_username_url + "?username=" + document.getElementById('id_username').value,  
            beforeSend: function() {
                // Hide icon and message fail
                var fail_elements = document.getElementsByClassName('username_fail');
                for(var i=0;i<fail_elements.length;i++){
                    fail_elements[i].style.display = "none";
                }
                // Start spinning
                document.getElementById('spinner').style.display = "";
            },
            success: function (response) {  
                // 200
                // Hide spinning
                document.getElementById('spinner').style.display = "none";
            },
            statusCode: {
                404: function() {
                    // Hide spinning
                    document.getElementById('spinner').style.display = "none";
                    // show icon and message fail
                    var fail_elements = document.getElementsByClassName('username_fail');
                    for(var i=0;i<fail_elements.length;i++){
                        fail_elements[i].style.display = "";
                    }
                }
            },
        });
    });
});