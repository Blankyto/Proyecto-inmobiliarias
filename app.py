import os

from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask import session as sess
from sqlalchemy import and_
import datetime

from werkzeug.utils import secure_filename

STATIC_FOLDER = 'templates/assets'
app = Flask(__name__,
            static_folder=STATIC_FOLDER)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///databases/realstate.db"
db = SQLAlchemy(app)
session = db.session
UPLOAD_FOLDER = 'templates/assets/img/properties'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg', 'gif'])
app.secret_key = "caircocoders-ednalan"


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


class Casas(db.Model):
    __tablename__ = "Casas"

    id = db.Column(db.Integer, primary_key=True)
    Casa = db.Column(db.String(200))
    Vendedor = db.Column(db.String(200))
    Area = db.Column(db.String(200))
    Dormitorio = db.Column(db.String(200))
    Banios = db.Column(db.String(200))
    Precio = db.Column(db.String(200))
    Estado = db.Column(db.String(200))
    Tipo = db.Column(db.String(200))
    DescripcionR = db.Column(db.String(200))
    DescripcionC = db.Column(db.String(500))
    Ubicacion = db.Column(db.String(200))
    Imagen = db.Column(db.String(200))


class Caract(db.Model):
    __tablename__ = "Caract"

    id = db.Column(db.Integer, primary_key=True)
    Casa = db.Column(db.Integer)
    Caracteristicas = db.Column(db.String(200))


class Imagenes(db.Model):
    __tablename__ = "Imagenes"
    id = db.Column(db.Integer, primary_key=True)
    casa = db.Column(db.Integer)
    archivo = db.Column(db.String(200))
    fecha = db.Column(db.String(200))
    primaria = db.Column(db.Boolean, default=False, nullable=False)


class Agente(db.Model):
    __tablename__ = "Agente"

    nombre = db.Column(db.String(200), primary_key=True)
    Empresa = db.Column(db.String(200))
    Telefono = db.Column(db.String(200))
    Email = db.Column(db.String(200))
    Desscripcion = db.Column(db.String(200))


class Usuarios(db.Model):
    __tablename__ = "Usuarios"

    id = db.Column(db.Integer, primary_key=True)

    Email = db.Column(db.String(200))

    Clave = db.Column(db.String(200))


db.create_all()
db.session.commit()


@app.route('/')
def index():
    c = db.session.query(Casas).order_by(Casas.id.desc()).limit(2)

    return render_template("/Index.html", c=c)


@app.route("/lista", methods=["GET", "POST"])
def lista():
    c = db.session.query(Casas).order_by(Casas.id.desc()).limit(2)
    if request.method == "GET":
        c = session.query(Casas).order_by(Casas.id.desc()).limit(2)
        busqueda = session.query(Casas).all()
        t = []
        d = []
        b = []
        u = []
        e = []
        ROWS_PER_PAGE = 20
        page = request.args.get('page', 1, type=int)

        busqueda2 = Casas.query.paginate(page=page, per_page=ROWS_PER_PAGE)
        rows = session.query(Casas).count()
        for i in busqueda:
            if i.Tipo not in t:
                t.append(i.Tipo)
            if i.Dormitorio not in d:
                d.append(i.Dormitorio)
            if i.Banios not in b:
                b.append(i.Banios)
            if i.Ubicacion not in u:
                u.append(i.Ubicacion)
            if i.Estado not in e:
                e.append(i.Estado)

        return render_template("/lista.html", lista2=busqueda, lista=busqueda2, c=c, rows=rows, tf=t, dor=d, ban=b,
                               est=e, ub=u)
    if request.method == "POST":
        c = session.query(Casas).order_by(Casas.id.desc()).limit(2)
        estado = request.form.get("estado")
        dormitorio = request.form.get("dormitorio")
        tipo = request.form.get("tipo")
        banio = request.form.get("banio")
        busqueda2 = db.session.query(Casas).filter(
            and_(Casas.Estado.ilike("%" + estado + "%"), Casas.Dormitorio.ilike("%" + dormitorio + "%"),
                 Casas.Tipo.ilike("%" + tipo + "%"), Casas.Banios.ilike("%" + banio + "%")))
        busqueda = session.query(Casas).all()
        t = []
        d = []
        b = []
        u = []
        e = []

        rows = busqueda2.count()
        for i in busqueda:
            if i.Tipo not in t:
                t.append(i.Tipo)
            if i.Dormitorio not in d:
                d.append(i.Dormitorio)
            if i.Banios not in b:
                b.append(i.Banios)
            if i.Ubicacion not in u:
                u.append(i.Ubicacion)
            if i.Estado not in e:
                e.append(i.Estado)

        return render_template("/lista.html", lista=busqueda2, c=c, rows=rows, tf=t, dor=d, ban=b, est=e, ub=u)


