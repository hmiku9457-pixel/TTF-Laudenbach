from datetime import datetime, timedelta

today = datetime.today()
start_date = (today - timedelta(days=30)).strftime("%Y-%m-%d")
end_date = (today + timedelta(days=30)).strftime("%Y-%m-%d")


# ==========================================
# ==== SPIELPLÄNE ==========================
# ==========================================
SPIELPLAENE = [
    {
        "id": "spieleStartseite",
        "name": "Startseite Spiele",
        "url": f"https://www.mytischtennis.de/click-tt/TTBW/25--26/verein/07041/TTF_Laudenbach/spielplan?date_start={start_date}&date_end={end_date}",
        "type": "startseite"
    },
    {
        "id": "spieleHerren1",
        "name": "Spiele Herren 1",
        "url": "https://www.mytischtennis.de/click-tt/TTBW/25--26/ligen/E_Bezirksklasse_B_Gr.1/gruppe/494235/mannschaft/2959945/TTF_Laudenbach/spielerbilanzen/gesamt",
        "type": "mannschaft"
    },
    {
        "id": "spieleHerren2",
        "name": "Spiele Herren 2",
        "url": "https://www.mytischtennis.de/click-tt/TTBW/25--26/ligen/E_Kreisliga_A_Gr._2/gruppe/494509/mannschaft/2957619/TTF_Laudenbach_II/spielerbilanzen/gesamt",
        "type": "mannschaft"
    },
    {
        "id": "spieleHerren3",
        "name": "Spiele Herren 3",
        "url": "https://www.mytischtennis.de/click-tt/TTBW/25--26/ligen/E_Kreisliga_B_Gr._3/gruppe/494867/mannschaft/2961414/TTF_Laudenbach_III/spielerbilanzen/gesamt",
        "type": "mannschaft"
    },
    {
        "id": "spieleJugend1",
        "name": "Spiele Jugend 1",
        "url": "https://www.mytischtennis.de/click-tt/TTBW/25--26/ligen/Kreisliga_C_Ost/gruppe/494792/mannschaft/2958834/TTF_Laudenbach/spielerbilanzen/gesamt",
        "type": "mannschaft"
    },
    {
        "id": "spieleJugend2",
        "name": "Spiele Jugend 2",
        "url": "https://www.mytischtennis.de/click-tt/TTBW/25--26/ligen/Kreisliga_E2_Ost/gruppe/494250/mannschaft/2991365/TTF_Laudenbach_II/spielerbilanzen/gesamt",
        "type": "mannschaft"
    }
]


# ==========================================
# ==== TABELLEN ============================
# ==========================================
TABELLEN = [
    {
        "id": "tabelleHerren1",
        "name": "Tabelle Herren 1",
        "url": "https://www.mytischtennis.de/click-tt/TTBW/25--26/ligen/E_Bezirksklasse_B_Gr.1/gruppe/494235/tabelle/gesamt"
    },
    {
        "id": "tabelleHerren2",
        "name": "Tabelle Herren 2",
        "url": "https://www.mytischtennis.de/click-tt/TTBW/25--26/ligen/E_Kreisliga_A_Gr._2/gruppe/494509/tabelle/gesamt"
    },
    {
        "id": "tabelleHerren3",
        "name": "Tabelle Herren 3",
        "url": "https://www.mytischtennis.de/click-tt/TTBW/25--26/ligen/E_Kreisliga_B_Gr._3/gruppe/494867/tabelle/gesamt"
    },
    {
        "id": "tabelleJugend1",
        "name": "Tabelle Jugend 1",
        "url": "https://www.mytischtennis.de/click-tt/TTBW/25--26/ligen/Kreisliga_C_Ost/gruppe/494792/tabelle/gesamt"
    },
    {
        "id": "tabelleJugend2",
        "name": "Tabelle Jugend 2",
        "url": "https://www.mytischtennis.de/click-tt/TTBW/25--26/ligen/Kreisliga_E2_Ost/gruppe/494250/tabelle/gesamt"
    }
]


# ==========================================
# ==== EXTERNE LINKS =======================
# ==========================================
LINKS = [
    {
        "gruppe": "tt-links",
        "links": [
            {
                "id": "click-tt",
                "name": "click-tt",
                "url": "https://ttvwh.click-tt.de/"
            },
            {
                "id": "tischtennisbezirk_hohenlohe",
                "name": "Tischtennisbezirk Hohenlohe",
                "url": "https://www.ttbw.de/hohenlohe"
            },
            {
                "id": "ttvwh",
                "name": "TTVWH",
                "url": "https://www.ttvwh.de/"
            },
            {
                "id": "dttb",
                "name": "DTTB",
                "url": "https://www.tischtennis.de/"
            }
        ]
    },
    {
        "gruppe": "sport_allgemein",
        "links": [
            {
                "id": "wlsb",
                "name": "WLSB",
                "url": "https://www.wlsb.de/"
            },
            {
                "id": "sportkreis_mergentheim",
                "name": "Sportkreis Mergentheim",
                "url": "https://sportkreis-mergentheim.de/"
            }
        ]
    },
    {
        "gruppe": "dies_und_das",
        "links": [
            {
                "id": "weinort_laudenbach",
                "name": "Weinort Laudenbach",
                "url": "https://weinort-laudenbach.de/"
            }
        ]
    },
    {
        "gruppe": "sponsoren",
        "links": [
            {
                "id": "sponsor1",
                "name": "JAKO",
                "bild": "./assets/images/TTF-Laudenbach_Logo.png",
                "url": "http://www.jako.com/"
            },
            {
                "id": "sponsor2",
                "name": "Vier Elemente",
                "bild": "./assets/images/TTF-Laudenbach_Logo.png",
                "url": "https://vierelemente2018.de/"
            },
            {
                "id": "sponsor3",
                "name": "Endin",
                "bild": "./assets/images/TTF-Laudenbach_Logo.png",
                "url": "https://endin.eu/"
            },
            {
                "id": "sponsor4",
                "name": "Tuwa",
                "bild": "./assets/images/TTF-Laudenbach_Logo.png",
                "url": "https://www.instagram.com/tuwa_feinkost/"
            }
        ]
    }
]
