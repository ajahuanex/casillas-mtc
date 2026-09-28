"""
Motor de Cómputo de Plazos Legales y Notificaciones Electrónicas.
Basado estrictamente en:
- TUO de la Ley N° 27444 - Ley del Procedimiento Administrativo General (LPAG), Arts. 20, 25, 143 y 145.
- Decreto Supremo N° 001-2020-MTC (Reglamento del Sistema de Casilla Electrónica del MTC) y modificatorias (Art. 11).
- Calendario Oficial de Días Inhábiles del Estado Peruano y Región Puno.
"""

from datetime import datetime, date, time, timedelta, timezone
from typing import Set, Tuple, Dict, Any, Optional

# Feriados Nacionales de Perú (Año 2026) y Feriados Cívico-Regionales de Puno
FERIADOS_PERU_2026: Set[date] = {
    date(2026, 1, 1),    # Año Nuevo
    date(2026, 4, 2),    # Jueves Santo
    date(2026, 4, 3),    # Viernes Santo
    date(2026, 5, 1),    # Día del Trabajo
    date(2026, 6, 7),    # Día de la Bandera
    date(2026, 6, 29),   # San Pedro y San Pablo
    date(2026, 7, 23),   # Día de la Fuerza Aérea
    date(2026, 7, 28),   # Fiestas Patrias
    date(2026, 7, 29),   # Fiestas Patrias
    date(2026, 8, 6),    # Batalla de Junín
    date(2026, 8, 30),   # Santa Rosa de Lima
    date(2026, 10, 8),   # Combate de Angamos
    date(2026, 11, 1),   # Día de Todos los Santos
    date(2026, 11, 4),   # Aniversario de la Ciudad de Puno (Feriado no laborable regional)
    date(2026, 12, 8),   # Inmaculada Concepción
    date(2026, 12, 9),   # Batalla de Ayacucho
    date(2026, 12, 25),  # Navidad
}


def es_dia_habil(d: date) -> bool:
    """
    Determina si una fecha es día hábil administrativo.
    Excluye sábados (weekday 5), domingos (weekday 6) y feriados oficiales.
    """
    if d.weekday() >= 5:
        return False
    if d in FERIADOS_PERU_2026:
        return False
    return True


def siguiente_dia_habil(d: date) -> date:
    """Retorna el primer día hábil estrictamente posterior a la fecha dada."""
    curr = d + timedelta(days=1)
    while not es_dia_habil(curr):
        curr += timedelta(days=1)
    return curr


def sumar_dias_habiles(fecha_inicio: date, dias_habiles: int) -> date:
    """
    Suma 'dias_habiles' consecutivos excluyendo sábados, domingos y feriados.
    """
    if dias_habiles <= 0:
        return fecha_inicio
    
    curr = fecha_inicio
    contados = 0
    while contados < dias_habiles:
        curr += timedelta(days=1)
        if es_dia_habil(curr):
            contados += 1
    return curr


def contar_dias_habiles_entre(fecha_desde: date, fecha_hasta: date) -> int:
    """
    Calcula la cantidad de días hábiles restantes entre dos fechas.
    Si fecha_hasta < fecha_desde, retorna un valor negativo.
    """
    if fecha_hasta < fecha_desde:
        # Contar en negativo
        curr = fecha_hasta
        dias = 0
        while curr < fecha_desde:
            if es_dia_habil(curr):
                dias += 1
            curr += timedelta(days=1)
        return -dias

    curr = fecha_desde
    dias = 0
    while curr < fecha_hasta:
        curr += timedelta(days=1)
        if es_dia_habil(curr):
            dias += 1
    return dias


