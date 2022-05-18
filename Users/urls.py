from django.urls import path
from .views import (
    CustomUserRegistration,
    UserLogIn,
    BlackListToken,
    GetPersonalUserInfo,
    SubmitPersonalUserInfo,
)

app_name = "Users"

urlpatterns = [
    path("register/", CustomUserRegistration.as_view(), name="create_user"),
    path("login/", UserLogIn.as_view(), name="log_in_user"),
    path("logout/", BlackListToken.as_view(), name="log_out"),
    path("userInfo/", GetPersonalUserInfo.as_view(), name="test_auth"),
    path(
        "submitPersonalUserInfo/",
        SubmitPersonalUserInfo.as_view(),
        name="personal_user_info_submit",
    ),
]
