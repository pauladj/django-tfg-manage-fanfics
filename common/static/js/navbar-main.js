
// COnfigure scroll
// https://www.jqueryscript.net/demo/Facebook-like-jQuery-Scrollbar-Plugin-slimScroll/examples/
$(function () {
    $('#notification-content').slimScroll({

        // width in pixels of the visible scroll area
        width: '100%',

        // height in pixels of the visible scroll area
        height: '370px',

        // width in pixels of the scrollbar and rail
        size: '7px',
        // scrollbar color, accepts any hex/color value
        color: '#000',

        // scrollbar position - left/right
        position: 'right',

        // distance in pixels between the side edge and the scrollbar
        distance: '1px',

        // default scroll position on load - top / bottom / $('selector')
        start: 'top',

        // sets scrollbar opacity
        oppacity: .4,

        // enables always-on mode for the scrollbar
        alwaysVisible: false,

        // check if we should hide the scrollbar when user is hovering over
        disableFadeOut: false,

        // sets visibility of the rail
        railVisible: false,

        // sets rail color
        railColor: '#333',

        // sets rail opacity
        railOpacity: .2,

        // whether  we should use <a href="https://www.jqueryscript.net/tags.php?/jQuery UI/">jQuery UI</a> Draggable to enable bar dragging
        railDraggable: true,

        // defautlt CSS class of the slimscroll rail
        railClass: 'slimScrollRail',

        // defautlt CSS class of the slimscroll bar
        barClass: 'slimScrollBar',

        // defautlt CSS class of the slimscroll wrapper
        wrapperClass: 'slimScrollDiv',

        // check if mousewheel should scroll the window if we reach top/bottom
        allowPageScroll: false,

        // scroll amount applied to each mouse wheel step
        wheelStep: 20,

        // scroll amount applied when user is using gestures
        touchScrollStep: 200,

        // sets border radius
        borderRadius: '7px',

        // sets border radius of the rail
        railBorderRadius: '7px'

    });
});


$(document).ready(function () {
    // Show dropdown and hide it when clicking outside of it
    $(document).mouseup(function (e) {
        event.preventDefault();

        var container = $(".nav-show-hide-content");
        $(".nav-show-hide-button").each((index, element) => {
            var iconButton = $(element)
            if (iconButton.is(e.target) || iconButton.has(e.target).length > 0) {
                // show or hide
                if (iconButton.parent().hasClass("is-active")) {
                    iconButton.parent().removeClass("is-active");
                } else {
                    iconButton.parent().addClass("is-active");
                    if ($(".notification-bell-nav").is(e.target) || $(".notification-bell-nav").has(e.target).length > 0) {
                        mark_all_as_seen();
                    }
                }
            } else if (!container.is(e.target) && container.has(e.target).length === 0) {
                // if the target of the click isn't the container nor a descendant of the container
                iconButton.parent().removeClass("is-active");
            }
        });
    });
});