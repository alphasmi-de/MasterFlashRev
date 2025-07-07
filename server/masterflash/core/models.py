# type: ignore
from django.db import models
from django.conf import settings
from cryptography.fernet import Fernet
import json


class LinePress(models.Model):
    name = models.CharField(max_length=50)
    status = models.CharField(max_length=50)
    comments = models.TextField(null=True, blank=True)


class StatePress(models.Model):
    name = models.CharField(max_length=50)
    shift = models.CharField(max_length=50, null=True, blank=True)
    date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField(null=True, blank=True)
    total_time = models.FloatField(null=True, blank=True)
    state = models.CharField(max_length=50)
    employee_number = models.IntegerField(null=True, blank=True)
    comments = models.TextField(null=True, blank=True)
    

    class Meta:
        indexes = [
            # Índice para consultas por nombre y fecha
            models.Index(fields=["name", "date"]),
        ]


class StateTroquelado(models.Model):
    name = models.CharField(max_length=50)
    shift = models.CharField(max_length=50, null=True, blank=True)
    date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField(null=True, blank=True)
    total_time = models.FloatField(null=True, blank=True)
    state = models.CharField(max_length=50)
    employee_number = models.IntegerField(null=True, blank=True)
    comments = models.TextField(null=True, blank=True)


class StateBarwell(models.Model):
    name = models.CharField(max_length=50)
    shift = models.CharField(max_length=50, null=True, blank=True)
    date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField(null=True, blank=True)
    total_time = models.FloatField(null=True, blank=True)
    state = models.CharField(max_length=50)
    employee_number = models.IntegerField(null=True, blank=True)
    comments = models.TextField(null=True, blank=True)


class WorkedHours(models.Model):
    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["press"],
                condition=models.Q(end_time__isnull=True),
                name="Unique_open_worked_hours_per_press",
            )
        ]

    press = models.CharField(default=None, max_length=50)
    start_time = models.DateTimeField(null=True, blank=True)
    end_time = models.DateTimeField(null=True, blank=True)

    @property
    def duration(self):
        """Calcula la duración(horas trabajadas) si se tiene hora de inicio y fin"""
        if self.start_time and self.end_time:
            return self.end_time - self.start_time
        return None


class ProductionPress(models.Model):
    press = models.CharField(default=None, max_length=50)
    date_time = models.DateTimeField()
    employee_number = models.IntegerField(null=True, blank=True)
    pieces_ok = models.IntegerField(null=True, blank=True)
    pieces_scrap = models.IntegerField(null=True, blank=True)
    pieces_rework = models.IntegerField(null=True, blank=True)
    part_number = models.CharField(max_length=50, blank=True)
    work_order = models.CharField(max_length=50, blank=True)
    pieces_order = models.IntegerField(null=True, blank=True)
    shift = models.CharField(default="", max_length=50)
    molder_number = models.IntegerField(default=None, null=True, blank=True)
    relay = models.BooleanField(default=False)
    caliber = models.FloatField(null=True, blank=True)

    worked_hours = models.ForeignKey(
        WorkedHours,
        #! si se borra un workedHours, se borran TODAS las producciones asociadas
        on_delete=models.CASCADE,
        related_name="productions",
        blank=True,
        null=True,
    )

    class Meta:
        indexes = [
            # Índice para consultas por prensa y fecha
            models.Index(fields=["press", "date_time"]),
            # Índice para consultas por turno
            models.Index(fields=["shift"]),
            # Índice para consultas por número de parte
            models.Index(fields=["part_number"]),
        ]


class Insert(models.Model):
    insert = models.CharField(max_length=50, blank=True, null=True)
    chemlok = models.FloatField(null=True, blank=True)
    weight = models.FloatField(null=True, blank=True)
    caliber = models.FloatField(null=True, blank=True)

    def to_dict(self):
        return {
            "id": self.id,
            "insert": self.insert,
            "caliber": self.caliber,
            "weight": self.weight,
            "chemlok": self.chemlok,
        }


def upload_path(filename):
    return "/".join(["images"], filename)


