from django.db import models


class Reminders(models.Model):
    user_id = models.IntegerField()
    reminder_date_time = models.DateTimeField()
    reminder_title = models.CharField(max_length=300)
    reminder_info = models.CharField(max_length=1500, blank=True, null=True)


class BloodPressure(models.Model):
    user_id = models.IntegerField()
    systolic_blood_pressure = models.FloatField()
    diastolic_blood_pressure = models.FloatField()
    blood_pulse = models.FloatField()
    measurement_date_time = models.DateTimeField()


class Meals(models.Model):
    user_id = models.IntegerField()
    meal_name = models.CharField(max_length=300)
    meal_type = models.CharField(max_length=50)
    calories = models.FloatField(blank=True, null=True)
    fats = models.FloatField(blank=True, null=True)
    carbs = models.FloatField(blank=True, null=True)
    proteins = models.FloatField(blank=True, null=True)
    info = models.CharField(max_length=1500, blank=True, null=True)
    measurement_date_time = models.DateTimeField(blank=True, null=True)


class Activity(models.Model):
    user_id = models.IntegerField()
    activity_type = models.CharField(max_length=100)
    duration = models.FloatField()
    intensity = models.CharField(max_length=50)
    measurement_date_time = models.DateTimeField(blank=True, null=True)


class Weight(models.Model):
    user_id = models.IntegerField()
    weight = models.FloatField()
    measurement_date_time = models.DateTimeField(blank=True, null=True)


class Medication(models.Model):
    user_id = models.IntegerField()
    category = models.CharField(max_length=50)
    madication_name = models.CharField(max_length=100)
    dose = models.IntegerField()
    monday = models.BooleanField()
    tuesday = models.BooleanField()
    wednesday = models.BooleanField()
    thursday = models.BooleanField()
    friday = models.BooleanField()
    saturday = models.BooleanField()
    sunday = models.BooleanField()
    dose_time = models.TimeField()


class EmergencyMedication(models.Model):
    user_id = models.IntegerField()
    category = models.CharField(max_length=50)
    madication_name = models.CharField(max_length=100)
    dose = models.IntegerField()
    measurement_date_time = models.DateTimeField(blank=True, null=True)


class Glucose(models.Model):
    user_id = models.IntegerField()
    glucose_measurement = models.FloatField()
    glucose_type = models.CharField(max_length=50)
    insulin_dose = models.FloatField(null=True)
    insulin_type = models.CharField(max_length=50, blank=True, null=True)
    hypoglycemia_carbs = models.FloatField(blank=True, null=True)
    measurement_date_time = models.DateTimeField(blank=True, null=True)


class MenstrualCycle(models.Model):
    user_id = models.IntegerField()
    cycle_start_date = models.DateField()
    period_end_date = models.DateField()
    fertility_start_date = models.DateField()
    fertility_end_date = models.DateField()
    cycle_end_date = models.DateField(blank=True, null=True)


class MealsListInfo(models.Model):
    meal_name = models.CharField(max_length=100)
    meal_simple_name = models.CharField(max_length=100)
    energy = models.FloatField()
    protein = models.FloatField()
    fat = models.FloatField()
    carbs = models.FloatField()
    fats_equivalents = models.FloatField()
    carbs_equivalents = models.FloatField()


class DeviceTokenPerUser(models.Model):
    user_id = models.IntegerField()
    device_token = models.CharField(max_length=100)
