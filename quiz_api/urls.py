from django.urls import path
from .views import (
    ApiRootView,
    CategoryListView,
    CategoryQuestionsView,
    QuizSubmitView,
    LeaderboardView,
    GlobalLeaderboardView,
    GenerateAiQuizView,
)

app_name = "quiz_api"

urlpatterns = [
    path("", ApiRootView.as_view(), name="api-root"),
    path("categories/", CategoryListView.as_view(), name="category-list"),
    path("categories/<slug:slug>/questions/", CategoryQuestionsView.as_view(), name="category-questions"),
    path("quiz/submit/", QuizSubmitView.as_view(), name="quiz-submit"),
    path("quiz/generate-ai/", GenerateAiQuizView.as_view(), name="quiz-generate-ai"),
    path("leaderboard/", LeaderboardView.as_view(), name="leaderboard"),
    path("leaderboard/global/", GlobalLeaderboardView.as_view(), name="leaderboard-global"),
]
