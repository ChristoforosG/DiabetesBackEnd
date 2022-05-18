from django.contrib import admin
from .models import (
    Reminders,
    BloodPressure,
    Meals,
    Activity,
    Weight,
    Medication,
    EmergencyMedication,
    Glucose,
    MenstrualCycle,
    MealsListInfo,
    DeviceTokenPerUser,
)
from django.contrib.admin import ModelAdmin


class BloodPressureConfig(ModelAdmin):
    ordering = ("user_id", "-measurement_date_time")
    list_filter = (
        "user_id",
        "measurement_date_time",
    )
    list_display = (
        "user_id",
        "systolic_blood_pressure",
        "diastolic_blood_pressure",
        "blood_pulse",
        "measurement_date_time",
    )


class RemindersConfig(ModelAdmin):
    ordering = ("user_id", "-reminder_date_time")
    list_filter = (
        "user_id",
        "reminder_date_time",
    )
    list_display = (
        "user_id",
        "reminder_date_time",
        "reminder_title",
        "reminder_info",
    )


class MealsConfig(ModelAdmin):
    ordering = ("user_id", "-measurement_date_time")
    list_filter = (
        "user_id",
        "measurement_date_time",
    )
    list_display = (
        "user_id",
        "meal_name",
        "meal_type",
        "calories",
        "carbs",
        "fats",
        "proteins",
        "info",
        "measurement_date_time",
    )


class ActivityConfig(ModelAdmin):
    ordering = ("user_id", "-measurement_date_time")
    list_filter = (
        "user_id",
        "measurement_date_time",
    )
    list_display = (
        "user_id",
        "activity_type",
        "duration",
        "intensity",
        "measurement_date_time",
    )


class WeightConfig(ModelAdmin):
    ordering = ("user_id", "-measurement_date_time")
    list_filter = (
        "user_id",
        "measurement_date_time",
    )
    list_display = (
        "user_id",
        "weight",
        "measurement_date_time",
    )


class MedicationConfig(ModelAdmin):
    ordering = ("user_id",)
    list_filter = ("user_id",)
    list_display = (
        "user_id",
        "category",
        "madication_name",
        "dose",
        "monday",
        "tuesday",
        "wednesday",
        "thursday",
        "friday",
        "saturday",
        "sunday",
        "dose_time",
    )


class EmergencyMedicationConfig(ModelAdmin):
    ordering = ("user_id",)
    list_filter = ("user_id",)
    list_display = (
        "user_id",
        "category",
        "madication_name",
        "dose",
        "measurement_date_time",
    )


class GlucoseConfig(ModelAdmin):
    ordering = ("user_id", "-measurement_date_time")
    list_filter = ("user_id", "measurement_date_time")
    list_display = (
        "user_id",
        "glucose_measurement",
        "glucose_type",
        "insulin_dose",
        "insulin_type",
        "hypoglycemia_carbs",
        "measurement_date_time",
    )


class MenstrualCycleConfig(ModelAdmin):
    ordering = ("user_id", "-cycle_start_date")
    list_filter = ("user_id",)
    list_display = (
        "pk",
        "user_id",
        "cycle_start_date",
        "period_end_date",
        "fertility_start_date",
        "fertility_end_date",
        "cycle_end_date",
    )


class MealsListInfoConfig(ModelAdmin):
    ordering = ("meal_name",)
    list_display = (
        "pk",
        "meal_name",
        "energy",
        "protein",
        "fat",
        "carbs",
        "fats_equivalents",
        "carbs_equivalents",
    )


class DeviceTokenPerUserConfig(ModelAdmin):
    list_display = (
        "pk",
        "user_id",
        "device_token",
    )


admin.site.register(Reminders, RemindersConfig)
admin.site.register(BloodPressure, BloodPressureConfig)
admin.site.register(Meals, MealsConfig)
admin.site.register(Activity, ActivityConfig)
admin.site.register(Weight, WeightConfig)
admin.site.register(Medication, MedicationConfig)
admin.site.register(EmergencyMedication, EmergencyMedicationConfig)
admin.site.register(Glucose, GlucoseConfig)
admin.site.register(MenstrualCycle, MenstrualCycleConfig)
admin.site.register(MealsListInfo, MealsListInfoConfig)
admin.site.register(DeviceTokenPerUser, DeviceTokenPerUserConfig)
