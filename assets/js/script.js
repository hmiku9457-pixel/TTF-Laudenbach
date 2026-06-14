// ==========================================
// ===== INHALTSVERZEICHNIS =================
// ==========================================
//
// 01 - DOM READY
// 02 - HEADER LADEN
// 03 - FOOTER LADEN
// 04 - NEWS SLIDER
// 05 - SLIDER LOGIK
// 06 - ANIMATIONEN
// 07 - TABELLEN SUCHE
// 08 - THEME SWITCHER
// 09 - iFRAME CONSENT (DSGVO)
// 10 - GENERISCHER TABLE LOADER
// 11 - SPIELE KONFIG
// 12 - TABELLEN KONFIG
// 13 - HILFSFUNKTIONEN
// 14 - LINKS LOADER
// 15 - KONTAKTFORMULAR
// 16 - HISTORISCHE FOTOS
//
// ==========================================


// ==========================================
// ===== 01 - DOM READY =====================
// ==========================================

// Wartet bis das komplette HTML geladen ist,
// damit alle DOM-Elemente sicher verfügbar sind
document.addEventListener("DOMContentLoaded", () => {

	// ==========================================
	// ===== 02 - HEADER LADEN ==================
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
	// ===== 03 - FOOTER LADEN ==================
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
	// ===== 04 - NEWS SLIDER ===================
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
	// ===== 05 - SLIDER LOGIK ==================
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
	// ===== 06 - ANIMATIONEN ===================
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
	// ===== 07 - TABELLEN SUCHE ================
	// ==========================================

	function initTableSearch() {

		const input = document.getElementById("searchInput");
		const rows = document.querySelectorAll(".table-ewigeRangliste tbody tr");

		if(!input || rows.length === 0) return;

		input.addEventListener("input", () => {

			const search = input.value.toLowerCase();

			rows.forEach(row => {
				const name = row.children[1].textContent.toLowerCase();
				row.style.display = name.includes(search) ? "" : "none";
			});
		});
	}

	initTableSearch();

	// ==========================================
	// ===== 08 - THEME SWITCHER ================
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
	// ===== 09 - iFRAME CONSENT ================
	// ==========================================

	function createIframe(container, src) {

		const iframe = document.createElement("iframe");

		iframe.src = src;
		iframe.style.width = "100%";
		iframe.style.height = "250px";
		iframe.style.border = "0";
		iframe.loading = "lazy";
		iframe.referrerPolicy = "no-referrer-when-downgrade";
		iframe.allowFullscreen = true;

		container.innerHTML = "";
		container.appendChild(iframe);
	}

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
	// ===== 10 - GENERISCHER TABLE LOADER ======
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

			// QoL: Suche nach dynamischem Laden neu initialisieren
			initTableSearch();

		} catch (error) {
			console.error(`Fehler bei ${config.url}:`, error);
		}
	}

	// ==========================================
	// ===== 11 - SPIELE KONFIG =================
	// ==========================================

	
	const spieleConfigs = [
		// Startseite: Spiele des gesamten Vereins
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
		{ targetId: "spiele-herren1", url: "/TTF-Laudenbach/assets/data/spieleHerren1.json", render: renderStandardSpiele },
		{ targetId: "spiele-herren2", url: "/TTF-Laudenbach/assets/data/spieleHerren2.json", render: renderStandardSpiele },
		{ targetId: "spiele-herren3", url: "/TTF-Laudenbach/assets/data/spieleHerren3.json", render: renderStandardSpiele },
		{ targetId: "spiele-jugend1", url: "/TTF-Laudenbach/assets/data/spieleJugend1.json", render: renderStandardSpiele },
		{ targetId: "spiele-jugend2", url: "/TTF-Laudenbach/assets/data/spieleJugend2.json", render: renderStandardSpiele }
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
	// ===== 12 - TABELLEN KONFIG ===============
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
		{ targetId: "tabelle-herren1", url: "/TTF-Laudenbach/assets/data/tabelleHerren1.json", render: renderStandardTabelle },
		{ targetId: "tabelle-herren2", url: "/TTF-Laudenbach/assets/data/tabelleHerren2.json", render: renderStandardTabelle },
		{ targetId: "tabelle-herren3", url: "/TTF-Laudenbach/assets/data/tabelleHerren3.json", render: renderStandardTabelle },
		{ targetId: "tabelle-jugend1", url: "/TTF-Laudenbach/assets/data/tabelleJugend1.json", render: renderStandardTabelle },
		{ targetId: "tabelle-jugend2", url: "/TTF-Laudenbach/assets/data/tabelleJugend2.json", render: renderStandardTabelle }
	];

	// Tabellen laden
	tabellenConfigs.forEach(cfg => loadTable(cfg));

	// ==========================================
	// ===== 13 - HILFSFUNKTIONEN ===============
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
		if (istHeimspiel) return `${heimPunkte}:${gastPunkte}`;
		
		// Wenn Laudenbach Gast ist → drehen
		return `${gastPunkte}:${heimPunkte}`;
	}

	// ==========================================
	// ===== 14 - LINKS LOADER ==================
	// ==========================================
	
	async function loadLinks() {
	
		try {
			const response = await fetch('/TTF-Laudenbach/assets/data/links.json');
			const data = await response.json();

			// =====================================
			// ===== TABELLEN LINKS ===============
			// =====================================
			
			data.tabellen.forEach(e => {
			
				const el = document.getElementById("link-" + e.id);
			
				if (el) {
					el.href = e.url;
				}
			});

			// =====================================
			// ===== SPIELPLAN LINKS ==============
			// =====================================
			
			data.spielplaene.forEach(e => {
			
				const el = document.getElementById("link-" + e.id);
			
				if (el) {
					el.href = e.url;
				}
			});
	
			// =====================================
			// ===== LINK-GRUPPEN ==================
			// =====================================
	
			data.links.forEach(gruppe => {
	
				// WICHTIG: exakt gleiche ID wie HTML
				const container = document.getElementById("gruppe-" + gruppe.gruppe);
	
				if (!container) return;
	
				container.innerHTML = "";
	
				gruppe.links.forEach(link => {
				
					const a = document.createElement("a");
				
					a.href = link.url;
					a.target = "_blank";
					a.rel = "noopener noreferrer";
					a.className = "button button--card";
				
					// Text
					a.textContent = link.name;
				
					// WICHTIG: eindeutige ID setzen um einzelne IDs aus der Gruppe verwenden zu können
					a.id = `gruppe-link-${link.id}`;
				
					container.appendChild(a);
				});
			});

			// =====================================
			// ===== FOOTER (SPONSOR) LINKS ========
			// =====================================
			
			const sponsorSlots = ["sponsor1", "sponsor2", "sponsor3", "sponsor4"];
			
			data.links.forEach(gruppe => {
				gruppe.links.forEach(link => {
			
					if (!sponsorSlots.includes(link.id)) return;
			
					// Bugfix damit der Link gleichzeitig in Main und Footer existieren kann
					const targets = [
						`link-${link.id}`,
						`link-${link.id}-main`,
						`link-${link.id}-footer`
					];
			
					targets.forEach(id => {
						const el = document.getElementById(id);
			
						if (el) {
							el.href = link.url;
							el.textContent = link.name;
						}
					});
				});
			});
	
		} catch (error) {
			console.error("Fehler beim Laden der links.json:", error);
		}
	}

	// ==========================================
	// ===== 15 - KONTAKTFORMULAR ===============
	// ==========================================
	
	function initContactForm() {
	
		const contactForm = document.getElementById("contactForm");
	
		if (!contactForm) return;
	
		const submitButton = document.getElementById("contactSubmitButton");
	
		if (!submitButton) return;
	
		function isMobileView() {
			return window.matchMedia("(max-width: 768px)").matches;
		}
	
		function resetContactForm() {
			contactForm.reset();
	
			submitButton.classList.remove(
				"is-sending",
				"is-success",
				"is-error"
			);
	
			submitButton.textContent = "Nachricht senden";
			submitButton.disabled = false;
		}
	
		contactForm.addEventListener("submit", async (event) => {
	
			event.preventDefault();
	
			// Erfolg -> Formular zurücksetzen
			if (submitButton.classList.contains("is-success")) {
				resetContactForm();
				return;
			}
			
			// Fehler -> Status entfernen und erneut senden
			if (submitButton.classList.contains("is-error")) {
			
				submitButton.classList.remove("is-error");
				submitButton.textContent = "Nachricht senden";
			
				// kein return!
				// Formular wird direkt erneut gesendet
			}
	
			const formData = new FormData(contactForm);
	
			submitButton.disabled = true;
			submitButton.classList.remove(
				"is-success",
				"is-error"
			);
	
			submitButton.classList.add("is-sending");
			submitButton.textContent = "Wird gesendet...";
	
			try {
	
				const response = await fetch(contactForm.action, {
					method: contactForm.method,
					body: formData,
					headers: {
						"Accept": "application/json"
					}
				});
	
				submitButton.classList.remove("is-sending");
	
				if (response.ok) {
	
					if (isMobileView()) {
						alert("Vielen Dank! Ihre Nachricht wurde erfolgreich gesendet.");
						resetContactForm();
					} else {
						submitButton.classList.add("is-success");
						submitButton.textContent = "✓ Gesendet – Weitere Nachricht senden?";
						submitButton.disabled = false;
					}
	
				} else {
	
					if (isMobileView()) {
						alert("Beim Senden ist ein Fehler aufgetreten.");
						submitButton.classList.remove("is-error");
						submitButton.textContent = "Nachricht senden";
						submitButton.disabled = false;
					} else {
						submitButton.classList.add("is-error");
						submitButton.textContent = "✗ Fehler – Erneut versuchen?";
						submitButton.disabled = false;
					}
				}
	
			} catch (error) {
	
				console.error(error);
	
				submitButton.classList.remove("is-sending");
	
				if (isMobileView()) {
					alert("Es konnte keine Verbindung hergestellt werden.");
					submitButton.textContent = "Nachricht senden";
					submitButton.disabled = false;
				} else {
					submitButton.classList.add("is-error");
					submitButton.textContent = "✗ Verbindungsfehler – Erneut versuchen?";
					submitButton.disabled = false;
				}
			}
		});
	}

	// ==========================================
	// ===== 16 - HISTORISCHE FOTOS =============
	// ==========================================
	
	async function initHistoricalImages() {
	
		const galleryContainer = document.getElementById("images-gallery-container");
		const eventList = document.getElementById("images-event-list");
		const loadingBox = document.getElementById("images-loading");
	
		if (!galleryContainer || !eventList) return;
	
		try {
			const response = await fetch("/TTF-Laudenbach/assets/data/gallerie.json");
			const data = await response.json();
	
			const galleries = data.galleries || [];
			const defaultGalleryId = data.defaultGallery || "general";
	
			if (galleries.length === 0) {
				galleryContainer.innerHTML = `
					<div class="box">
						<p class="u-text-center">Keine Bilder gefunden.</p>
					</div>
				`;
				eventList.innerHTML = "";
				if (loadingBox) loadingBox.style.display = "none";
				return;
			}
	
			function renderGallery(galleryId) {
	
				const gallery = galleries.find(item => item.id === galleryId);
	
				if (!gallery) return;
	
				galleryContainer.innerHTML = `
					<section class="box images-gallery is-active" data-gallery="${gallery.id}">
						<h3 class="u-text-center">${gallery.title}</h3>
	
						<div class="masonry-gallery">
							${gallery.images.map((image, index) => `
								<img src="${image}" alt="${gallery.title} Bild ${index + 1}" loading="lazy">
							`).join("")}
						</div>
					</section>
				`;
	
				document.querySelectorAll(".images-event-button").forEach(button => {
					button.classList.toggle(
						"is-active",
						button.dataset.target === gallery.id
					);
				});
	
				if (loadingBox) loadingBox.style.display = "none";
			}
	
			eventList.innerHTML = "";
	
			galleries.forEach(gallery => {
	
				const button = document.createElement("button");
	
				button.type = "button";
				button.className = "images-event-button";
				button.dataset.target = gallery.id;
				button.textContent = gallery.title;
	
				if (gallery.id === defaultGalleryId) {
					button.classList.add("is-active");
				}
	
				button.addEventListener("click", () => {
					renderGallery(gallery.id);
				});
	
				eventList.appendChild(button);
			});
	
			renderGallery(defaultGalleryId);
	
		} catch (error) {
			console.error("Fehler beim Laden der gallerie.json:", error);
	
			galleryContainer.innerHTML = `
				<div class="box">
					<p class="u-text-center">Die Bilder konnten nicht geladen werden.</p>
				</div>
			`;
	
			eventList.innerHTML = "";
			if (loadingBox) loadingBox.style.display = "none";
		}
	}
	
	initHistoricalImages();
	
	initContactForm();

	loadLinks();
	
});
