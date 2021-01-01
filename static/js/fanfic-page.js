$(document).ready(function () {
    $('.checking-reading').mouseover(function (e) {
        var isChecked = $(this).hasClass("checked-reading");
        if (isChecked === false) {
            this.style.color = "#eae5ff";
        }
    }).mouseout(function (e) {
        var isChecked = $(this).hasClass("checked-reading");
        if (isChecked === false) {
            $(this).removeAttr("style");
        }
    }).click(function () {
        var fanficId = $(this).attr("data-fanficid");
        var chapterId = $(this).attr("data-chapterid");
        toggleMarkAsRead(this, fanficId, chapterId);
    });

    $('.edit-button').click(function () {
        this.style.display = "none"; // hide edit button
        // show editor, with text if there is already
        var existingNote = $(this).parent().find('.existing-note');
        existingNote.attr("style", "display:none");
        var text = existingNote.text();
        if (text.length !== 0) {
            changeCharacterCount(text, this);
        }

        var editorHTML = `<textarea class="textarea"  placeholder="e.g. Write here your private note">${text}</textarea>`;
        var editorElement = $(this).parent().find('.editor');
        editorElement.html(editorHTML);
        editorElement.on('input propertychange paste',function () {
            // if text changes
            text = $(this).find('.textarea').val();
            changeCharacterCount(text, this);
        });

        $(this).next('.note-editor').removeAttr("style");
    });

    $('.cancel-button').click(function () {
        $(this).parent().parent().parent().attr("style", "display:none");
        $(this).parent().parent().parent().parent().find('.edit-button').removeAttr("style");
        $(this).parent().parent().parent().parent().find('.existing-note').removeAttr("style");
    });

    $('.save-button').click(function () {
        var fanficId = $(this).attr("data-fanficid");
        var chapterId = $(this).attr("data-chapterid");
        savePrivateNote(this, fanficId, chapterId);
    });

});

function changeCharacterCount(text, currentElement) {
    var characterCount = 200 - text.length;
    var characterCountElement = $(currentElement).parent().find('.character-count');
    characterCountElement.text(characterCount);
    if (characterCount < 0) {
        characterCountElement.attr("style", "color:red");
    } else {
        characterCountElement.removeAttr("style");
    }
}

function savePrivateNote(obj, fanficId, chapterId) {
    var text = $(obj).parent().parent().parent().find("textarea").val();
    if (text.length > 200) {
        showToast("The text cannot be longer than 200 characters.", false);
        return;
    }

    $.ajax({
        type: "POST",
        data: {"text": text},
        url: `/fickeeper/fanfics/${fanficId}/chapters/${chapterId}/notes/`,
        beforeSend: function (xhr, settings) {
            xhr.setRequestHeader("X-CSRFToken", csrftoken);
        },
        success: function (response) {
            // 200
            var jsonObj = JSON.parse(response);
            if (jsonObj.success !== true) {
                showToast(jsonObj.message, false)
            } else {
                var parent = $(obj).parent().parent().parent().parent();
                var existingNote = parent.find(".existing-note");
                existingNote.text(text);

                var noteEditor = parent.find(".note-editor");
                noteEditor.attr("style", "display:none");

                existingNote.removeAttr("style");
                var editButton = parent.find(".edit-button");
                editButton.removeAttr("style");

            }
        },
        error: function (response) {
            showToast("There was an unexpected error trying to update the" +
                " private note.", false);
        }
    });
}

function toggleMarkAsRead(obj, fanficId, chapterId) {
    $.ajax({
        type: "POST",
        url: `/fickeeper/fanfics/${fanficId}/chapters/${chapterId}/`,
        beforeSend: function (xhr, settings) {
            xhr.setRequestHeader("X-CSRFToken", csrftoken);
        },
        success: function (response) {
            // 200
            var jsonObj = JSON.parse(response);
            if (jsonObj.success !== true) {
                showToast(jsonObj.message)
            } else {
                if (jsonObj.message != null && jsonObj.message != undefined){
                    showToast(jsonObj.message, true);
                }
                if (jsonObj.checked === true) {
                    // Change color of mark check
                    $(obj).removeClass("unchecked-reading");
                    $(obj).addClass("checked-reading");
                    $(obj).removeAttr("style");
                } else {
                    $(obj).removeClass("checked-reading");
                    $(obj).addClass("unchecked-reading");
                }

            }
        },
        error: function (response) {
            showToast("There was an unexpected error trying to update the" +
                " chapter status.", false);
        }
    });
}

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