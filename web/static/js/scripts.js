'use strict';

//mobile menu 

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