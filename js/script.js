const container = document.querySelector('.news-slider');

fetch('data/news.json')
  .then(res => res.json())
  .then(data => {
    data.forEach((item, i) => {
      const div = document.createElement('div');
      div.classList.add('news-slide');

      if (i === 0) div.classList.add('active');

      div.innerHTML = `
        <img src="${item.image}">
        <h3>${item.title}</h3>
        <p>${item.text}</p>
        <a href="${item.link}">Mehr lesen</a>
      `;

      container.appendChild(div);
    });

    startSlider();
  });

function startSlider() {
  const slides = document.querySelectorAll('.news-slide');
  let index = 0;

  setInterval(() => {
    slides[index].classList.remove('active');
    index = (index + 1) % slides.length;
    slides[index].classList.add('active');
  }, 6000);
}
