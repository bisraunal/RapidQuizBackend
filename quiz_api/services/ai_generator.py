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
    1. First tries live Gemini API (if GEMINI_API_KEY configured).
    2. If no key, searches rich curated domain banks (Coğrafya, Kuantum, LOTR, vb.).
    3. If topic is unknown and no key is present, raises a clear descriptive error.
    """
    topic_clean = topic.strip()
    if not topic_clean:
        topic_clean = "Genel Kültür"

    api_key = os.environ.get("GEMINI_API_KEY", "").strip()
    quiz_data = None
    last_api_error = None

    # --- 1. Real Gemini API Generation ---
    if api_key:
        try:
            from google import genai
            from google.genai import types

            client = genai.Client(api_key=api_key, http_options={"timeout": 25000})
            prompt = f"""
Sen uzman bir bilgi yarışması soru yazarısın.
Konu: "{topic_clean}"

Lütfen doğrudan "{topic_clean}" konusuyla ilgili tam 5 adet özgün, ilgi çekici, mantıklı ve 10 saniyelik refleks testine uygun çoktan seçmeli soru hazırla.

KESİN KURALLAR:
1. Sorular tamamen ve sadece "{topic_clean}" konusunun gerçek bilgileriyle (tarihler, kişiler, eserler, kavramlar, terimler) ilgili olmalıdır. Asla genel geçer veya uydurma sorular yazma.
2. Her sorunun tam 4 şıkkı olmalıdır (1 doğru, 3 mantıklı ve o konuya ait yanlış şık).
3. Yanlış şıklar da konuyla ilgili gerçekçi kavramlar olmalıdır; asla 'Hiçbiri', 'Hepsi' veya anlamsız kelimeler kullanma.
4. Doğru şıkkı 'choices' dizisinde rastgele bir sıraya koy (sürekli ilk sırada olmasın).

Çıktıyı sadece aşağıdaki JSON formatında ver:
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
            models_to_try = [
                "gemini-3.5-flash-lite",
                "gemini-3.5-flash",
                "gemini-3.8-flash",
                "gemini-2.5-flash",
            ]
            for model_name in models_to_try:
                try:
                    response = client.models.generate_content(
                        model=model_name,
                        contents=prompt,
                        config=types.GenerateContentConfig(
                            response_mime_type="application/json",
                            temperature=0.7,
                        ),
                    )
                    parsed = json.loads(response.text)
                    if parsed and "questions" in parsed and len(parsed["questions"]) >= 5:
                        quiz_data = parsed
                        break
                except Exception as m_err:
                    last_api_error = str(m_err)
                    continue
        except Exception as e:
            print(f"[AI Generator] Gemini API call failed: {e}")
            last_api_error = str(e)
            quiz_data = None

    # --- 2. Curated Domain Knowledge Base ---
    if not quiz_data or "questions" not in quiz_data or len(quiz_data["questions"]) < 5:
        curated = _get_curated_knowledge_bank(topic_clean)
        if curated:
            quiz_data = curated

    # --- 3. If Still No Questions (Unknown topic & No API Key or API error) ---
    if not quiz_data or "questions" not in quiz_data or len(quiz_data["questions"]) < 5:
        if last_api_error:
            raise ValueError(
                f"Gemini API ile soru üretilirken hata oluştu: {last_api_error}. "
                "Lütfen API anahtarınızı veya internet bağlantınızı kontrol edin."
            )
        else:
            raise ValueError(
                f"'{topic_clean}' konusu için canlı yapay zeka üretimi yapmak üzere "
                "Backend'de GEMINI_API_KEY tanımlanmalıdır. Lütfen önerilen konulardan birini seçin "
                "veya .env dosyasına Gemini API anahtarınızı ekleyin."
            )

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

        raw_choices = list(q_info["choices"][:4])
        random.shuffle(raw_choices)

        for ch_info in raw_choices:
            Choice.objects.create(
                question=q,
                text=ch_info["text"],
                is_correct=bool(ch_info.get("is_correct", False)),
            )
        created_questions.append(q)

    # Output formatting for frontend (is_correct hidden)
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