@app.route("/upload", methods=["POST", "GET"])
def upload():
    casa = db.session.query(Casas).all()
    c = db.session.query(Casas).order_by(Casas.id.desc()).limit(2)
    now = datetime.datetime.now()
    estado = request.form.get("estado")
    if request.method == 'POST':
        files = request.files.getlist('files[]')
        estado = request.form.get("estado")
        estado = int(estado)
        primaria = request.form.get("primaria")
        primaria = primaria == "True"
        for file in files:
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)

                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                imagenes = Imagenes(casa=estado, archivo=filename, fecha=now, primaria=primaria)
                if primaria is True:
                    imagen = db.session.query(Casas).filter(Casas.id == estado).one()

                    imagen.Imagen = filename
                    print(imagen.Imagen)
                    db.session.commit()
                db.session.add(imagenes)
                db.session.commit()

        flash('Fotos cargadas')
    return render_template("/upload.html", casa=casa, c=c)
    if request.method == 'GET':
        return render_template("/upload.html", casa=casa)


@app.route("/cargar", methods=["POST", "GET"])
def cargar():
    if 'loggedin' in sess:

        c = db.session.query(Casas).order_by(Casas.id.desc()).limit(2)
        if request.method == "POST":
            precio = request.form.get("price")
            descripcionr = request.form.get("description")
            descripcionc = request.form.get("description2")
            titulo = request.form.get("title")
            ubic = request.form.get("ubi")
            tipo = request.form.get("tipo")
            estado = request.form.get("type")
            dorm = request.form.get("dorm")
            banios = request.form.get("banios")
            area = request.form.get("area")
            garage = request.form.get("garages")
            foto = request.files.getlist('files[]')

            for file in foto:
                filename = secure_filename(file.filename)
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                casa = Casas(Casa=titulo, Vendedor=" ", Area=area, Dormitorio=dorm, Banios=banios, Precio=precio,
                             Estado=estado, Tipo=tipo, DescripcionR=descripcionr, Ubicacion=ubic,
                             DescripcionC=descripcionc,
                             Imagen=filename)
                db.session.add(casa)
                db.session.commit()
                print("llego")
                flash('Casa Cargada')
                return render_template("/cargar.html", c=c)
        return render_template("/cargar.html", c=c)
    return redirect(url_for('login'))


@app.route("/Casa/<id>")
def Casa(id):
    busqueda = db.session.query(Casas).filter_by(id=int(id)).one()

    fotos = db.session.query(Imagenes).filter(Imagenes.casa == id).all()
    carac = db.session.query(Caract).filter(Caract.Casa == id).all()
    return render_template("Casa.html", casa=busqueda, fotos=fotos, carac=carac)


@app.route("/login", methods=["GET", "POST"])
def login():
    msg = ''
    if request.method == 'POST' and 'usuario' in request.form and 'pass' in request.form:
        username = request.form['usuario']
        password = request.form['pass']

        account = session.query(Usuarios).filter(and_(Usuarios.Email == username, Usuarios.Clave == password)).first()

        if account:

            if account.Email is not None:
                sess['loggedin'] = True
                sess['id'] = account.id
                sess['username'] = account.Email
                return redirect(url_for('cargar'))

            msg = 'Incorrect username/password!'
            return render_template("login.html", msg=msg)

        else:

            msg = 'Incorrect username/password! este error?'
            return render_template("login.html", msg=msg)
    else:
        return render_template("login.html", msg=msg)

    msg = 'Incorrect username/password!'
    return render_template("login.html", msg=msg)


