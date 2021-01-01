$( document ).ready(function() {
    $('#button').click(function() {
        var empty = true;
        $('input[type="text"]').each(function(){
           if($(this).val()!=""){
              empty =false;
              return false;
            }
         });

         if(empty == false){
            deleteErrorMessages();
            // load icon
            var boton = document.getElementById("button").innerHTML = '<i id="spinner" class="fa fa-spinner fa-spin"></i>';
         }
    })

    // delete error messages
    function deleteErrorMessages(){
       $('div.notification.is-danger').remove()
       $('#url_fanfic').removeClass('.is-danger')
    }
})