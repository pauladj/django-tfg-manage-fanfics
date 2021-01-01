document.addEventListener("DOMContentLoaded", function (event) {
    /*
    Menu expand/collapse
    */
    var menu = document.querySelector('#navbarBasicExample');
    var iconExpandMenu = document.querySelector('.navbar-burger');

    if (iconExpandMenu != null) {
        iconExpandMenu.addEventListener('click', function () {
            if (menu.classList) {
                menu.classList.toggle("is-active");
            } else {
                // For IE9
                var classes = menu.className.split(" ");
                var i = classes.indexOf("is-active");

                if (i >= 0)
                    classes.splice(i, 1);
                else
                    classes.push("is-active");
                menu.className = classes.join(" ");
            }
        });
    }

    /*
    Close error messages
    */
    var close_buttons = document.querySelectorAll('.delete');

    for (var i = 0; i < close_buttons.length; i++) {
        close_buttons[i].addEventListener('click', function () {
            var parent = this.parentElement;
            parent.style.display = "none";
        })
    }

    /*
    Open/close modal
     */
    $('.open-modal').click(function () {
        $('#modal').addClass('is-active');
        $('.modal-card-head').removeAttr("style");
    });

    $('.open-modal-two').click(function () {
        $('#modal-two').addClass('is-active');
        $('.modal-card-head').removeAttr("style");
    });


    $('.cancel-modal').click(function () {
        $('#modal').removeClass('is-active');
        $('#modal-two').removeClass('is-active');

    });

    $('button.delete').click(function () {
        $('#modal').removeClass('is-active');
        $('#modal-two').removeClass('is-active');

    });

    $('.modal-background').click(function () {
        $('#modal').removeClass('is-active');
        $('#modal-two').removeClass('is-active');

    });


});