@app.route("/caracteristicas", methods=["POST", "GET"])
def caracteristicas():
    if 'loggedin' in sess:
        c = db.session.query(Casas).order_by(Casas.id.desc()).limit(2)
        casa = db.session.query(Casas).all()
        if request.method == "GET":

            return render_template("/caracteristicas.html", c=c, casa=casa)


        else:
            cara = request.form.get("carac")
            casa = request.form.get("estado")
            l = []
            for i in cara.split(","):
                print(i)
                l.append(i)
            for i in l:
                print(l)
                carac = Caract(Casa=casa, Caracteristicas=i)
                db.session.add(carac)
                db.session.commit()
            return render_template("/caracteristicas.html", c=c, casa=casa)


@app.route("/modificar", methods=["GET", "POST"])
def modificar():
    if "loggedin" in sess:

        if request.method == "GET":
            page = request.args.get('page', 1, type=int)

            casa = db.session.query(Casas).paginate(page=page, per_page=20)

            return render_template("/modificar.html", lista=casa, casa=casa)
        if request.method == "POST":
            page = request.args.get('page', 1, type=int)

            casa = Casas.query.paginate(page=page, per_page=4)

            return render_template("/modificar.html", lista=casa, casa=casa)
    return redirect(url_for('login'))


@app.route("/modificarC", methods=["GET", "POST"])
def modificarC():
    if "loggedin" in sess:

        if request.method == "GET":
            page = request.args.get('page', 1, type=int)

            carac = Caract.query.paginate(page=page, per_page=20)
            casa = db.session.query(Casas).all()
            return render_template("/modificarC.html", casa=casa, carac=carac)
        if request.method == "POST":
            page = request.args.get('page', 1, type=int)
            casa = db.session.query(Casas).all()
            carac = Caract.query.paginate(page=page, per_page=20)

            return render_template("/modificarC.html", carac=carac, casa=casa)
    return redirect(url_for('login'))


@app.route("/modificarI", methods=["GET", "POST"])
def modificarI():
    if "loggedin" in sess:

        if request.method == "GET":
            page = request.args.get('page', 1, type=int)

            imagen = Imagenes.query.paginate(page=page, per_page=20)
            casa = db.session.query(Casas).all()
            return render_template("/modificarI.html", casa=casa, fotos=imagen)
        if request.method == "POST":
            page = request.args.get('page', 1, type=int)
            casa = db.session.query(Casas).all()
            imagen = Imagenes.query.paginate(page=page, per_page=20)

            return render_template("/modificarI.html", fotos=Imagenes, casa=casa)
    return redirect(url_for('login'))


@app.route("/eliminar/<id>", methods=["GET", "POST"])
def eliminar(id):
    if "loggedin" in sess:
        if request.method == "GET":
            casa = db.session.query(Casas).filter(Casas.id == int(id)).delete()
            db.session.commit()
            return redirect(url_for("modificar"))
        else:
            return redirect(url_for("modificar"))


@app.route("/eliminarC/<id>", methods=["GET", "POST"])
def eliminarC(id):
    if "loggedin" in sess:
        if request.method == "GET":
            carac = db.session.query(Caract).filter(Caract.id == int(id)).delete()
            db.session.commit()
            return redirect(url_for("modificarC"))
        else:
            return redirect(url_for("modificarC"))


@app.route("/eliminarI/<id>", methods=["GET", "POST"])
def eliminarI(id):
    if "loggedin" in sess:
        if request.method == "GET":
            Fotos = db.session.query(Imagenes).filter(Imagenes.id == int(id)).delete()
            db.session.commit()
            return redirect(url_for("modificarI"))
        else:
            return redirect(url_for("modificarI"))


if __name__ == "__main__":
    app.run(debug=True)
