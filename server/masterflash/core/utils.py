from datetime import time, datetime, timedelta
from django.conf import settings
from django.db.models import Q, Sum, Max
import redis

from masterflash.core.models import (
    LinePress,
    ProductionPress,
    ShiftSchedule,
    StatePress,
    WorkedHours,
)

from datetime import datetime, time, timedelta

def get_shift(current_time: time) -> str:
    """
    Determina el nombre del turno basado en la hora actual (`current_time`).
    
    Utiliza el horario almacenado en la base de datos (`ShiftSchedule` con `id=1`).
    Soporta correctamente turnos que cruzan la medianoche (por ejemplo, de 16:30 a 01:20).

    Retorna:
        - "First"  → si la hora está dentro del primer turno
        - "Second" → si está dentro del segundo turno (aunque cruce la medianoche)
        - "Free"   → si no pertenece a ningún turno definido
    """

    try:
        # Se obtiene el registro de turnos (solo se espera uno configurado con id=1).
        schedule = ShiftSchedule.objects.get(id=1)
    except ShiftSchedule.DoesNotExist:
        # Si no existe configuración, retorna "Free" como valor por defecto.
        return "Free"

    # Extrae los horarios de inicio y fin para ambos turnos desde el modelo.
    first_start = schedule.first_shift_start       # Ej. 07:00
    first_end = schedule.first_shift_end           # Ej. 16:25

    second_start = schedule.second_shift_start     # Ej. 16:30
    second_end = schedule.second_shift_end         # Ej. 01:20

    # -----------------------------
    # Lógica para el primer turno
    # -----------------------------
    # Si la hora actual está entre el inicio y el fin del primer turno, retorna "First".
    if first_start <= current_time <= first_end:
        return "First"

    # -----------------------------
    # Lógica para el segundo turno
    # -----------------------------

    # Verifica si el segundo turno NO cruza la medianoche.
    # Ejemplo: 16:30 a 23:59
    if second_start <= second_end:
        # Si la hora actual está dentro del rango simple, pertenece al segundo turno.
        if second_start <= current_time <= second_end:
            return "Second"
    else:
        # El turno cruza la medianoche. Ejemplo: 16:30 a 01:20
        # En este caso, la hora actual puede estar después de `second_start` (hoy)
        # o antes de `second_end` (mañana), y aun así seguir siendo el mismo turno.
        if current_time >= second_start or current_time <= second_end:
            return "Second"

    # -----------------------------
    # Si no entra en ningún turno definido, se considera "Libre"
    # -----------------------------
    return "Free"




def get_shift_date_filter(shift: str, query_date):
    """
    Retorna filtros para date_time basados en el turno solicitado y la fecha.
    Controla:
      - Validaciones de entrada
      - Turnos que cruzan la medianoche
      - Turnos mal configurados
      - Casos extremos como horarios iguales
    """

    # Validación inicial
    if not shift or not query_date:
        raise ValueError("Se requieren ambos valores: shift y query_date")

    # Validación de tipo
    if not isinstance(query_date, datetime) and not isinstance(query_date, (datetime, type(datetime.now().date()))):
        raise ValueError("query_date debe ser una fecha o datetime válida")

    if shift not in ["First", "Second"]:
        raise ValueError(f"Shift '{shift}' no es válido. Usa 'First' o 'Second'.")

    # Obtener horario
    schedule = ShiftSchedule.objects.first()
    if not schedule:
        raise ValueError("No existe ninguna configuración de turnos en la base de datos.")

    try:
        # Turno 1
        if shift == "First":
            start_time = schedule.first_shift_start
            end_time = schedule.first_shift_end

            if not start_time or not end_time:
                raise ValueError("Horario incompleto para el primer turno.")

            if start_time == end_time:
                raise ValueError("El horario del primer turno no puede tener misma hora de inicio y fin.")

            start_datetime = datetime.combine(query_date, start_time)
            end_datetime = datetime.combine(query_date, end_time)

            if end_datetime <= start_datetime:
                # Error lógico
                raise ValueError("La hora de fin del primer turno debe ser después de la hora de inicio.")

            return Q(date_time__gte=start_datetime, date_time__lt=end_datetime), Q()

        # Turno 2
        elif shift == "Second":
            start_time = schedule.second_shift_start
            end_time = schedule.second_shift_end

            if not start_time or not end_time:
                raise ValueError("Horario incompleto para el segundo turno.")

            if start_time == end_time:
                raise ValueError("El horario del segundo turno no puede tener misma hora de inicio y fin.")

            # Turno cruza la medianoche
            if end_time < start_time:
                start_datetime = datetime.combine(query_date, start_time)
                end_datetime = datetime.combine(query_date + timedelta(days=1), end_time)
            else:
                # Turno dentro del mismo día
                start_datetime = datetime.combine(query_date, start_time)
                end_datetime = datetime.combine(query_date, end_time)

            if end_datetime <= start_datetime:
                raise ValueError("El rango de tiempo del segundo turno no es válido.")

            return Q(date_time__gte=start_datetime, date_time__lt=end_datetime), Q()

    except Exception as e:
        raise ValueError(f"Error al construir el filtro para el turno '{shift}': {str(e)}")



