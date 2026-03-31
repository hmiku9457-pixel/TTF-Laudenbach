const slides = document.querySelectorAll('.news-slide');
let index = 0;

function nextSlide() {
  slides[index].classList.remove('active');
  index = (index + 1) % slides.length;
  slides[index].classList.add('active');
}

setInterval(nextSlide, 6000);
