from os import stat
from django.shortcuts import render
from django.core import serializers
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from django.db.models.functions import TruncDate
from django.db.models import Sum, Avg
from rest_framework.permissions import AllowAny, IsAuthenticated
from jwt import decode
from django.conf import settings
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
import datetime
import numpy as np


class RemindersView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        token_decoded = decode(
            request.headers["Authorization"].removeprefix("Bearer "),
            settings.SECRET_KEY,
            algorithms=["HS256"],
        )
        user = token_decoded["user_id"]
        reminders = Reminders.objects.filter(user_id=user).order_by(
            "-reminder_date_time"
        )
        data = serializers.serialize("json", reminders)
        return Response(
            data,
            status=status.HTTP_200_OK,
        )

    def post(self, request):
        token_decoded = decode(
            request.headers["Authorization"].removeprefix("Bearer "),
            settings.SECRET_KEY,
            algorithms=["HS256"],
        )
        user = token_decoded["user_id"]
        reminderInfo = request.data
        reminder = Reminders(
            user_id=user,
            reminder_date_time=reminderInfo["date_time"],
            reminder_title=reminderInfo["title"],
            reminder_info=reminderInfo["info"],
        )
        reminder.save()
        return Response(
            {"Reminder": "Inserted"},
            status=status.HTTP_200_OK,
        )


