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

				// Theme-Switcher erst initialisieren,
				// wenn der Header wirklich im DOM ist
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

					// Erstes Element direkt sichtbar machen
					if(i === 0) div.classList.add('active');

					div.innerHTML = `
						<img src="${item.image}" alt="${item.title}">
						<h3>${item.title}</h3>
						<p>${item.text}</p>
						<a href="${item.link}" class="read-more">Mehr lesen</a>
					`;

					container.appendChild(div);
				});

				// Slider + Animation erst starten,
				// nachdem Inhalte existieren
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

		// Tabellenzeilen einzeln animieren
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
	// ===== 6. GENERISCHER JSON LOADER =========
	// ==========================================

	// Universelle Funktion zum Laden von JSON-Daten
	// und Einfügen in eine Tabelle
	async function loadTable(config) {

		const tbody = document.getElementById(config.targetId);

		// Falls Element nicht existiert → nichts tun
		if(!tbody) return;

		try {
			const response = await fetch(config.url);
			const data = await response.json();

			tbody.innerHTML = "";

			data.forEach(item => {

				const tr = document.createElement("tr");

				// Jede Tabelle definiert selbst,
				// wie eine Zeile aussehen soll
				tr.innerHTML = config.render(item);

				tbody.appendChild(tr);
			});

		} catch (error) {
			console.error(`Fehler bei ${config.url}:`, error);
		}
	}

	// ==========================================
	// ===== 7. SPIELE LADEN ====================
	// ==========================================

	loadTable({
		targetId: "spiele-body",
		url: "/TTF-Laudenbach/assets/data/spiele.json",

		render: (spiel) => {

			const istHeimspiel = spiel.heim.includes("Laudenbach");

			return `
				<td>${spiel.datum}</td>
				<td>${formatUhrzeit(spiel.uhrzeit)}</td>
				<td>${getMannschaft(spiel.heim, spiel.gast, spiel.klasse)}</td>
				<td>${getGegner(spiel.heim, spiel.gast)}</td>
				<td>${getSpielort(spiel.spielort, istHeimspiel)}</td>
				<td>${getErgebnis(spiel)}</td>
			`;
		}
	});

	// ==========================================
	// ===== 8. STANDARD TABELLEN RENDER ========
	// ==========================================

	// Einheitliche Darstellung für alle Tabellen
	function renderStandardTabelle(row) {
		return `
			<td>${row.rang}</td>
			<td>${row.mannschaft}</td>
			<td>${row.partien}</td>
			<td>${row.siege}</td>
			<td>${row.unentschieden}</td>
			<td>${row.niederlagen}</td>
			<td>${row.spiele}</td>
			<td>${row.spieleDifferenz}</td>
			<td>${row.punkte}</td>
		`;
	}

	// ==========================================
	// ===== 9. TABELLEN LADEN ==================
	// ==========================================

	const tabellenConfigs = [

		{
			targetId: "tabelle-herren1",
			url: "/TTF-Laudenbach/assets/data/tabelleHerren1.json",
			render: renderStandardTabelle
		},

		{
			targetId: "tabelle-herren2",
			url: "/TTF-Laudenbach/assets/data/tabelleHerren2.json",
			render: renderStandardTabelle
		}

	];

	// Alle Tabellen automatisch laden
	tabellenConfigs.forEach(cfg => loadTable(cfg));

	// ==========================================
	// ===== 10. HILFSFUNKTIONEN SPIELE =========
	// ==========================================

	function getMannschaft(heim, gast, klasse) {

		let team = "";

		if (heim.includes("Laudenbach")) {
			team = heim;
		} else if (gast.includes("Laudenbach")) {
			team = gast;
		} else {
			return "-";
		}

		const match = team.match(/(I|II|III|IV|V)$/);
		const nummer = match ? match[0] : "I";

		if (klasse.startsWith("J")) return "Jugend " + nummer;
		if (klasse.startsWith("E")) return "Herren " + nummer;

		return nummer;
	}

	function getGegner(heim, gast) {
		if (heim.includes("Laudenbach")) return gast;
		if (gast.includes("Laudenbach")) return heim;
		return "-";
	}

	function getSpielort(code, istHeimspiel) {

		if (!istHeimspiel) return "";

		switch (code) {
			case "1": return "Großsporthalle Weikersheim";
			case "2": return "Zehntscheune Laudenbach";
			case "3": return "Ausweichhalle";
			default: return "-";
		}
	}

	function formatUhrzeit(uhrzeit) {
		return uhrzeit.replace("\n", " ");
	}

	function getErgebnis(spiel) {
		if (spiel.status === "geplant") return "-:-";
		return spiel.ergebnis || "-:-";
	}

});