class Part_Number(models.Model):
    part_number = models.CharField(max_length=50, blank=True, null=True)
    client = models.CharField(max_length=50, blank=True, null=True)
    box = models.CharField(max_length=50, blank=True, null=True)
    pieces_x_box = models.IntegerField(null=True, blank=True)
    rubber_compound = models.CharField(max_length=50, blank=True, null=True)
    price = models.FloatField(null=True, blank=True)
    standard = models.IntegerField(null=True, blank=True)
    pallet = models.CharField(max_length=50, blank=True, null=True)
    box_x_pallet = models.IntegerField(null=True, blank=True)
    pieces_x_pallet = models.IntegerField(null=True, blank=True)
    assembly = models.CharField(max_length=50, blank=True, null=True)
    accessories = models.CharField(max_length=50, blank=True, null=True)
    mold = models.CharField(max_length=50, blank=True, null=True)
    instructive = models.CharField(max_length=50, blank=True, null=True)
    insert = models.CharField(max_length=50, blank=True, null=True)
    gripper = models.CharField(max_length=50, blank=True, null=True)
    caliber = models.CharField(max_length=50, blank=True, null=True)
    paint = models.CharField(max_length=50, blank=True, null=True)
    std_paint = models.IntegerField(null=True, blank=True)
    painter = models.FloatField(null=True, blank=True)
    scrap = models.FloatField(null=True, blank=True)
    box_logo = models.CharField(max_length=50, blank=True, null=True)
    cavities = models.IntegerField(null=True, blank=True)
    category = models.CharField(max_length=50, blank=True, null=True)
    type2 = models.CharField(max_length=50, blank=True, null=True)
    measurement = models.CharField(max_length=50, blank=True, null=True)
    special = models.CharField(max_length=50, blank=True, null=True)
    piece_label = models.CharField(max_length=50, blank=True, null=True)
    qty_piece_labels = models.IntegerField(null=True, blank=True)
    box_label = models.CharField(max_length=20, blank=True, null=True)
    qty_box_labels = models.IntegerField(null=True, blank=True)
    box_label_2 = models.CharField(max_length=20, blank=True, null=True)
    qty_box_labels_2 = models.IntegerField(null=True, blank=True)
    box_label_3 = models.CharField(max_length=20, blank=True, null=True)
    qty_box_labels_3 = models.IntegerField(null=True, blank=True)
    made_in_mexico = models.CharField(max_length=50, blank=True, null=True)
    staples = models.CharField(max_length=50, blank=True, null=True)
    image_piece_label = models.ImageField(upload_to=upload_path, null=True, blank=True)
    image_box_label = models.ImageField(upload_to=upload_path, null=True, blank=True)
    image_box_label_2 = models.ImageField(upload_to=upload_path, null=True, blank=True)
    image_box_label_3 = models.ImageField(upload_to=upload_path, null=True, blank=True)


