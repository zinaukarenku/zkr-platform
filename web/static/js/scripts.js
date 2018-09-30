'use strict';

//mobile menu 
$(document).ready(function () {
    const d = document;
    const body = d.querySelector('body');
    const openMenuButton = d.querySelector('#open_menu');
    const closeMenuButton = d.querySelector('#close_menu');
    const mobileNav = d.body.querySelector('#mobile_nav');

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


    openMenuButton.addEventListener('click', toggleMobileMenu);
    closeMenuButton.addEventListener('click', toggleMobileMenu);

    $('.subscribe-form').each(function () {
        let subscribeForm = $(this);
        subscribeForm.submit(function () {
            $.ajax({
                type: subscribeForm.attr('method'),
                url: subscribeForm.attr('action'),
                data: subscribeForm.serialize(),
                success: function (response) {
                    toastr.success('E-mail subscription succeeded!');
                },
                error: function (request, textStatus, errorThrown) {
                    toastr.error(request.responseText, 'Error occurred');
                }
            });
            return false;
        });
    });

	const countDownClock = (hours, minutes, Seconds) => {
  
		const d = document;
		const hoursElement = d.querySelector('#hours');
		const minutesElement = d.querySelector('#minutes');
		const secondsElement = d.querySelector('#seconds');
		let countdown;
		let hoursInSeconds = hours * 60 * 60;
		let minutesInSeconds = minutes * 60;
		let seconds = hoursInSeconds + minutesInSeconds + Seconds;
		
		const timer = (seconds) => {
			
			const now = Date.now();
			const then = now + seconds * 1000;
			
			countdown = setInterval(() => {
			const secondsLeft = Math.round((then - Date.now())/ 1000);
			
			if(secondsLeft <= 0) {
				clearInterval(countdown);
				return;
			}
			
			displayTimeLeft(secondsLeft);
			
			}, 1000);
			
			const displayTimeLeft = (seconds) => {
			if (hoursElement || minutesElement || secondsElement) {
				hoursElement.textContent = Math.floor((seconds % 86400)/ 3600) < 10 ? `0${Math.floor((seconds % 86400)/ 3600)}` : Math.floor((seconds % 86400)/ 3600);
				minutesElement.textContent = Math.floor((seconds % 86400) % 3600/60) % 60 < 10 ? `0${Math.floor((seconds % 86400) % 3600/60)}` : Math.floor((seconds % 86400) % 3600/60);
				secondsElement.textContent = seconds % 60 < 10 ? `0${seconds % 60}` : seconds % 60;
			}
			
			};
			
		};  
		
		timer(seconds);
	
	}

	const setTimer = () => {
		let currentTime = new Date();
		let deadline = new Date(2018, 9, 16, 19, 0, 0);
		let timeLeft = deadline - currentTime;
		let hours = (timeLeft/(1000*60*60)) % 24;
		let minutes = (timeLeft/(1000*60)) % 60;
		let seconds = (timeLeft/1000) % 60;

		countDownClock(hours, minutes, seconds);
	}

	setTimer();

});