import os
import re
import unicodedata
from django.utils.text import slugify
from quiz_api.models import Category, Question, Choice

def turkish_slugify(text):
    """Generates a clean slug handling Turkish characters"""
    text = text.replace("ı", "i").replace("İ", "i").replace("ğ", "g").replace("Ğ", "g")
    text = text.replace("ş", "s").replace("Ş", "s").replace("ç", "c").replace("Ç", "c")
    text = text.replace("ö", "o").replace("Ö", "o").replace("ü", "u").replace("Ü", "u")
    slug = slugify(text)
    return slug or "ai-quiz"

def generate_ai_quiz(topic: str):
    """
    Generates a 5-question 10-second reflex quiz on any user-provided topic
    using Gemini API (with fallback if key not configured).
    Saves the category and questions into DB, then returns ready-to-play category data.
    """
    topic_clean = topic.strip()
    if not topic_clean:
        topic_clean = "Genel Kültür"

    api_key = os.environ.get("GEMINI_API_KEY", "").strip()
    quiz_data = None

    if api_key:
        try:
            from google import genai
            from google.genai import types

            client = genai.Client(api_key=api_key)
            prompt = f"""
Sen profesyonel bir quiz içerik üreticisisin.
Konu: "{topic_clean}"

Lütfen bu konu hakkında tam 5 adet özgün, ilgi çekici ve 10 saniyelik refleks testine uygun çoktan seçmeli soru hazırla.
Her soruda:
- Anlaşılır, vurucu bir soru metni
- 4 adet şık (1 doğru, 3 mantıklı/yanıltıcı yanlış şık)

Çıktıyı kesinlikle aşağıdaki JSON şemasında ver:
{{
  "category_name": "AI: {topic_clean.title()}",
  "questions": [
    {{
      "text": "Soru metni?",
      "choices": [
        {{"text": "Doğru Cevap", "is_correct": true}},
        {{"text": "Yanlış Seçenek 1", "is_correct": false}},
        {{"text": "Yanlış Seçenek 2", "is_correct": false}},
        {{"text": "Yanlış Seçenek 3", "is_correct": false}}
      ]
    }}
  ]
}}
"""
            response = client.models.generate_content(
                model="gemini-2.5-flash",
                contents=prompt,
                config=types.GenerateContentConfig(
                    response_mime_type="application/json",
                    temperature=0.7,
                ),
            )
            import json
            quiz_data = json.loads(response.text)
        except Exception as e:
            print(f"[AI Generator] Gemini API error, falling back: {e}")
            quiz_data = None

    # Fallback generator if no API key or error
    if not quiz_data or "questions" not in quiz_data or len(quiz_data["questions"]) == 0:
        quiz_data = _generate_fallback_quiz(topic_clean)

    # Save to Database
    category_slug = f"ai-{turkish_slugify(topic_clean)[:30]}"
    category_name = f"AI: {topic_clean.title()}"

    category, _ = Category.objects.update_or_create(
        slug=category_slug,
        defaults={
            "name": category_name[:100],
            "icon": "Sparkles",
            "color_theme": "purple",
            "music_url": "https://assets.mixkit.co/music/preview/mixkit-tech-house-vibes-130.mp3",
            "music_title": "AI Neural Pulse - Synthwave Generation",
            "is_active": True,
        }
    )

    # Clean existing questions for this AI category
    category.questions.all().delete()

    created_questions = []
    for order, q_info in enumerate(quiz_data["questions"][:5], start=1):
        q = Question.objects.create(
            category=category,
            text=q_info["text"],
            points=10,
            order=order,
            is_active=True,
        )
        for ch_info in q_info["choices"][:4]:
            Choice.objects.create(
                question=q,
                text=ch_info["text"],
                is_correct=bool(ch_info["is_correct"]),
            )
        created_questions.append(q)

    # Format output for frontend (hiding is_correct)
    questions_output = []
    for q in created_questions:
        choices_output = []
        for c in q.choices.all():
            choices_output.append({
                "id": str(c.id),
                "text": c.text,
            })
        questions_output.append({
            "id": str(q.id),
            "text": q.text,
            "code_snippet": None,
            "points": q.points,
            "order": q.order,
            "choices": choices_output,
        })

    return {
        "category": category.name,
        "category_slug": category.slug,
        "icon": category.icon,
        "color_theme": category.color_theme,
        "music_url": category.music_url,
        "music_title": category.music_title,
        "time_per_question": 10,
        "total_questions": len(questions_output),
        "questions": questions_output,
    }


def _generate_fallback_quiz(topic: str):
    """Fallback generator with tailored smart templates for any topic"""
    t = topic.title()
    return {
        "category_name": f"AI: {t}",
        "questions": [
            {
                "text": f"'{t}' denildiğinde bu alanda temel yapı taşı veya en çok bilinen kavram hangisidir?",
                "choices": [
                    {"text": f"{t} Çekirdek Prensibi", "is_correct": True},
                    {"text": "Rastgele Dalgaboyu Modeli", "is_correct": False},
                    {"text": "Statik Değişken Döngüsü", "is_correct": False},
                    {"text": "Kritik Eşik Boşluğu", "is_correct": False}
                ]
            },
            {
                "text": f"Aşağıdakilerden hangisi '{t}' konusunun gelişimine en büyük katkıyı sağlamıştır?",
                "choices": [
                    {"text": "Modern Araştırma ve Teknolojik Gelişmeler", "is_correct": True},
                    {"text": "Geleneksel Manuel Hesaplamalar", "is_correct": False},
                    {"text": "İnternet Öncesi İletişim Kanalları", "is_correct": False},
                    {"text": "Mekanik Buhar Pistonları", "is_correct": False}
                ]
            },
            {
                "text": f"'{t}' alanındaki en kritik zorluk veya tartışma konusu genellikle nedir?",
                "choices": [
                    {"text": "Verimlilik, Güvenlik ve Ölçeklenebilirlik", "is_correct": True},
                    {"text": "Kağıt Tüketimi Miktarı", "is_correct": False},
                    {"text": "Ofis Masalarının Düzeni", "is_correct": False},
                    {"text": "Hava Basıncı Seviyesi", "is_correct": False}
                ]
            },
            {
                "text": f"Geleceğe yönelik trendlere göre '{t}' alanı en çok hangi sektörle entegre olmaktadır?",
                "choices": [
                    {"text": "Yapay Zeka ve Dijital Otomasyon", "is_correct": True},
                    {"text": "Geleneksel Matbaacılık", "is_correct": False},
                    {"text": "Telgraf Şebekeleri", "is_correct": False},
                    {"text": "Daktilo Üretimi", "is_correct": False}
                ]
            },
            {
                "text": f"Bir uzman '{t}' alanında başarı sağlamak için öncelikle hangi beceriye odaklanmalıdır?",
                "choices": [
                    {"text": "Analitik Düşünme ve Problem Çözme", "is_correct": True},
                    {"text": "Yalnızca Ezberleme Yeteneği", "is_correct": False},
                    {"text": "Hızlı Klavye Yazımı", "is_correct": False},
                    {"text": "Monitör Parlaklığını Azaltma", "is_correct": False}
                ]
            }
        ]
    }
