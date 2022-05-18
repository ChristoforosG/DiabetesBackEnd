from django.urls import path
from .views import (
    RemindersView,
    BloodPressureView,
    MealsView,
    ActivityView,
    WeightView,
    MedicationView,
    EmergencyMedicationView,
    GlucoseView,
    MenstrualCycleView,
    MealsListInfoView,
    SubmitDeviceToken,
)
from .PushNotification.views import (
    PushNotificationTest,
    BloodGlucosePushNotification,
    MedicationReminderPushNotification,
)
from .adminViews import MigrateDataToMealsInfo

app_name = "DataAPI"

urlpatterns = [
    path("reminder/", RemindersView.as_view(), name="reminder"),
    path(
        "blood-pressure-ingestion/",
        BloodPressureView.as_view(),
        name="blood pressure ingestion",
    ),
    path("meals/", MealsView.as_view(), name="meal ingestion"),
    path("activity/", ActivityView.as_view(), name="activity ingestion"),
    path("weight/", WeightView.as_view(), name="weight ingestion"),
    path("medication/", MedicationView.as_view(), name="medication ingestion"),
    path(
        "medication-once/",
        EmergencyMedicationView.as_view(),
        name="medication just once ingestion",
    ),
    path("glucose/", GlucoseView.as_view(), name="glucose ingestion"),
    path("menstrual-cycle/", MenstrualCycleView.as_view(), name="menstrual cycle"),
    path(
        "pushNotificationTest/",
        PushNotificationTest.as_view(),
        name="Push Notification Test",
    ),
    path(
        "migrate-meals-csv/",
        MigrateDataToMealsInfo.as_view(),
        name="Migrate Meals Data from CSV to Database",
    ),
    path(
        "meals-info-list/",
        MealsListInfoView.as_view(),
        name="Meals Info List",
    ),
    path(
        "blood-glucose-push-notification/",
        BloodGlucosePushNotification.as_view(),
        name="Blood Glucose Push Notification",
    ),
    path(
        "submit-device-token/",
        SubmitDeviceToken.as_view(),
        name="submit device token",
    ),
    path(
        "medication-reminder-push-notification/",
        MedicationReminderPushNotification.as_view(),
        name="medication reminder push notification",
    ),
]
