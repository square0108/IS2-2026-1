from app.db_model import Usuario

def test_usuario_set_password():
    """Prueba que el hash de la contraseña se genere y valide correctamente."""
    u = Usuario(username="nuevo.user", nombre_completo="Nuevo Usuario")
    u.set_password("mi_clave_segura")
    
    # La contraseña original no debe estar expuesta
    assert u.password != "mi_clave_segura"
    
    # La verificación debe funcionar
    assert u.check_password("mi_clave_segura") is True
    assert u.check_password("clave_equivocada") is False

def test_relacion_estudiante_curso(init_database):
    """Prueba que las relaciones de SQLAlchemy funcionen en memoria."""
    from app.db_model import Estudiante, Curso
    
    estudiante = Estudiante.query.filter_by(rut="111-1").first()
    curso = Curso.query.first()
    
    assert estudiante is not None
    assert curso is not None
    assert estudiante.curso_id == curso.id
    assert estudiante.curso.nombre == "1 Medio A"