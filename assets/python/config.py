from datetime import datetime, timedelta

today = datetime.today()
start_date = (today - timedelta(days=30)).strftime("%Y-%m-%d")
end_date = (today + timedelta(days=30)).strftime("%Y-%m-%d")

SPIELPLAENE = [
    {
        "name": "spieleStartseite",
        "url": f"https://www.mytischtennis.de/click-tt/TTBW/25--26/verein/07041/TTF_Laudenbach/spielplan?date_start={start_date}&date_end={end_date}",
        "type": "startseite"
    },
    {
        "name": "spieleHerren1",
        "url": "https://www.mytischtennis.de/click-tt/TTBW/25--26/ligen/E_Bezirksklasse_B_Gr.1/gruppe/494235/mannschaft/2959945/TTF_Laudenbach/spielerbilanzen/gesamt",
        "type": "mannschaft"
    },
    {
        "name": "spieleHerren2",
        "url": "https://www.mytischtennis.de/click-tt/TTBW/25--26/ligen/E_Kreisliga_A_Gr._2/gruppe/494509/mannschaft/2957619/TTF_Laudenbach_II/spielerbilanzen/gesamt",
        "type": "mannschaft"
    },
    {
        "name": "spieleHerren3",
        "url": "https://www.mytischtennis.de/click-tt/TTBW/25--26/ligen/E_Kreisliga_B_Gr._3/gruppe/494867/mannschaft/2961414/TTF_Laudenbach_III/spielerbilanzen/gesamt",
        "type": "mannschaft"
    },
    {
        "name": "spieleJugend1",
        "url": "https://www.mytischtennis.de/click-tt/TTBW/25--26/ligen/Kreisliga_C_Ost/gruppe/494792/mannschaft/2958834/TTF_Laudenbach/spielerbilanzen/gesamt",
        "type": "mannschaft"
    },
    {
        "name": "spieleJugend2",
        "url": "https://www.mytischtennis.de/click-tt/TTBW/25--26/ligen/Kreisliga_E2_Ost/gruppe/494250/mannschaft/2991365/TTF_Laudenbach_II/spielerbilanzen/gesamt",
        "type": "mannschaft"
    }
]

TABELLEN = [
    {
        "name": "tabelleHerren1",
        "url": "https://www.mytischtennis.de/click-tt/TTBW/25--26/ligen/E_Bezirksklasse_B_Gr.1/gruppe/494235/tabelle/gesamt"
    },
    {
        "name": "tabelleHerren2",
        "url": "https://www.mytischtennis.de/click-tt/TTBW/25--26/ligen/E_Kreisliga_A_Gr._2/gruppe/494509/tabelle/gesamt"
    },
    {
        "name": "tabelleHerren3",
        "url": "https://www.mytischtennis.de/click-tt/TTBW/25--26/ligen/E_Kreisliga_B_Gr._3/gruppe/494867/tabelle/gesamt"
    },
    {
        "name": "tabelleJugend1",
        "url": "https://www.mytischtennis.de/click-tt/TTBW/25--26/ligen/Kreisliga_C_Ost/gruppe/494792/tabelle/gesamt"
    },
    {
        "name": "tabelleJugend2",
        "url": "https://www.mytischtennis.de/click-tt/TTBW/25--26/ligen/Kreisliga_E2_Ost/gruppe/494250/tabelle/gesamt"
    }
]

LINKS = [
    {
        "gruppe": "TT-Links",
        "links": [
            {
                "name": "click-tt",
                "url": "https://ttvwh.click-tt.de/"
            },
            {
                "name": "Tischtennisbezirk_Hohenlohe",
                "url": "https://www.ttbw.de/hohenlohe"
            },
            {
                "name": "TTVWH",
                "url": "https://www.ttvwh.de/"
            },
            {
                "name": "DTTB",
                "url": "https://www.tischtennis.de/"
            }
        ]
    },
    {
        "gruppe": "Sport_allgemein",
        "links": [
            {
                "name": "WLSB",
                "url": "https://www.wlsb.de/"
            },
            {
                "name": "Sportkreis_Mergentheim",
                "url": "https://sportkreis-mergentheim.de/"
            }
        ]
    },
    {
        "gruppe": "Dies_und_das",
        "links": [
            {
                "name": "Weinort_Laudenbach",
                "url": "https://weinort-laudenbach.de/"
            }
        ]
    },
    {
        "gruppe": "Sponsoren",
        "links": [
            # Name bezieht sich auf die ID im HTML Code.
            # Für eine bessere Übersicht sollte der Anzeigename in Display eingetragen werden.
            {
                "name": "sponsor1",
                "display": "JAKO",
                "url": "http://www.jako.com/"
            },
            {
                "name": "sponsor2",
                "display": "Vier Elemente",
                "url": "https://vierelemente2018.de/"
            },
            {
                "name": "sponsor3",
                "display": "Endin",
                "url": "https://endin.eu/"
            }
        ]
    }
]
