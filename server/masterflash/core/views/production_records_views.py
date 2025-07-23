from datetime import datetime
from django.utils.dateparse import parse_datetime
import json
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import  require_POST
from django.http import JsonResponse
from ..models import Production_records


@csrf_exempt
@require_POST
def save_production_records(request):
    try:
        data = json.loads(request.body)
        date = data["date"]
        shift = data["shift"]
        records = data["records"]
        overwrite = data.get("overwrite", False)

        # Verifica si ya existen registros para la misma fecha y turno
        # Nota: Aquí no usamos get_shift_date_filter porque Production_records
        # tiene un campo date explícito, no date_time como ProductionPress
        existing_records = Production_records.objects.filter(date=date, shift=shift)

        if existing_records.exists() and not overwrite:
            return JsonResponse(
                {
                    "status": "exists",
                    "message": "Ya existen registros para la fecha y turno seleccionados. ¿Desea sobrescribirlos?",
                },
                status=200,
            )

        if overwrite:
            # Elimina los registros anteriores si se decide sobrescribir
            existing_records.delete()

        # Crea nuevos registros
        for record in records:
            Production_records.objects.create(
                press=record["press"],
                employee_number=record["employee_number"],
                part_number=record["part_number"],
                work_order=record["work_order"],
                caliber=record["caliber"],
                worked_hrs=record["worked_hrs"],
                dead_time_cause_1=record["dead_time_cause_1"],
                cavities=record["cavities"],
                standard=record["standard"],
                proposed_standard=record["proposed_standard"],
                dead_time_cause_2=record["dead_time_cause_2"],
                pieces_ok=record["pieces_ok"],
                efficiency=record["efficiency"],
                date=date,
                shift=shift,
                mod_date=datetime.now(),
            )

        return JsonResponse({"status": "success"}, status=200)

    except Exception as e:
        return JsonResponse({"status": "error", "message": str(e)}, status=400)

@csrf_exempt
@require_POST
def get_pieces_ok_by_date_range(request):
    try:
        data = json.loads(request.body)
        start_date = parse_datetime(data.get("start_date"))
        end_date = parse_datetime(data.get("end_date"))

        if not start_date or not end_date:
            return JsonResponse(
                {"error": "start_date and end_date are required"}, status=400
            )

        records = Production_records.objects.filter(date__range=(start_date, end_date))

        # Serializa los datos
        response_data = [
            {
                "id": record.id,
                "press": record.press,
                "employee_number": record.employee_number,
                "part_number": record.part_number,
                "work_order": record.work_order,
                "caliber": record.caliber,
                "worked_hrs": float(record.worked_hrs)
                if record.worked_hrs is not None
                else None,
                "dead_time_cause_1": record.dead_time_cause_1,
                "cavities": record.cavities,
                "standard": record.standard,
                "proposed_standard": record.proposed_standard,
                "dead_time_cause_2": record.dead_time_cause_2,
                "pieces_ok": record.pieces_ok,
                "efficiency": float(record.efficiency),
                "date": record.date,
                "shift": record.shift,
                "mod_date": record.mod_date,
            }
            for record in records
        ]

        return JsonResponse(response_data, safe=False)

    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON"}, status=400)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)


@csrf_exempt
def get_record_by_id(request, id):
    try:
        record = Production_records.objects.filter(id=id).values().first()

        if record is None:
            return JsonResponse({"error": "Record not found"}, status=404)

        return JsonResponse(record, status=200)

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)