class Qc_Scrap(models.Model):
    date_time = models.DateTimeField()
    shift = models.CharField(max_length=50, blank=True, null=True)
    line = models.CharField(max_length=50, blank=True, null=True)
    auditor_qc = models.IntegerField(null=True, blank=True)
    molder_number = models.IntegerField(null=True, blank=True)
    part_number = models.CharField(max_length=50, blank=True, null=True)
    compound = models.CharField(max_length=50, blank=True, null=True)
    mold = models.CharField(max_length=50, blank=True, null=True)
    insert = models.CharField(max_length=50, blank=True, null=True)
    gripper = models.CharField(max_length=50, blank=True, null=True)
    caliber = models.CharField(max_length=50, blank=True, null=True)
    B = models.IntegerField(null=True, blank=True)
    CC = models.IntegerField(null=True, blank=True)
    CD = models.IntegerField(null=True, blank=True)
    CH = models.IntegerField(null=True, blank=True)
    CM = models.IntegerField(null=True, blank=True)
    CMB = models.IntegerField(null=True, blank=True)
    CR = models.IntegerField(null=True, blank=True)
    CROP = models.IntegerField(null=True, blank=True)
    CS = models.IntegerField(null=True, blank=True)
    D = models.IntegerField(null=True, blank=True)
    DI = models.IntegerField(null=True, blank=True)
    DP = models.IntegerField(null=True, blank=True)
    F = models.IntegerField(null=True, blank=True)
    FC = models.IntegerField(null=True, blank=True)
    FPM = models.IntegerField(null=True, blank=True)
    FPO = models.IntegerField(null=True, blank=True)
    GA = models.IntegerField(null=True, blank=True)
    GM = models.IntegerField(null=True, blank=True)
    H = models.IntegerField(null=True, blank=True)
    _ID = models.IntegerField(null=True, blank=True)
    IM = models.IntegerField(null=True, blank=True)
    IMC = models.IntegerField(null=True, blank=True)
    IP = models.IntegerField(null=True, blank=True)
    IR = models.IntegerField(null=True, blank=True)
    M = models.IntegerField(null=True, blank=True)
    MR = models.IntegerField(null=True, blank=True)
    O = models.IntegerField(null=True, blank=True)
    PD = models.IntegerField(null=True, blank=True)
    PR = models.IntegerField(null=True, blank=True)
    Q = models.IntegerField(null=True, blank=True)
    R = models.IntegerField(null=True, blank=True)
    RC = models.IntegerField(null=True, blank=True)
    RPM = models.IntegerField(null=True, blank=True)
    SG = models.IntegerField(null=True, blank=True)
    SI = models.IntegerField(null=True, blank=True)
    SL = models.IntegerField(null=True, blank=True)
    SR = models.IntegerField(null=True, blank=True)
    total_pieces = models.IntegerField(null=True, blank=True)
    rubber_weight = models.FloatField(null=True, blank=True)
    insert_weight_wout_rubber = models.FloatField(null=True, blank=True)
    gripper_weight_wout_rubber = models.FloatField(null=True, blank=True)
    insert_weight_w_rubber = models.FloatField(null=True, blank=True)
    chemlok_x_insert_w_rubber = models.FloatField(null=True, blank=True)
    gripper_weight_w_rubber = models.FloatField(null=True, blank=True)
    recycled_inserts = models.IntegerField(null=True, blank=True)
    total_bodies_weight = models.FloatField(null=True, blank=True)
    total_inserts_weight = models.FloatField(null=True, blank=True)
    total_grippers_weight = models.FloatField(null=True, blank=True)
    total_rubber_weight_in_insert = models.FloatField(null=True, blank=True)
    total_rubber_weight_in_gripper = models.FloatField(null=True, blank=True)
    total_rubber_weight = models.FloatField(null=True, blank=True)
    total_bodies_weight_lbs = models.FloatField(null=True, blank=True)
    total_inserts_weight_lbs = models.FloatField(null=True, blank=True)
    total_grippers_weight_lbs = models.FloatField(null=True, blank=True)
    total_rubber_weight_in_insert_lbs = models.FloatField(null=True, blank=True)
    total_rubber_weight_in_gripper_lbs = models.FloatField(null=True, blank=True)
    total_rubber_weight_lbs = models.FloatField(null=True, blank=True)
    inserts_total = models.IntegerField(null=True, blank=True)
    grippers_total = models.IntegerField(null=True, blank=True)


class Mold_presses(models.Model):
    press = models.CharField(max_length=50, blank=True, null=True)
    mold = models.CharField(max_length=50, blank=True, null=True)


class Presses_monthly_goals(models.Model):
    month = models.IntegerField()
    year = models.IntegerField()
    target_amount = models.IntegerField()

    def __str__(self):
        return f"{self.month}/{self.year} - {self.target_amount}"


class Production_records(models.Model):
    press = models.CharField(default=None, max_length=50)
    employee_number = models.IntegerField(null=True, blank=True)
    part_number = models.CharField(max_length=50, blank=True)
    work_order = models.CharField(max_length=50, blank=True)
    caliber = models.CharField(max_length=50, blank=True, null=True)
    worked_hrs = models.DecimalField(
        max_digits=5, decimal_places=2, null=True, blank=True
    )
    dead_time_cause_1 = models.CharField(max_length=50, null=True, blank=True)
    cavities = models.PositiveIntegerField(null=True, blank=True)
    standard = models.IntegerField(null=True, blank=True)
    proposed_standard = models.PositiveIntegerField(null=True, blank=True)
    dead_time_cause_2 = models.CharField(max_length=50, null=True, blank=True)
    pieces_ok = models.PositiveIntegerField(null=True, blank=True)
    efficiency = models.DecimalField(max_digits=5, decimal_places=2)
    date = models.DateField()
    shift = models.CharField(default="", max_length=50)
    mod_date = models.DateTimeField()

    def __str__(self) -> str:
        return f"{self.press} - {self.employee_number} - {self.part_number}"

    class Meta:
        verbose_name = "Production Record"
        verbose_name_plural = "Production Records"


class Rubber_Query_history(models.Model):
    query_date = models.DateTimeField()
    start_date = models.DateField()
    end_date = models.DateField()
    compound = models.CharField(max_length=100)
    total_weight = models.FloatField()
    comments = models.CharField(max_length=50, null=True)

    def __str__(self) -> str:
        return f"{self.query_date} - {self.compound}"


class Insert_Query_history(models.Model):
    query_date = models.DateTimeField()
    start_date = models.DateField()
    end_date = models.DateField()
    insert = models.CharField(max_length=50, null=True)
    total_chemlok = models.FloatField(default=0)
    total_insert = models.FloatField(default=0)
    total_rubber = models.FloatField(default=0)
    total_metal = models.FloatField(default=0)
    total_sum = models.FloatField(default=0)

    def __str__(self) -> str:
        return f"{self.query_date} - {self.compound}"