class BloodPressureView(APIView):
    permission_classes = [IsAuthenticated]

    def createGraphObject(self, pressure_list, mod):
        graph_data = dict()
        graph_data["systolic"] = dict()
        graph_data["systolic"]["labels"] = []
        graph_data["systolic"]["datasets"] = []
        graph_data["diastolic"] = dict()
        graph_data["diastolic"]["labels"] = []
        graph_data["diastolic"]["datasets"] = []
        graph_data["pulse"] = dict()
        graph_data["pulse"]["labels"] = []
        graph_data["pulse"]["datasets"] = []
        systolic_data = []
        diastolic_data = []
        pulse_data = []
        systolic_dict = dict()
        diastolic_dict = dict()
        pulse_dict = dict()
        for i, pressure in enumerate(pressure_list):
            if i % mod == 0:
                graph_data["systolic"]["labels"].append(
                    pressure["date"].strftime("%m/%d")
                )
                graph_data["diastolic"]["labels"].append(
                    pressure["date"].strftime("%m/%d")
                )
                graph_data["pulse"]["labels"].append(pressure["date"].strftime("%m/%d"))
            elif mod == 5 and (i % mod == 1 or i % mod == 4):
                graph_data["systolic"]["labels"].append(" ")
                graph_data["diastolic"]["labels"].append(" ")
                graph_data["pulse"]["labels"].append(" ")
            else:
                graph_data["systolic"]["labels"].append("-")
                graph_data["diastolic"]["labels"].append("-")
                graph_data["pulse"]["labels"].append("-")
            systolic_data.append(pressure["daily_systolic_blood_pressure"])
            diastolic_data.append(pressure["daily_diastolic_blood_pressure"])
            pulse_data.append(pressure["daily_blood_pulse"])
        systolic_dict["data"] = systolic_data
        diastolic_dict["data"] = diastolic_data
        pulse_dict["data"] = pulse_data
        graph_data["systolic"]["datasets"].append(systolic_dict)
        graph_data["diastolic"]["datasets"].append(diastolic_dict)
        graph_data["pulse"]["datasets"].append(pulse_dict)
        return graph_data

    def fillEmptyDays(self, pressure_list):
        if len(pressure_list) < 2:
            return pressure_list
        pressure_dense_list = []
        for i, pressure in enumerate(pressure_list[: len(pressure_list) - 1]):
            pressure_dense_list.append(pressure)
            days = (pressure_list[i + 1]["date"] - pressure["date"]).days - 1
            if days > 0:
                day_list = [
                    pressure["date"] + datetime.timedelta(days=d + 1)
                    for d in range(days)
                ]
                systolic = np.linspace(
                    pressure["daily_systolic_blood_pressure"],
                    pressure_list[i + 1]["daily_systolic_blood_pressure"],
                    num=days,
                )
                diastolic = np.linspace(
                    pressure["daily_diastolic_blood_pressure"],
                    pressure_list[i + 1]["daily_diastolic_blood_pressure"],
                    num=days,
                )
                pulse = np.linspace(
                    pressure["daily_blood_pulse"],
                    pressure_list[i + 1]["daily_blood_pulse"],
                    num=days,
                )
                for day in range(days):
                    pr = dict()
                    pr["date"] = day_list[day]
                    pr["daily_systolic_blood_pressure"] = systolic[day]
                    pr["daily_diastolic_blood_pressure"] = diastolic[day]
                    pr["daily_blood_pulse"] = pulse[day]
                    pressure_dense_list.append(pr)
            if i == len(pressure_list) - 2:
                pressure_dense_list.append(pressure_list[i + 1])
        return pressure_dense_list

    def padPressureListAtBeginning(self, pressure_list):
        past_days = (
            30
            - (
                pressure_list[len(pressure_list) - 1]["date"] - pressure_list[0]["date"]
            ).days
        )
        paddedPressureList = []
        for day in range(past_days, 0, -1):
            pressure_dict = dict()
            pressure_dict["date"] = pressure_list[0]["date"] - datetime.timedelta(
                days=day
            )
            pressure_dict["daily_systolic_blood_pressure"] = 0
            pressure_dict["daily_diastolic_blood_pressure"] = 0
            pressure_dict["daily_blood_pulse"] = 0
            paddedPressureList.append(pressure_dict)
        paddedPressureList.extend(pressure_list)
        return paddedPressureList

    def aggregateDataPerDate(self, user_id):
        startdate = datetime.date.today() + datetime.timedelta(days=1)
        enddate = startdate - datetime.timedelta(days=30)
        pressure_list = (
            BloodPressure.objects.filter(user_id=user_id)
            .filter(measurement_date_time__range=[enddate, startdate])
            .annotate(date=TruncDate("measurement_date_time"))
            .values(
                "date",
            )
            .annotate(
                daily_systolic_blood_pressure=Avg("systolic_blood_pressure"),
                daily_diastolic_blood_pressure=Avg("diastolic_blood_pressure"),
                daily_blood_pulse=Avg("blood_pulse"),
            )
            .values(
                "date",
                "daily_systolic_blood_pressure",
                "daily_diastolic_blood_pressure",
                "daily_blood_pulse",
            )
        )
        return pressure_list

    def post(self, request):
        token_decoded = decode(
            request.headers["Authorization"].removeprefix("Bearer "),
            settings.SECRET_KEY,
            algorithms=["HS256"],
        )
        user = token_decoded["user_id"]
        bloodPressureInfo = request.data
        print(bloodPressureInfo)
        bloodPressure = BloodPressure(
            user_id=user,
            systolic_blood_pressure=bloodPressureInfo["systolic_blood_pressure"],
            diastolic_blood_pressure=bloodPressureInfo["diastolic_blood_pressure"],
            blood_pulse=bloodPressureInfo["blood_pulse"],
            measurement_date_time=bloodPressureInfo["measurement_date_time"],
        )
        bloodPressure.save()
        return Response({"Blood_Pressure": "Inserted"}, status=status.HTTP_200_OK)

    def get(self, request):
        token_decoded = decode(
            request.headers["Authorization"].removeprefix("Bearer "),
            settings.SECRET_KEY,
            algorithms=["HS256"],
        )
        user = token_decoded["user_id"]
        pressure_list = self.aggregateDataPerDate(user)
        pressure_dense_list = self.fillEmptyDays(pressure_list)
        padded_pressure_list = pressure_dense_list
        # padded_pressure_list = self.padPressureListAtBeginning(pressure_dense_list)
        graph_data = dict()
        data_len = len(padded_pressure_list)
        if data_len <= 7:
            week = padded_pressure_list
            fifteen = padded_pressure_list
        elif data_len <= 15:
            week = padded_pressure_list[(data_len - 7) :]
            fifteen = padded_pressure_list
        else:
            week = padded_pressure_list[(data_len - 7) :]
            fifteen = padded_pressure_list[(data_len - 15) :]

        graph_data["weekly"] = self.createGraphObject(week, 1)
        graph_data["fifteen"] = self.createGraphObject(fifteen, 3)
        graph_data["monthly"] = self.createGraphObject(padded_pressure_list, 5)

        return Response(
            graph_data,
            status=status.HTTP_200_OK,
        )


