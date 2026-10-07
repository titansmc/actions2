#!/usr/bin/env python3
"""comprova_desplegaments.py

Eina de línia de comandes que comprova l'estat d'una llista de llocs web
desplegats (per exemple, els desplegaments d'un projecte) i genera un
informe en pantalla i, opcionalment, en un fitxer CSV.

Només utilitza la biblioteca estàndard de Python: no cal instal·lar cap
paquet amb pip per a executar-la.

Ús:
    python comprova_desplegaments.py exemple.com
    python comprova_desplegaments.py exemple.com httpbin.org/status/500
    python comprova_desplegaments.py --fitxer urls.txt --eixida informe.csv
"""
from __future__ import annotations

import argparse
import csv
import datetime
import sys
import urllib.error
import urllib.request


def comprova_url(url: str, timeout: float = 5.0) -> dict:
    """Fa una petició HTTP a `url` i retorna un diccionari amb el resultat."""
    if not url.startswith(("http://", "https://")):
        url = "https://" + url

    inici = datetime.datetime.now()
    codi = None
    estat = "OK"

    try:
        with urllib.request.urlopen(url, timeout=timeout) as resposta:
            codi = resposta.status
            estat = "OK" if codi < 400 else "ERROR"
    except urllib.error.HTTPError as err:
        codi = err.code
        estat = "ERROR"
    except urllib.error.URLError as err:
        estat = f"SENSE RESPOSTA ({err.reason})"

    durada = (datetime.datetime.now() - inici).total_seconds()

    return {
        "url": url,
        "codi": codi,
        "estat": estat,
        "segons": round(durada, 3),
        "comprovat_el": inici.isoformat(timespec="seconds"),
    }


def llig_urls(args: argparse.Namespace) -> list[str]:
    urls = list(args.urls)
    if args.fitxer:
        with open(args.fitxer, encoding="utf-8") as f:
            urls += [linia.strip() for linia in f if linia.strip() and not linia.startswith("#")]
    if not urls:
        sys.exit("Cal indicar almenys una URL (com a paràmetre o amb --fitxer).")
    return urls


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Comprova l'estat HTTP d'una llista de desplegaments web."
    )
    parser.add_argument("urls", nargs="*", help="URLs a comprovar")
    parser.add_argument("--fitxer", help="Fitxer de text amb una URL per línia")
    parser.add_argument("--eixida", help="Fitxer CSV on guardar l'informe")
    args = parser.parse_args()

    resultats = [comprova_url(u) for u in llig_urls(args)]

    print(f"{'URL':40} {'ESTAT':22} {'CODI':6} SEGONS")
    for r in resultats:
        print(f"{r['url']:40} {r['estat']:22} {str(r['codi']):6} {r['segons']}")

    if args.eixida:
        with open(args.eixida, "w", newline="", encoding="utf-8") as f:
            escriptor = csv.DictWriter(f, fieldnames=resultats[0].keys())
            escriptor.writeheader()
            escriptor.writerows(resultats)
        print(f"\nInforme guardat a {args.eixida}")


if __name__ == "__main__":
    main()
