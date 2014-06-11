


/*=========================*/
/*====main navigation hover dropdown====*/
/*==========================*/
$(document).ready(function() {

    $('.js-activated').dropdownHover({
        instantlyCloseOthers: false,
        delay: 0
    }).dropdown();

});

/*====flex  slider for main slider or testimonials====*/
$('.main-flex-slider,.testimonials').flexslider({
    slideshowSpeed: 5000,
    directionNav: false,
    animation: "fade"
});

/*========portfolio mix====*/
$('#grid').mixitup();

/*========tooltip and popovers====*/

$("[data-toggle=popover]").popover();

$("[data-toggle=tooltip]").tooltip();


/*========flex-gallery slide====*/
$(window).load(function() {
    $('.flexslider').flexslider({
        directionNav: false,
        slideshowSpeed: 3000,
        animation: "fade"
    });
});


/*========sticky nav====*/
$(function() {

    var stickyHeader = $('.sticky-nav');
    var stickyHeaderTop = 0;
    if (stickyHeader.length)
    {
        stickyHeaderTop = stickyHeader.offset().top;
    }

    $(window).scroll(function() {
        if ($(window).scrollTop() > stickyHeaderTop) {
            $('.sticky-nav').css({position: 'fixed', top: '0px'});
            $('.sticky-nav').css('display', 'block');
        } else {
            $('.sticky-nav').css({position: 'static', top: '0px'});

        }
    });
});
