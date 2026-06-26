import sys
import os
from datetime import datetime, timedelta, timezone

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from app import create_app
from app.db_model import (
    db, Usuario, Curso, Estudiante, 
    Incidente, Observacion, 
    Caso, Accion
)

app = create_app()

with app.app_context():
    print("🔄 Borrando base de datos actual...")
    db.drop_all()
    print("🏗️ Creando nueva estructura de base de datos...")
    db.create_all()

    now = datetime.now(timezone.utc)

    # ==========================================
    # 1. USUARIOS (Luis y Ana centralizan la Demo)
    # ==========================================
    print("👥 Generando usuarios...")
    reportador_luis = Usuario(username="luis.profesor", nombre_completo="Luis Fernández (Profesor)", es_reportador=True)
    reportador_luis.set_password("123")
    
    reportador_maria = Usuario(username="maria.inspectora", nombre_completo="María Soto (Inspectora)", es_reportador=True)
    reportador_maria.set_password("123")
    
    encargada_ana = Usuario(username="ana.directora", nombre_completo="Ana Silva (Encargada Convivencia)", es_encargado=True)
    encargada_ana.set_password("1234")
    
    encargado_roberto = Usuario(username="roberto.convivencia", nombre_completo="Roberto Gómez (Co-encargado)", es_encargado=True)
    encargado_roberto.set_password("1234")

    db.session.add_all([reportador_luis, reportador_maria, encargada_ana, encargado_roberto])
    db.session.commit()

    # ==========================================
    # 2. CURSOS Y ESTUDIANTES
    # ==========================================
    print("🏫 Generando cursos y estudiantes...")
    curso_a = Curso(nombre="1 Medio A")
    curso_b = Curso(nombre="2 Medio B")
    db.session.add_all([curso_a, curso_b])
    db.session.commit()

    estudiantes_data = [
        ("11111111-1", "Lucas Tapia", curso_a),
        ("22222222-2", "Martina Rojas", curso_a),
        ("33333333-3", "Mateo Valdés", curso_a),
        ("44444444-4", "Sofía Riquelme", curso_a),
        ("55555555-5", "Benjamín Castro", curso_a),
        ("66666666-6", "Isidora Fuentes", curso_a),
        ("77777777-7", "Tomás Herrera", curso_b),
        ("88888888-8", "Florencia Pinto", curso_b),
        ("99999999-9", "Agustín Vega", curso_b),
        ("10101010-0", "Antonia Lira", curso_b),
        ("12121212-2", "Vicente Navarro", curso_b),
        ("13131313-3", "Camila Guzmán", curso_b)
    ]

    est_dict = {}
    for rut, nombre, curso in estudiantes_data:
        e = Estudiante(rut=rut, nombre_completo=nombre, curso=curso)
        est_dict[nombre.split()[0]] = e
        db.session.add(e)
    
    db.session.commit()

    # ==========================================
    # 3. ANTECEDENTES Y CASOS 
    # ==========================================
    print("📁 Generando historial con reportes compartidos y nuevas acciones para Ana...")

    # --- CASO 1: Acoso Escolar Físico (Mateo vs Lucas) ---
    c1_ant1 = Observacion(
        descripcion_corta="Tensión conductual en aula", descripcion_extendida="Durante la supervisión de salas noté un clima hostil recurrente entre Mateo y Lucas.",
        estudiantes=[est_dict["Mateo"], est_dict["Lucas"]], creador=encargada_ana, fecha_adicion=now - timedelta(days=60)
    )
    # 🔄 REPORTE 1 MOVIDO A ANA: Presenciado directamente por ella en el pasillo central
    c1_ant2 = Incidente(
        descripcion_corta="Zancadilla en el pasillo", descripcion_extendida="Mateo le hizo una zancadilla a Lucas a la salida de la sala. Yo iba pasando por el sector.", respuesta_inmediata="Llamado de atención verbal estricto en el lugar y orden de disculpas.", categoria="Físico",
        estudiantes=[est_dict["Mateo"], est_dict["Lucas"]], creador=encargada_ana, fecha_adicion=now - timedelta(days=50)
    )
    c1_ant3 = Incidente(
        descripcion_corta="Pelea a golpes en recreo", descripcion_extendida="Lucas reaccionó a provocaciones previas golpeando a Mateo en la cara. Intervine como testigo presencial.", respuesta_inmediata="Procedí a separarlos y activar el reporte inmediato a Ana.", categoria="Físico",
        estudiantes=[est_dict["Mateo"], est_dict["Lucas"]], creador=reportador_luis, fecha_adicion=now - timedelta(days=20)
    )
    caso1 = Caso(nombre="Bullying Físico Reiterado - Mateo y Lucas", encargado=encargada_ana, estado="EN PROGRESO", fecha_creacion=now - timedelta(days=19))
    caso1.evidencias.extend([c1_ant1, c1_ant2, c1_ant3])

    # Acciones Caso 1
    a1_ana = Accion(descripcion_corta="Citación apoderados en Dirección", descripcion_extendida="Reunión formal con tutores para informar sobre las agresiones físicas.", resultado="Apoderados toman conocimiento y exigen medidas de aula inmediatas.", estado="COMPLETADA", caso=caso1, asignado=encargada_ana, fecha_emision=now - timedelta(days=18), fecha_completacion=now - timedelta(days=15))
    
    Accion(descripcion_corta="Reordenamiento de puestos en aula", descripcion_extendida="A raíz de la reunión con apoderados, reubicar a Mateo y Lucas en extremos opuestos de la sala.", resultado="Estudiantes reubicados exitosamente.", estado="COMPLETADA", caso=caso1, asignado=reportador_luis, fecha_emision=now - timedelta(days=15), fecha_completacion=now - timedelta(days=14))
    Accion(descripcion_corta="Bitácora conductual semanal", descripcion_extendida="Monitorear e informar los días viernes si persisten las provocaciones.", resultado="", estado="PENDIENTE", caso=caso1, asignado=reportador_luis, fecha_emision=now - timedelta(days=14))


    # --- CASO 2: Ciberacoso (Martina y Florencia) ---
    c2_ant1 = Incidente(
        descripcion_corta="Mensajes ofensivos en WhatsApp", descripcion_extendida="La alumna Florencia me exhibió evidencia digital donde Martina levanta calumnias graves sobre ella en un grupo escolar.", respuesta_inmediata="Contención a la alumna en la sala de profesores y captura de pantallas.", categoria="Ciberacoso",
        estudiantes=[est_dict["Martina"], est_dict["Florencia"]], creador=reportador_luis, fecha_adicion=now - timedelta(days=40)
    )
    c2_ant2 = Observacion(
        descripcion_corta="Aislamiento posterior al incidente", descripcion_extendida="Monitoreo en patios revela que el grupo curso marginó por completo a Martina tras la filtración del chat.",
        estudiantes=[est_dict["Martina"]], creador=encargada_ana, fecha_adicion=now - timedelta(days=35)
    )
    caso2 = Caso(nombre="Ciberacoso y Aislamiento - WhatsApp", encargado=encargada_ana, estado="RESUELTO", fecha_creacion=now - timedelta(days=39))
    caso2.evidencias.extend([c2_ant1, c2_ant2])

    Accion(descripcion_corta="Charla de concientización digital", descripcion_extendida="Intervención grupal sobre los impactos del ciberacoso.", resultado="Curso reflexiona positivamente.", estado="COMPLETADA", caso=caso2, asignado=encargada_ana, fecha_emision=now - timedelta(days=38), fecha_completacion=now - timedelta(days=30))


    # --- CASO 3: Alerta Salud Mental (Sofía) ---
    c3_ant1 = Incidente(
        descripcion_corta="Discusión descontrolada en evaluación", descripcion_extendida="Sofía sufrió un colapso nervioso gritando insultos al aire y manifestando frustración severa durante la prueba escrita.", respuesta_inmediata="Se detuvo su evaluación y la acompañé al área médica por resguardo.", categoria="Verbal",
        estudiantes=[est_dict["Sofía"]], creador=reportador_luis, fecha_adicion=now - timedelta(days=15)
    )
    c3_ant2 = Observacion(
        descripcion_corta="Análisis del historial de notas", descripcion_extendida="Se constata caída abrupta en los rendimientos globales de Sofía. Posible detonante familiar.",
        estudiantes=[est_dict["Sofía"]], creador=encargada_ana, fecha_adicion=now - timedelta(days=5)
    )
    caso3 = Caso(nombre="Alerta Salud Mental - Sofía Riquelme", encargado=encargada_ana, estado="ABIERTO", fecha_creacion=now - timedelta(days=4))
    caso3.evidencias.extend([c3_ant1, c3_ant2])

    # Acciones Caso 3 
    a3_ana = Accion(descripcion_corta="Evaluación de contención psicológica", descripcion_extendida="Entrevista en profundidad con la psicóloga del centro.", resultado="Se determina alta vulnerabilidad y necesidad de flexibilidad académica.", estado="COMPLETADA", caso=caso3, asignado=encargada_ana, fecha_emision=now - timedelta(days=3), fecha_completacion=now - timedelta(days=2))
    
    Accion(descripcion_corta="Ajuste del entorno de evaluación", descripcion_extendida="Aplicar un protocolo de evaluación adaptada para disminuir la ansiedad de Sofía.", resultado="Se administró control adaptado con éxito.", estado="COMPLETADA", caso=caso3, asignado=reportador_luis, fecha_emision=now - timedelta(days=2), fecha_completacion=now - timedelta(days=1))
    
    # 🎯 ACCIÓN PENDIENTE 1: CREADA POR ELLA MISMA (Autoasignada)
    Accion(
        descripcion_corta="Reunión de urgencia con tutor legal",
        descripcion_extendida="Citación prioritaria gestionada por mí para coordinar el apoyo psicológico externo con la madre de Sofía.",
        resultado="",
        estado="PENDIENTE", caso=caso3, asignado=encargada_ana,
        fecha_emision=now
    )


    # --- CASO 4: Disrupción Grupal (Agustín, Tomás, Vicente) ---
    c4_ant1 = Incidente(
        descripcion_corta="Uso temerario de inmobiliario", descripcion_extendida="Los alumnos rompieron el diario mural lanzando objetos contundentes dentro de la sala.", respuesta_inmediata="Registro en el libro de clases.", categoria="Físico",
        estudiantes=[est_dict["Agustín"], est_dict["Tomás"], est_dict["Vicente"]], creador=reportador_maria, fecha_adicion=now - timedelta(days=10)
    )
    c4_ant2 = Incidente(
        descripcion_corta="Gritos e insultos a profesor sustituto", descripcion_extendida="Falta de respeto masiva mediante burlas ruidosas y descalificaciones directas al docente de reemplazo.", respuesta_inmediata="Los estudiantes fueron desalojados hacia inspectoría.", categoria="Verbal",
        estudiantes=[est_dict["Agustín"], est_dict["Tomás"], est_dict["Vicente"]], creador=reportador_maria, fecha_adicion=now - timedelta(days=2)
    )
    caso4 = Caso(nombre="Disrupción Grupal Crítica - 2 Medio B", encargado=encargada_ana, estado="PENDIENTE", fecha_creacion=now - timedelta(days=1))
    caso4.evidencias.extend([c4_ant1, c4_ant2])


    # --- CASO 5: Conflicto Verbal en Casino ---
    c5_ant1 = Incidente(
        descripcion_corta="Insultos cruzados en fila de almuerzo", descripcion_extendida="Benjamín agredió verbalmente con epítetos de alto calibre a Camila tras una disputa por turnos.", respuesta_inmediata="Fueron separados por mi persona en el comedor escolar.", categoria="Verbal",
        estudiantes=[est_dict["Benjamín"], est_dict["Camila"]], creador=reportador_luis, fecha_adicion=now - timedelta(days=90)
    )
    caso5 = Caso(nombre="Altercado en el casino", encargado=encargada_ana, estado="CERRADO", fecha_creacion=now - timedelta(days=89))
    caso5.evidencias.append(c5_ant1)


    # --- CASO 6: Aislamiento (Antonia) ---
    c6_ant1 = Observacion(
        descripcion_corta="Aislamiento crónico en recreos", descripcion_extendida="Se detecta que Antonia evade todo contacto social y pasa los descansos sola de forma persistente.",
        estudiantes=[est_dict["Antonia"]], creador=encargado_roberto, fecha_adicion=now - timedelta(days=12)
    )
    caso6 = Caso(nombre="Posible aislamiento social - Antonia", encargado=encargado_roberto, estado="EN PROGRESO", fecha_creacion=now - timedelta(days=10))
    caso6.evidencias.append(c6_ant1)


    # --- CASO 7: Reincidencia Crítica (Lucas) ---
    # 🔄 REPORTE 2 MOVIDO A ANA: Descubierto por ella en una ronda inspectora sorpresa
    c7_ant1 = Incidente(
        descripcion_corta="Fumando en el baño", descripcion_extendida="Sorprendí in fraganti a Lucas utilizando un vaporizador electrónico al interior de los servicios higiénicos.", respuesta_inmediata="Decomiso inmediato del aparato y apertura directa del folio disciplinario.", categoria="Verbal", # Se asume Verbal o adecuada
        estudiantes=[est_dict["Lucas"]], creador=encargada_ana, fecha_adicion=now - timedelta(days=8)
    )
    c7_ant2 = Incidente(
        descripcion_corta="Fuga con fuerza perimetral", descripcion_extendida="El alumno forzó los accesos de la reja trasera y abandonó el colegio corriendo.", respuesta_inmediata="Activación de llamados de emergencia al apoderado de manera inmediata.", categoria="Físico",
        estudiantes=[est_dict["Lucas"]], creador=reportador_luis, fecha_adicion=now - timedelta(days=1)
    )
    caso7 = Caso(nombre="Reincidencia y Fugas - Lucas Tapia", encargado=encargada_ana, estado="ABIERTO", fecha_creacion=now)
    caso7.evidencias.extend([c7_ant1, c7_ant2])

    # Acciones Caso 7
    a7_ana = Accion(descripcion_corta="Activación de Protocolo RICE por falta gravísima", descripcion_extendida="Notificación escrita de la condicionalidad extrema de matrícula debido a fugas e insultos.", resultado="Apoderado asiste firmando de disconformidad.", estado="COMPLETADA", caso=caso7, asignado=encargada_ana, fecha_emision=now - timedelta(days=1), fecha_completacion=now)
    
    Accion(descripcion_corta="Preparación de material de estudio para suspensión", descripcion_extendida="Elaborar el dosier con las guías de estudio de matemáticas.", resultado="Guías entregadas en recepción.", estado="COMPLETADA", caso=caso7, asignado=reportador_luis, fecha_emision=now - timedelta(days=1), fecha_completacion=now)
    
    # 🎯 ACCIÓN PENDIENTE 2: DERIVADA POR OTRA PERSONA (Luis se la asigna a Ana)
    Accion(
        descripcion_corta="Firma obligatoria de última advertencia",
        descripcion_extendida="El profesor Luis solicita formalmente que la Directora Ana cite al estudiante a firmar la última acta de amonestación en presencia de la directiva escolar.",
        resultado="",
        estado="PENDIENTE", caso=caso7, asignado=encargada_ana,
        fecha_emision=now
    )


    # Guardar todo
    db.session.add_all([
        c1_ant1, c1_ant2, c1_ant3, c2_ant1, c2_ant2, c3_ant1, c3_ant2,
        c4_ant1, c4_ant2, c5_ant1, c6_ant1, c7_ant1, c7_ant2,
        caso1, caso2, caso3, caso4, caso5, caso6, caso7
    ])
    
    db.session.commit()

    print("=====================================================")
    print("🚀 ¡Base de datos re-calibrada con éxito para la Demo!")
    print("📌 RESTRICCIONES VERIFICADAS:")
    print("   - Ana Directora registró 2 incidentes directo de su autoría (Pasillo y Baño).")
    print("   - Ana Directora tiene una acción PENDIENTE autoasignada (Caso Sofía).")
    print("   - Ana Directora tiene una acción PENDIENTE derivada por el Profesor Luis (Caso Lucas).")
    print("=====================================================")