import datetime

# Función helper para imprimir DateTime's sólo hasta precisión de segundos en el frontend
def datetime_sin_miliseg(value: datetime) -> str:
    if value is None:
        return "Fecha Pendiente"
    # Asegúrate de que es un objeto datetime antes de formatear
    return value.strftime('%Y-%m-%d %H:%M:%S')