// ==========================================
// ===== 1. WARTEN BIS DOM GELADEN IST =====
// ==========================================

// Stellt sicher, dass das HTML komplett geladen ist,
// bevor wir Elemente auswählen oder verändern
document.addEventListener("DOMContentLoaded", () => {

  // ==========================================
  // ===== 2. NEWS SLIDER LADEN (FETCH) =======
  // ==========================================

  // Container aus dem HTML holen
  const container = document.querySelector('.news-slider');

  // Daten aus JSON laden (async!)
  fetch('data/news.json')
    .then(res => res.json()) // Antwort → JSON umwandeln
    .then(data => {

      // Für jeden News-Eintrag ein Element erzeugen
      data.forEach((item, i) => {

        const div = document.createElement('div');
        div.classList.add('news-slide');

        // Erstes Element sichtbar machen
        if (i === 0) div.classList.add('active');

        // HTML-Inhalt einsetzen
        div.innerHTML = `
          <img src="${item.image}" alt="${item.title}">
          <h3>${item.title}</h3>
          <p>${item.text}</p>
          <a href="${item.link}" class="read-more">Mehr lesen</a>
        `;

        // In den Slider einfügen
        container.appendChild(div);
      });

      // Slider starten (nachdem Elemente existieren!)
      startSlider();

      // Animation starten (auch erst danach!)
      initAnimations();
    });


  // ==========================================
  // ===== 3. SLIDER LOGIK ====================
  // ==========================================

  function startSlider() {

    // Alle Slides holen
    const slides = document.querySelectorAll('.news-slide');

    let index = 0;

    // Alle 18 Sekunden wechseln
    setInterval(() => {

      // aktuelles Slide ausblenden
      slides[index].classList.remove('active');

      // Index erhöhen (mit Loop zurück zu 0)
      index = (index + 1) % slides.length;

      // neues Slide anzeigen
      slides[index].classList.add('active');

    }, 18000);
  }


  // ==========================================
  // ===== 4. BOX ANIMATION ===================
  // ==========================================

  function initAnimations() {

    // Alle Elemente auswählen, die animiert werden sollen
    const elements = document.querySelectorAll('.box, .team-box, .news-slider');

    elements.forEach((el, index) => {

      // Verzögerung setzen (für "nacheinander reinfliegen")
      el.style.animationDelay = (index * 0.1) + "s";

      // Animation aktivieren (CSS übernimmt den Rest)
      el.classList.add("animate");
    });
  }


  // ==========================================
  // ===== 5. THEME SWITCHER ==================
  // ==========================================

  const switcher = document.getElementById("themeSwitcher");

  // Falls das Element existiert (Sicherheit!)
  if (switcher) {

    switcher.addEventListener("change", (e) => {

      // Alte Themes entfernen
      document.body.classList.remove("theme-red", "theme-dark");

      // Neues Theme hinzufügen
      document.body.classList.add("theme-" + e.target.value);
    });
  }

});
