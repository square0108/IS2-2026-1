from app.db_model import Estudiante, Curso


CONSULTAS = {
    "estudiantes_por_curso": {
        "nombre": "Estudiantes por curso",
        "parametros": ["curso"]
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

    return []
