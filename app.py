import os
from flask import Flask, render_template, request, redirect, url_for, flash
from sqlalchemy import create_engine, Column, Integer, String, Text
from sqlalchemy.orm import DeclarativeBase, Session

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "dev-secret")

DATABASE_URL = os.environ.get("DATABASE_URL", "sqlite:///dynasties.db")
engine = create_engine(DATABASE_URL)

class Base(DeclarativeBase):
    pass

class Dynasty(Base):
    __tablename__ = "dynasties"
    id          = Column(Integer, primary_key=True, autoincrement=True)
    name        = Column(String(100), nullable=False)
    ruler       = Column(String(100), nullable=False)
    year_start  = Column(Integer, nullable=False)
    year_end    = Column(Integer, nullable=False)
    capital     = Column(String(100))
    description = Column(Text)

Base.metadata.create_all(engine)

def seed():
    with Session(engine) as s:
        if s.query(Dynasty).count() > 0:
            return
        s.add_all([
            Dynasty(name="Хань",  ruler="Лю Бан (Гао-цзу)",   year_start=-206, year_end=220,  capital="Чанъань",       description="Расцвет конфуцианства и Шёлкового пути."),
            Dynasty(name="Тан",   ruler="Ли Юань (Гао-цзу)",  year_start=618,  year_end=907,  capital="Чанъань",       description="Золотой век поэзии и культуры."),
            Dynasty(name="Сун",   ruler="Чжао Куанъинь",      year_start=960,  year_end=1279, capital="Кайфэн",        description="Изобретение пороха, компаса, книгопечатания."),
            Dynasty(name="Мин",   ruler="Чжу Юаньчжан",       year_start=1368, year_end=1644, capital="Нанкин/Пекин",  description="Строительство Великой стены, экспедиции Чжэн Хэ."),
            Dynasty(name="Цин",   ruler="Нурхаци",             year_start=1644, year_end=1912, capital="Пекин",         description="Последняя императорская династия."),
            Dynasty(name="Цинь",  ruler="Цинь Шихуанди",      year_start=-221, year_end=-206, capital="Сяньян",        description="Первая объединённая империя. Терракотовая армия."),
        ])
        s.commit()

seed()

@app.route("/")
def index():
    node = os.environ.get("NODE_NAME", "—")
    with Session(engine) as s:
        rows = s.query(Dynasty).order_by(Dynasty.year_start).all()
        dynasties = [{"id": d.id, "name": d.name, "ruler": d.ruler,
                      "year_start": d.year_start, "year_end": d.year_end,
                      "capital": d.capital, "description": d.description}
                     for d in rows]
    return render_template("index.html", dynasties=dynasties, node=node)

@app.route("/add", methods=["GET", "POST"])
def add():
    if request.method == "POST":
        try:
            with Session(engine) as s:
                s.add(Dynasty(
                    name=request.form["name"],
                    ruler=request.form["ruler"],
                    year_start=int(request.form["year_start"]),
                    year_end=int(request.form["year_end"]),
                    capital=request.form.get("capital", ""),
                    description=request.form.get("description", ""),
                ))
                s.commit()
            flash("Запись добавлена.", "success")
            return redirect(url_for("index"))
        except Exception as e:
            flash(f"Ошибка: {e}", "danger")
    return render_template("form.html", title="Добавить", dynasty=None)

@app.route("/edit/<int:id>", methods=["GET", "POST"])
def edit(id):
    with Session(engine) as s:
        d = s.get(Dynasty, id)
        if not d:
            flash("Запись не найдена.", "danger")
            return redirect(url_for("index"))
        data = {"id": d.id, "name": d.name, "ruler": d.ruler,
                "year_start": d.year_start, "year_end": d.year_end,
                "capital": d.capital, "description": d.description}
    if request.method == "POST":
        try:
            with Session(engine) as s:
                d = s.get(Dynasty, id)
                d.name        = request.form["name"]
                d.ruler       = request.form["ruler"]
                d.year_start  = int(request.form["year_start"])
                d.year_end    = int(request.form["year_end"])
                d.capital     = request.form.get("capital", "")
                d.description = request.form.get("description", "")
                s.commit()
            flash("Запись обновлена.", "success")
            return redirect(url_for("index"))
        except Exception as e:
            flash(f"Ошибка: {e}", "danger")
    return render_template("form.html", title="Редактировать", dynasty=data)

@app.route("/delete/<int:id>", methods=["POST"])
def delete(id):
    with Session(engine) as s:
        d = s.get(Dynasty, id)
        if d:
            s.delete(d)
            s.commit()
            flash("Запись удалена.", "success")
        else:
            flash("Запись не найдена.", "danger")
    return redirect(url_for("index"))

@app.route("/health")
def health():
    try:
        with Session(engine) as s:
            s.query(Dynasty).count()
        return {"status": "ok"}, 200
    except Exception as e:
        return {"status": "error", "detail": str(e)}, 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=4000)