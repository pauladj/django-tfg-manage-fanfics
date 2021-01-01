$(document).ready(function () {
    $('.search-in-fandom-sidebar').on('input', function () {
        var scope = this;
        var elementsContainer = $('.one-fandom-row');

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


    $('#choose-list').change(function () {
        var selectedElement = $(this).children("option:selected");
        var listId = selectedElement.val();
        var fandomId = selectedElement.attr("data-fandomid");
        var url = `/fickeeper/users/${user_id}/fanfics?fandom_id=${fandomId}&list=${listId}`;
        window.location.href = url;
    });
});