def get_shift_production(shift: str, part_number: str = None, work_order: str = None):
    """
    Obtiene la producción total para un turno completo, independientemente de la fecha.
    
    Args:
        shift: El turno a consultar ("First" o "Second")
        part_number: Filtrar por número de parte (opcional)
        work_order: Filtrar por orden de trabajo (opcional)
        
    Returns:
        Dict con totales de piezas OK y piezas para retrabajo
    """
    # Construir el filtro base por turno
    query = Q(shift=shift)
    
    # Aplicar filtros adicionales si se proporcionan
    if part_number:
        query &= Q(part_number=part_number)
    if work_order:
        query &= Q(work_order=work_order)
    
    # Obtener la suma de piezas
    result = ProductionPress.objects.filter(query).aggregate(
        total_ok=Sum('pieces_ok'),
        total_rework=Sum('pieces_rework')
    )
    
    return {
        'total_ok': result['total_ok'] or 0,
        'total_rework': result['total_rework'] or 0
    }


def sum_pieces(machine: LinePress, shift: str, current_date) -> int:
    """
    Suma las piezas producidas para una máquina, turno y fecha dados,
    tomando como referencia el último registro de producción para determinar
    el part_number y work_order. Si no hay registros o el turno no es válido, retorna 0.
    """
    # Obtener el último registro de producción para la máquina.
    last_record = (
        ProductionPress.objects.filter(press=machine.name)
        .order_by("-date_time")
        .values("part_number", "work_order")
        .first()
    )
    if not last_record:
        return 0

    # Obtener los filtros de fecha y turno
    date_filter, shift_filter = get_shift_date_filter(shift, current_date)

    # Filtrar y agregar la suma de piezas OK
    result = (
        ProductionPress.objects.filter(
            press=machine.name,
            shift=shift,
            part_number=last_record["part_number"],
            work_order=last_record["work_order"],
        )
        .filter(date_filter)
        .filter(shift_filter)
        .aggregate(total_pieces=Sum("pieces_ok"))
    )

    return result["total_pieces"] or 0


