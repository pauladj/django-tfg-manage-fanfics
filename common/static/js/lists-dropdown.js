$(document).ready(function () {
    $('.add-fanfic-button-dropdown').click(function () {
        var container = $(this).next(".libraries-container-dropdown")[0];
        if (container.hasAttribute("style")) {
            $(container).removeAttr("style");
        } else {
            $(container).attr("style", "display:none");
        }
    });

    $('.libraries-container-dropdown').mouseleave(function () {
        $(this).attr("style", "display:none");
    });

    $('.libraries-search').on('input', function () {
        var scope = this;
        var elementsContainer = $(this).parentsUntil('.libraries-container-dropdown').parent()[0];
        elementsContainer = $(elementsContainer).children('.libraries-list-checkbox').children('div');

        if (!scope.value || scope.value === "") {
            elementsContainer.show();
            return;
        }

        elementsContainer.each(function (i, div) {
            var $div = $(div);
            var $text = $div.text().toLowerCase();
            $div.toggle($text.indexOf(scope.value.toLowerCase()) > -1);
        })
    });

    $('.list-fanfic-checkbox').click(function (e) {
        e.preventDefault();
        var inputCheckbox = this;
        var fanficId = $(inputCheckbox).attr("data-fanficid");
        var listId = $(inputCheckbox).attr("data-listid");
        var url = `/fickeeper/lists/${listId}/`;
        var checked = $(inputCheckbox)[0].hasAttribute("checked");

        // send ajax with the new data
        $.ajax({
            type: "POST",
            url: url,
            data: {'fanficId': fanficId, 'join': !checked},
            beforeSend: function (xhr, settings) {
                var csrftoken = getCookie('csrftoken');
                xhr.setRequestHeader("X-CSRFToken", csrftoken);
            },
            success: function (response) {
                // 200
                var responseJSON = JSON.parse(response);
                var message = responseJSON['message'];

                if (responseJSON['success'] === true) {
                    var list_name = responseJSON['list_name'];
                    var list_id_checked = responseJSON['list_id_checked'];

                    var buttonToChange = $('#button' + fanficId);

                    if (list_name == null && list_id_checked == null && !checked === false) {
                        // nothing checked
                        $(inputCheckbox).prop('checked', false);
                        $(inputCheckbox).removeAttr('checked');
                        // change button styles if it was green
                        if ($(buttonToChange).hasClass('action-outline-green')) {
                            $(buttonToChange).removeClass('action-outline-green');
                            $(buttonToChange).addClass('action-colored-inverse-gray');
                            $(buttonToChange).find('p').text("Add it");
                        }
                    } else {
                        // remove previously checked one
                        var otherInputsCheckbox = $(inputCheckbox).parentsUntil('.libraries-list-checkbox').parent()[0];
                        otherInputsCheckbox = $(otherInputsCheckbox).find('input');
                        otherInputsCheckbox.each(function () {
                            var dataListId = $(this).attr("data-listid");
                            if (dataListId == list_id_checked) {
                                // mark new one
                                $(this).prop('checked', true);
                                $(this).attr('checked', true);
                            } else {
                                $(this).prop('checked', false);
                                $(this).removeAttr('checked');
                            }
                        });

                        // change button styles if it was grey
                        if ($(buttonToChange).hasClass('action-colored-inverse-gray')) {
                            $(buttonToChange).removeClass('action-colored-inverse-gray');
                            $(buttonToChange).addClass('action-outline-green');
                            $(buttonToChange).find('p').text(list_name);
                        } else {
                            // just change the list
                            $(buttonToChange).find('p').text(list_name);
                        }
                    }
                    toast(true, message)

                } else {
                    // error
                    toast(false, message)
                }
            },
            error: function (response) {
                toast(false, 'There was an error, try again in a few' +
                    ' seconds.');
            }
        });

    });
});

function toast(success, message) {
    // show toast with error
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
    };

    if (success == true) {
        toastr.success(message);
    } else {
        toastr.error(message);
    }
}

function getCookie(name) {
    var cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        var cookies = document.cookie.split(';');
        for (var i = 0; i < cookies.length; i++) {
            var cookie = cookies[i].trim();
            // Does this cookie string begin with the name we want?
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}