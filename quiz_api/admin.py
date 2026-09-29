from django.contrib import admin
from .models import Category, Question, Choice, Score


class ChoiceInline(admin.TabularInline):
    model = Choice
    extra = 4
    min_num = 2
    fields = ("text", "is_correct")


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "slug", "icon", "color_theme", "is_active", "question_count", "created_at")
    list_filter = ("is_active", "created_at")
    search_fields = ("name", "slug")
    prepopulated_fields = {"slug": ("name",)}

    def question_count(self, obj):
        return obj.questions.count()
    question_count.short_description = "Soru Sayısı"


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ("short_text", "category", "points", "order", "is_active", "choice_count", "created_at")
    list_filter = ("category", "is_active", "created_at")
    search_fields = ("text", "code_snippet")
    inlines = [ChoiceInline]

    def short_text(self, obj):
        return obj.text[:60] + ("..." if len(obj.text) > 60 else "")
    short_text.short_description = "Soru Metni"

    def choice_count(self, obj):
        return obj.choices.count()
    choice_count.short_description = "Şık Sayısı"


@admin.register(Choice)
class ChoiceAdmin(admin.ModelAdmin):
    list_display = ("text", "question", "is_correct")
    list_filter = ("is_correct", "question__category")
    search_fields = ("text", "question__text")


@admin.register(Score)
class ScoreAdmin(admin.ModelAdmin):
    list_display = (
        "player_name",
        "category",
        "total_score",
        "correct_count",
        "wrong_count",
        "empty_count",
        "total_time_taken",
        "created_at",
    )
    list_filter = ("category", "created_at")
    search_fields = ("player_name",)
    readonly_fields = (
        "category",
        "player_name",
        "total_score",
        "correct_count",
        "wrong_count",
        "empty_count",
        "total_time_taken",
        "created_at",
    )
