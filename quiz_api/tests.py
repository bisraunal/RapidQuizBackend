from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from .models import Category, Question, Choice, Score


class RapidQuizAPITests(TestCase):
    def setUp(self):
        self.client = APIClient()

        # Create test category
        self.category = Category.objects.create(
            name="Yazılım",
            slug="yazilim",
            icon="Code2",
            color_theme="cyan",
            is_active=True,
        )

        # Create 2 test questions with 4 choices each
        self.q1 = Question.objects.create(
            category=self.category,
            text="Python'da immutable veri tipi hangisidir?",
            points=10,
            order=1,
            is_active=True,
        )
        self.c1_correct = Choice.objects.create(question=self.q1, text="Tuple", is_correct=True)
        self.c1_wrong1 = Choice.objects.create(question=self.q1, text="List", is_correct=False)
        self.c1_wrong2 = Choice.objects.create(question=self.q1, text="Dict", is_correct=False)
        self.c1_wrong3 = Choice.objects.create(question=self.q1, text="Set", is_correct=False)

        self.q2 = Question.objects.create(
            category=self.category,
            text="Git'te geçici saklama komutu nedir?",
            points=10,
            order=2,
            is_active=True,
        )
        self.c2_correct = Choice.objects.create(question=self.q2, text="git stash", is_correct=True)
        self.c2_wrong = Choice.objects.create(question=self.q2, text="git save", is_correct=False)

    def test_category_list(self):
        """Test GET /api/v1/categories/"""
        url = reverse("quiz_api:category-list")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["slug"], "yazilim")
        self.assertEqual(response.data[0]["question_count"], 2)

    def test_category_questions_no_cheat(self):
        """Test GET /api/v1/categories/<slug>/questions/ and ensure is_correct is not leaked"""
        url = reverse("quiz_api:category-questions", kwargs={"slug": "yazilim"})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["total_questions"], 2)
        questions = response.data["questions"]
        self.assertEqual(len(questions), 2)

        # Ensure choice object does NOT contain 'is_correct' field
        for q in questions:
            for choice in q["choices"]:
                self.assertNotIn("is_correct", choice)
                self.assertIn("id", choice)
                self.assertIn("text", choice)

    def test_quiz_submit_and_scoring(self):
        """Test POST /api/v1/quiz/submit/ with correct answers and speed bonus"""
        url = reverse("quiz_api:quiz-submit")
        payload = {
            "category_slug": "yazilim",
            "player_name": "TestPlayer",
            "answers": [
                {
                    "question_id": str(self.q1.id),
                    "selected_choice_id": str(self.c1_correct.id),
                    "time_taken": 2.0,  # 3.0s remaining -> speed_bonus = round(3.0 * 2) = 6 -> 16 pts
                },
                {
                    "question_id": str(self.q2.id),
                    "selected_choice_id": str(self.c2_wrong.id),
                    "time_taken": 3.5,  # wrong choice -> 0 pts
                },
            ],
        }

        response = self.client.post(url, payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["player_name"], "TestPlayer")
        self.assertEqual(response.data["correct_count"], 1)
        self.assertEqual(response.data["wrong_count"], 1)
        self.assertEqual(response.data["empty_count"], 0)
        self.assertEqual(response.data["total_score"], 16)
        self.assertEqual(response.data["rank"], 1)
        self.assertTrue(len(response.data["top_10"]) >= 1)

    def test_leaderboard(self):
        """Test GET /api/v1/leaderboard/?category=yazilim and /api/v1/leaderboard/global/"""
        # Create some scores
        Score.objects.create(
            category=self.category,
            player_name="Champion",
            total_score=190,
            correct_count=19,
            total_time_taken=25.0,
        )
        Score.objects.create(
            category=self.category,
            player_name="RunnerUp",
            total_score=150,
            correct_count=15,
            total_time_taken=30.0,
        )

        url = reverse("quiz_api:leaderboard") + "?category=yazilim"
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["leaderboard"]), 2)
        self.assertEqual(response.data["leaderboard"][0]["player_name"], "Champion")

        # Global leaderboard
        global_url = reverse("quiz_api:leaderboard-global")
        global_resp = self.client.get(global_url)
        self.assertEqual(global_resp.status_code, status.HTTP_200_OK)
        self.assertEqual(len(global_resp.data["leaderboard"]), 2)
