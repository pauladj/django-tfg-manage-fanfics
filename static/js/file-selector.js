$(document).ready(function () {

    var file = document.getElementById("file");
    if (file != null){
        file.onchange = function(){
            if(file.files.length > 0){
                document.getElementById('filename').innerHTML = file.files[0].name;
            }
        };
        
        var submitButton = document.getElementById("submitButton");
        submitButton.onclick = function(e){
            var files = document.getElementById("file").files;
            if (files.length > 0){ 
                // there si a file
                var size = files[0].size; // bytes
                if (size > 1200000){// more than 1MB
                    e.preventDefault();
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
                
                    toastr.warning('The image size is bigger than 1MB');
                }
            }
        };
    }
   
})