def send_production_data():
    """
    Recopila y envía datos de producción de las máquinas disponibles en la planta.

    Retorna:
        dict: Datos de producción de las máquinas y estadísticas generales.
    """
    print("Sending production data...")
    now = datetime.now()
    current_date = now.date()
    current_time = now.time()
    shift = get_shift(current_time)

    # Obtener todas las máquinas disponibles
    machines = list(LinePress.objects.filter(status="Available"))
    machine_names = [machine.name for machine in machines]

    # Obtener los estados de las máquinas
    states_dict = {
        s["name"]: s["state"] for s in StatePress.objects.all().values("name", "state")
    }

    # Obtener la última fecha de producción de cada máquina
    latest_dates = (
        ProductionPress.objects.filter(press__in=machine_names)
        .values("press")
        .annotate(max_date=Max("date_time"))
    )

    # Diccionario con la última producción de cada máquina
    latest_prod_dict = {}
    for item in latest_dates:
        prod = ProductionPress.objects.filter(
            press=item["press"], date_time=item["max_date"]
        ).first()
        if prod:
            latest_prod_dict[item["press"]] = prod

    # Obtener las últimas horas trabajadas para cada máquina
    latest_hours = (
        WorkedHours.objects.filter(
            press__in=machine_names,
            end_time__isnull=True,
            start_time__date=current_date,
            start_time__lte=now,
        )
        .values("press")
        .annotate(max_start_time=Max("start_time"))
    )

    worked_hours_dict = {}
    for item in latest_hours:
        wh = WorkedHours.objects.filter(
            press=item["press"], start_time=item["max_start_time"]
        ).first()
        if wh:
            worked_hours_dict[item["press"]] = wh

    # Obtener los filtros de fecha y turno usando la función auxiliar
    date_filter, shift_filter = get_shift_date_filter(shift, current_date)

    # Obtener la producción total del turno actual
    shift_productions = (
        ProductionPress.objects.filter(shift=shift)
        .filter(date_filter)
        .filter(shift_filter)
        .values("press")
        .annotate(total_ok=Sum("pieces_ok"), total_rework=Sum("pieces_rework"))
    )

    shift_data = {item["press"]: item for item in shift_productions}

    # Conexión a Redis para obtener los números de molde previos
    redis_client = redis.StrictRedis(
        host=settings.REDIS_HOST, port=settings.REDIS_PORT, db=0
    )
    molder_keys = [f"previous_molder_number_{machine.name}" for machine in machines]
    previous_molders = redis_client.mget(molder_keys)

    molder_dict = {
        machine.name: val.decode("utf-8") if val else "----"
        for machine, val in zip(machines, previous_molders)
    }

    machines_data = []
    total_piecesProduced = 0

    # Obtener el total de piezas producidas en el mes actual
    total_pieces = (
        ProductionPress.objects.filter(
            date_time__year=current_date.year, date_time__month=current_date.month
        ).aggregate(total=Sum("pieces_ok"))["total"]
        or 0
    )

    for machine in machines:
        latest_production = latest_prod_dict.get(machine.name)

        # Determinar si hay un número de parte registrado
        if (
            latest_production
            and latest_production.worked_hours
            and latest_production.worked_hours.end_time
            and not latest_production.relay
        ):
            part_number = "----"
        else:
            part_number = getattr(latest_production, "part_number", "--------")

        employeeNumber = getattr(latest_production, "employee_number", "----")
        workOrder = getattr(latest_production, "work_order", "")
        molder_number = getattr(latest_production, "molder_number", "----")
        caliber = getattr(latest_production, "caliber", "----")
        pieces_order = getattr(latest_production, "pieces_order", 0)

        # Obtener las horas trabajadas
        worked_hours_entry = worked_hours_dict.get(machine.name)
        start_time = worked_hours_entry.start_time if worked_hours_entry else None

        # Obtener datos de producción del turno actual
        shift_info = shift_data.get(machine.name, {})
        total_ok = shift_info.get("total_ok", 0)
        total_rework = shift_info.get("total_rework", 0)
        actual_ok = sum_pieces(machine, shift, current_date) if shift else 0

        # Obtener el estado de la máquina
        machine_state = states_dict.get(machine.name, "Inactive")

        previous_molder_number = molder_dict.get(machine.name, "----")
        final_molder_number = (
            previous_molder_number
            if previous_molder_number != "----"
            else molder_number
        )

        machine_data = {
            "name": machine.name,
            "state": machine_state,
            "employee_number": employeeNumber,
            "pieces_ok": actual_ok,
            "pieces_rework": total_rework,
            "part_number": part_number,
            "work_order": workOrder,
            "pieces_order": pieces_order,
            "total_ok": total_ok,
            "molder_number": final_molder_number,
            "previous_molder_number": previous_molder_number,
            "caliber": caliber,
            "start_time": start_time.isoformat() if start_time else None,
            "worked_hours_id": worked_hours_entry.pk if worked_hours_entry else None,
        }
        total_piecesProduced += total_ok
        machines_data.append(machine_data)

    response_data = {
        "machines_data": machines_data,
        "total_piecesProduced": total_piecesProduced,
        "actual_produced": total_pieces,
    }

    return response_data
