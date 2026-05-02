// ==========================================
// ===== DOM READY ==========================
// ==========================================

// Wartet bis das komplette HTML geladen ist,
// damit alle DOM-Elemente sicher verfügbar sind
document.addEventListener("DOMContentLoaded", () => {

	// ==========================================
	// ===== HEADER LADEN =======================
	// ==========================================

	const headerContainer = document.getElementById('header-container');

	if(headerContainer) {
		fetch('/TTF-Laudenbach/components/header.html')
			.then(res => res.text())
			.then(html => {
				headerContainer.innerHTML = html;

				// Theme Switcher erst nach Header-Insert aktivieren
				initThemeSwitcher();
			});
	}

	// ==========================================
	// ===== FOOTER LADEN =======================
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
	// ===== NEWS SLIDER ========================
	// ==========================================

	const newsContainer = document.querySelector('.news-slider');

	if(newsContainer) {

		// News-Daten laden und als Slides rendern
		fetch('/TTF-Laudenbach/assets/data/news.json')
			.then(res => res.json())
			.then(data => {

				data.forEach((item, i) => {

					const div = document.createElement('div');
					div.classList.add('news-slide');

					// erstes Slide aktiv setzen
					if(i === 0) div.classList.add('active');

					// Slide-Inhalt
					div.innerHTML = `
						<img src="${item.image}" alt="${item.title}">
						<h3>${item.title}</h3>
						<p>${item.text}</p>
						<a href="${item.link}" class="read-more">Mehr lesen</a>
					`;

					newsContainer.appendChild(div);
				});

				// Slider & Animation starten
				startSlider();
				initAnimations();
			});
	}

	// ==========================================
	// ===== SLIDER LOGIK =======================
	// ==========================================

	function startSlider() {

		const slides = document.querySelectorAll('.news-slide');
		let index = 0;

		// automatischer Wechsel alle 10 Sekunden
		setInterval(() => {

			slides[index].classList.remove('active');
			index = (index + 1) % slides.length;
			slides[index].classList.add('active');

		}, 10000);
	}

	// ==========================================
	// ===== ANIMATIONEN ========================
	// ==========================================

	function initAnimations() {

		// Boxen, Buttons und Slider animieren
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

	// Observer für dynamisch nachgeladene Inhalte
	const observer = new MutationObserver(() => {
		initAnimations();
	});

	observer.observe(document.body, { childList: true, subtree: true });

	// Initiale Animation beim Laden
	initAnimations();

	// ==========================================
	// ===== THEME SWITCHER =====================
	// ==========================================

	function initThemeSwitcher() {

		const switcher = document.getElementById("themeSwitcher");

		// Theme-Wechsel über Dropdown
		if(switcher) {
			switcher.addEventListener("change", (e) => {
				document.body.classList.remove("theme-red", "theme-dark");
				document.body.classList.add("theme-" + e.target.value);
			});
		}
	}

	// ==========================================
	// ===== iFRAME CONSENT (DSGVO) =============
	// ==========================================
	
	function createIframe(container, src) {
	
		const iframe = document.createElement("iframe");
	
		iframe.src = src;
		iframe.style.width = "100%";
		iframe.style.height = "250px"; // WICHTIG
		iframe.style.border = "0";
		iframe.loading = "lazy";
		iframe.referrerPolicy = "no-referrer-when-downgrade";
		iframe.allowFullscreen = true;
	
		container.innerHTML = "";
		container.appendChild(iframe);
	}
	
	// GLOBAL machen (wichtig!)
	window.loadIframe = function(button) {
	
		const container = button.parentElement;
		const src = container.getAttribute("data-src");
	
		localStorage.setItem("externalContentAccepted", "true");
	
		createIframe(container, src);
	}
	
	// Auto-Load bei gespeicherter Zustimmung
	if (localStorage.getItem("externalContentAccepted") === "true") {
		document.querySelectorAll(".iframe-consent").forEach(container => {
			createIframe(container, container.dataset.src);
		});
	}
	
	// ==========================================
	// ===== GENERISCHER TABLE LOADER ===========
	// ==========================================

	// Lädt JSON und rendert es in Tabellen
	async function loadTable(config) {

		const tbody = document.getElementById(config.targetId);

		// nur ausführen wenn Tabelle existiert
		if(!tbody) return;

		try {
			const response = await fetch(config.url);
			const data = await response.json();

			// Tabelle leeren
			tbody.innerHTML = "";

			// jede Zeile rendern
			data.forEach(item => {
				const tr = document.createElement("tr");
				tr.innerHTML = config.render(item);
				tbody.appendChild(tr);
			});

		} catch (error) {
			console.error(`Fehler bei ${config.url}:`, error);
		}
	}

	// ==========================================
	// ===== SPIELE KONFIG ======================
	// ==========================================

	const spieleConfigs = [

		// Startseite Spiele
		{
			targetId: "spiele-startseite",
			url: "/TTF-Laudenbach/assets/data/spieleStartseite.json",
			render: (spiel) => {

				const istHeimspiel = spiel.heim.includes("Laudenbach");
				const gegner = istHeimspiel ? spiel.gast : spiel.heim;

				return `
					<td>${spiel.datum}</td>
					<td>${formatUhrzeit(spiel.uhrzeit)}</td>
					<td>${getMannschaft(spiel.heim, spiel.gast, spiel.klasse)}</td>
					<td>${gegner}</td>
					<td>${getSpielort(spiel.spielort, istHeimspiel)}</td>
					<td>${getErgebnis(spiel)}</td>
				`;
			}
		},

		// Mannschafts-Spiele
		{
			targetId: "spiele-herren1",
			url: "/TTF-Laudenbach/assets/data/spieleHerren1.json",
			render: renderStandardSpiele
		},
		{
			targetId: "spiele-herren2",
			url: "/TTF-Laudenbach/assets/data/spieleHerren2.json",
			render: renderStandardSpiele
		},
		{
			targetId: "spiele-herren3",
			url: "/TTF-Laudenbach/assets/data/spieleHerren3.json",
			render: renderStandardSpiele
		},
		{
			targetId: "spiele-jugend1",
			url: "/TTF-Laudenbach/assets/data/spieleJugend1.json",
			render: renderStandardSpiele
		},
		{
			targetId: "spiele-jugend2",
			url: "/TTF-Laudenbach/assets/data/spieleJugend2.json",
			render: renderStandardSpiele
		}
	];

	// Standard Rendering für Spiele
	function renderStandardSpiele(row) {

		const istHeimspiel = row.heim.includes("Laudenbach");
		const gegner = istHeimspiel ? row.gast : row.heim;

		return `
			<td>${row.datum}</td>
			<td>${formatUhrzeit(row.uhrzeit)}</td>
			<td>${getSpielort(row.spielort, istHeimspiel)}</td>
			<td>${gegner}</td>
			<td>${formatErgebnis(row.heim, row.gast, row.ergebnis)}</td>
		`;
	}

	// Spiele laden
	spieleConfigs.forEach(cfg => loadTable(cfg));

	// ==========================================
	// ===== TABELLEN KONFIG ====================
	// ==========================================

	// Standard Tabellen Renderer
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
		},
		{
			targetId: "tabelle-herren3",
			url: "/TTF-Laudenbach/assets/data/tabelleHerren3.json",
			render: renderStandardTabelle
		},
		{
			targetId: "tabelle-jugend1",
			url: "/TTF-Laudenbach/assets/data/tabelleJugend1.json",
			render: renderStandardTabelle
		},
		{
			targetId: "tabelle-jugend2",
			url: "/TTF-Laudenbach/assets/data/tabelleJugend2.json",
			render: renderStandardTabelle
		}
	];

	// Tabellen laden
	tabellenConfigs.forEach(cfg => loadTable(cfg));

	// ==========================================
	// ===== HILFSFUNKTIONEN ====================
	// ==========================================

	// Mannschaft bestimmen (Jugend / Herren + Nummer)
	function getMannschaft(heim, gast, klasse) {

		let team = "";

		if (heim.includes("Laudenbach")) team = heim;
		else if (gast.includes("Laudenbach")) team = gast;
		else return "-";

		const match = team.match(/(I|II|III|IV|V)$/);
		const nummer = match ? match[0] : "I";

		if (klasse.startsWith("J")) return "Jugend " + nummer;
		if (klasse.startsWith("E")) return "Herren " + nummer;

		return nummer;
	}

	// Spielort nur bei Heimspielen anzeigen
	function getSpielort(code, istHeimspiel) {

		if (!istHeimspiel) return "Auswärtsspiel";

		switch (code) {
			case "1": return "Großsporthalle Weikersheim";
			case "2": return "Zehntscheune Laudenbach";
			case "3": return "Ausweichhalle";
			default: return "Unbekannt";
		}
	}

	// Uhrzeit formatieren
	function formatUhrzeit(uhrzeit) {
		return uhrzeit.replace("\n", " ").replace(/\s+v$/, " v");
	}

	// Ergebnis oder Platzhalter
	function getErgebnis(spiel) {
		if (spiel.status === "geplant") return "-:-";
		return spiel.ergebnis || "-:-";
	}

	function formatErgebnis(heim, gast, ergebnis) {
	
		if (!ergebnis) return "-:-";
	
		const [heimPunkte, gastPunkte] = ergebnis.split(":").map(Number);
	
		const istHeimspiel = heim.includes("TTF Laudenbach");
	
		// Wenn Laudenbach Heim ist → nichts ändern
		if (istHeimspiel) {
			return `${heimPunkte}:${gastPunkte}`;
		}
	
		// Wenn Laudenbach Gast ist → drehen
		return `${gastPunkte}:${heimPunkte}`;
	}

});
