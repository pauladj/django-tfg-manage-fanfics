window.onload = function() {


    window.notifierSocket = new WebSocket(
        'ws://' + window.location.host +
        '/ws/notification/');

    var notificationBubble = document.getElementById("notification-bubble")

    notifierSocket.onmessage = function(e) {
        var data = JSON.parse(e.data);
        var action = data['action'];
        if (action == "mark_as_read"){
            var notificationId = data['notificationid'];
            var element = $("article.notification").find("[data-notificationid='" + notificationId + "']"); 
            $(element).parent().parent().removeClass('unread');
        }else if(action == "new_notification"){
            // Info
            var notificationId = data['notificationid'];
            var link = data['link'] == null ? '' : data['link'];
            var read = data['read'] == false ? 'unread' : "";
            var subject = data['subject'];
            var reverse = data['reverse'];
            var verb = data['verb'];
            var target = data['target'];
            var image = data['image'];
            var date = data['date'];
       
            // Add to bubble
            var unseenNotifications = parseInt(notificationBubble.getAttribute("data-badge")) + 1;
            if (unseenNotifications == 1){
                $("#notification-bubble").addClass("bubble");
            }
            if (unseenNotifications >= 100){
                $("#notification-bubble").attr('data-badge', 99);
            }else{
                $("#notification-bubble").attr('data-badge', unseenNotifications);
            }
            
            // add element
            var newNotification = `<a href="${link}">
<article class="media ${read} notification ">`;
            if (image != null){
                newNotification += `<figure class="media-left" style="margin-right: 0.5em;">
      <p class="image is-48x48">
        <img src="${image}" style="width: 48px; border-radius: 100%; height: 48px; object-fit: cover; max-width: 40px; min-width: 40px;">
      </p>
    </figure>`;
            }
    
            newNotification += `
    <div class="media-content">
      <div class="content">
        <p>
          <strong>`;

            if (reverse == true){
                newNotification += `${target}</strong> ${verb} ${subject}`;
            }else{
                newNotification += `${subject}</strong> ${verb} ${target}`;
            }

            newNotification+=`
            
          <br>
          <span class="notifier-when">${date}</span>
        </p>
      </div>
    </div>
    <div class="media-right">
            <span 
            data-notificationid=${notificationId}
            data-tippy-content='Mark as read'
            data-tippy-arrow="true" 
            data-tippy-animation="fade" 
            style="font-size: 0.6rem; color: #0003" class="tippy hidden circle"><i class="fas fa-circle fa-xs"></i></span>
    </div>
  </article></a>`;
            
            // añadir elemento creado
            if ($('.empty-block').length) {
                $('#notification-container .empty-block').remove();
            }
            $("#notification-container").prepend(newNotification);
            newNotification = $("#notification-container").children().eq(0).find('article.notification')
            showSymbolOnHover(newNotification);
            addSymbolListener(newNotification.find("span.circle"))
            tippy('.tippy') // popover
        }else if(action == "mark_all_as_read"){
            if (data['message'] == "success"){
                $("article.notification").removeClass('unread');
            }
        }else if(action == "mark_all_as_seen"){
            if (data['message'] == "success"){
                $("#notification-bubble").removeClass("bubble");
            }
        }else if(action == "error"){
            var errorMsg = data['message'];

            toastr.error(errorMsg, 'Notification error');

        }
    };

    notifierSocket.onclose = function(e) {
        show_floating_error();
    };
    
    // if hover over notification show mark as read symbol
    function showSymbolOnHover(element){
        $(element).hover(function(){
            if ($(this).hasClass("unread")){
                $(this).find("span.circle").removeClass("hidden");
            }
        }, function() {
            $(this).find("span.circle").addClass("hidden");
        });
    }
    showSymbolOnHover("article.notification");

    // add listener to symbol to send mark as read
    function addSymbolListener(element){
        $(element).on("click",function(e){
            e.preventDefault();
            e.stopPropagation();
            var notificationId = this.getAttribute('data-notificationid');
            if (notifierSocket.readyState == 2 || notifierSocket.readyState == 3){
                show_floating_error();
            }else{
                notifierSocket.send(JSON.stringify({
                    'action': "mark_as_read",
                    'notificationid': notificationId
                }));
            }
            
        });
    }
    addSymbolListener("span.circle");
    
    $(".all-as-read").on("click",function(e){
        e.preventDefault();
        e.stopPropagation();
        if (notifierSocket.readyState == 2 || notifierSocket.readyState == 3){
            show_floating_error();
        }else{
            notifierSocket.send(JSON.stringify({
                'action': "mark_all_as_read",
            }));
        }
    });
}

/**
 * Mark all the notifications as seen so they don't appear in the bubble
 */
function mark_all_as_seen(){
    if (notifierSocket.readyState == 2 || notifierSocket.readyState == 3){
        show_floating_error();
    }else{
        notifierSocket.send(JSON.stringify({
            'action': "mark_all_as_seen",
        }));
    }
}

/**
 * Show a floating error message
 */
function show_floating_error(){
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

    toastr.error('There was a connection error with the server. Try to reload the page :(','Notification error');

}

