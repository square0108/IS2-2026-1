from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()

class EvidenciaCaso(db.Model):
    __tablename__ = 'caso_evidencia'
    caso_id = db.Column(db.Integer, db.ForeignKey('casos.id', ondelete="CASCADE"), primary_key=True)
    antecedente_id = db.Column(db.Integer, db.ForeignKey('antecedentes.id', ondelete="CASCADE"), primary_key=True)
    fecha_vinculacion = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

class Usuario(db.Model):
    __tablename__ = 'usuarios'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(225), nullable=False) # hashear esto mas tarde jejeje
    nombre_completo = db.Column(db.String(100), nullable=False)

    es_reportador = db.Column(db.Boolean, default=False, nullable=False)
    es_encargado = db.Column(db.Boolean, default=False, nullable=False)
    es_orientador = db.Column(db.Boolean, default=False, nullable=False)
    
    antecedentes_creados = db.relationship('Antecedente', backref='creador', lazy=True)

    #Hash de contraseña
    def set_password(self, raw_password):
        self.password = generate_password_hash(raw_password)

    def check_password(self, raw_password):
        return check_password_hash(self.password, raw_password)

class Curso(db.Model):
    __tablename__ = 'cursos'
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(50), unique=True, nullable=False)
    estudiantes = db.relationship('Estudiante', backref='curso', lazy=True)

class Estudiante(db.Model):
    __tablename__ = 'estudiantes'
    id = db.Column(db.Integer, primary_key=True)
    rut = db.Column(db.String(12), unique=True, nullable=False)
    nombre_completo = db.Column(db.String(100), nullable=False)
    curso_id = db.Column(db.Integer, db.ForeignKey('cursos.id'), nullable=False)

estudiante_antecedente = db.Table(
    'estudiante_antecedente',
    db.Column('estudiante_id', db.Integer, db.ForeignKey('estudiantes.id', ondelete="CASCADE"), primary_key=True),
    db.Column('antecedente_id', db.Integer, db.ForeignKey('antecedentes.id', ondelete="CASCADE"), primary_key=True)
)

class Antecedente(db.Model):
    __tablename__ = 'antecedentes'
    id = db.Column(db.Integer, primary_key=True)
    fecha_adicion = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    descripcion = db.Column(db.Text, nullable=False)
    tipo_antecedente = db.Column(db.String(30), nullable=False)
    
    creador_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=False)
    
    # relación muchos a muchos
    estudiantes = db.relationship(
        'Estudiante',
        secondary=estudiante_antecedente,
        backref=db.backref('antecedentes', lazy=True),
        lazy=True
    )

    __mapper_args__ = {
        'polymorphic_on': tipo_antecedente,
        'polymorphic_identity': 'ANTECEDENTE'
    }

class Incidente(Antecedente):
    respuesta_inmediata = db.Column(db.Text, nullable=True)
    categoria = db.Column(db.Text, nullable=True)
    __mapper_args__ = {'polymorphic_identity': 'INCIDENTE'}

class Diagnostico(Antecedente):
    # TODO: restricción no modelada: diagnosticos referencian a exactamente un estudiante
    __mapper_args__ = {'polymorphic_identity': 'DIAGNOSTICO'}

class Observacion(Antecedente):
    __mapper_args__ = {'polymorphic_identity': 'OBSERVACION'}

class Caso(db.Model):
    __tablename__ = 'casos'
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(150), nullable=False, default="Caso de Investigación")
    estado = db.Column(db.String(30), nullable=False, default='ABIERTO')
    fecha_creacion = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    fecha_limite = db.Column(db.DateTime, nullable=True)

    encargado_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=False)
    encargado = db.relationship('Usuario', backref=db.backref('casos_gestionados', lazy=True))
    
    evidencias = db.relationship(
        'Antecedente',
        secondary='caso_evidencia',
        backref=db.backref('casos_asociados', lazy=True),
        lazy=True
    )