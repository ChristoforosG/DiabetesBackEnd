from os import stat
from django.shortcuts import render
from django.core import serializers
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny, IsAuthenticated, IsAdminUser
from jwt import decode
from django.conf import settings
from .models import MealsListInfo
import csv
import unidecode


class MigrateDataToMealsInfo(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        path = request.data["path"]
        a = []
        with open(path, "r", encoding="utf8") as f:
            for row in csv.DictReader(f, skipinitialspace=True):
                try:
                    a = MealsListInfo(
                        meal_name=row["meal_name"],
                        meal_simple_name=row["meal_simple_name"],
                        energy=row["energy"],
                        protein=row["protein"],
                        fat=row["fat"],
                        carbs=row["carbs"],
                        fats_equivalents=row["fats_equivalents"],
                        carbs_equivalents=row["carbs_equivalents"],
                    )
                    a.save()
                except Exception as e:
                    print("ERROR: ")
                    print(e)
                    print(row)
        return Response({"Migration": "Successful"}, status=status.HTTP_200_OK)
