$(document).ready(function () {
    const body = document.querySelector('body');
    const openMenuButton = document.querySelector('#open_menu');
    const closeMenuButton = document.querySelector('#close_menu');
    const mobileNav = document.body.querySelector('#mobile_nav');
    const filtersPoliticianButton = document.body.querySelector('#filtersPoliticianButton');
    const filtersPoliticiansCard = document.body.querySelector('#filtersPoliticiansCard');
    const closeFilters = document.body.querySelector('#close_filters');


    function toggleMobileMenu() {
        if (mobileNav.classList.contains('d-none')) {
            body.classList.add('overflow-hidden');
            mobileNav.classList.remove('d-none');
            mobileNav.classList.add('d-sm-block');
            openMenuButton.classList.add('d-none');
            closeMenuButton.classList.remove('d-none');
        } else {
            body.classList.remove('overflow-hidden');
            mobileNav.classList.remove('d-sm-block');
            mobileNav.classList.add('d-none');
            openMenuButton.classList.remove('d-none');
            closeMenuButton.classList.add('d-none');
        }
    }

    function togglePoliticianFilters() {
        if (filtersPoliticiansCard.classList.contains('d-none')) {
            body.classList.add('overflow-hidden');
            filtersPoliticiansCard.classList.remove('d-none');
            filtersPoliticiansCard.classList.add('d-sm-block');
        } else {
            body.classList.remove('overflow-hidden');
            filtersPoliticiansCard.classList.remove('d-sm-block');
            filtersPoliticiansCard.classList.add('d-none');
        }
    }

    if (openMenuButton !== null && closeMenuButton !== null) {
        openMenuButton.addEventListener('click', toggleMobileMenu);
        closeMenuButton.addEventListener('click', toggleMobileMenu);
    }

    if (filtersPoliticianButton !== null && closeFilters !== null && window.screen.width < 992) {
        filtersPoliticianButton.addEventListener('click', togglePoliticianFilters);
        closeFilters.addEventListener('click', togglePoliticianFilters);
    }





    $('.subscribe-form').each(function () {
        let subscribeForm = $(this);
        subscribeForm.submit(function () {
            $.ajax({
                type: subscribeForm.attr('method'),
                url: subscribeForm.attr('action'),
                data: subscribeForm.serialize(),
                success: function (response) {
                    toastr.success('Naujienlaiškis užprenumeruotas!');
                },
                error: function (request, textStatus, errorThrown) {
                    toastr.error(request.responseText, 'Klaida');
                }
            });
            return false;
        });
    });



});



//Google maps for debates
//const mapContainer = document.body.querySelector('#map');
//
//if (mapContainer !== null) {
//
//    function initMap() {
//        let lithuania = {lat: 55.1267529, lng: 23.9179474};
//        let map = new google.maps.Map(mapContainer, {zoom: 8.07, center: lithuania})
//    }
//
//    initMap();
//}
