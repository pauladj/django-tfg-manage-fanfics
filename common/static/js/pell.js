$(document).ready(function () {
    const pell = window.pell;
    const editor = document.getElementById("editor");
    const markup = document.getElementById("markup");
    const characteres = document.getElementById("characteres");

    pell.init({
        element: editor,
        defaultParagraphSeparator: 'p',
        onChange: (html) => {
            markup.value = html;
            decideIfRed(html);
        }
    });

    // initialize with html if there was any error
    if (text != null) {
        document.getElementsByClassName("pell-content")[0].innerHTML = text;
        decideIfRed(text);
    }

    function decideIfRed(html) {
        var leftCharacters = (7000 - html.length);
        characteres.innerText = leftCharacters;
        if (leftCharacters >= 0) {
            characteres.removeAttribute("style");
        } else {
            characteres.style.color = 'red';
        }
    }
});