def _get_curated_knowledge_bank(topic: str):
    """
    Rich, accurate, 100% verified question pools for popular subjects.
    Never produces generic or nonsensical answers.
    """
    t = topic.lower().strip()

    # --- Coğrafya ---
    if any(k in t for k in ["coğrafya", "cografya", "dünya", "dunya", "harita", "kıta"]):
        return {
            "category_name": f"AI: Coğrafya",
            "questions": [
                {
                    "text": "Dünyanın en yüksek zirvesi olan Everest Tepesi hangi dağ silsilesinde yer alır?",
                    "choices": [
                        {"text": "Himalayalar", "is_correct": True},
                        {"text": "And Dağları", "is_correct": False},
                        {"text": "Alpler", "is_correct": False},
                        {"text": "Ural Dağları", "is_correct": False}
                    ]
                },
                {
                    "text": "Dünyanın en derin noktası olan Mariana Çukuru (yaklaşık 11.000 metre) hangi okyanustadır?",
                    "choices": [
                        {"text": "Büyük Okyanus (Pasifik)", "is_correct": True},
                        {"text": "Atlas Okyanusu (Atlantik)", "is_correct": False},
                        {"text": "Hint Okyanusu", "is_correct": False},
                        {"text": "Kuzey Buz Denizi (Arktik)", "is_correct": False}
                    ]
                },
                {
                    "text": "Türkiye sınırları içerisinden doğup Karadeniz'e dökülen en uzun nehir hangisidir?",
                    "choices": [
                        {"text": "Kızılırmak", "is_correct": True},
                        {"text": "Yeşilırmak", "is_correct": False},
                        {"text": "Fırat", "is_correct": False},
                        {"text": "Sakarya", "is_correct": False}
                    ]
                },
                {
                    "text": "Dünyanın en büyük sıcak çölü olan Büyük Sahra Çölü hangi kıtada yer alır?",
                    "choices": [
                        {"text": "Afrika", "is_correct": True},
                        {"text": "Asya", "is_correct": False},
                        {"text": "Güney Amerika", "is_correct": False},
                        {"text": "Avustralya", "is_correct": False}
                    ]
                },
                {
                    "text": "Dünyanın kendi ekseni etrafında batıdan doğuya dönmesi sonucunda hangisi gerçekleşir?",
                    "choices": [
                        {"text": "Gece ve gündüzün birbirini takip etmesi", "is_correct": True},
                        {"text": "Dört mevsimin oluşması", "is_correct": False},
                        {"text": "Güneş ışınlarının yıllık düşme açısının değişmesi", "is_correct": False},
                        {"text": "Ay tutulmasının meydana gelmesi", "is_correct": False}
                    ]
                }
            ]
        }

    # --- Kuantum / Fizik ---
    if any(k in t for k in ["kuantum", "quantum", "fizik", "atom", "parçacık"]):
        return {
            "category_name": f"AI: Kuantum Fiziği",
            "questions": [
                {
                    "text": "Schrödinger'in kedisi düşünce deneyi, kuantum fiziğindeki hangi ilkeyi anlatmak için tasarlanmıştır?",
                    "choices": [
                        {"text": "Kuantum Süperpozisyonu", "is_correct": True},
                        {"text": "Kuantum Dolanıklığı", "is_correct": False},
                        {"text": "Fotoelektrik Rezonans", "is_correct": False},
                        {"text": "Doppler Etkisi", "is_correct": False}
                    ]
                },
                {
                    "text": "Heisenberg Belirsizlik İlkesine göre bir mikro parçacığın hangi iki özelliği aynı anda kesin ölçülemez?",
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
                    "text": "Kuantum bilgisayarlarında klasik 0 ve 1 bitleri yerine kullanılan temel hesaplama birimi nedir?",
                    "choices": [
                        {"text": "Qubit (Kuantum Bit)", "is_correct": True},
                        {"text": "Teraflop", "is_correct": False},
                        {"text": "Nanobyte", "is_correct": False},
                        {"text": "Foton Transistörü", "is_correct": False}
                    ]
                },
                {
                    "text": "Bir parçacığın klasik fizikte aşamayacağı bir enerji bariyerini dalga özelliğiyle geçebilmesine ne denir?",
                    "choices": [
                        {"text": "Kuantum Tünelleme (Quantum Tunneling)", "is_correct": True},
                        {"text": "Işık Kırılması", "is_correct": False},
                        {"text": "Nükleer Füzyon", "is_correct": False},
                        {"text": "Manyetik Rezonans", "is_correct": False}
                    ]
                }
            ]
        }

    # --- Yüzüklerin Efendisi / LOTR ---
    if any(k in t for k in ["yüzük", "yuzuk", "lotr", "lord of the rings", "frodo", "tolkien", "orta dünya"]):
        return {
            "category_name": f"AI: Yüzüklerin Efendisi",
            "questions": [
                {
                    "text": "Tek Yüzük'ü yok etmek amacıyla kurulan Yüzük Kardeşliği kaç üyeden oluşmaktadır?",
                    "choices": [
                        {"text": "9 Kişi", "is_correct": True},
                        {"text": "7 Kişi", "is_correct": False},
                        {"text": "11 Kişi", "is_correct": False},
                        {"text": "12 Kişi", "is_correct": False}
                    ]
                },
                {
                    "text": "Tek Yüzük'ün eritilerek yok edilebileceği Orta Dünya'daki tek volkanik yanardağ neresidir?",
                    "choices": [
                        {"text": "Hüküm Dağı (Mount Doom)", "is_correct": True},
                        {"text": "Yalnız Dağ (Erebor)", "is_correct": False},
                        {"text": "Puslu Dağlar", "is_correct": False},
                        {"text": "Demir Tepeler", "is_correct": False}
                    ]
                },
                {
                    "text": "Gondor'un gerçek varisi olan ve 'Yolgezer' adıyla tanınan Kolcu kimdir?",
                    "choices": [
                        {"text": "Aragorn", "is_correct": True},
                        {"text": "Boromir", "is_correct": False},
                        {"text": "Faramir", "is_correct": False},
                        {"text": "Theoden", "is_correct": False}
                    ]
                },
                {
                    "text": "Gandalf, Khazad-dûm Köprüsü'nde Balrog'u durdururken hangi unutulmaz repliği haykırmıştır?",
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

    # --- Cyberpunk 2077 / Oyun Dünyası ---
    if any(k in t for k in ["cyberpunk", "cyber", "oyun", "gaming", "witcher", "gta"]):
        return {
            "category_name": f"AI: Cyberpunk 2077",
            "questions": [
                {
                    "text": "Cyberpunk 2077 evreninde ana hikayenin geçtiği distopik metropolün adı nedir?",
                    "choices": [
                        {"text": "Night City", "is_correct": True},
                        {"text": "Raccoon City", "is_correct": False},
                        {"text": "Los Santos", "is_correct": False},
                        {"text": "Neo Tokyo", "is_correct": False}
                    ]
                },
                {
                    "text": "Cyberpunk 2077'de Johnny Silverhand karakterini canlandıran ünlü Hollywood aktörü kimdir?",
                    "choices": [
                        {"text": "Keanu Reeves", "is_correct": True},
                        {"text": "Mads Mikkelsen", "is_correct": False},
                        {"text": "Idris Elba", "is_correct": False},
                        {"text": "Norman Reedus", "is_correct": False}
                    ]
                },
                {
                    "text": "Night City'nin en güçlü Japon kökenli acımasız megacorporation (mega şirket) devi hangisidir?",
                    "choices": [
                        {"text": "Arasaka", "is_correct": True},
                        {"text": "Umbrella Corporation", "is_correct": False},
                        {"text": "Vault-Tec", "is_correct": False},
                        {"text": "Aperture Science", "is_correct": False}
                    ]
                },
                {
                    "text": "Cyberpunk evreninde siber donanımların aşırı yüklenmesiyle zihnini kaybeden saldırganlara ne denir?",
                    "choices": [
                        {"text": "Cyberpsycho (Siberpsikotik)", "is_correct": True},
                        {"text": "Netrunner", "is_correct": False},
                        {"text": "Fixer", "is_correct": False},
                        {"text": "Solo", "is_correct": False}
                    ]
                },
                {
                    "text": "Cyberpunk 2077 ve The Witcher serisinin arkasındaki ünlü oyun stüdyosu hangisidir?",
                    "choices": [
                        {"text": "CD Projekt RED", "is_correct": True},
                        {"text": "Rockstar Games", "is_correct": False},
                        {"text": "Bethesda", "is_correct": False},
                        {"text": "Ubisoft", "is_correct": False}
                    ]
                }
            ]
        }

    # --- Mitoloji ---
    if any(k in t for k in ["mitoloji", "mythology", "zeus", "thor", "odin", "yunan", "iskandinav"]):
        return {
            "category_name": f"AI: Mitoloji",
            "questions": [
                {
                    "text": "İskandinav mitolojisinde şimşek tanrısı Thor'un kullandığı efsanevi çekicin adı nedir?",
                    "choices": [
                        {"text": "Mjölnir", "is_correct": True},
                        {"text": "Gungnir", "is_correct": False},
                        {"text": "Gram", "is_correct": False},
                        {"text": "Hofud", "is_correct": False}
                    ]
                },
                {
                    "text": "Yunan mitolojisinde ölüler diyarı ve yer altı dünyasının hükümdarı olan tanrı kimdir?",
                    "choices": [
                        {"text": "Hades", "is_correct": True},
                        {"text": "Poseidon", "is_correct": False},
                        {"text": "Ares", "is_correct": False},
                        {"text": "Dionysos", "is_correct": False}
                    ]
                },
                {
                    "text": "İskandinav mitolojisinde tanrıların ve evrenin sonunu simgeleyen kıyamet savaşına ne denir?",
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

    # --- Formula 1 ---
    if any(k in t for k in ["formula", "f1", "yarış", "motorsport", "ferrari", "hız"]):
        return {
            "category_name": f"AI: Formula 1",
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
                    "text": "F1 araçlarında hava direncini azaltarak geçiş kolaylığı sağlayan hareketli arka kanat sistemine ne denir?",
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
                    "text": "Pilotların baş ve boyun bölgesini korumak için kokpitin üstüne takılan titanyum yapının adı nedir?",
                    "choices": [
                        {"text": "Halo", "is_correct": True},
                        {"text": "Aeroscreen", "is_correct": False},
                        {"text": "Roll Hoop", "is_correct": False},
                        {"text": "Crash Box", "is_correct": False}
                    ]
                }
            ]
        }

    # --- Edebiyat ---
    if any(k in t for k in ["edebiyat", "roman", "kitap", "yazar", "şiir"]):
        return {
            "category_name": f"AI: Edebiyat",
            "questions": [
                {
                    "text": "Dostoyevski'nin Raskolnikov karakterinin vicdan muhasebesini anlattığı başyapıtı hangisidir?",
                    "choices": [
                        {"text": "Suç ve Ceza", "is_correct": True},
                        {"text": "Karamazov Kardeşler", "is_correct": False},
                        {"text": "Budala", "is_correct": False},
                        {"text": "Yeraltından Notlar", "is_correct": False}
                    ]
                },
                {
                    "text": "'Kürk Mantolu Madonna' ve 'Kuyucaklı Yusuf' romanlarının usta yazarı kimdir?",
                    "choices": [
                        {"text": "Sabahattin Ali", "is_correct": True},
                        {"text": "Reşat Nuri Güntekin", "is_correct": False},
                        {"text": "Yaşar Kemal", "is_correct": False},
                        {"text": "Orhan Pamuk", "is_correct": False}
                    ]
                },
                {
                    "text": "İstiklal Marşı'mızın şairi olan milli edebiyatçımız kimdir?",
                    "choices": [
                        {"text": "Mehmet Akif Ersoy", "is_correct": True},
                        {"text": "Tevfik Fikret", "is_correct": False},
                        {"text": "Yahya Kemal Beyatlı", "is_correct": False},
                        {"text": "Ziya Gökalp", "is_correct": False}
                    ]
                },
                {
                    "text": "Çukurova'nın efsanevi başkaldırı hikayesi 'İnce Memed' serisinin yazarı kimdir?",
                    "choices": [
                        {"text": "Yaşar Kemal", "is_correct": True},
                        {"text": "Kemal Tahir", "is_correct": False},
                        {"text": "Orhan Kemal", "is_correct": False},
                        {"text": "Tarık Buğra", "is_correct": False}
                    ]
                },
                {
                    "text": "Türk edebiyatındaki ilk yerli roman kabul edilen 'Taaşşuk-ı Tal'at ve Fitnat'ın yazarı kimdir?",
                    "choices": [
                        {"text": "Şemsettin Sami", "is_correct": True},
                        {"text": "Namık Kemal", "is_correct": False},
                        {"text": "Ahmet Mithat Efendi", "is_correct": False},
                        {"text": "Recaizade Mahmut Ekrem", "is_correct": False}
                    ]
                }
            ]
        }

    # --- Biyoloji / Sağlık ---
    if any(k in t for k in ["biyoloji", "hücre", "insan", "vücut", "sağlık", "genetik"]):
        return {
            "category_name": f"AI: Biyoloji",
            "questions": [
                {
                    "text": "Hücrenin temel enerji santrali olarak ATP üreten organel hangisidir?",
                    "choices": [
                        {"text": "Mitokondri", "is_correct": True},
                        {"text": "Ribozom", "is_correct": False},
                        {"text": "Lizozom", "is_correct": False},
                        {"text": "Golgi Cisimciği", "is_correct": False}
                    ]
                },
                {
                    "text": "İnsan kanında dokulara oksijen taşımakla görevli kırmızı kan hücrelerine ne denir?",
                    "choices": [
                        {"text": "Alyuvar (Eritrosit)", "is_correct": True},
                        {"text": "Akyuvar (Lökosit)", "is_correct": False},
                        {"text": "Trombosit (Kan Pulcuğu)", "is_correct": False},
                        {"text": "Plazma", "is_correct": False}
                    ]
                },
                {
                    "text": "DNA'nın çift sarmallı yapısında Adenin (A) bazının karşısına daima hangi baz gelir?",
                    "choices": [
                        {"text": "Timin (T)", "is_correct": True},
                        {"text": "Guanin (G)", "is_correct": False},
                        {"text": "Sitozin (C)", "is_correct": False},
                        {"text": "Urasil (U)", "is_correct": False}
                    ]
                },
                {
                    "text": "İnsan vücudundaki en büyük iç organ hangisidir?",
                    "choices": [
                        {"text": "Karaciğer", "is_correct": True},
                        {"text": "Akciğer", "is_correct": False},
                        {"text": "Kalp", "is_correct": False},
                        {"text": "Böbrek", "is_correct": False}
                    ]
                },
                {
                    "text": "Klorofil pigmentine sahip bitkilerin güneş ışığıyla organik besin üretmesine ne denir?",
                    "choices": [
                        {"text": "Fotosentez", "is_correct": True},
                        {"text": "Kemosentez", "is_correct": False},
                        {"text": "Fermantasyon", "is_correct": False},
                        {"text": "Hücresel Solunum", "is_correct": False}
                    ]
                }
            ]
        }

    return None