class MealsView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        token_decoded = decode(
            request.headers["Authorization"].removeprefix("Bearer "),
            settings.SECRET_KEY,
            algorithms=["HS256"],
        )
        user = token_decoded["user_id"]
        mealsInfo = request.data
        if mealsInfo["calories"] == "":
            mealsInfo["calories"] = None
        if mealsInfo["fats"] == "":
            mealsInfo["fats"] = None
        if mealsInfo["carbs"] == "":
            mealsInfo["carbs"] = None
        if mealsInfo["proteins"] == "":
            mealsInfo["proteins"] = None
        meals = Meals(
            user_id=user,
            meal_name=mealsInfo["meal_name"],
            meal_type=mealsInfo["meal_type"],
            calories=mealsInfo["calories"],
            fats=mealsInfo["fats"],
            carbs=mealsInfo["carbs"],
            proteins=mealsInfo["proteins"],
            info=mealsInfo["info"],
            measurement_date_time=mealsInfo["measurement_date_time"],
        )
        meals.save()
        return Response({"Meal": "Inserted"}, status=status.HTTP_200_OK)


class ActivityView(APIView):
    permission_classes = [IsAuthenticated]

    def createGraphObject(self, activity_list, mod):
        graph_data = dict()
        graph_data["activity"] = dict()
        graph_data["activity"]["labels"] = []
        graph_data["activity"]["datasets"] = []
        activity_data = []
        activity_dict = dict()
        for i, activity in enumerate(activity_list):
            if i % mod == 0:
                graph_data["activity"]["labels"].append(
                    activity["date"].strftime("%m/%d")
                )
            elif mod == 5 and (i % mod == 1 or i % mod == 4):
                graph_data["activity"]["labels"].append(" ")
            else:
                graph_data["activity"]["labels"].append("-")
            activity_data.append(activity["daily_activity_duration"])

        activity_dict["data"] = activity_data

        graph_data["activity"]["datasets"].append(activity_dict)
        return graph_data

    def fillEmptyDays(self, activity_list):
        activity_dense_list = []
        if len(activity_list) < 2:
            return activity_list
        for i, activity in enumerate(activity_list[: len(activity_list) - 1]):
            activity_dense_list.append(activity)
            days = (activity_list[i + 1]["date"] - activity["date"]).days - 1
            if days > 0:
                day_list = [
                    activity["date"] + datetime.timedelta(days=d + 1)
                    for d in range(days)
                ]

                for day in range(days):
                    act = dict()
                    act["date"] = day_list[day]
                    act["daily_activity_duration"] = 0
                    activity_dense_list.append(act)
            if i == len(activity_list) - 2:
                activity_dense_list.append(activity_list[i + 1])
        return activity_dense_list

    def aggregateDataPerDate(self, user_id):
        startdate = datetime.date.today() + datetime.timedelta(days=1)
        enddate = startdate - datetime.timedelta(days=30)
        activity_list = (
            Activity.objects.filter(user_id=user_id)
            .filter(measurement_date_time__range=[enddate, startdate])
            .annotate(date=TruncDate("measurement_date_time"))
            .values(
                "date",
            )
            .annotate(
                daily_activity_duration=Sum("duration"),
            )
            .values(
                "date",
                "daily_activity_duration",
            )
        )
        return activity_list

    def post(self, request):
        token_decoded = decode(
            request.headers["Authorization"].removeprefix("Bearer "),
            settings.SECRET_KEY,
            algorithms=["HS256"],
        )
        user = token_decoded["user_id"]
        activityInfo = request.data
        activity = Activity(
            user_id=user,
            activity_type=activityInfo["activity_type"],
            duration=activityInfo["duration"],
            intensity=activityInfo["intensity"],
            measurement_date_time=activityInfo["measurement_date_time"],
        )
        activity.save()
        return Response({"Activity": "Inserted"}, status=status.HTTP_200_OK)

    def get(self, request):
        token_decoded = decode(
            request.headers["Authorization"].removeprefix("Bearer "),
            settings.SECRET_KEY,
            algorithms=["HS256"],
        )
        user = token_decoded["user_id"]
        activity_list = self.aggregateDataPerDate(user)
        activity_dense_list = self.fillEmptyDays(activity_list)
        padded_activity_list = activity_dense_list
        # padded_pressure_list = self.padPressureListAtBeginning(pressure_dense_list)
        graph_data = dict()
        data_len = len(padded_activity_list)
        if data_len <= 7:
            week = padded_activity_list
            fifteen = padded_activity_list
        elif data_len <= 15:
            week = padded_activity_list[(data_len - 7) :]
            fifteen = padded_activity_list
        else:
            week = padded_activity_list[(data_len - 7) :]
            fifteen = padded_activity_list[(data_len - 15) :]

        graph_data["weekly"] = self.createGraphObject(week, 1)
        graph_data["fifteen"] = self.createGraphObject(fifteen, 3)
        graph_data["monthly"] = self.createGraphObject(padded_activity_list, 5)

        return Response(
            graph_data,
            status=status.HTTP_200_OK,
        )


