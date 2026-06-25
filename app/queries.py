from app.db_model import Estudiante, Curso, Incidente, Accion, db
from datetime import datetime, timezone
from flask import request, flash, redirect, url_for


CONSULTAS = {
    "estudiantes_por_curso": {
        "nombre": "Estudiantes por curso",
        "parametros": ["curso"]
    },
    "buscar_estudiantes": {
        "nombre": "Buscar estudiantes",
        "parametros": ["q", "curso"]
    },
    "buscar_incidentes": {
        "nombre": "Buscar incidentes",
        "parametros": ["q", "creador_id"]
    }
}

def db_tryCompletarAccion(db, accion: Accion):
    """
    Procesa el POST request para completar una Acción, extrayendo el resultado, e intenta registrarla a la base de datos (Respuesta + Estado=COMPLETADA + Setear fecha de completacion)
    Parameters: 
    - db: Conexión a alguna base de datos existente.
    - accion: Objeto Accion recuperado de la BD.
    - redirect_endpoint: String del endpoint al que redirigir (ej: 'reportador.detalleAccion' o 'encargado_de_convivencia.detalleAccion').
    """
    accion.resultado = request.form.get('resultado')
    accion.estado = "COMPLETADA"
    accion.fecha_completacion = datetime.now(timezone.utc)

    try:
        db.session.commit()
        flash("Acción completada exitosamente.", "success")
    except Exception as e:
        db.session.rollback()
        flash("Error al guardar la acción.", "danger")
        print(f"Error al completar acción: {e}")

def buscar_incidentes(q=None, creador_id=None):
    """
    Construye la consulta de incidentes con búsqueda opcional por nombre
    de estudiante involucrado y filtro opcional por autor.

    Parameters:
    - q: término de búsqueda (subcadena) sobre el nombre del estudiante.
    - creador_id: si se entrega, limita a los incidentes creados por ese usuario.

    Returns:
    - Un objeto query de SQLAlchemy (no ejecutado), para que la ruta pueda
      aplicar .paginate() u otras operaciones encima.
    """
    query = Incidente.query

    if creador_id is not None:
        query = query.filter(Incidente.creador_id == creador_id)

    q = (q or "").strip()
    if q:
        like_q = f"%{q}%"
        query = (
            query.join(Incidente.estudiantes)
            .filter(Estudiante.nombre_completo.ilike(like_q))
            .distinct()
        )

    return query.order_by(Incidente.fecha_adicion.desc())


def listar_consultas():
    # Devuelve las definiciones de consultas para que el frontend las muestre.
    return [
        {
            "tipo": tipo,
            "nombre": data["nombre"],
            "parametros": data["parametros"]
        }
        for tipo, data in CONSULTAS.items()
    ]


def ejecutar_consulta(tipo, params):
    # Deriva a la implementacion de consulta segun el tipo.
    if tipo == "estudiantes_por_curso":
        curso = params.get("curso")
        if not curso:
            return []

        resultados = (
            Estudiante.query
            .join(Curso)
            .filter(Curso.nombre == curso)
            .all()
        )

        return [
            {
                "id": e.id,
                "rut": e.rut,
                "nombre_completo": e.nombre_completo,
                "curso": e.curso.nombre
            }
            for e in resultados
        ]

    if tipo == "buscar_estudiantes":
        q = (params.get("q") or "").strip()
        curso = (params.get("curso") or "").strip()
        raw = bool(params.get("raw"))

        query = Estudiante.query.join(Curso)

        if curso:
            query = query.filter(Curso.nombre == curso)

        if q:
            like_q = f"%{q}%"
            query = query.filter(Estudiante.nombre_completo.ilike(like_q))

        resultados = query.order_by(
            Estudiante.nombre_completo.asc(),
            Curso.nombre.asc()
        ).all()

        if raw:
            return resultados

        return [
            {
                "id": e.id,
                "rut": e.rut,
                "nombre_completo": e.nombre_completo,
                "curso": e.curso.nombre
            }
            for e in resultados
        ]

    return []
