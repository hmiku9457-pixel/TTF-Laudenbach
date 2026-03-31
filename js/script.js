const container = document.querySelector('.news-slider');

fetch('data/news.json')
  .then(res => res.json())
  .then(data => {
    data.forEach((item, i) => {
      const div = document.createElement('div');
      div.classList.add('news-slide');
      if (i === 0) div.classList.add('active');

      // Wichtig: href direkt hier im Template Literal
      div.innerHTML = `
        <img src="${item.image}" alt="${item.title}">
        <h3>${item.title}</h3>
        <p>${item.text}</p>
        <a href="${item.link}" class="read-more">Mehr lesen</a>
      `;
      container.appendChild(div);
    });

    startSlider(data.length); // Länge übergeben
  });

function startSlider(length) {
  const slides = document.querySelectorAll('.news-slide');
  let index = 0;

  setInterval(() => {
    slides[index].classList.remove('active');
    index = (index + 1) % length;
    slides[index].classList.add('active');
  }, 6000);
}