class WeightView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        token_decoded = decode(
            request.headers["Authorization"].removeprefix("Bearer "),
            settings.SECRET_KEY,
            algorithms=["HS256"],
        )
        user = token_decoded["user_id"]
        weightInfo = request.data
        weight = Weight(
            user_id=user,
            weight=weightInfo["weight"],
            measurement_date_time=weightInfo["measurement_date_time"],
        )
        weight.save()
        return Response({"Weight": "Inserted"}, status=status.HTTP_200_OK)


class MedicationView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        token_decoded = decode(
            request.headers["Authorization"].removeprefix("Bearer "),
            settings.SECRET_KEY,
            algorithms=["HS256"],
        )
        user = token_decoded["user_id"]
        medicationInfo = request.data
        medication = Medication(
            user_id=user,
            category=medicationInfo["category"],
            madication_name=medicationInfo["madication_name"],
            dose=medicationInfo["dose"],
            monday=medicationInfo["monday"],
            tuesday=medicationInfo["tuesday"],
            wednesday=medicationInfo["wednesday"],
            thursday=medicationInfo["thursday"],
            friday=medicationInfo["friday"],
            sutarday=medicationInfo["sutarday"],
            sunday=medicationInfo["sunday"],
            dose_time=medicationInfo["dose_time"],
        )
        medication.save()
        return Response({"Medication": "Inserted"}, status=status.HTTP_200_OK)


class EmergencyMedicationView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        token_decoded = decode(
            request.headers["Authorization"].removeprefix("Bearer "),
            settings.SECRET_KEY,
            algorithms=["HS256"],
        )
        user = token_decoded["user_id"]
        medicationInfo = request.data
        medication = EmergencyMedication(
            user_id=user,
            category=medicationInfo["category"],
            madication_name=medicationInfo["madication_name"],
            dose=medicationInfo["dose"],
            measurement_date_time=medicationInfo["measurement_date_time"],
        )
        medication.save()
        return Response({"Emergency Medication": "Inserted"}, status=status.HTTP_200_OK)


