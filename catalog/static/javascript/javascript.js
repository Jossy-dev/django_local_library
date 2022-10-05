wow = new WOW(
    {
        boxClass: 'wow',      // default
        animateClass: 'animated', // default
        offset: 0,          // default
        mobile: true,       // default
        live: true        // default
    }
)
wow.init();

$(document).ready(function() {
    $('#id_genre').select2();
});

$(document).ready(function() {
    $('#id_author').select2();
});

$(document).ready(function() {
    $('#id_favourite_genre').select2();
});

$(document).ready(function() {
    $('#id_nationality').select2();
});
