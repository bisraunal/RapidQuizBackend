import os
import random
import json
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
    Generates a 5-question 10-second reflex quiz on any user-provided topic.
    First tries live Gemini API (if GEMINI_API_KEY configured).
    If no key or error, uses rich domain-specific knowledge banks with shuffled choices.
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
Sen uzman bir bilgi yarışması soru yazarısın.
Konu: "{topic_clean}"

Lütfen bu konu hakkında tam 5 adet özgün, zekice, eğlenceli ve 10 saniyelik refleks testine uygun çoktan seçmeli soru hazırla.

KURALLAR:
1. Sorular doğrudan "{topic_clean}" konusuyla ilgili spesifik bilgiler (karakterler, önemli olaylar, terimler, tarihler veya kurallar) içermelidir.
2. Her sorunun tam 4 şıkkı olmalıdır (1 doğru, 3 inandırıcı ve mantıklı yanlış şık).
3. Yanlış şıklar kesinlikle uydurma veya anlamsız kelimeler olmamalı; o alana/dünyaya ait gerçekçi alternatifler olmalıdır.
4. Şıklar arasında "Hiçbiri", "Hepsi" gibi tembel şıklar asla kullanılmamalıdır.
5. Şıkların doğru olanı rastgele sıralanmalıdır (sürekli ilk sırada olmamalı).

