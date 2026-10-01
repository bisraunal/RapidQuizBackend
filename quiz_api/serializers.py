from rest_framework import serializers
from .models import Category, Question, Choice, Score


class CategorySerializer(serializers.ModelSerializer):
    question_count = serializers.SerializerMethodField()

    class Meta:
        model = Category
        fields = [
            "id",
            "name",
            "slug",
            "icon",
            "color_theme",
            "music_url",
            "music_title",
            "is_active",
            "question_count",
        ]

    def get_question_count(self, obj):
        return obj.questions.filter(is_active=True).count()


class ChoiceSerializer(serializers.ModelSerializer):
    """
    Public choice serializer used during quiz.
    `is_correct` is intentionally omitted to prevent client-side inspection/cheating.
    """
    class Meta:
        model = Choice
        fields = ["id", "text"]


class QuestionSerializer(serializers.ModelSerializer):
    choices = ChoiceSerializer(many=True, read_only=True)

    class Meta:
        model = Question
        fields = [
            "id",
            "text",
            "code_snippet",
            "points",
            "order",
            "choices",
        ]


class ScoreSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source="category.name", read_only=True)
    category_slug = serializers.CharField(source="category.slug", read_only=True)

    class Meta:
        model = Score
        fields = [
            "id",
            "category",
            "category_name",
            "category_slug",
            "player_name",
            "total_score",
            "correct_count",
            "wrong_count",
            "empty_count",
            "total_time_taken",
            "created_at",
        ]


class LeaderboardSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source="category.name", read_only=True)
    category_slug = serializers.CharField(source="category.slug", read_only=True)

    class Meta:
        model = Score
        fields = [
            "id",
            "player_name",
            "total_score",
            "correct_count",
            "wrong_count",
            "empty_count",
            "total_time_taken",
            "category_name",
            "category_slug",
            "created_at",
        ]


class AnswerSubmissionSerializer(serializers.Serializer):
    question_id = serializers.UUIDField()
    selected_choice_id = serializers.UUIDField(allow_null=True, required=False)
    time_taken = serializers.FloatField(min_value=0.0, max_value=30.0, default=5.0)


class QuizSubmissionSerializer(serializers.Serializer):
    category_slug = serializers.SlugField()
    player_name = serializers.CharField(max_length=50, min_length=2, trim_whitespace=True)
    answers = AnswerSubmissionSerializer(many=True)