class ShiftSchedule(models.Model):
    first_shift_start = models.TimeField(default="05:00")
    first_shift_end = models.TimeField(default="16:35")
    second_shift_start = models.TimeField(default="16:36")
    second_shift_end = models.TimeField(default="01:20")

    def __str__(self):
        return f"Shift Schedule: first shift from {self.first_shift_start} until {self.first_shift_end}, second shift from {self.second_shift_start} until {self.second_shift_end}"


class Params(models.Model):
    partnum = models.CharField(max_length=100)
    auditor = models.IntegerField()
    shift = models.CharField(max_length=50, null=True, blank=True)
    mp = models.CharField(max_length=100)
    molder = models.IntegerField()
    icc = models.BooleanField()
    register_date = models.DateTimeField()
    mold = models.CharField(max_length=100)
    cavities = models.IntegerField()
    metal = models.CharField(max_length=50, null=True)
    body = models.FloatField()
    strips = models.FloatField()
    full_cycle = models.FloatField()
    cycle_time = models.FloatField(default=0)
    screen_superior = models.FloatField(default=0)
    screen_inferior = models.FloatField(default=0)
    mold_superior = models.FloatField(default=0)
    mold_inferior = models.FloatField(default=0)
    platen_superior = models.FloatField(default=0)
    platen_inferior = models.FloatField(default=0)
    pressure = models.FloatField()
    waste_pct = models.FloatField()
    batch = models.CharField(max_length=100)
    julian = models.FloatField(null=True, blank=True)
    ts2 = models.FloatField(null=True, blank=True)
    cavities_arr = models.JSONField()

    def __str__(self):
        return f"Params for {self.partnum} - {self.mold}"

    def to_dict(self):
        return {
            "general_info": {
                "Máquina": self.mp,
                "Fecha": self.register_date,
                "Turno": self.shift,
                "Número de Parte": self.partnum,
                "Auditor": self.auditor,
                "Moldeador": self.molder,
                "No. Cavidades": self.cavities,
                "icc": "Sí" if self.icc else "No",
            },
            "parameters": {
                "Molde": self.mold,
                "Metal": self.metal,
                "Cuerpo": self.body,
                "Tiras": self.strips,
                "Ciclo completo": self.full_cycle,
                "Tiempo de ciclo": self.cycle_time,
                "Presión": self.pressure,
                "Porcentaje de waste": self.waste_pct,
            },
            "temperature": {
                "labels": [
                    "Pantalla superior",
                    "Pantalla inferior",
                    "Molde superior",
                    "Molde inferior",
                    "Platina superior",
                    "Platina inferior",
                ],
                "values": [
                    self.screen_superior,
                    self.screen_inferior,
                    self.mold_superior,
                    self.mold_inferior,
                    self.platen_superior,
                    self.platen_inferior,
                ],
            },
            "batch_info": {
                "Batch": self.batch,
                "Julian": self.julian,
                "ts2": self.ts2,
            },
            "cavities_arr": self.cavities_arr,
        }


SECRET_KEY = settings.SECRET_KEY_EMAIL_ENCRYPTION


class EmailConfig(models.Model):
    sender_email = models.EmailField()
    sender_username = models.CharField(max_length=128)
    sender_password = models.CharField(max_length=128)
    recipients = models.TextField()
    smtp_host = models.CharField(max_length=255, default="smtp.gmail.com")
    smtp_port = models.PositiveIntegerField(default=587)
    use_tls = models.BooleanField(default=True)

    def set_password(self, password: str):
        fernet = Fernet(SECRET_KEY)
        self.sender_password = fernet.encrypt(password.encode()).decode()

    def get_password(self):
        fernet = Fernet(SECRET_KEY)
        return fernet.decrypt(self.sender_password.encode()).decode()

    def get_recipients_list(self):
        """Convierte la cadena JSON en una lista de correos."""
        try:
            return json.loads(self.recipients)
        except json.JSONDecodeError:
            return []

    def set_recipients_list(self, recipient_list):
        """Convierte una lista de correos a JSON."""
        self.recipients = json.dumps(recipient_list)

    def save(self, *args, **kwargs):
        """Garantiza que solo exista un único registro."""
        if not self.pk and EmailConfig.objects.exists():
            raise Exception("Solo puede existir una configuración de correo")
        super().save(*args, **kwargs)
