# Gera telas_estaticas/static/deck/Optima-PDV-Deck.pdf a partir de deck/deck.html (rode na raiz do app-demo).
import pathlib
from playwright.sync_api import sync_playwright
raiz = pathlib.Path(".").resolve()
src = raiz/"deck/deck.html"; pdf = raiz/"telas_estaticas/static/deck/Optima-PDV-Deck.pdf"
import os; shots = pathlib.Path(os.environ["TEMP"])/"shots"
with sync_playwright() as p:
    b = p.chromium.launch(channel="msedge")
    pg = b.new_page(viewport={"width":1920,"height":1080})
    pg.goto(src.as_uri()); pg.wait_for_load_state("networkidle"); pg.wait_for_timeout(500)
    pg.pdf(path=str(pdf), width="1920px", height="1080px", print_background=True, prefer_css_page_size=True)
    n = pg.evaluate("document.querySelectorAll('.slide').length")
    for i in range(n):
        pg.evaluate(f"document.querySelectorAll('.slide')[{i}].scrollIntoView()")
        pg.screenshot(path=str(shots/f"deck_{i+1:02d}.png"))
    b.close()
print("slides:", n, "| pdf:", pdf.stat().st_size//1024, "KB")
