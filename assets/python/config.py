from datetime import datetime, timedelta

today = datetime.today()
start_date = (today - timedelta(days=30)).strftime("%Y-%m-%d")
end_date = (today + timedelta(days=30)).strftime("%Y-%m-%d")

SPIELE_URL = f"https://www.mytischtennis.de/click-tt/TTBW/25--26/verein/07041/TTF_Laudenbach/spielplan?date_start={start_date}&date_end={end_date}"

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
        "url": "https://hmiku9457-pixel.github.io/TTF-Laudenbach/pages/aktiverSpielbetrieb/jugend2.html"
    }
]
