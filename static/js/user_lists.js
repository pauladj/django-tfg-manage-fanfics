$(document).ready(function () {

    var changedField = $('#changed-field-input');
    $(".one-list-manage-input").click(function () {
        appendToVal($(this).attr('data-listid'));
    });

    function appendToVal(newValue) {
        var val = changedField.val();
        if (val.length > 0) {
            changedField.val(val + "," + newValue);
        } else {
            changedField.val(newValue);
        }
    }


    $('#add').click(function () {

        // add new field
        $(this).before(` <input name="new" class="input"
                               maxlength="12"
                               type="text"
                               placeholder="New list name...">`);
    });

});

