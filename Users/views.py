from os import stat
from django.shortcuts import render
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from .serializers import RegisterUserSerializer
from rest_framework.permissions import AllowAny, IsAuthenticated
from django.contrib.auth import authenticate
from jwt import decode
from django.conf import settings
from rest_framework_simplejwt.tokens import RefreshToken
from .models import Users


class GetPersonalUserInfo(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):

        token_decoded = decode(
            request.headers["Authorization"].removeprefix("Bearer "),
            settings.SECRET_KEY,
            algorithms=["HS256"],
        )
        user = Users.objects.get(pk=token_decoded["user_id"])
        return Response(
            {
                "user_name": user.user_name,
                "first_name": user.first_name,
                "gender": user.gender,
                "is_in_insulin_therapy": user.is_in_insulin_therapy,
                "date_of_birth": user.date_of_birth,
            },
            status=status.HTTP_200_OK,
        )


class SubmitPersonalUserInfo(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        userPersonalInfoDict = request.data
        user = Users.objects.get(user_name=userPersonalInfoDict["user_name"])
        if user is None:
            return Response(
                {"error": "User does not exist"}, status=status.HTTP_404_NOT_FOUND
            )
        user.first_name = userPersonalInfoDict["first_name"]
        user.gender = userPersonalInfoDict["gender"]
        user.date_of_birth = userPersonalInfoDict["date_of_birth"]
        user.is_in_insulin_therapy = userPersonalInfoDict["is_in_insulin"]
        user.first_login = False
        user.save()
        return Response(
            {"First Name": userPersonalInfoDict["first_name"]},
            status=status.HTTP_200_OK,
        )


class UserLogIn(APIView):
    permission_classes = [AllowAny]
    authentication_classes = []

    def post(self, request):
        userDict = request.data
        user = authenticate(
            user_name=userDict["username"], password=userDict["password"]
        )
        if user is None:
            return Response(
                {"error": "Wrong credentials"}, status=status.HTTP_404_NOT_FOUND
            )
        else:
            refresh = RefreshToken.for_user(user)
            return Response(
                {
                    "user": user.user_name,
                    "first_login": user.first_login,
                    "refresh": str(refresh),
                    "access": str(refresh.access_token),
                },
                status=status.HTTP_200_OK,
            )


class BlackListToken(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            refresh_token = request.data["refresh_token"]
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response(status=status.HTTP_200_OK)
        except Exception as e:
            return Response(status=status.HTTP_400_BAD_REQUEST)


class NewRefreshToken(APIView):
    permission_classes = [AllowAny]
    authentication_classes = []


class CustomUserRegistration(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        reg_serializer = RegisterUserSerializer(data=request.data)
        if reg_serializer.is_valid():
            new_user = reg_serializer.save()
            if new_user:
                return Response(status=status.HTTP_201_CREATED)
        return Response(reg_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
