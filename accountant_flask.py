from flask import Flask, render_template, request, redirect, url_for
from datetime import datetime
from models import db, Saldo, Produkt, Historia

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///accountant.db'
db.init_app(app)


@app.route("/")
def index():
    saldo_obj = Saldo.query.first()
    saldo = saldo_obj.wartosc if saldo_obj else 0.0
    magazyn = Produkt.query.all()
    return render_template("index.html", saldo=saldo, magazyn=magazyn)


@app.route("/zakup", methods=["POST"])
def zakup():
    produkt_nazwa = request.form["produkt"].strip()
    cena = float(request.form["cena"])
    ilosc = int(request.form["ilosc"])

    try:
        saldo_obj = Saldo.query.first()
        saldo = saldo_obj.wartosc

        koszt = cena * ilosc

        if saldo < koszt:
            return "Brak wystarczających środków na koncie!"
        saldo_obj.wartosc -= koszt

        produkt = Produkt.query.filter_by(nazwa=produkt_nazwa).first()
        if produkt:
            produkt.ilosc += ilosc
        else:
            nowy_produkt = Produkt(nazwa=produkt_nazwa, ilosc=ilosc)
            db.session.add(nowy_produkt)

        nowy_wpis_historii = Historia(opis=f"Zakup - {produkt_nazwa},  {ilosc} szt., {koszt} PLN")
        db.session.add(nowy_wpis_historii)

        db.session.commit()
        return redirect(url_for("index"))

    except Exception as e:
        db.session.rollback()
        return f"Wystąpił błąd podczas zakupu: {e}"


@app.route("/sprzedaz", methods=["POST"])
def sprzedaz():
    produkt_nazwa = request.form["produkt"].strip()
    ilosc = int(request.form["ilosc"])
    cena_jednostkowa = float(request.form["cena"])

    try:
        produkt = Produkt.query.filter_by(nazwa=produkt_nazwa).first()

        if not produkt or produkt.ilosc < ilosc:
            return "Za mało towaru w magazynie!"

        przychod = cena_jednostkowa * ilosc

        produkt.ilosc -= ilosc

        if produkt.ilosc == 0:
            db.session.delete(produkt)

        saldo_obj = Saldo.query.first()
        saldo_obj.wartosc += przychod

        nowy_wpis_historii = Historia(opis=f"Sprzedaż - {produkt_nazwa}, {ilosc} szt., {przychod} PLN")
        db.session.add(nowy_wpis_historii)

        db.session.commit()
        return redirect(url_for("index"))

    except Exception as e:
        db.session.rollback()
        return f"Wystąpił błąd podczas sprzedaży: {e}"


@app.route("/zmiana_salda", methods=["POST"])
def zmiana_salda():
    wartosc = float(request.form["wartosc"])
    komentarz = request.form["komentarz"].strip()

    try:
        saldo_obj = Saldo.query.first()
        saldo_obj.wartosc += wartosc

        nowy_wpis_historii = Historia(opis=f"Zmiana salda - {wartosc} PLN, Komentarz: {komentarz}")
        db.session.add(nowy_wpis_historii)

        db.session.commit()
        return redirect(url_for("index"))

    except Exception as e:
        db.session.rollback()
        return f"Wystąpił błąd podczas zmiany salda: {e}"


@app.route("/historia/")
@app.route("/historia/<int:start>/<int:end>")
def historia(start=None, end=None):
    historia_operacji = Historia.query.order_by(Historia.data.desc()).all()

    komunikat= ""
    widoczne_historie = []

    if start is not None and end is not None:
        if start < 1 or end > len(historia_operacji) or start > end:
            komunikat = f"Błąd zakresu! Historia ma {len(historia_operacji)} pozycji."
            widoczne_historie = historia_operacji
        else:
            widoczne_historie = historia_operacji[start - 1:end]
    else:
        widoczne_historie = historia_operacji

    return render_template("historia.html", historia=list(enumerate(widoczne_historie)), komunikat=komunikat)


if __name__ == "__main__":
    with app.app_context():
        pass

    app.run()
