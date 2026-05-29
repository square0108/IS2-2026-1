from app.db_model import Estudiante, Curso


CONSULTAS = {
    "estudiantes_por_curso": {
        "nombre": "Estudiantes por curso",
        "parametros": ["curso"]
    },
    "buscar_estudiantes": {
        "nombre": "Buscar estudiantes",
        "parametros": ["q", "curso"]
    }
}


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