class GlucoseView(APIView):
    permission_classes = [IsAuthenticated]

    def _checkGlucoseValue(self, type, value):
        if type == "pre":
            if value < 80:
                return [1, 0, 0]
            if value < 130:
                return [0, 1, 0]
            return [0, 0, 1]
        if type == "post":
            if value < 80:
                return [1, 0, 0]
            if value < 180:
                return [0, 1, 0]
            return [0, 0, 1]
        if type == "sleep":
            if value < 140:
                return [1, 0, 0]
            if value < 180:
                return [0, 1, 0]
            return [0, 0, 1]

    def _filter(self, glucose_list):
        type_dict = dict()
        type_dict["pre"] = (glucose_list.filter(glucose_type="Προγευματική"),)
        type_dict["post"] = (glucose_list.filter(glucose_type="Μεταγευματική"),)
        type_dict["sleep"] = (glucose_list.filter(glucose_type="Προ ύπνου"),)
        return type_dict

    def _median(self, querySet):
        term = "daily_glucose"
        count = querySet.count()
        values = querySet.values_list(term, flat=True).order_by(term)
        if count == 0:
            return 0
        if count == 1:
            return values[0]
        if count == 2:
            return sum(values) / 2
        if count % 2 == 1:
            return values[int(round(count / 2))]
        else:
            return sum(values[count / 2 - 1 : count / 2 + 1]) / 2

    def _aggregatePerDateAndType(self, user_id, time_window):
        startdate = datetime.date.today() + datetime.timedelta(days=1)
        enddate = startdate - datetime.timedelta(days=time_window)
        glucose_list = (
            Glucose.objects.filter(user_id=user_id)
            .filter(measurement_date_time__range=[enddate, startdate])
            .annotate(date=TruncDate("measurement_date_time"))
            .values("date", "glucose_type")
            .annotate(
                daily_glucose=Avg("glucose_measurement"),
            )
            .values(
                "date",
                "glucose_type",
                "daily_glucose",
            )
        )
        return glucose_list

    def calculatePercentageValues(self, user_id):
        week_list = self._aggregatePerDateAndType(user_id, 7)
        fifteen_list = self._aggregatePerDateAndType(user_id, 15)
        month_list = self._aggregatePerDateAndType(user_id, 30)
        glucose_dict = dict()
        glucose_dict["week"] = self._filter(week_list)
        glucose_dict["fifteen"] = self._filter(fifteen_list)
        glucose_dict["month"] = self._filter(month_list)
        percentages_dict = dict()
        for (duration, duration_value) in glucose_dict.items():
            type_dict = dict()
            for (type, queryset) in duration_value.items():
                count = np.array([0, 0, 0])
                for queryitem in queryset[0]:
                    if queryitem:
                        count += np.array(
                            self._checkGlucoseValue(type, queryitem["daily_glucose"])
                        )
                if sum(count) == 0:
                    type_dict[type] = count
                else:
                    type_dict[type] = count / sum(count)
            percentages_dict[duration] = type_dict

        return percentages_dict

    def calculateMedian(self, user_id, time_window):
        glucose_list = self._aggregatePerDateAndType(user_id, time_window)
        premeal = self._median(glucose_list.filter(glucose_type="Προγευματική"))
        postmeal = self._median(glucose_list.filter(glucose_type="Μεταγευματική"))
        presleep = self._median(glucose_list.filter(glucose_type="Προ ύπνου"))
        return [premeal, postmeal, presleep]

    def padGlucoseListAtBeginning(self, glucose_list):
        past_days = (
            30
            - (
                glucose_list[len(glucose_list) - 1]["date"] - glucose_list[0]["date"]
            ).days
        )
        paddedGlucoseList = []
        for day in range(past_days, 0, -1):
            glucose_dict = dict()
            glucose_dict["date"] = glucose_list[0]["date"] - datetime.timedelta(
                days=day
            )
            glucose_dict["daily_glucose"] = 0
            paddedGlucoseList.append(glucose_dict)
        paddedGlucoseList.extend(glucose_list)
        return paddedGlucoseList

    def fillEmptyDays(self, glucose_list):
        if len(glucose_list) < 2:
            return glucose_list
        glucose_dense_list = []
        for i, glucose in enumerate(glucose_list[: len(glucose_list) - 1]):
            glucose_dense_list.append(glucose)
            days = (glucose_list[i + 1]["date"] - glucose["date"]).days - 1
            if days > 0:
                day_list = [
                    glucose["date"] + datetime.timedelta(days=d + 1)
                    for d in range(days)
                ]
                daily_glucose = np.linspace(
                    glucose["daily_glucose"],
                    glucose_list[i + 1]["daily_glucose"],
                    num=days,
                )
                for day in range(days):
                    gluc = dict()
                    gluc["date"] = day_list[day]
                    gluc["daily_glucose"] = daily_glucose[day]
                    glucose_dense_list.append(gluc)
            if i == len(glucose_list) - 2:
                glucose_dense_list.append(glucose_list[i + 1])
        return glucose_dense_list

    def aggregateDataPerDate(self, user_id):
        startdate = datetime.date.today() + datetime.timedelta(days=1)
        enddate = startdate - datetime.timedelta(days=30)
        glucose_list = (
            Glucose.objects.filter(user_id=user_id)
            .filter(measurement_date_time__range=[enddate, startdate])
            .annotate(date=TruncDate("measurement_date_time"))
            .values(
                "date",
            )
            .annotate(
                daily_glucose=Avg("glucose_measurement"),
            )
            .values(
                "date",
                "daily_glucose",
            )
        )
        return glucose_list

    def createGraphObject(self, glucose_list, mod):
        graph_data = dict()

        graph_data["labels"] = []
        graph_data["datasets"] = []

        glucose_data = []
        glucose_dict = dict()

        for i, glucose in enumerate(glucose_list):
            if i % mod == 0:
                graph_data["labels"].append(glucose["date"].strftime("%m/%d"))
            elif mod == 5 and (i % mod == 1 or i % mod == 4):
                graph_data["labels"].append(" ")
            else:
                graph_data["labels"].append("-")
            glucose_data.append(glucose["daily_glucose"])
        glucose_dict["data"] = glucose_data
        graph_data["datasets"].append(glucose_dict)
        return graph_data

    def constructDict(self, gl_list, medians, percentages):
        response_dict = dict()
        response_dict["graph"] = gl_list
        response_dict["median"] = medians
        response_dict["percent"] = percentages
        return response_dict

    def get(self, request):
        token_decoded = decode(
            request.headers["Authorization"].removeprefix("Bearer "),
            settings.SECRET_KEY,
            algorithms=["HS256"],
        )
        user = token_decoded["user_id"]
        glucose_list = self.aggregateDataPerDate(user)
        glucose_dense_list = self.fillEmptyDays(glucose_list)
        # glucose_padded_list = self.padGlucoseListAtBeginning(glucose_dense_list)
        glucose_padded_list = glucose_dense_list
        graph_data = dict()
        data_len = len(glucose_padded_list)
        if data_len <= 7:
            week = glucose_padded_list
            fifteen = glucose_padded_list
        elif data_len <= 15:
            week = glucose_padded_list[(data_len - 7) :]
            fifteen = glucose_padded_list
        else:
            week = glucose_padded_list[(data_len - 7) :]
            fifteen = glucose_padded_list[(data_len - 15) :]

        graph_data["weekly"] = self.createGraphObject(week, 1)
        graph_data["fifteen"] = self.createGraphObject(fifteen, 3)
        graph_data["monthly"] = self.createGraphObject(glucose_padded_list, 5)

        glucose_medians = dict()
        glucose_medians["weekly"] = self.calculateMedian(user, 7)
        glucose_medians["fifteen"] = self.calculateMedian(user, 15)
        glucose_medians["monthly"] = self.calculateMedian(user, 30)

        glucose_percentages = self.calculatePercentageValues(user)

        glucose_response = self.constructDict(
            graph_data, glucose_medians, glucose_percentages
        )

        return Response(
            glucose_response,
            status=status.HTTP_200_OK,
        )

    def post(self, request):
        token_decoded = decode(
            request.headers["Authorization"].removeprefix("Bearer "),
            settings.SECRET_KEY,
            algorithms=["HS256"],
        )
        user = token_decoded["user_id"]
        glucoseInfo = request.data
        if glucoseInfo["insulin_dose"] == "":
            glucoseInfo["insulin_dose"] = None
        if glucoseInfo["insulin_type"] == "None":
            glucoseInfo["insulin_type"] = None
        if glucoseInfo["hypoglycemia_carbs"] == "":
            glucoseInfo["hypoglycemia_carbs"] = None
        glucose = Glucose(
            user_id=user,
            glucose_measurement=glucoseInfo["glucose_measurement"],
            glucose_type=glucoseInfo["glucose_type"],
            insulin_dose=glucoseInfo["insulin_dose"],
            insulin_type=glucoseInfo["insulin_type"],
            hypoglycemia_carbs=glucoseInfo["hypoglycemia_carbs"],
            measurement_date_time=glucoseInfo["measurement_date_time"],
        )
        glucose.save()
        return Response({"Glucose": "Inserted"}, status=status.HTTP_200_OK)


