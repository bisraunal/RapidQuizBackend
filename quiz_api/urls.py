from django.urls import path
from .views import (
    CategoryListView,
    CategoryQuestionsView,
    QuizSubmitView,
    LeaderboardView,
    GlobalLeaderboardView,
)

app_name = "quiz_api"

urlpatterns = [
    path("categories/", CategoryListView.as_view(), name="category-list"),
    path("categories/<slug:slug>/questions/", CategoryQuestionsView.as_view(), name="category-questions"),
    path("quiz/submit/", QuizSubmitView.as_view(), name="quiz-submit"),
    path("leaderboard/", LeaderboardView.as_view(), name="leaderboard"),
    path("leaderboard/global/", GlobalLeaderboardView.as_view(), name="leaderboard-global"),
]
