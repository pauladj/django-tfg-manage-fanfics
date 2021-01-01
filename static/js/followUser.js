$( document ).ready(function() {

    $('#follow').click(function() {
        $.ajax({  
            type: "POST",  
            url: toggleFollowUser,
            data: {'targetId': profileUserId},
            beforeSend: function(xhr, settings) {
                xhr.setRequestHeader("X-CSRFToken", csrftoken);
                // Start spinning
                document.getElementById('spinner').style.display = "";
                // hide icons
                document.getElementById("symbol").style.display = "none";
            },
            success: function (response) {  
                // 200
                // Hide spinning
                document.getElementById('spinner').style.display = "none";
                 // show icons
                document.getElementById("symbol").style.display = "";

                // Change button
                $("#follow").toggleClass("action-outline-red");
                $("#follow").toggleClass("action-outline-green");

                $("#symbol").toggleClass("fa-times");
                $("#symbol").toggleClass("fa-plus");

                var text = $("#follow").find("p")

                if (response == "created"){
                    // following now
                    text.text("Unfollow");
                
                }else if(response == "deleted"){
                    // no following anymore
                    text.text("Follow");
                }
            },
            error: function (response){
                // show toast with error
                document.getElementById('spinner').style.display = "none";
                toastr.options = {
                    "closeButton": true,
                    "debug": false,
                    "newestOnTop": true,
                    "progressBar": false,
                    "positionClass": "toast-top-center",
                    "preventDuplicates": true,
                    "onclick": null,
                    "showDuration": "100",
                    "hideDuration": "1000",
                    "timeOut": "9000",
                    "extendedTimeOut": "1000",
                    "showEasing": "swing",
                    "hideEasing": "linear",
                    "showMethod": "fadeIn",
                    "hideMethod": "fadeOut"
                    }
            
                toastr.error('There was an error, try again in a few seconds.');
            }
        });
    });
});