class MenstrualCycleView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        token_decoded = decode(
            request.headers["Authorization"].removeprefix("Bearer "),
            settings.SECRET_KEY,
            algorithms=["HS256"],
        )
        user = token_decoded["user_id"]
        menstrualCycleInfo = request.data
        if menstrualCycleInfo["cycle_end_date"] == "":
            menstrualCycleInfo["cycle_end_date"] = None
        menstrual = (
            MenstrualCycle.objects.filter(user_id=user)
            .order_by("-cycle_start_date")
            .first()
        )
        if menstrual:
            menstrual.cycle_end_date = datetime.datetime.strptime(
                menstrualCycleInfo["cycle_start_date"], "%Y-%m-%d"
            ) - datetime.timedelta(days=1)
            menstrual.save()

        menstrualCycle = MenstrualCycle(
            user_id=user,
            cycle_start_date=menstrualCycleInfo["cycle_start_date"],
            period_end_date=menstrualCycleInfo["period_end_date"],
            fertility_start_date=menstrualCycleInfo["fertility_start_date"],
            fertility_end_date=menstrualCycleInfo["fertility_end_date"],
            cycle_end_date=menstrualCycleInfo["cycle_end_date"],
        )
        menstrualCycle.save()
        return Response({"Menstrual Cycle": "Inserted"}, status=status.HTTP_200_OK)

    def get(self, request):
        token_decoded = decode(
            request.headers["Authorization"].removeprefix("Bearer "),
            settings.SECRET_KEY,
            algorithms=["HS256"],
        )

        user = token_decoded["user_id"]
        menstrual_list = (
            MenstrualCycle.objects.filter(user_id=user)
            .order_by("-cycle_start_date")
            .values()
        )

        latest_menstrual = (
            MenstrualCycle.objects.filter(user_id=user)
            .order_by("-cycle_start_date")
            .first()
        )
        print(latest_menstrual)

        if menstrual_list == None:
            return Response(
                status=status.HTTP_204_NO_CONTENT,
            )

        if len(menstrual_list) < 3:
            response = dict()
            response["avg_cycle"] = "-"
            response["avg_period"] = "-"
            response["stats"] = []
            response["cycle_start_date"] = latest_menstrual.cycle_start_date
            response["fertility_start_date"] = latest_menstrual.fertility_start_date
            response["max_days"] = 0
            return Response(
                response,
                status=status.HTTP_200_OK,
            )
        statistics = []
        avg_cycle = 0
        avg_period = 0
        max_days = 0
        for menstrual in menstrual_list[:7]:
            if menstrual["cycle_end_date"]:
                menstrual_dict = dict()
                menstrual_dict["cycle_duration"] = (
                    menstrual["cycle_end_date"] - menstrual["cycle_start_date"]
                ).days
                if menstrual_dict["cycle_duration"] < 20:
                    continue
                if max_days < menstrual_dict["cycle_duration"]:
                    max_days = menstrual_dict["cycle_duration"]
                avg_cycle += menstrual_dict["cycle_duration"]
                menstrual_dict["period_day"] = (
                    menstrual["period_end_date"] - menstrual["cycle_start_date"]
                ).days
                avg_period += menstrual_dict["period_day"]
                menstrual_dict["date"] = (
                    menstrual["cycle_start_date"].strftime("%B %d")
                    + " - "
                    + menstrual["cycle_end_date"].strftime("%B %d")
                )
                statistics.append(menstrual_dict)
        avg_cycle = avg_cycle / len(statistics)
        avg_period = avg_period / len(statistics)

        menstrual_dict = dict()
        menstrual_dict["cycle_duration"] = avg_cycle
        menstrual_dict["period_day"] = avg_period
        menstrual_dict["date"] = (
            latest_menstrual.cycle_start_date.strftime("%B %d") + " - Now"
        )
        statistics.insert(0, menstrual_dict)

        response = dict()

        response["avg_cycle"] = avg_cycle
        response["avg_period"] = avg_period
        response["stats"] = statistics
        response["cycle_start_date"] = latest_menstrual.cycle_start_date
        response["fertility_start_date"] = latest_menstrual.fertility_start_date
        response["max_days"] = max_days

        return Response(
            response,
            status=status.HTTP_200_OK,
        )


