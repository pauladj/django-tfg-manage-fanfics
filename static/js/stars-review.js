$(document).ready(function () {
    var starsCont = 0;
    if (stars !== undefined && stars !== null && stars !== "0") {
        starsCont = Number(stars);
        $('#stars-value').val(starsCont);
        redrawStars();
    }
    $('.star-new').mouseover(function (e) {
        starsCont = $(this).attr('data-star');
        $('#stars-value').val(starsCont);
        redrawStars();
    }).click(function () {
        $('#stars-value').val(starsCont);
    });

    $('#stars-new-review').mouseout(function () {
        if ($('#stars-value').val() === "0") {
            starsCont = 1;
            redrawStars();
        }
    });

    function redrawStars() {
        var children = $('#stars-new-review').children('img');
        for (var i = 0; i < starsCont; i++) {
            var oneChild = children.eq(i);
            oneChild.attr("src", urlStar);
        }
        for (var i = starsCont; i < children.length; i++) {
            var oneChild = children.eq(i);
            oneChild.attr("src", urlStarLight);
        }

    }
});