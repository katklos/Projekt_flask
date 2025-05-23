from flask import Flask, render_template, request, redirect
import os

app = Flask(__name__)


SALDO_FILE = "saldo.txt"
MAGAZYN_FILE = "magazyn.txt"
HISTORIA_FILE = "historia.txt"


def czytaj_saldo():
    if not os.path.exists(SALDO_FILE):
        return 0
    with open(SALDO_FILE, "r") as f:
        return float(f.read())


def zapisz_saldo(saldo):
    with open(SALDO_FILE, "w") as f:
        f.write(str(saldo))


def czytaj_magazyn():
    magazyn = {}
    if os.path.exists(MAGAZYN_FILE):
        with open(MAGAZYN_FILE, "r") as f:
            for linia in f:
                produkt, ilosc = linia.strip().split(",")
                magazyn[produkt] = int(ilosc)
    return magazyn


def zapisz_magazyn(magazyn):
    with open(MAGAZYN_FILE, "w") as f:
        for produkt, ilosc in magazyn.items():
            f.write(f"{produkt},{ilosc}\n")


def dodaj_do_historii(tekst):
    with open(HISTORIA_FILE, "a") as f:
        f.write(tekst + "\n")


@app.route("/")
def index():
    saldo = czytaj_saldo()
    magazyn = czytaj_magazyn()
    return render_template("index.html", saldo=saldo, magazyn=magazyn)


@app.route("/zakup", methods=["POST"])
def zakup():
    produkt = request.form["produkt"]
    cena = float(request.form["cena"])
    ilosc = int(request.form["ilosc"])

    saldo = czytaj_saldo()
    koszt = cena * ilosc

    if saldo < koszt:
        return "Brak wystarczających środków na koncie!"

    saldo -= koszt
    zapisz_saldo(saldo)

    magazyn = czytaj_magazyn()
    magazyn[produkt] = magazyn.get(produkt, 0) + ilosc
    zapisz_magazyn(magazyn)

    dodaj_do_historii(f"Zakup - {produkt}, {ilosc} szt., {koszt} PLN")

    return redirect("/")


@app.route("/sprzedaz", methods=["POST"])
def sprzedaz():
    produkt = request.form["produkt"]
    ilosc = int(request.form["ilosc"])
    cena_jednostkowa = float(request.form["cena"])

    magazyn = czytaj_magazyn()

    if produkt not in magazyn or magazyn[produkt] < ilosc:
        return "Za mało towaru w magazynie!"

    przychod = cena_jednostkowa * ilosc

    magazyn[produkt] -= ilosc
    zapisz_magazyn(magazyn)

    saldo = czytaj_saldo()
    saldo += przychod
    zapisz_saldo(saldo)

    dodaj_do_historii(f"Sprzedaż - {produkt}, {ilosc} szt., {przychod} PLN")

    return redirect("/")


@app.route("/zmiana_salda", methods=["POST"])
def zmiana_salda():
    wartosc = float(request.form["wartosc"])
    komentarz = request.form["komentarz"]

    saldo = czytaj_saldo()
    saldo += wartosc
    zapisz_saldo(saldo)

    dodaj_do_historii(f"Zmiana salda - {wartosc} PLN, Komentarz: {komentarz}")

    return redirect("/")


@app.route("/historia/")
@app.route("/historia/<int:start>/<int:end>")
def historia(start=None, end=None):
    if not os.path.exists(HISTORIA_FILE):
        historia = []
    else:
        with open(HISTORIA_FILE, "r") as f:
            historia = f.readlines()

    komunikat = ""
    if start is not None and end is not None:
        if start < 1 or end > len(historia) or start > end:
            komunikat = f"Błąd zakresu! Historia ma {len(historia)} pozycji."
            widoczne = historia
        else:
            widoczne = historia[start-1:end]
    else:
        widoczne = historia

    return render_template("historia.html", historia=list(enumerate(widoczne)), komunikat=komunikat)


if __name__ == "__main__":
    app.run(debug=True)
