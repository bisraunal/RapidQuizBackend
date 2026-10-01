from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response

from .models import Category, Question, Choice, Score
from .serializers import (
    CategorySerializer,
    QuestionSerializer,
    LeaderboardSerializer,
    QuizSubmissionSerializer,
)


class CategoryListView(APIView):
    """
    GET /api/v1/categories/
    Returns list of all active categories.
    """
    def get(self, request):
        categories = Category.objects.filter(is_active=True)
        serializer = CategorySerializer(categories, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class CategoryQuestionsView(APIView):
    """
    GET /api/v1/categories/<slug>/questions/
    Returns up to 20 questions for the given category with choices (is_correct omitted).
    """
    def get(self, request, slug):
        category = get_object_or_404(Category, slug=slug, is_active=True)
        # Fetch up to 20 active questions ordered by order / creation
        questions = category.questions.filter(is_active=True).prefetch_related('choices')[:20]
        question_serializer = QuestionSerializer(questions, many=True)

        return Response({
            "category": category.name,
            "category_slug": category.slug,
            "icon": category.icon,
            "color_theme": category.color_theme,
            "music_url": category.music_url,
            "music_title": category.music_title,
            "time_per_question": 5,
            "total_questions": len(question_serializer.data),
            "questions": question_serializer.data,
        }, status=status.HTTP_200_OK)


class QuizSubmitView(APIView):
    """
    POST /api/v1/quiz/submit/
    Calculates score based on answers and response times, saves score, and returns results with top 10.
    """
    def post(self, request):
        serializer = QuizSubmissionSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        data = serializer.validated_data
        category_slug = data["category_slug"]
        player_name = data["player_name"]
        answers = data["answers"]

        category = get_object_or_404(Category, slug=category_slug, is_active=True)

        # Collect question IDs and load correct choices from database
        question_ids = [ans["question_id"] for ans in answers]
        questions_map = {
            q.id: q
            for q in Question.objects.filter(id__in=question_ids).prefetch_related("choices")
        }

        correct_count = 0
        wrong_count = 0
        empty_count = 0
        total_score = 0
        total_time_taken = 0.0
        results_breakdown = []

        for ans in answers:
            q_id = ans["question_id"]
            selected_choice_id = ans.get("selected_choice_id")
            time_taken = float(ans.get("time_taken", 5.0))
            time_taken = max(0.0, min(5.0, time_taken))  # clamp between 0 and 5 seconds
            total_time_taken += time_taken

            question = questions_map.get(q_id)
            if not question:
                continue

            # Find correct choice and selected choice
            choices_list = list(question.choices.all())
            correct_choice = next((c for c in choices_list if c.is_correct), None)
            correct_choice_id = str(correct_choice.id) if correct_choice else None
            correct_choice_text = correct_choice.text if correct_choice else ""

            selected_choice = None
            if selected_choice_id:
                selected_choice = next((c for c in choices_list if str(c.id) == str(selected_choice_id)), None)
            selected_choice_text = selected_choice.text if selected_choice else None

            is_correct = False
            earned_points = 0

            if selected_choice_id is None:
                empty_count += 1
            elif correct_choice and str(selected_choice_id) == correct_choice_id:
                is_correct = True
                correct_count += 1
                # Base 10 points + speed bonus: up to 10 extra points based on remaining time (5 - time_taken) * 2
                remaining_time = max(0.0, 5.0 - time_taken)
                speed_bonus = int(round(remaining_time * 2))
                earned_points = question.points + speed_bonus
                total_score += earned_points
            else:
                wrong_count += 1

            results_breakdown.append({
                "question_id": str(q_id),
                "question_text": question.text,
                "code_snippet": question.code_snippet,
                "selected_choice_id": str(selected_choice_id) if selected_choice_id else None,
                "selected_choice_text": selected_choice_text,
                "correct_choice_id": correct_choice_id,
                "correct_choice_text": correct_choice_text,
                "is_correct": is_correct,
                "time_taken": time_taken,
                "earned_points": earned_points,
            })

        total_time_taken = round(total_time_taken, 2)

        # Save score record
        score_record = Score.objects.create(
            category=category,
            player_name=player_name,
            total_score=total_score,
            correct_count=correct_count,
            wrong_count=wrong_count,
            empty_count=empty_count,
            total_time_taken=total_time_taken,
        )

        # Calculate player rank in this category
        better_scores_count = Score.objects.filter(
            category=category,
            total_score__gt=total_score
        ).count()
        # Same score but faster time
        same_score_faster_count = Score.objects.filter(
            category=category,
            total_score=total_score,
            total_time_taken__lt=total_time_taken
        ).count()
        rank = better_scores_count + same_score_faster_count + 1

        # Fetch Top 10 for category
        top_10_scores = Score.objects.filter(category=category).order_by(
            "-total_score", "total_time_taken", "-created_at"
        )[:10]
        top_10_serializer = LeaderboardSerializer(top_10_scores, many=True)

        return Response({
            "score_id": str(score_record.id),
            "player_name": player_name,
            "category_name": category.name,
            "category_slug": category.slug,
            "total_score": total_score,
            "correct_count": correct_count,
            "wrong_count": wrong_count,
            "empty_count": empty_count,
            "total_time_taken": total_time_taken,
            "rank": rank,
            "results_breakdown": results_breakdown,
            "top_10": top_10_serializer.data,
        }, status=status.HTTP_201_CREATED)


class LeaderboardView(APIView):
    """
    GET /api/v1/leaderboard/?category=<slug>
    Returns top 10 scores for a category or global.
    """
    def get(self, request):
        category_slug = request.query_params.get("category")
        limit = int(request.query_params.get("limit", 10))
        limit = max(1, min(100, limit))

        queryset = Score.objects.all()
        category_obj = None

        if category_slug and category_slug != "global":
            category_obj = get_object_or_404(Category, slug=category_slug)
            queryset = queryset.filter(category=category_obj)

        scores = queryset.order_by("-total_score", "total_time_taken", "-created_at")[:limit]
        serializer = LeaderboardSerializer(scores, many=True)

        return Response({
            "category": category_obj.name if category_obj else "Global",
            "category_slug": category_obj.slug if category_obj else "global",
            "leaderboard": serializer.data,
        }, status=status.HTTP_200_OK)


class GlobalLeaderboardView(APIView):
    """
    GET /api/v1/leaderboard/global/
    Returns top 10 scores across all categories.
    """
    def get(self, request):
        scores = Score.objects.all().order_by("-total_score", "total_time_taken", "-created_at")[:10]
        serializer = LeaderboardSerializer(scores, many=True)
        return Response({
            "category": "Global",
            "category_slug": "global",
            "leaderboard": serializer.data,
        }, status=status.HTTP_200_OK)
