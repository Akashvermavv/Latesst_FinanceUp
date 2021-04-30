$(document).ready(function() {
    /* Navbar Shrink */
    $(window).on('scroll', function() {
        if ($(this).scrollTop() > 90) {
            $('header').addClass('header-shrink');
        } else {
            $('header').removeClass('header-shrink');
        }
    });
    if ($(window).scrollTop() > 90) {
        $('header').addClass('header-shrink');
    } else {
        $('header').removeClass('header-shrink');
    }


    /* Home Owl Carousel */
    $('.home-carousel').owlCarousel({
        loop: true,
        margin: 10,
        autoplay: true,
        responsiveClass: true,
        responsive: {
            0: {
                items: 1,
            },
            600: {
                items: 1,
            },
            1000: {
                items: 1,
            }
        }
    });


    /* Client Logo Owl Carousel */
    $('.logo-carousel').owlCarousel({
        loop: true,
        margin: 10,
        autoplay: true,
        responsiveClass: true,
        responsive: {
            0: {
                items: 1,
            },
            300: {
                items: 1,
            },
            600: {
                items: 4,
            },
            1000: {
                items: 6,
            }
        }
    });

    /* Stand for Owl Carousel */
    $('.stand-carousel').owlCarousel({
        loop: true,
        margin: 10,
        autoplay: true,
        responsiveClass: true,
        responsive: {
            0: {
                items: 1,
            },
            600: {
                items: 2,
            },
            1000: {
                items: 2,
            }
        }
    });

    /* Team Owl Carousel */
    $('.team-carousel').owlCarousel({
        loop: true,
        margin: 10,
        autoplay: true,
        responsiveClass: true,
        responsive: {
            0: {
                items: 1,
            },
            600: {
                items: 2,
            },
            1000: {
                items: 3,
            }
        }
    });

    /* Team Owl Carousel */
    $('.sponsor-carousel').owlCarousel({
        loop: true,
        margin: 10,
        autoplay: true,
        responsiveClass: true,
        responsive: {
            0: {
                items: 2,
            },
            600: {
                items: 3,
            },
            1000: {
                items: 6,
            }
        }
    });

    /* Navbar Collapse */
    $('.nav-link').on('click', function() {
        $('.navbar-collapse').collapse('hide');
    });
});


/* Preloader */
window.addEventListener('load', function() {
    document.querySelector('.preloader').style.display = 'none';
});