import uuid
from django.db import models


class Category(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100, verbose_name="Kategori Adı")
    slug = models.SlugField(max_length=100, unique=True, verbose_name="Kategori Slug")
    icon = models.CharField(max_length=50, default="HelpCircle", verbose_name="Lucide İkon Adı")
    color_theme = models.CharField(max_length=50, default="cyan", verbose_name="Renk Teması")
    music_url = models.URLField(max_length=500, blank=True, null=True, verbose_name="Arka Plan Müziği URL'si")
    music_title = models.CharField(max_length=100, blank=True, null=True, verbose_name="Müzik Başlığı")
    is_active = models.BooleanField(default=True, verbose_name="Aktif mi?")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Oluşturulma Tarihi")

    class Meta:
        verbose_name = "Kategori"
        verbose_name_plural = "Kategoriler"
        ordering = ["name"]

    def __str__(self):
        return self.name


class Question(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    category = models.ForeignKey(
        Category,
        on_delete=models.CASCADE,
        related_name="questions",
        verbose_name="Kategori"
    )
    text = models.TextField(verbose_name="Soru Metni")
    code_snippet = models.TextField(blank=True, null=True, verbose_name="Kod veya Formül Parçacığı")
    points = models.IntegerField(default=10, verbose_name="Puan Değeri")
    order = models.IntegerField(default=0, verbose_name="Sıralama")
    is_active = models.BooleanField(default=True, verbose_name="Aktif mi?")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Oluşturulma Tarihi")

    class Meta:
        verbose_name = "Soru"
        verbose_name_plural = "Sorular"
        ordering = ["order", "created_at"]

    def __str__(self):
        return f"[{self.category.name}] {self.text[:50]}..."


class Choice(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    question = models.ForeignKey(
        Question,
        on_delete=models.CASCADE,
        related_name="choices",
        verbose_name="Soru"
    )
    text = models.CharField(max_length=255, verbose_name="Şık Metni")
    is_correct = models.BooleanField(default=False, verbose_name="Doğru Şık mı?")

    class Meta:
        verbose_name = "Şık"
        verbose_name_plural = "Şıklar"

    def __str__(self):
        return f"{self.text} ({'✓ Doğru' if self.is_correct else '✗ Yanlış'})"


class Score(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    category = models.ForeignKey(
        Category,
        on_delete=models.CASCADE,
        related_name="scores",
        null=True,
        blank=True,
        verbose_name="Kategori"
    )
    player_name = models.CharField(max_length=50, verbose_name="Oyuncu Adı")
    total_score = models.IntegerField(default=0, verbose_name="Toplam Skor")
    correct_count = models.IntegerField(default=0, verbose_name="Doğru Sayısı")
    wrong_count = models.IntegerField(default=0, verbose_name="Yanlış Sayısı")
    empty_count = models.IntegerField(default=0, verbose_name="Boş Sayısı")
    total_time_taken = models.FloatField(default=0.0, verbose_name="Toplam Süre (sn)")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Kayıt Tarihi")

    class Meta:
        verbose_name = "Skor Kaydı"
        verbose_name_plural = "Skor Kayıtları"
        ordering = ["-total_score", "total_time_taken", "-created_at"]

    def __str__(self):
        cat_name = self.category.name if self.category else "Global"
        return f"{self.player_name} - {cat_name}: {self.total_score} Puan"
