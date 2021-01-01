$(document).ready(function () {

    // Use library selectize for selects
    $('.custom-select-with-blank').selectize({
        create: false,
        sortField: 'text',
        allowEmptyOption: true
    });

    $('.custom-select').selectize({
        create: false,
        sortField: 'text',
    });

    // change style of rows, so the dropdown list can be seen
    var fandomFormRow = $('.form-row.field-primary_fandom');
    if (fandomFormRow !== undefined) {
        fandomFormRow.attr("style", "overflow:visible");
    }

    fandomFormRow = $('.form-row.field-secondary_fandom');
    if (fandomFormRow !== undefined) {
        fandomFormRow.attr("style", "overflow:visible");
    }

    /*
     * CharacterFanfic admin page
     */
    // if the fanfic value changes, get the possible characters to assign
    $('.fanfic-select').change(function () {
        var newId = $(this).val();
        var url = `/fickeeper/fanfics/${newId}/characters/`;

        $.ajax({
            type: "GET",
            url: url,
            beforeSend: function (xhr, settings) {
                var csrftoken = getCookie('csrftoken');
                xhr.setRequestHeader("X-CSRFToken", csrftoken);
            },
            success: function (response) {
                // 200
                var values = JSON.parse(response).values;
                var selectize = $(".character-select")[0].selectize;
                selectize.clear();
                selectize.clearOptions();
                selectize.refreshItems();
                selectize.load(function (callback) {
                    callback(values);
                });
                selectize.refreshItems();
                console.log(3);

            },
            error: function (response) {
                console.log(response);
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

                toastr.error('There was an error, try again in a few seconds.');
            }
        });
    });
});

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