$(document).ready(function () {
    $(".mark-as-read").click(function () {
        var fanficId = $(this).attr("data-fanficid");
        var parent = $(this).parent();
        var thisButton = $(this);
        var totalCount = $(parent).find('.total-count');
        var chaptersCount = $(parent).find('.how-many');

        $.ajax({
            type: "POST",
            url: `/fickeeper/fanfics/${fanficId}/chapters/read/`,
            beforeSend: function (xhr, settings) {
                xhr.setRequestHeader("X-CSRFToken", csrftoken);
            },
            success: function (response) {
                // 200
                var jsonObj = JSON.parse(response);
                if (jsonObj.success !== true) {
                    showToast(jsonObj.message)
                } else {
                    if (jsonObj.message != null && jsonObj.message != undefined) {
                        showToast(jsonObj.message, true);
                    }
                    if (jsonObj.moreChapters == false) {
                        // there are no more chapters
                        $(thisButton).attr("style", "display:none");
                    } else {
                        // update total count of chapters
                        totalCount.text(jsonObj.totalCount);
                    }
                    // update read chapters text
                    chaptersCount.text(jsonObj.chaptersReadCount);
                }
            },
            error: function (response) {
                showToast("There was an unexpected error trying to update the" +
                    " chapter status.", false);
            }
        });
    });
});


function showToast(msg = null, success = false) {
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

    if (success === true) {
        toastr.success(msg);
    } else {
        toastr.error(msg);
    }
}