def evaluar_computo_notificacion(
    fecha_deposito: datetime,
    fecha_lectura: Optional[datetime] = None,
    plazo_dias_habiles: int = 15,
    fecha_referencia: Optional[datetime] = None
) -> Dict[str, Any]:
    """
    Aplica rigurosamente la regla del Artículo 11 del D.S. N° 001-2020-MTC
    y los Artículos 25 y 145 del TUO de la Ley N° 27444.

    Reglas:
    1. Gracia de 5 días hábiles para apertura voluntaria desde el depósito.
    2. Supuesto A (Lectura anticipada):
       - Si el administrado lee dentro de los 5 días hábiles, surte efectos el día de la lectura.
       - Cómputo del plazo del acto inicia el DÍA HÁBIL SIGUIENTE a la lectura.
    3. Supuesto B (Ficción legal de notificación):
       - Si transcurren 5 días hábiles sin apertura, la notificación surte efectos el 5° día hábil a las 23:59:59.
       - Cómputo del plazo del acto inicia indefectiblemente el DÍA HÁBIL SUBSIGUIENTE (primer día hábil tras los 5 días).
    """
    if not fecha_referencia:
        fecha_referencia = datetime.now(timezone.utc)

    # Convertir a fechas (date) en zona horaria peruana (UTC-5)
    f_deposito_date = (fecha_deposito - timedelta(hours=5)).date()
    f_ref_date = (fecha_referencia - timedelta(hours=5)).date()

    # 1. Calcular el 5° día hábil de gracia desde el depósito
    # El cómputo de los 5 días de gracia inicia al día hábil siguiente del depósito
    dia_inicio_gracia = siguiente_dia_habil(f_deposito_date)
    # Sumar 4 días hábiles adicionales para completar los 5 días hábiles
    quinto_dia_habil = sumar_dias_habiles(dia_inicio_gracia, 4)
    fecha_limite_gracia_5dias = datetime.combine(quinto_dia_habil, time(23, 59, 59), tzinfo=timezone.utc)

    # 2. Determinar si hubo lectura voluntaria o aplica ficción legal
    es_lectura_voluntaria = False
    es_ficcion_legal = False
    fecha_notificacion_efectiva: Optional[datetime] = None
    tipo_eficacia: str = "PENDIENTE_LECTURA"

    if fecha_lectura:
        f_lectura_date = (fecha_lectura - timedelta(hours=5)).date()
        if f_lectura_date <= quinto_dia_habil:
            es_lectura_voluntaria = True
            fecha_notificacion_efectiva = fecha_lectura
            tipo_eficacia = "LECTURA_VOLUNTARIA"
        else:
            # Leyó después de consumada la ficción legal
            es_ficcion_legal = True
            fecha_notificacion_efectiva = fecha_limite_gracia_5dias
            tipo_eficacia = "FICCION_LEGAL_CONSUMADA"
    else:
        if f_ref_date > quinto_dia_habil:
            es_ficcion_legal = True
            fecha_notificacion_efectiva = fecha_limite_gracia_5dias
            tipo_eficacia = "FICCION_LEGAL_5_DIAS"
        else:
            # Todavía está dentro de los 5 días hábiles de gracia para abrir
            tipo_eficacia = "EN_GRACIA_LECTURA"

    # 3. Cómputo del plazo del acto administrativo si la notificación ya surtió efectos
    fecha_inicio_computo: Optional[date] = None
    fecha_vencimiento_plazo: Optional[date] = None
    dias_habiles_restantes: Optional[int] = None
    porcentaje_transcurrido: float = 0.0
    estado_plazo: str = "EN_ESPERA_LECTURA"

    if fecha_notificacion_efectiva:
        f_efectiva_date = (fecha_notificacion_efectiva - timedelta(hours=5)).date()
        # El plazo corre a partir del DÍA HÁBIL SIGUIENTE a la notificación efectiva
        fecha_inicio_computo = siguiente_dia_habil(f_efectiva_date)
        # Fecha de vencimiento: inicio + (plazo - 1) días hábiles
        fecha_vencimiento_plazo = sumar_dias_habiles(fecha_inicio_computo, max(0, plazo_dias_habiles - 1))
        
        # Días restantes
        dias_habiles_restantes = contar_dias_habiles_entre(f_ref_date, fecha_vencimiento_plazo)

        # Cálculo de porcentaje transcurrido
        dias_transcurridos = contar_dias_habiles_entre(fecha_inicio_computo, f_ref_date)
        if dias_transcurridos <= 0:
            porcentaje_transcurrido = 0.0
        elif plazo_dias_habiles > 0:
            porcentaje_transcurrido = min(100.0, round((dias_transcurridos / plazo_dias_habiles) * 100, 1))

        # Determinar semáforo de estado de plazo
        if dias_habiles_restantes < 0:
            estado_plazo = "PLAZO_FENECIDO"
        elif dias_habiles_restantes == 0:
            estado_plazo = "VENCE_HOY"
        elif dias_habiles_restantes <= 2:
            estado_plazo = "POR_VENCER_48H"
        else:
            estado_plazo = "EN_PLAZO"
    else:
        # Si aún no es notificado efectivamente, calculamos días de gracia restantes
        dias_gracia_restantes = contar_dias_habiles_entre(f_ref_date, quinto_dia_habil)
        estado_plazo = "EN_GRACIA_LECTURA"
        dias_habiles_restantes = dias_gracia_restantes

    return {
        "fecha_deposito": fecha_deposito,
        "fecha_limite_gracia_5dias": fecha_limite_gracia_5dias,
        "quinto_dia_habil": quinto_dia_habil,
        "tipo_eficacia": tipo_eficacia,
        "es_lectura_voluntaria": es_lectura_voluntaria,
        "es_ficcion_legal": es_ficcion_legal,
        "fecha_notificacion_efectiva": fecha_notificacion_efectiva,
        "fecha_inicio_computo": fecha_inicio_computo,
        "fecha_vencimiento_plazo": fecha_vencimiento_plazo,
        "plazo_dias_habiles": plazo_dias_habiles,
        "dias_habiles_restantes": dias_habiles_restantes,
        "porcentaje_transcurrido": porcentaje_transcurrido,
        "estado_plazo": estado_plazo
    }
