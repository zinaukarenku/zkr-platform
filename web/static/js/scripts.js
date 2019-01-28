$(document).ready(function () {
    const d = document;
    const body = d.querySelector('body');
    const openMenuButton = d.querySelector('#open_menu');
    const closeMenuButton = d.querySelector('#close_menu');
    const mobileNav = d.body.querySelector('#mobile_nav');
    const filtersPoliticianButton = d.body.querySelector('#filtersPoliticianButton');
    const submitPoliticianFilterButton = d.body.querySelector('#submit-id-filter');
    const filtersPoliticiansCard = d.body.querySelector('#filtersPoliticiansCard');
    const closeFilters = d.body.querySelector('#close_filters');

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


    openMenuButton.addEventListener('click', toggleMobileMenu);
    closeMenuButton.addEventListener('click', toggleMobileMenu);

    if (window.screen.width < 992) {
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