class MealsListInfoView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        meals = MealsListInfo.objects.all()
        meals_lower = []
        meals_mapping = dict()
        meals_details = dict()
        for meal in meals:
            meals_lower.append(meal.meal_simple_name)
            meals_mapping[meal.meal_simple_name] = meal.meal_name
            meals_details[meal.meal_name] = [meal.protein, meal.carbs, meal.fat]
        output_dict = dict()
        output_dict["lowercase"] = meals_lower
        output_dict["mapping"] = meals_mapping
        output_dict["details"] = meals_details
        return Response(output_dict, status=status.HTTP_200_OK)


class SubmitDeviceToken(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        token_decoded = decode(
            request.headers["Authorization"].removeprefix("Bearer "),
            settings.SECRET_KEY,
            algorithms=["HS256"],
        )
        user = token_decoded["user_id"]
        deviceAlreadyExists = DeviceTokenPerUser.objects.get(user_id=user)
        if deviceAlreadyExists:
            deviceAlreadyExists.device_token = request.data["device_token"]
            deviceAlreadyExists.save()
            return Response({"Device Token": "Updated"}, status=status.HTTP_200_OK)
        newDevice = DeviceTokenPerUser(
            user_id=user, device_token=request.data["device_token"]
        )
        newDevice.save()
        return Response({"Device Token": "Inserted"}, status=status.HTTP_200_OK)
