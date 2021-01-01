$(document).ready(function () {
    $readMoreJS.init({
        target: '.reading',        // Selector of the element the plugin
        // applies to (any CSS selector, eg: '#', '.'). Default: ''
        numOfWords: 100,            // Number of words to initially display
        // (any number). Default: 50
        toggle: true,              // If true, user can toggle between 'read more' and 'read less'. Default: true
        moreLink: 'Read more ...', // The text of 'Read more' link.
        // Default: 'read more ...'
        lessLink: 'Read less',      // The text of 'Read less' link.
        // Default: 'read less'
        linkClass: 'rm-link',       // The class given to the read more link. Defaul: 'rm-link'
        containerClass: 'rm-container' // The class given to the div container of the read more link. Default: false
    });
});