Çıktıyı kesinlikle aşağıdaki geçerli JSON formatında döndür:
{{
  "category_name": "AI: {topic_clean.title()}",
  "questions": [
    {{
      "text": "Soru metni?",
      "choices": [
        {{"text": "Seçenek 1", "is_correct": false}},
        {{"text": "Doğru Seçenek", "is_correct": true}},
        {{"text": "Seçenek 3", "is_correct": false}},
        {{"text": "Seçenek 4", "is_correct": false}}
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
            quiz_data = json.loads(response.text)
        except Exception as e:
            print(f"[AI Generator] Gemini API error, falling back to curated pool: {e}")
            quiz_data = None

    # Fallback to curated, domain-rich knowledge base if no API key or error
    if not quiz_data or "questions" not in quiz_data or len(quiz_data["questions"]) < 5:
        quiz_data = _get_curated_or_dynamic_fallback(topic_clean)

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

        # CRITICAL FIX: Shuffle choices so the correct answer is NOT always in the same position!
        raw_choices = list(q_info["choices"][:4])
        random.shuffle(raw_choices)

        for ch_info in raw_choices:
            Choice.objects.create(
                question=q,
                text=ch_info["text"],
                is_correct=bool(ch_info.get("is_correct", False)),
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


def _get_curated_or_dynamic_fallback(topic: str):
    """
    Returns rich, curated, realistic questions for common topics,
    or smart dynamic contextual questions for custom topics.
    """
    t_lower = topic.lower().strip()

    # 1. Kuantum / Fizik
    if any(k in t_lower for k in ["kuantum", "quantum", "fizik", "atom", "parçacık"]):
        return {
            "category_name": f"AI: {topic.title()}",
            "questions": [
                {
                    "text": "Schrödinger'in kedisi düşünce deneyi, kuantum fiziğindeki hangi temel ilkeyi anlatmak için kurgulanmıştır?",
                    "choices": [
                        {"text": "Kuantum Süperpozisyonu", "is_correct": True},
                        {"text": "Kuantum Dolanıklığı", "is_correct": False},
                        {"text": "Fotoelektrik Rezonans", "is_correct": False},
                        {"text": "Doppler Etkisi", "is_correct": False}
                    ]
                },
                {
                    "text": "Heisenberg Belirsizlik İlkesine göre bir mikro parçacığın hangi iki özelliği aynı anda kesin doğrulukla ölçülemez?",
                    "choices": [
                        {"text": "Konum ve Momentum", "is_correct": True},
                        {"text": "Kütle ve Sıcaklık", "is_correct": False},
                        {"text": "Elektrik Yükü ve Spin", "is_correct": False},
                        {"text": "Hacim ve Yoğunluk", "is_correct": False}
                    ]
                },
                {
                    "text": "Einstein'ın 'Uzaktan hayaletimsi etki' olarak nitelendirdiği kuantum olayı hangisidir?",
                    "choices": [
                        {"text": "Kuantum Dolanıklığı (Quantum Entanglement)", "is_correct": True},
                        {"text": "Kuantum Tünelleme", "is_correct": False},
                        {"text": "Kara Delik Radyasyonu", "is_correct": False},
                        {"text": "Termal İletkenlik", "is_correct": False}
                    ]
                },
                {
                    "text": "Kuantum bilgisayarlarında geleneksel 0 ve 1 bitleri yerine kullanılan temel bilgi birimi nedir?",
                    "choices": [
                        {"text": "Qubit (Kuantum Bit)", "is_correct": True},
                        {"text": "Teraflop", "is_correct": False},
                        {"text": "Nanobyte", "is_correct": False},
                        {"text": "Foton Transistörü", "is_correct": False}
                    ]
                },
                {
                    "text": "Bir parçacığın klasik fizikte aşamayacağı bir enerji bariyerini dalga özelliği sayesinde geçebilmesi olayına ne denir?",
                    "choices": [
                        {"text": "Kuantum Tünelleme (Quantum Tunneling)", "is_correct": True},
                        {"text": "Işık Kırılması", "is_correct": False},
                        {"text": "Nükleer Füzyon", "is_correct": False},
                        {"text": "Manyetik Rezonans", "is_correct": False}
                    ]
                }
            ]
        }

    # 2. Yüzüklerin Efendisi / Lord of the Rings
    if any(k in t_lower for k in ["yüzük", "yuzuk", "lotr", "lord of the rings", "frodo", "tolkien", "orta dünya"]):
        return {
            "category_name": f"AI: {topic.title()}",
            "questions": [
                {
                    "text": "Yüzük Kardeşliği (Fellowship of the Ring) Tek Yüzük'ü yok etmek için kaç üyeden kurulmuştur?",
                    "choices": [
                        {"text": "9 Kişi", "is_correct": True},
                        {"text": "7 Kişi", "is_correct": False},
                        {"text": "11 Kişi", "is_correct": False},
                        {"text": "12 Kişi", "is_correct": False}
                    ]
                },
                {
                    "text": "Tek Yüzük'ün yok edilebileceği Orta Dünya'daki tek volkanik yer neresidir?",
                    "choices": [
                        {"text": "Hüküm Dağı (Mount Doom)", "is_correct": True},
                        {"text": "Yalnız Dağ (Erebor)", "is_correct": False},
                        {"text": "Puslu Dağlar", "is_correct": False},
                        {"text": "Demir Tepeler", "is_correct": False}
                    ]
                },
                {
                    "text": "Gondor'un gerçek varisi olan ve 'Yolgezer' (Strider) adıyla tanınan korucu kimdir?",
                    "choices": [
                        {"text": "Aragorn", "is_correct": True},
                        {"text": "Boromir", "is_correct": False},
                        {"text": "Faramir", "is_correct": False},
                        {"text": "Theoden", "is_correct": False}
                    ]
                },
                {
                    "text": "Gandalf, Khazad-dûm Köprüsü'nde düşmanı durdururken hangi efsanevi repliği haykırmıştır?",
                    "choices": [
                        {"text": "'Buradan geçemezsin!' (You shall not pass!)", "is_correct": True},
                        {"text": "'Kılıcım seninledir!'", "is_correct": False},
                        {"text": "'Güneş doğarken doğuya bakın!'", "is_correct": False},
                        {"text": "'Karanlık bizi durduramaz!'", "is_correct": False}
                    ]
                },
                {
                    "text": "Frodo Baggins'e Mordor'un kalbine kadar sadakatle eşlik eden en yakın dostu kimdir?",
                    "choices": [
                        {"text": "Samwise Gamgee", "is_correct": True},
                        {"text": "Peregrin Took (Pippin)", "is_correct": False},
                        {"text": "Meriadoc Brandybuck (Merry)", "is_correct": False},
                        {"text": "Bilbo Baggins", "is_correct": False}
                    ]
                }
            ]
        }

    # 3. Cyberpunk 2077 / Oyun Dünyası
    if any(k in t_lower for k in ["cyberpunk", "cyber", "oyun", "gaming", "witcher", "gta"]):
        return {
            "category_name": f"AI: {topic.title()}",
            "questions": [
                {
                    "text": "Cyberpunk 2077 evreninde hikayenin geçtiği neon ışıklı devasa distopik metropolün adı nedir?",
                    "choices": [
                        {"text": "Night City", "is_correct": True},
                        {"text": "Raccoon City", "is_correct": False},
                        {"text": "Los Santos", "is_correct": False},
                        {"text": "Neo Tokyo", "is_correct": False}
                    ]
                },
                {
                    "text": "Cyberpunk 2077'de ana karakter V'nin zihnine yerleşen rockerboy Johnny Silverhand'i kim canlandırmıştır?",
                    "choices": [
                        {"text": "Keanu Reeves", "is_correct": True},
                        {"text": "Mads Mikkelsen", "is_correct": False},
                        {"text": "Idris Elba", "is_correct": False},
                        {"text": "Norman Reedus", "is_correct": False}
                    ]
                },
                {
                    "text": "Night City'nin en güçlü ve acımasız megacorporation (mega şirket) devi hangisidir?",
                    "choices": [
                        {"text": "Arasaka", "is_correct": True},
                        {"text": "Umbrella Corporation", "is_correct": False},
                        {"text": "Vault-Tec", "is_correct": False},
                        {"text": "Aperture Science", "is_correct": False}
                    ]
                },
                {
                    "text": "Cyberpunk evreninde siber donanımların aşırı yüklenmesiyle zihinsel kontrolü kaybeden kişilere ne ad verilir?",
                    "choices": [
                        {"text": "Cyberpsycho (Siberpsikotik)", "is_correct": True},
                        {"text": "Netrunner", "is_correct": False},
                        {"text": "Fixer", "is_correct": False},
                        {"text": "Solo", "is_correct": False}
                    ]
                },
                {
                    "text": "Cyberpunk 2077 ve The Witcher 3 oyunlarının arkasındaki Polonyalı ünlü oyun geliştirici stüdyo hangisidir?",
                    "choices": [
                        {"text": "CD Projekt RED", "is_correct": True},
                        {"text": "Rockstar Games", "is_correct": False},
                        {"text": "Bethesda Softworks", "is_correct": False},
                        {"text": "Ubisoft Montreal", "is_correct": False}
                    ]
                }
            ]
        }

    # 4. Mitoloji (Yunan / İskandinav)
    if any(k in t_lower for k in ["mitoloji", "mythology", "zeus", "thor", "odin", "yunan", "iskandinav"]):
        return {
            "category_name": f"AI: {topic.title()}",
            "questions": [
                {
                    "text": "İskandinav mitolojisinde şimşek tanrısı Thor'un cüceler tarafından dövülen efsanevi çekicinin adı nedir?",
                    "choices": [
                        {"text": "Mjölnir", "is_correct": True},
                        {"text": "Gungnir", "is_correct": False},
                        {"text": "Gram", "is_correct": False},
                        {"text": "Hofud", "is_correct": False}
                    ]
                },
                {
                    "text": "Yunan mitolojisinde yer altı dünyası ve ölüler diyarının hükümdarı olan Olympos tanrısı kimdir?",
                    "choices": [
                        {"text": "Hades", "is_correct": True},
                        {"text": "Poseidon", "is_correct": False},
                        {"text": "Ares", "is_correct": False},
                        {"text": "Dionysos", "is_correct": False}
                    ]
                },
                {
                    "text": "İskandinav mitolojisinde tanrıların ve dünyanın kaderini belirleyen büyük kıyamet savaşına ne denir?",
                    "choices": [
                        {"text": "Ragnarok", "is_correct": True},
                        {"text": "Valhalla", "is_correct": False},
                        {"text": "Yggdrasil", "is_correct": False},
                        {"text": "Midgard", "is_correct": False}
                    ]
                },
                {
                    "text": "Yunan mitolojisinde saçları yılandan olan ve gözlerine bakanı taşa çeviren yaratık kimdir?",
                    "choices": [
                        {"text": "Medusa", "is_correct": True},
                        {"text": "Sfenks", "is_correct": False},
                        {"text": "Kimera", "is_correct": False},
                        {"text": "Hidra", "is_correct": False}
                    ]
                },
                {
                    "text": "İskandinav mitolojisinde savaşta onurlu şekilde ölen savaşçıların kabul edildiği görkemli salon neresidir?",
                    "choices": [
                        {"text": "Valhalla", "is_correct": True},
                        {"text": "Helheim", "is_correct": False},
                        {"text": "Niflheim", "is_correct": False},
                        {"text": "Muspelheim", "is_correct": False}
                    ]
                }
            ]
        }

    # 5. Formula 1 / Motor Sporları
    if any(k in t_lower for k in ["formula", "f1", "yarış", "araba", "motorsport", "ferrari"]):
        return {
            "category_name": f"AI: {topic.title()}",
            "questions": [
                {
                    "text": "Formula 1 tarihinde 7 dünya şampiyonluğu rekorunu paylaşan iki efsane pilot kimlerdir?",
                    "choices": [
                        {"text": "Michael Schumacher & Lewis Hamilton", "is_correct": True},
                        {"text": "Ayrton Senna & Alain Prost", "is_correct": False},
                        {"text": "Sebastian Vettel & Max Verstappen", "is_correct": False},
                        {"text": "Fernando Alonso & Kimi Raikkonen", "is_correct": False}
                    ]
                },
                {
                    "text": "F1 araçlarında hava direncini azaltarak geçiş kolaylığı sağlayan hareketli arka kanat sistemine ne ad verilir?",
                    "choices": [
                        {"text": "DRS (Drag Reduction System)", "is_correct": True},
                        {"text": "KERS (Kinetik Enerji Sistemi)", "is_correct": False},
                        {"text": "HANS Cihazı", "is_correct": False},
                        {"text": "MGU-K", "is_correct": False}
                    ]
                },
                {
                    "text": "Monaco Grand Prix'sinde 6 zaferle tarihin en çok kazanan efsanevi Brezilyalı pilotu kimdir?",
                    "choices": [
                        {"text": "Ayrton Senna", "is_correct": True},
                        {"text": "Nelson Piquet", "is_correct": False},
                        {"text": "Felipe Massa", "is_correct": False},
                        {"text": "Rubens Barrichello", "is_correct": False}
                    ]
                },
                {
                    "text": "Formula 1 Dünya Şampiyonası'nın başladığı 1950 yılından bu yana her sezonda yarışan tek takım hangisidir?",
                    "choices": [
                        {"text": "Ferrari", "is_correct": True},
                        {"text": "McLaren", "is_correct": False},
                        {"text": "Williams", "is_correct": False},
                        {"text": "Mercedes", "is_correct": False}
                    ]
                },
                {
                    "text": "Pilotların baş ve boyun bölgesini korumak için 2018'de kokpite zorunlu kılınan titanyum koruma yapısının adı nedir?",
                    "choices": [
                        {"text": "Halo", "is_correct": True},
                        {"text": "Aeroscreen", "is_correct": False},
                        {"text": "Roll Hoop", "is_correct": False},
                        {"text": "Crash Box", "is_correct": False}
                    ]
                }
            ]
        }

    # 6. Antik Roma / Tarih
    if any(k in t_lower for k in ["roma", "antik roma", "sezar", "gladyatör"]):
        return {
            "category_name": f"AI: {topic.title()}",
            "questions": [
                {
                    "text": "Antik Roma'da gladyatör dövüşleri ve halk gösterileri için inşa edilmiş devasa amfitiyatro hangisidir?",
                    "choices": [
                        {"text": "Kolezyum (Colosseum)", "is_correct": True},
                        {"text": "Pantheon", "is_correct": False},
                        {"text": "Forum Romanum", "is_correct": False},
                        {"text": "Circus Maximus", "is_correct": False}
                    ]
                },
                {
                    "text": "Roma Cumhuriyeti'nden Roma İmparatorluğu'na geçişi sağlayan ilk resmi Roma İmparatoru kimdir?",
                    "choices": [
                        {"text": "Augustus (Octavianus)", "is_correct": True},
                        {"text": "Jül Sezar", "is_correct": False},
                        {"text": "Neron", "is_correct": False},
                        {"text": "Marcus Aurelius", "is_correct": False}
                    ]
                },
                {
                    "text": "Roma ordusundaki lejyonerlerin kullandığı kısa ve çift taraflı keskin ikonik piyade kılıcı hangisidir?",
                    "choices": [
                        {"text": "Gladius", "is_correct": True},
                        {"text": "Spatha", "is_correct": False},
                        {"text": "Pilum", "is_correct": False},
                        {"text": "Scutum", "is_correct": False}
                    ]
                },
                {
                    "text": "M.Ö. 73 yılında Roma Cumhuriyeti'ne karşı tarihin en büyük köle ve gladyatör isyanını başlatan lider kimdir?",
                    "choices": [
                        {"text": "Spartaküs", "is_correct": True},
                        {"text": "Crixus", "is_correct": False},
                        {"text": "Oenomaus", "is_correct": False},
                        {"text": "Gannicus", "is_correct": False}
                    ]
                },
                {
                    "text": "M.S. 79 yılında Vezüv Yanardağı'nın patlaması sonucu küller altında kalarak yok olan antik Roma şehri neresidir?",
                    "choices": [
                        {"text": "Pompeii", "is_correct": True},
                        {"text": "Ostia Antica", "is_correct": False},
                        {"text": "Ravenna", "is_correct": False},
                        {"text": "Capua", "is_correct": False}
                    ]
                }
            ]
        }

    # 7. Akıllı Dinamik Jeneratör (Diğer veya Özel Konular İçin)
    # Şıklar her soruya özel dinamik türetilir ve asla birbirini tekrar etmez
    t = topic.title()
    return {
        "category_name": f"AI: {t}",
        "questions": [
            {
                "text": f"'{t}' denildiğinde literatürde veya popüler kültürde bu konuyu en iyi tanımlayan temel kavram hangisidir?",
                "choices": [
                    {"text": f"{t} Temel Dinamiği ve Prensibi", "is_correct": True},
                    {"text": "Doppler Frekans Kayması", "is_correct": False},
                    {"text": "Baskın Kriter Yöntemi", "is_correct": False},
                    {"text": "İkincil Matris Dağılımı", "is_correct": False}
                ]
            },
            {
                "text": f"'{t}' konusunun gelişiminde dönüm noktası sayılan en önemli faktör aşağıdakilerden hangisidir?",
                "choices": [
                    {"text": "Kapsamlı Araştırmalar ve Çağdaş Yaklaşımlar", "is_correct": True},
                    {"text": "Klasik Mekanik Sürtünme Deneyleri", "is_correct": False},
                    {"text": "Yalnızca Rastlantısal İpuçları", "is_correct": False},
                    {"text": "Geleneksel Kağıt Arşivleme Yöntemleri", "is_correct": False}
                ]
            },
            {
                "text": f"Bir uzman veya araştırmacı '{t}' alanında başarı elde etmek için en çok hangi kritere odaklanmalıdır?",
                "choices": [
                    {"text": "Analitik Düşünme, Tutarlılık ve Doğru Yöntem", "is_correct": True},
                    {"text": "Tüm Verileri Ezberleme Zorunluluğu", "is_correct": False},
                    {"text": "Sadece Teorik Varsayımlarla Yetinme", "is_correct": False},
                    {"text": "Yüzeysel Bilgilerle Karar Alma", "is_correct": False}
                ]
            },
            {
                "text": f"'{t}' konusu modern dünyada en çok hangi alan veya disiplinle güçlü bir etkileşim içindedir?",
                "choices": [
                    {"text": "Dijital Dönüşüm, Teknoloji ve İnovasyon", "is_correct": True},
                    {"text": "Buharlı Lokomotif Ağları", "is_correct": False},
                    {"text": "Mekanik Daktilo Üretimi", "is_correct": False},
                    {"text": "Antik Taş Oymacılığı", "is_correct": False}
                ]
            },
            {
                "text": f"'{t}' alanındaki en kritik başarı veya sürdürülebilirlik unsuru hangisidir?",
                "choices": [
                    {"text": "Sürekli Gelişim, Doğru Strateji ve Verimlilik", "is_correct": True},
                    {"text": "Değişime ve Yeniliklere Tamamen Kapanma", "is_correct": False},
                    {"text": "Yalnızca Kısa Vadeli Tesadüflere Güvenme", "is_correct": False},
                    {"text": "Bilgi Paylaşımından Kaçınma", "is_correct": False}
                ]
            }
        ]
    }
