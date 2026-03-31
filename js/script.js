const newsItems = document.querySelectorAll('.news-item');
let current = 0;

function showNextNews() {
  newsItems[current].classList.remove('active');
  current = (current + 1) % newsItems.length;
  newsItems[current].classList.add('active');
}

setInterval(showNextNews, 5000); // alle 5 Sekunden wechseln
