from os import stat
from django.shortcuts import render
from django.core import serializers
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from jwt import decode
from django.conf import settings
from .pushNotificationHandler import send_push_message
from ..models import Glucose, DeviceTokenPerUser, Medication
from django.db.models import Avg, Max, Min
from datetime import date, datetime, time, timedelta


class PushNotificationTest(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        token = request.data["token"]
        message = request.data["message"]
        title = request.data["title"]
        send_push_message(token, message, title)
        return Response({"PushNotification": "Sent"}, status=status.HTTP_200_OK)


class BloodGlucosePushNotification(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        measurementDateTimePerDevice = (
            Glucose.objects.all()
            .values("user_id")
            .annotate(latest_date=Max("measurement_date_time"))
        )

        now = datetime.now().date()
        message = "Δεν εχεις μετρησει την Γλυκόζη σου!"
        title = "Μέτρηση Γλυκόζης"
        for device in measurementDateTimePerDevice:
            token = DeviceTokenPerUser.objects.get(
                user_id=device["user_id"]
            ).device_token
            if now > device["latest_date"].date():
                token = token
                send_push_message(token, message, title)
        return Response({"PushNotification": "BloodGlucose"}, status=status.HTTP_200_OK)


class MedicationReminderPushNotification(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        title = "Υπενθύμιση"
        medicationRemindersPerDevice = Medication.objects.all().values()
        for medicationReminder in medicationRemindersPerDevice:
            if medicationReminder[datetime.today().strftime("%A").lower()]:
                duration = datetime.combine(
                    date.today(), datetime.now().time()
                ) - datetime.combine(date.today(), medicationReminder["dose_time"])
                if duration > timedelta(minutes=-10) and duration < timedelta(
                    minutes=10
                ):
                    message = "{} {}".format(
                        medicationReminder["category"],
                        medicationReminder["madication_name"],
                    )
                    token = DeviceTokenPerUser.objects.get(
                        user_id=medicationReminder["user_id"]
                    ).device_token
                    send_push_message(token, message, title)
        # print(medicationRemindersPerDevice)
        return Response(
            {"PushNotification": "MedicationReminder"}, status=status.HTTP_200_OK
        )
