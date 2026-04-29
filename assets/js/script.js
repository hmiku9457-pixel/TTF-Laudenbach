// ==========================================
// ===== 1. WARTEN BIS DOM GELADEN IST =====
// ==========================================

// Stellt sicher, dass das HTML komplett geladen ist,
// bevor wir Elemente auswählen oder verändern
document.addEventListener("DOMContentLoaded", () => {

	// ==========================================
	// ===== 1A. HEADER & NAVIGATION LADEN =====
	// ==========================================

	const headerContainer = document.getElementById('header-container');

	if(headerContainer) {
		fetch('/TTF-Laudenbach/components/header.html')
			.then(res => res.text())
			.then(html => {
				headerContainer.innerHTML = html;
				initThemeSwitcher();
			});
	}

	// ==========================================
	// ===== 1B. FOOTER LADEN ===================
	// ==========================================
	
	const footerContainer = document.getElementById('footer-container');
	
	if(footerContainer) {
	    fetch('/TTF-Laudenbach/components/footer.html')
	        .then(res => res.text())
	        .then(html => {
	            footerContainer.innerHTML = html;
	        });
	}

	// ==========================================
	// ===== 2. NEWS SLIDER LADEN (FETCH) =======
	// ==========================================

	const container = document.querySelector('.news-slider');

	if(container) {

		fetch('/TTF-Laudenbach/assets/data/news.json')
			.then(res => res.json())
			.then(data => {

				data.forEach((item, i) => {

					const div = document.createElement('div');
					div.classList.add('news-slide');

					if(i === 0) div.classList.add('active');

					div.innerHTML = `
						<img src="${item.image}" alt="${item.title}">
						<h3>${item.title}</h3>
						<p>${item.text}</p>
						<a href="${item.link}" class="read-more">Mehr lesen</a>
					`;

					container.appendChild(div);
				});

				startSlider();
				initAnimations();
			});
	}

	// ==========================================
	// ===== 3. SLIDER LOGIK ====================
	// ==========================================

	function startSlider() {

		const slides = document.querySelectorAll('.news-slide');
		let index = 0;

		setInterval(() => {

			slides[index].classList.remove('active');
			index = (index + 1) % slides.length;
			slides[index].classList.add('active');

		}, 10000);
	}

	// ==========================================
	// ===== 4. BOX ANIMATION ===================
	// ==========================================

	function initAnimations() {

		const elements = document.querySelectorAll('.box, .team-box, .news-slider, .button');

		elements.forEach((el, index) => {
			el.style.animationDelay = (index * 0.2) + "s";
			el.classList.add("animate");
		});

		// Tabelle: jede Zeile separat
		const rows = document.querySelectorAll('.table-ewigeRangliste tbody tr');
		rows.forEach((row, index) => {
			row.style.animationDelay = (index * 0.08) + "s";
			row.classList.add("animate");
		});
	}

	// ==========================================
	// ===== 4A. OBSERVER FÜR DYNAMISCHE BOXEN =
	// ==========================================

	const observer = new MutationObserver(() => {
		initAnimations();
	});

	observer.observe(document.body, { childList: true, subtree: true });
	initAnimations();
	
	// ==========================================
	// ===== 5. THEME SWITCHER ==================
	// ==========================================

	function initThemeSwitcher() {

		const switcher = document.getElementById("themeSwitcher");

		if(switcher) {
			switcher.addEventListener("change", (e) => {
				document.body.classList.remove("theme-red", "theme-dark");
				document.body.classList.add("theme-" + e.target.value);
			});
		}
	}

	// ==========================================
	// ===== 6. SPIELE LADEN (JSON) =============
	// ==========================================

	loadSpiele();

	async function loadSpiele() {

		const tbody = document.getElementById("spiele-body");

		// Falls Tabelle nicht existiert → abbrechen
		if(!tbody) return;

		try {
			const response = await fetch("/TTF-Laudenbach/assets/data/spiele.json");
			const spiele = await response.json();

			tbody.innerHTML = "";

			spiele.forEach(spiel => {

				const tr = document.createElement("tr");

				// Prüfen ob Heimspiel
				const istHeimspiel = spiel.heim.includes("Laudenbach");

				tr.innerHTML = `
					<td>${spiel.datum}</td>
					<td>${formatUhrzeit(spiel.uhrzeit)}</td>
					<td>${getMannschaft(spiel.heim, spiel.gast)}</td>
					<td>${spiel.gast}</td>
					<td>${getSpielort(spiel.spielort, istHeimspiel)}</td>
				`;

				tbody.appendChild(tr);
			});

		} catch (error) {
			console.error("Fehler beim Laden der Spiele:", error);
		}
	}

	// ==========================================
	// ===== 7. HILFSFUNKTIONEN SPIELE ==========
	// ==========================================

	// Mannschaft bestimmen (Laudenbach hervorheben)
	function getMannschaft(heim, gast) {
		if (heim.includes("Laudenbach")) return heim;
		if (gast.includes("Laudenbach")) return gast;
		return "-";
	}

	// Spielort umwandeln (nur bei Heimspielen)
	function getSpielort(code, istHeimspiel) {

		if(!istHeimspiel) {
			return code; // Auswärtsspiel → nur Zahl anzeigen
		}

		switch (code) {
			case "1":
				return "Großsporthalle Weikersheim";
			case "2":
				return "Zehntscheune Laudenbach";
			case "3":
				return "Ausweichhalle";
			default:
				return "-";
		}
	}

	// Uhrzeit formatieren (\n entfernen)
	function formatUhrzeit(uhrzeit) {
		return uhrzeit.replace("\n", " ");
	}

});
