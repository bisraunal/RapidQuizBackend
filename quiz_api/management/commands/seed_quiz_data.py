import uuid
from django.core.management.base import BaseCommand
from django.db import transaction
from quiz_api.models import Category, Question, Choice

CATEGORIES_DATA = [
    {
        "name": "Yazılım",
        "slug": "yazilim",
        "icon": "Code2",
        "color_theme": "cyan",
        "music_url": "https://assets.mixkit.co/music/preview/mixkit-cyber-city-110.mp3",
        "music_title": "Cyber City - Synthwave Code Beat",
        "questions": [
            {
                "text": "Python dilinde değiştirilemez (immutable) veri tipi hangisidir?",
                "points": 10,
                "order": 1,
                "choices": [
                    {"text": "Tuple", "is_correct": True},
                    {"text": "List", "is_correct": False},
                    {"text": "Dictionary", "is_correct": False},
                    {"text": "Set", "is_correct": False}
                ]
            },
            {
                "text": "JavaScript'te '===' operatörünün '==' den farkı nedir?",
                "points": 10,
                "order": 2,
                "choices": [
                    {"text": "Değer ile birlikte veri tipini de kontrol eder", "is_correct": True},
                    {"text": "Sadece string ifadeleri karşılaştırır", "is_correct": False},
                    {"text": "Tipleri otomatik olarak birbirine dönüştürür", "is_correct": False},
                    {"text": "Referans adreslerini karşılaştırmaz", "is_correct": False}
                ]
            },
            {
                "text": "Git'te yerel değişiklikleri commit yapmadan geçici olarak saklamak için hangi komut kullanılır?",
                "points": 10,
                "order": 3,
                "choices": [
                    {"text": "git stash", "is_correct": True},
                    {"text": "git save", "is_correct": False},
                    {"text": "git cache", "is_correct": False},
                    {"text": "git pause", "is_correct": False}
                ]
            },
            {
                "text": "REST mimarisinde bir kaynağı tamamen güncellemek için kullanılan standart idempotent HTTP metodu hangisidir?",
                "points": 10,
                "order": 4,
                "choices": [
                    {"text": "PUT", "is_correct": True},
                    {"text": "POST", "is_correct": False},
                    {"text": "PATCH", "is_correct": False},
                    {"text": "CONNECT", "is_correct": False}
                ]
            },
            {
                "text": "Nesne Yönelimli Programlamada (OOP) bir sınıfın başka bir sınıfın özellik ve metotlarını devralması ne olarak adlandırılır?",
                "points": 10,
                "order": 5,
                "choices": [
                    {"text": "Inheritance (Kalıtım)", "is_correct": True},
                    {"text": "Polymorphism (Çok Biçimlilik)", "is_correct": False},
                    {"text": "Encapsulation (Kapsülleme)", "is_correct": False},
                    {"text": "Abstraction (Soyutlama)", "is_correct": False}
                ]
            },
            {
                "text": "SQL'de tablodan çekilen verilerdeki tekrar eden kayıtları tekilleştirmek için hangi anahtar kelime kullanılır?",
                "points": 10,
                "order": 6,
                "choices": [
                    {"text": "DISTINCT", "is_correct": True},
                    {"text": "UNIQUE", "is_correct": False},
                    {"text": "GROUP", "is_correct": False},
                    {"text": "SINGLE", "is_correct": False}
                ]
            },
            {
                "text": "CSS Flexbox yapısında elemanları ana eksende (main-axis) ortalamak için hangi özellik kullanılır?",
                "points": 10,
                "order": 7,
                "choices": [
                    {"text": "justify-content: center;", "is_correct": True},
                    {"text": "align-items: center;", "is_correct": False},
                    {"text": "text-align: center;", "is_correct": False},
                    {"text": "flex-direction: center;", "is_correct": False}
                ]
            },
            {
                "text": "Web tarayıcılarında istemci depolaması için kullanılan ve tarayıcı sekmesi kapatıldığında silinen yapı hangisidir?",
                "points": 10,
                "order": 8,
                "choices": [
                    {"text": "sessionStorage", "is_correct": True},
                    {"text": "localStorage", "is_correct": False},
                    {"text": "IndexedDB", "is_correct": False},
                    {"text": "Cookies", "is_correct": False}
                ]
            },
            {
                "text": "Hangisi bir NoSQL veritabanı türü olan 'Doküman Tabanlı' (Document Store) veritabanıdır?",
                "points": 10,
                "order": 9,
                "choices": [
                    {"text": "MongoDB", "is_correct": True},
                    {"text": "PostgreSQL", "is_correct": False},
                    {"text": "Redis", "is_correct": False},
                    {"text": "Neo4j", "is_correct": False}
                ]
            },
            {
                "text": "Docker'da çalışan bir konteyneri arka planda (detached mode) başlatmak için hangi parametre kullanılır?",
                "points": 10,
                "order": 10,
                "choices": [
                    {"text": "-d", "is_correct": True},
                    {"text": "-b", "is_correct": False},
                    {"text": "-it", "is_correct": False},
                    {"text": "--daemon", "is_correct": False}
                ]
            },
            {
                "text": "Python'da liste üreteci (List Comprehension) kullanarak [0, 2, 4, 6, 8] listesini oluşturan ifade hangisidir?",
                "points": 10,
                "order": 11,
                "choices": [
                    {"text": "[x for x in range(10) if x % 2 == 0]", "is_correct": True},
                    {"text": "[x * 2 for x in range(10)]", "is_correct": False},
                    {"text": "[x in range(10) if x % 2 == 0]", "is_correct": False},
                    {"text": "list(range(0, 10, 1))", "is_correct": False}
                ]
            },
            {
                "text": "JavaScript'te asenkron işlemleri yönetmek için Promise yapısına alternatif olarak ES8 ile gelen sözdizimi nedir?",
                "points": 10,
                "order": 12,
                "choices": [
                    {"text": "async / await", "is_correct": True},
                    {"text": "try / catch", "is_correct": False},
                    {"text": "defer / resolve", "is_correct": False},
                    {"text": "yield / generator", "is_correct": False}
                ]
            },
            {
                "text": "Linux işletim sisteminde bir dosyanın izinlerini değiştirmek için hangi komut kullanılır?",
                "points": 10,
                "order": 13,
                "choices": [
                    {"text": "chmod", "is_correct": True},
                    {"text": "chown", "is_correct": False},
                    {"text": "ls -l", "is_correct": False},
                    {"text": "sudo perm", "is_correct": False}
                ]
            },
            {
                "text": "Yazılım tasarımında SOLID prensiplerinin 'S' harfi neyi temsil eder?",
                "points": 10,
                "order": 14,
                "choices": [
                    {"text": "Single Responsibility Principle", "is_correct": True},
                    {"text": "Simple Object Principle", "is_correct": False},
                    {"text": "Secure Code Principle", "is_correct": False},
                    {"text": "Singleton Pattern Principle", "is_correct": False}
                ]
            },
            {
                "text": "Hangi HTTP durum kodu (Status Code) 'Yetkilendirme Gerekli / Giriş Yapılmamış' anlamına gelir?",
                "points": 10,
                "order": 15,
                "choices": [
                    {"text": "401 Unauthorized", "is_correct": True},
                    {"text": "403 Forbidden", "is_correct": False},
                    {"text": "404 Not Found", "is_correct": False},
                    {"text": "500 Internal Server Error", "is_correct": False}
                ]
            },
            {
                "text": "Bir algoritmanın zaman karmaşıklığında 'İkili Arama' (Binary Search) algoritmasının karmaşıklığı nedir?",
                "points": 10,
                "order": 16,
                "choices": [
                    {"text": "O(log n)", "is_correct": True},
                    {"text": "O(n)", "is_correct": False},
                    {"text": "O(n log n)", "is_correct": False},
                    {"text": "O(1)", "is_correct": False}
                ]
            },
            {
                "text": "React veya modern frontend kütüphanelerinde DOM ağacını bellekte simüle edip yalnızca değişen kısımları güncelleyen yapı nedir?",
                "points": 10,
                "order": 17,
                "choices": [
                    {"text": "Virtual DOM", "is_correct": True},
                    {"text": "Shadow DOM", "is_correct": False},
                    {"text": "Real DOM", "is_correct": False},
                    {"text": "Proxy DOM", "is_correct": False}
                ]
            },
            {
                "text": "Hangisi tip güvenliği sağlayan ve JavaScript'e derlenen açık kaynaklı bir Microsoft programlama dilidir?",
                "points": 10,
                "order": 18,
                "choices": [
                    {"text": "TypeScript", "is_correct": True},
                    {"text": "Kotlin", "is_correct": False},
                    {"text": "Dart", "is_correct": False},
                    {"text": "Rust", "is_correct": False}
                ]
            },
            {
                "text": "Django web framework'ünde veritabanı tablolarını Python sınıfları olarak tanımlayan bileşen hangisidir?",
                "points": 10,
                "order": 19,
                "choices": [
                    {"text": "Models (ORM)", "is_correct": True},
                    {"text": "Views", "is_correct": False},
                    {"text": "Templates", "is_correct": False},
                    {"text": "Serializers", "is_correct": False}
                ]
            },
            {
                "text": "CI/CD süreçlerinde 'CD' kısaltması ne anlama gelir?",
                "points": 10,
                "order": 20,
                "choices": [
                    {"text": "Continuous Delivery / Continuous Deployment", "is_correct": True},
                    {"text": "Continuous Debugging", "is_correct": False},
                    {"text": "Code Distribution", "is_correct": False},
                    {"text": "Centralized Database", "is_correct": False}
                ]
            }
        ]
    },
    {
        "name": "Yapay Zeka",
        "slug": "yapay-zeka",
        "icon": "Bot",
        "color_theme": "purple",
        "music_url": "https://assets.mixkit.co/music/preview/mixkit-tech-house-vibes-130.mp3",
        "music_title": "Neural Network - Futuristic Tech Beats",
        "questions": [
            {
                "text": "Büyük Dil Modellerinde (LLM) 'GPT' kısaltmasındaki 'T' harfi neyi ifade eder?",
                "points": 10,
                "order": 1,
                "choices": [
                    {"text": "Transformer", "is_correct": True},
                    {"text": "Tensor", "is_correct": False},
                    {"text": "Translator", "is_correct": False},
                    {"text": "Training", "is_correct": False}
                ]
            },
            {
                "text": "Makine öğreniminde modelin eğitim verisini ezberleyip test verisinde kötü sonuç vermesi durumuna ne ad verilir?",
                "points": 10,
                "order": 2,
                "choices": [
                    {"text": "Overfitting (Aşırı Uyum)", "is_correct": True},
                    {"text": "Underfitting (Eksik Uyum)", "is_correct": False},
                    {"text": "Backpropagation", "is_correct": False},
                    {"text": "Regularization", "is_correct": False}
                ]
            },
            {
                "text": "Yapay sinir ağlarında nöronun çıkış değerini belirleyen ve modele doğrusal olmama (non-linearity) katan fonksiyon hangisidir?",
                "points": 10,
                "order": 3,
                "choices": [
                    {"text": "Aktivasyon Fonksiyonu (örn: ReLU, Sigmoid)", "is_correct": True},
                    {"text": "Kayıp Fonksiyonu (Loss Function)", "is_correct": False},
                    {"text": "Optimizasyon Fonksiyonu (Adam)", "is_correct": False},
                    {"text": "Batch Normalizasyonu", "is_correct": False}
                ]
            },
            {
                "text": "Yapay zekanın bir makine ile insanın ayırt edilemeyecek şekilde sohbet edip edemediğini test eden klasik test nedir?",
                "points": 10,
                "order": 4,
                "choices": [
                    {"text": "Turing Testi", "is_correct": True},
                    {"text": "Voight-Kampff Testi", "is_correct": False},
                    {"text": "Shannon Testi", "is_correct": False},
                    {"text": "Lovelace Kriteri", "is_correct": False}
                ]
            },
            {
                "text": "Görsel işleme ve görüntü sınıflandırma modellerinde en yaygın kullanılan derin öğrenme mimarisi hangisidir?",
                "points": 10,
                "order": 5,
                "choices": [
                    {"text": "CNN (Convolutional Neural Network)", "is_correct": True},
                    {"text": "RNN (Recurrent Neural Network)", "is_correct": False},
                    {"text": "MLP (Multi-Layer Perceptron)", "is_correct": False},
                    {"text": "SOM (Self-Organizing Map)", "is_correct": False}
                ]
            },
            {
                "text": "Etiketsiz verilerden örüntü ve gizli yapıları keşfetmeye dayalı makine öğrenimi türü hangisidir?",
                "points": 10,
                "order": 6,
                "choices": [
                    {"text": "Denetimsiz Öğrenme (Unsupervised Learning)", "is_correct": True},
                    {"text": "Denetimli Öğrenme (Supervised Learning)", "is_correct": False},
                    {"text": "Pekiştirmeli Öğrenme (Reinforcement Learning)", "is_correct": False},
                    {"text": "Transfer Öğrenme (Transfer Learning)", "is_correct": False}
                ]
            },
            {
                "text": "2017 yılında Google tarafından yayınlanan ve Transformer mimarisini tanıtan çığır açıcı makalenin başlığı nedir?",
                "points": 10,
                "order": 7,
                "choices": [
                    {"text": "Attention Is All You Need", "is_correct": True},
                    {"text": "Deep Learning for Vision", "is_correct": False},
                    {"text": "Neural Machine Translation", "is_correct": False},
                    {"text": "The Next Generation of AI", "is_correct": False}
                ]
            },
            {
                "text": "Yapay zeka modellerinin yanlış veya uydurma bilgiyi kendinden emin şekilde doğru gibi sunması fenomenine ne ad verilir?",
                "points": 10,
                "order": 8,
                "choices": [
                    {"text": "Halüsinasyon (Hallucination)", "is_correct": True},
                    {"text": "Bias (Önyargı)", "is_correct": False},
                    {"text": "Drift (Kayma)", "is_correct": False},
                    {"text": "Noise (Gürültü)", "is_correct": False}
                ]
            },
            {
                "text": "Satranç ve Go gibi oyunlarda kullanılan, ödül ve ceza mekanizmasıyla öğrenen yapay zeka yaklaşımı hangisidir?",
                "points": 10,
                "order": 9,
                "choices": [
                    {"text": "Reinforcement Learning (Pekiştirmeli Öğrenme)", "is_correct": True},
                    {"text": "Clustering (Kümeleme)", "is_correct": False},
                    {"text": "Dimensionality Reduction", "is_correct": False},
                    {"text": "Regression (Regresyon)", "is_correct": False}
                ]
            },
            {
                "text": "RAG (Retrieval-Augmented Generation) mimarisinin temel amacı nedir?",
                "points": 10,
                "order": 10,
                "choices": [
                    {"text": "Modele harici bir bilgi tabanından güncel veri getirip cevabı zenginleştirmek", "is_correct": True},
                    {"text": "Modelin parametre sayısını iki katına çıkarmak", "is_correct": False},
                    {"text": "Yalnızca görsel oluşturmak", "is_correct": False},
                    {"text": "Modeli GPU yerine sadece CPU'da çalıştırmak", "is_correct": False}
                ]
            },
            {
                "text": "PyTorch ve TensorFlow gibi kütüphanelerde çok boyutlu sayısal dizileri temsil eden temel veri yapısı nedir?",
                "points": 10,
                "order": 11,
                "choices": [
                    {"text": "Tensor", "is_correct": True},
                    {"text": "DataFrame", "is_correct": False},
                    {"text": "Vector3D", "is_correct": False},
                    {"text": "MatrixSet", "is_correct": False}
                ]
            },
            {
                "text": "Yapay zekada 'Self-Attention' (Öz-Dikkat) mekanizmasının görevi nedir?",
                "points": 10,
                "order": 12,
                "choices": [
                    {"text": "Bir cümledeki kelimelerin birbirleriyle olan anlamsal ilişkisini ağırlıklandırmak", "is_correct": True},
                    {"text": "Görüntüleri piksel piksel kırpmak", "is_correct": False},
                    {"text": "Modelin hafızasını her 10 saniyede bir sıfırlamak", "is_correct": False},
                    {"text": "Veri tabanındaki gereksiz sütunları silmek", "is_correct": False}
                ]
            },
            {
                "text": "Yapay sinir ağlarında hata gradyanlarının geriye doğru hesaplanarak ağırlıkların güncellenmesi algoritması nedir?",
                "points": 10,
                "order": 13,
                "choices": [
                    {"text": "Backpropagation (Geriye Yayılım)", "is_correct": True},
                    {"text": "Forward Feed", "is_correct": False},
                    {"text": "Genetic Algorithm", "is_correct": False},
                    {"text": "Monte Carlo Tree Search", "is_correct": False}
                ]
            },
            {
                "text": "Üretken Çekişmeli Ağlar (GAN - Generative Adversarial Networks) hangi iki temel bileşenden oluşur?",
                "points": 10,
                "order": 14,
                "choices": [
                    {"text": "Generator ve Discriminator", "is_correct": True},
                    {"text": "Encoder ve Decoder", "is_correct": False},
                    {"text": "Actor ve Critic", "is_correct": False},
                    {"text": "Sender ve Receiver", "is_correct": False}
                ]
            },
            {
                "text": "Metinleri yapay zekanın anlayabileceği sayısal vektörlere dönüştürme işlemine ne ad verilir?",
                "points": 10,
                "order": 15,
                "choices": [
                    {"text": "Embedding (Gömme)", "is_correct": True},
                    {"text": "Token Shuffling", "is_correct": False},
                    {"text": "Quantization", "is_correct": False},
                    {"text": "Pruning", "is_correct": False}
                ]
            },
            {
                "text": "Büyük dil modellerinin yanıtlarını insanların tercihlerine ve güvenliğe uygun hale getirmek için kullanılan yöntem nedir?",
                "points": 10,
                "order": 16,
                "choices": [
                    {"text": "RLHF (Reinforcement Learning from Human Feedback)", "is_correct": True},
                    {"text": "PCA (Principal Component Analysis)", "is_correct": False},
                    {"text": "K-Means Clustering", "is_correct": False},
                    {"text": "SVM (Support Vector Machine)", "is_correct": False}
                ]
            },
            {
                "text": "Vektör veritabanları (Vector Databases - örn: Pinecone, Chroma, Milvus) ne tür aramalar için optimize edilmiştir?",
                "points": 10,
                "order": 17,
                "choices": [
                    {"text": "Vektör benzerliği ve anlamsal (semantic) arama", "is_correct": True},
                    {"text": "Yalnızca tam metin anahtar kelime eşleşmesi", "is_correct": False},
                    {"text": "İlişkisel SQL sorguları (JOIN)", "is_correct": False},
                    {"text": "CSV dosyası sıkıştırma", "is_correct": False}
                ]
            },
            {
                "text": "Geniş bir veri kümesi üzerinde önceden eğitilmiş bir modelin belirli bir görev için küçük bir veri kümesiyle eğitilmesine ne ad verilir?",
                "points": 10,
                "order": 18,
                "choices": [
                    {"text": "Fine-Tuning (İnce Ayar)", "is_correct": True},
                    {"text": "Pre-training", "is_correct": False},
                    {"text": "Prompt Leaking", "is_correct": False},
                    {"text": "Cold Start", "is_correct": False}
                ]
            },
            {
                "text": "Diffusion (Yayılım) modelleri en çok hangi yapay zeka alanında devrim yaratmıştır?",
                "points": 10,
                "order": 19,
                "choices": [
                    {"text": "Metinden yüksek kaliteli görsel/video üretimi (Text-to-Image)", "is_correct": True},
                    {"text": "Kredi kartı dolandırıcılığı tespiti", "is_correct": False},
                    {"text": "DNS sunucu yönlendirmesi", "is_correct": False},
                    {"text": "Veri tabanı indeksleme", "is_correct": False}
                ]
            },
            {
                "text": "Yapay zeka modellerinin bellek kullanımını azaltıp hızını artırmak için ondalıklı sayı duyarlılığını (örn. FP32 -> INT8/INT4) düşürme işlemine ne denir?",
                "points": 10,
                "order": 20,
                "choices": [
                    {"text": "Quantization (Kuantalama)", "is_correct": True},
                    {"text": "Distillation", "is_correct": False},
                    {"text": "Tokenization", "is_correct": False},
                    {"text": "Normalization", "is_correct": False}
                ]
            }
        ]
    },
    {
        "name": "Bilgisayar Mühendisliği",
        "slug": "bilgisayar-muhendisligi",
        "icon": "Cpu",
        "color_theme": "blue",
        "music_url": "https://assets.mixkit.co/music/preview/mixkit-game-level-music-689.mp3",
        "music_title": "Logic Gate - Retro 8-bit Pulse",
        "questions": [
            {
                "text": "İşlemcide (CPU) aritmetik ve mantıksal işlemlerin yapıldığı ana donanım birimi hangisidir?",
                "points": 10,
                "order": 1,
                "choices": [
                    {"text": "ALU (Arithmetic Logic Unit)", "is_correct": True},
                    {"text": "Control Unit (CU)", "is_correct": False},
                    {"text": "Cache (Önbellek)", "is_correct": False},
                    {"text": "Register (Yazmaç)", "is_correct": False}
                ]
            },
            {
                "text": "OSI (Open Systems Interconnection) referans modeli toplamda kaç katmandan oluşur?",
                "points": 10,
                "order": 2,
                "choices": [
                    {"text": "7", "is_correct": True},
                    {"text": "4", "is_correct": False},
                    {"text": "5", "is_correct": False},
                    {"text": "6", "is_correct": False}
                ]
            },
            {
                "text": "İşletim sistemlerinde iki veya daha fazla sürecin birbirinin kaynak bırakmasını sonsuza kadar beklemesi durumuna ne denir?",
                "points": 10,
                "order": 3,
                "choices": [
                    {"text": "Deadlock (Kilitlenme)", "is_correct": True},
                    {"text": "Race Condition", "is_correct": False},
                    {"text": "Starvation", "is_correct": False},
                    {"text": "Context Switch", "is_correct": False}
                ]
            },
            {
                "text": "Bilgisayar mimarisinde en hızlı erişim süresine sahip bellek türü hangisidir?",
                "points": 10,
                "order": 4,
                "choices": [
                    {"text": "CPU Registers (Yazmaçlar)", "is_correct": True},
                    {"text": "L1 Cache", "is_correct": False},
                    {"text": "RAM", "is_correct": False},
                    {"text": "NVMe SSD", "is_correct": False}
                ]
            },
            {
                "text": "Mantık kapılarından hangisi 'Her iki giriş de 1 olduğunda 0, diğer durumlarda 1' çıkışı verir?",
                "points": 10,
                "order": 5,
                "choices": [
                    {"text": "NAND Kapısı", "is_correct": True},
                    {"text": "AND Kapısı", "is_correct": False},
                    {"text": "OR Kapısı", "is_correct": False},
                    {"text": "XOR Kapısı", "is_correct": False}
                ]
            },
            {
                "text": "TCP üçlü el sıkışma (3-way handshake) sırasındaki bayrak sırası hangisidir?",
                "points": 10,
                "order": 6,
                "choices": [
                    {"text": "SYN -> SYN-ACK -> ACK", "is_correct": True},
                    {"text": "ACK -> SYN -> ACK", "is_correct": False},
                    {"text": "SYN -> ACK -> FIN", "is_correct": False},
                    {"text": "HELLO -> READY -> OK", "is_correct": False}
                ]
            },
            {
                "text": "Sanal bellek (Virtual Memory) yönetiminde aranan sayfanın RAM'de bulunamaması durumunda ne tetiklenir?",
                "points": 10,
                "order": 7,
                "choices": [
                    {"text": "Page Fault", "is_correct": True},
                    {"text": "Segmentation Fault", "is_correct": False},
                    {"text": "Stack Overflow", "is_correct": False},
                    {"text": "Memory Leak", "is_correct": False}
                ]
            },
            {
                "text": "IPv4 adresleri kaç bitten oluşur?",
                "points": 10,
                "order": 8,
                "choices": [
                    {"text": "32 bit", "is_correct": True},
                    {"text": "64 bit", "is_correct": False},
                    {"text": "128 bit", "is_correct": False},
                    {"text": "16 bit", "is_correct": False}
                ]
            },
            {
                "text": "Yığın (Stack) veri yapısının temel çalışma prensibi hangisidir?",
                "points": 10,
                "order": 9,
                "choices": [
                    {"text": "LIFO (Last In First Out)", "is_correct": True},
                    {"text": "FIFO (First In First Out)", "is_correct": False},
                    {"text": "Random Access", "is_correct": False},
                    {"text": "Priority Order", "is_correct": False}
                ]
            },
            {
                "text": "Moore Yasası (Moore's Law) orijinal ifadesiyle yaklaşık neyi öngörmektedir?",
                "points": 10,
                "order": 10,
                "choices": [
                    {"text": "Bir mikroçipteki transistör sayısının yaklaşık 2 yılda bir ikiye katlanacağını", "is_correct": True},
                    {"text": "İşlemci saat hızının her yıl 10 kat artacağını", "is_correct": False},
                    {"text": "Yazılım hatalarının her güncellemede yarıya ineceğini", "is_correct": False},
                    {"text": "İnternet hızının her 6 ayda bir katlanacağını", "is_correct": False}
                ]
            },
            {
                "text": "DNS protokolü standart olarak hangi port numarasını kullanır?",
                "points": 10,
                "order": 11,
                "choices": [
                    {"text": "53", "is_correct": True},
                    {"text": "80", "is_correct": False},
                    {"text": "443", "is_correct": False},
                    {"text": "22", "is_correct": False}
                ]
            },
            {
                "text": "Von Neumann mimarisinde CPU ile bellek arasındaki veri aktarım darboğazına ne ad verilir?",
                "points": 10,
                "order": 12,
                "choices": [
                    {"text": "Von Neumann Darboğazı (Bottleneck)", "is_correct": True},
                    {"text": "Amdahl Sınırı", "is_correct": False},
                    {"text": "Turing Kısıtı", "is_correct": False},
                    {"text": "Pipeline Stall", "is_correct": False}
                ]
            },
            {
                "text": "İkili tabanda (Binary) '1011' sayısının onluk (Decimal) tabandaki karşılığı nedir?",
                "points": 10,
                "order": 13,
                "choices": [
                    {"text": "11", "is_correct": True},
                    {"text": "13", "is_correct": False},
                    {"text": "9", "is_correct": False},
                    {"text": "15", "is_correct": False}
                ]
            },
            {
                "text": "İşletim sisteminde kritik bölgeye (critical section) aynı anda yalnızca bir sürecin girmesini sağlayan senkronizasyon mekanizması nedir?",
                "points": 10,
                "order": 14,
                "choices": [
                    {"text": "Mutex / Semaphore", "is_correct": True},
                    {"text": "Spooling", "is_correct": False},
                    {"text": "Paging", "is_correct": False},
                    {"text": "DMA (Direct Memory Access)", "is_correct": False}
                ]
            },
            {
                "text": "Asimetrik şifreleme (Asymmetric Encryption) yöntemlerinde anahtar yapısı nasıldır?",
                "points": 10,
                "order": 15,
                "choices": [
                    {"text": "Genel (Public) ve Özel (Private) olmak üzere iki farklı anahtar kullanılır", "is_correct": True},
                    {"text": "Tek bir gizli ortak anahtar kullanılır", "is_correct": False},
                    {"text": "Hiç anahtar kullanılmaz, sadece hash hesaplanır", "is_correct": False},
                    {"text": "Her blok için rastgele yeni anahtar üretilir", "is_correct": False}
                ]
            },
            {
                "text": "Graf teorisinde tüm düğümleri en az maliyetle döngüsüz bağlayan alt grafiğe ne denir?",
                "points": 10,
                "order": 16,
                "choices": [
                    {"text": "Minimum Kapsayan Ağaç (Minimum Spanning Tree)", "is_correct": True},
                    {"text": "Tam Graf (Complete Graph)", "is_correct": False},
                    {"text": "İki Parçalı Graf (Bipartite Graph)", "is_correct": False},
                    {"text": "Euler Çevrimi", "is_correct": False}
                ]
            },
            {
                "text": "CPU mimarisinde komutların parçalara bölünerek eşzamanlı ve ardışık işlenmesi tekniğine ne ad verilir?",
                "points": 10,
                "order": 17,
                "choices": [
                    {"text": "Pipelining (Boru Hattı)", "is_correct": True},
                    {"text": "Overclocking", "is_correct": False},
                    {"text": "Hyper-Threading", "is_correct": False},
                    {"text": "Branch Prediction", "is_correct": False}
                ]
            },
            {
                "text": "Bir sabit diskin okuma/yazma kafasının istenen izin üzerine gelene kadar geçen süreye ne ad verilir?",
                "points": 10,
                "order": 18,
                "choices": [
                    {"text": "Seek Time (Arama Süresi)", "is_correct": True},
                    {"text": "Rotational Latency", "is_correct": False},
                    {"text": "Transfer Rate", "is_correct": False},
                    {"text": "Burst Rate", "is_correct": False}
                ]
            },
            {
                "text": "Veri tabanlarında ACID prensiplerindeki 'I' harfi neyi ifade eder?",
                "points": 10,
                "order": 19,
                "choices": [
                    {"text": "Isolation (Yalıtım)", "is_correct": True},
                    {"text": "Integrity (Bütünlük)", "is_correct": False},
                    {"text": "Indexing (İndeksleme)", "is_correct": False},
                    {"text": "Iteration (Yineleme)", "is_correct": False}
                ]
            },
            {
                "text": "RISC (Reduced Instruction Set Computer) işlemci mimarisinin temel avantajı nedir?",
                "points": 10,
                "order": 20,
                "choices": [
                    {"text": "Basitleştirilmiş komut seti ile komutların çoğunu tek bir saat çevriminde çalıştırmak", "is_correct": True},
                    {"text": "Binlerce karmaşık donanımsal komuta sahip olmak", "is_correct": False},
                    {"text": "Hiç önbellek (cache) gerektirmemesi", "is_correct": False},
                    {"text": "Sadece 8 bitlik verilerle çalışması", "is_correct": False}
                ]
            }
        ]
    },
    {
        "name": "Ülkeler",
        "slug": "ulkeler",
        "icon": "Globe",
        "color_theme": "emerald",
        "music_url": "https://assets.mixkit.co/music/preview/mixkit-traveling-around-the-world-1216.mp3",
        "music_title": "World Odyssey - Global Acoustic Journey",
        "questions": [
            {
                "text": "Avustralya'nın başkenti neresidir?",
                "points": 10,
                "order": 1,
                "choices": [
                    {"text": "Canberra", "is_correct": True},
                    {"text": "Sidney", "is_correct": False},
                    {"text": "Melbourne", "is_correct": False},
                    {"text": "Brisbane", "is_correct": False}
                ]
            },
            {
                "text": "Dünyanın yüzölçümü bakımından en büyük ülkesi hangisidir?",
                "points": 10,
                "order": 2,
                "choices": [
                    {"text": "Rusya", "is_correct": True},
                    {"text": "Kanada", "is_correct": False},
                    {"text": "Çin", "is_correct": False},
                    {"text": "Amerika Birleşik Devletleri", "is_correct": False}
                ]
            },
            {
                "text": "Brezilya'nın resmi dili hangisidir?",
                "points": 10,
                "order": 3,
                "choices": [
                    {"text": "Portekizce", "is_correct": True},
                    {"text": "İspanyolca", "is_correct": False},
                    {"text": "İngilizce", "is_correct": False},
                    {"text": "Fransızca", "is_correct": False}
                ]
            },
            {
                "text": "Dünyanın en uzun nehri olarak kabul edilen Nil Nehri hangi kıtadadır?",
                "points": 10,
                "order": 4,
                "choices": [
                    {"text": "Afrika", "is_correct": True},
                    {"text": "Güney Amerika", "is_correct": False},
                    {"text": "Asya", "is_correct": False},
                    {"text": "Avrupa", "is_correct": False}
                ]
            },
            {
                "text": "Hem Asya hem de Avrupa kıtasında toprağı bulunan transkontinental ülke hangisidir?",
                "points": 10,
                "order": 5,
                "choices": [
                    {"text": "Türkiye", "is_correct": True},
                    {"text": "Almanya", "is_correct": False},
                    {"text": "İran", "is_correct": False},
                    {"text": "İtalya", "is_correct": False}
                ]
            },
            {
                "text": "Japonya'nın en yüksek dağı hangisidir?",
                "points": 10,
                "order": 6,
                "choices": [
                    {"text": "Fuji Dağı", "is_correct": True},
                    {"text": "Everest Dağı", "is_correct": False},
                    {"text": "Kilimanjaro Dağı", "is_correct": False},
                    {"text": "Mont Blanc", "is_correct": False}
                ]
            },
            {
                "text": "Dünyanın en kalabalık nüfusuna sahip kıtası hangisidir?",
                "points": 10,
                "order": 7,
                "choices": [
                    {"text": "Asya", "is_correct": True},
                    {"text": "Afrika", "is_correct": False},
                    {"text": "Avrupa", "is_correct": False},
                    {"text": "Kuzey Amerika", "is_correct": False}
                ]
            },
            {
                "text": "İskandinav ülkesi olan İzlanda'nın başkenti neresidir?",
                "points": 10,
                "order": 8,
                "choices": [
                    {"text": "Reykjavik", "is_correct": True},
                    {"text": "Oslo", "is_correct": False},
                    {"text": "Helsinki", "is_correct": False},
                    {"text": "Kopenhag", "is_correct": False}
                ]
            },
            {
                "text": "Dünyanın en derin gölü olan Baykal Gölü hangi ülkededir?",
                "points": 10,
                "order": 9,
                "choices": [
                    {"text": "Rusya", "is_correct": True},
                    {"text": "Kanada", "is_correct": False},
                    {"text": "Moğolistan", "is_correct": False},
                    {"text": "Kazakistan", "is_correct": False}
                ]
            },
            {
                "text": "Akdeniz'i Atlas Okyanusu'na bağlayan stratejik boğaz hangisidir?",
                "points": 10,
                "order": 10,
                "choices": [
                    {"text": "Cebelitarık Boğazı", "is_correct": True},
                    {"text": "İstanbul Boğazı", "is_correct": False},
                    {"text": "Hürmüz Boğazı", "is_correct": False},
                    {"text": "Malakka Boğazı", "is_correct": False}
                ]
            },
            {
                "text": "Kanada'nın başkenti neresidir?",
                "points": 10,
                "order": 11,
                "choices": [
                    {"text": "Ottawa", "is_correct": True},
                    {"text": "Toronto", "is_correct": False},
                    {"text": "Montreal", "is_correct": False},
                    {"text": "Vancouver", "is_correct": False}
                ]
            },
            {
                "text": "Dünyanın en yüksek kesintisiz şelalesi olan Angel Şelalesi hangi Güney Amerika ülkesindedir?",
                "points": 10,
                "order": 12,
                "choices": [
                    {"text": "Venezuela", "is_correct": True},
                    {"text": "Brezilya", "is_correct": False},
                    {"text": "Arjantin", "is_correct": False},
                    {"text": "Kolombiya", "is_correct": False}
                ]
            },
            {
                "text": "Hangi ülkenin bayrağı dikdörtgen veya kare şeklinde olmayan tek ulusal bayraktır?",
                "points": 10,
                "order": 13,
                "choices": [
                    {"text": "Nepal", "is_correct": True},
                    {"text": "İsviçre", "is_correct": False},
                    {"text": "Vatikan", "is_correct": False},
                    {"text": "Bhutan", "is_correct": False}
                ]
            },
            {
                "text": "Afrika kıtasının en yüksek noktası olan Kilimanjaro Dağı hangi ülkededir?",
                "points": 10,
                "order": 14,
                "choices": [
                    {"text": "Tanzanya", "is_correct": True},
                    {"text": "Kenya", "is_correct": False},
                    {"text": "Etiyopya", "is_correct": False},
                    {"text": "Uganda", "is_correct": False}
                ]
            },
            {
                "text": "Dünyanın en küçük bağımsız devleti (yüzölçümü ve nüfus bakımından) hangisidir?",
                "points": 10,
                "order": 15,
                "choices": [
                    {"text": "Vatikan", "is_correct": True},
                    {"text": "Monako", "is_correct": False},
                    {"text": "San Marino", "is_correct": False},
                    {"text": "Lihtenştayn", "is_correct": False}
                ]
            },
            {
                "text": "Büyük Kanyon (Grand Canyon) hangi ülkede yer alır?",
                "points": 10,
                "order": 16,
                "choices": [
                    {"text": "Amerika Birleşik Devletleri", "is_correct": True},
                    {"text": "Meksika", "is_correct": False},
                    {"text": "Avustralya", "is_correct": False},
                    {"text": "Şili", "is_correct": False}
                ]
            },
            {
                "text": "Büyük Set Resifi (Great Barrier Reef) hangi ülkenin kıyılarında bulunur?",
                "points": 10,
                "order": 17,
                "choices": [
                    {"text": "Avustralya", "is_correct": True},
                    {"text": "Endonezya", "is_correct": False},
                    {"text": "Filipinler", "is_correct": False},
                    {"text": "Yeni Zelanda", "is_correct": False}
                ]
            },
            {
                "text": "Tarihi Machu Picchu antik şehri hangi ülkededir?",
                "points": 10,
                "order": 18,
                "choices": [
                    {"text": "Peru", "is_correct": True},
                    {"text": "Bolivya", "is_correct": False},
                    {"text": "Ekvador", "is_correct": False},
                    {"text": "Şili", "is_correct": False}
                ]
            },
            {
                "text": "Dünyanın en kurak sıcak çölü olan Atacama Çölü hangi ülkededir?",
                "points": 10,
                "order": 19,
                "choices": [
                    {"text": "Şili", "is_correct": True},
                    {"text": "Mısır", "is_correct": False},
                    {"text": "Suudi Arabistan", "is_correct": False},
                    {"text": "Namibya", "is_correct": False}
                ]
            },
            {
                "text": "Hollanda'nın anayasal başkenti neresidir?",
                "points": 10,
                "order": 20,
                "choices": [
                    {"text": "Amsterdam", "is_correct": True},
                    {"text": "Lahey (Den Haag)", "is_correct": False},
                    {"text": "Rotterdam", "is_correct": False},
                    {"text": "Utrecht", "is_correct": False}
                ]
            }
        ]
    },
    {
        "name": "Fizik",
        "slug": "fizik",
        "icon": "Atom",
        "color_theme": "orange",
        "music_url": "https://assets.mixkit.co/music/preview/mixkit-deep-space-ambient-588.mp3",
        "music_title": "Cosmic Horizon - Deep Space Ambient",
        "questions": [
            {
                "text": "Işığın boşluktaki yaklaşık hızı ne kadardır?",
                "points": 10,
                "order": 1,
                "choices": [
                    {"text": "300.000 km/s", "is_correct": True},
                    {"text": "150.000 km/s", "is_correct": False},
                    {"text": "3.000 km/s", "is_correct": False},
                    {"text": "1.000.000 km/s", "is_correct": False}
                ]
            },
            {
                "text": "Newton'un İkinci Hareket Yasası'nın temel formülü nedir?",
                "points": 10,
                "order": 2,
                "choices": [
                    {"text": "F = m * a", "is_correct": True},
                    {"text": "E = m * c^2", "is_correct": False},
                    {"text": "V = I * R", "is_correct": False},
                    {"text": "P = F / A", "is_correct": False}
                ]
            },
            {
                "text": "Termodinamiğin Sıfırıncı Yasası hangi temel fiziksel kavramı tanımlar?",
                "points": 10,
                "order": 3,
                "choices": [
                    {"text": "Sıcaklık ve Termal Denge", "is_correct": True},
                    {"text": "Entropi", "is_correct": False},
                    {"text": "Enerjinin Korunumu", "is_correct": False},
                    {"text": "Mutlak Sıfır Noktası", "is_correct": False}
                ]
            },
            {
                "text": "Kuantum mekaniğinde bir parçacığın hem konumunu hem de momentumunu aynı anda kesin olarak ölçemeyeceğimizi belirten ilke nedir?",
                "points": 10,
                "order": 4,
                "choices": [
                    {"text": "Heisenberg Belirsizlik İlkesi", "is_correct": True},
                    {"text": "Pauli Dışlama İlkesi", "is_correct": False},
                    {"text": "Schrödinger Dalga İlkesi", "is_correct": False},
                    {"text": "De Broglie Hipotezi", "is_correct": False}
                ]
            },
            {
                "text": "Albert Einstein'a 1921 yılında Nobel Fizik Ödülü'nü kazandıran çalışma hangisidir?",
                "points": 10,
                "order": 5,
                "choices": [
                    {"text": "Fotoelektrik Etki Açıklaması", "is_correct": True},
                    {"text": "Genel Görelilik Teorisi", "is_correct": False},
                    {"text": "Özel Görelilik Teorisi (E=mc^2)", "is_correct": False},
                    {"text": "Brown Hareketi", "is_correct": False}
                ]
            },
            {
                "text": "Elektrik akımının uluslararası (SI) birimi nedir?",
                "points": 10,
                "order": 6,
                "choices": [
                    {"text": "Amper (A)", "is_correct": True},
                    {"text": "Volt (V)", "is_correct": False},
                    {"text": "Ohm (Ω)", "is_correct": False},
                    {"text": "Watt (W)", "is_correct": False}
                ]
            },
            {
                "text": "Doğadaki dört temel kuvvet arasında en zayıf olanı hangisidir?",
                "points": 10,
                "order": 7,
                "choices": [
                    {"text": "Kütleçekim Kuvveti (Gravity)", "is_correct": True},
                    {"text": "Elektromanyetik Kuvvet", "is_correct": False},
                    {"text": "Güçlü Nükleer Kuvvet", "is_correct": False},
                    {"text": "Zayıf Nükleer Kuvvet", "is_correct": False}
                ]
            },
            {
                "text": "Mutlak sıfır noktası sıcaklığı Celsius cinsinden yaklaşık kaçtır?",
                "points": 10,
                "order": 8,
                "choices": [
                    {"text": "-273.15 °C", "is_correct": True},
                    {"text": "0 °C", "is_correct": False},
                    {"text": "-100 °C", "is_correct": False},
                    {"text": "-459.67 °C", "is_correct": False}
                ]
            },
            {
                "text": "Ses dalgaları hangi ortamda kesinlikle yayılamaz?",
                "points": 10,
                "order": 9,
                "choices": [
                    {"text": "Uzay Boşluğu (Vakum)", "is_correct": True},
                    {"text": "Su", "is_correct": False},
                    {"text": "Hava", "is_correct": False},
                    {"text": "Çelik", "is_correct": False}
                ]
            },
            {
                "text": "Elektromanyetik tayfta en yüksek enerjiye ve en kısa dalga boyuna sahip ışın türü hangisidir?",
                "points": 10,
                "order": 10,
                "choices": [
                    {"text": "Gama Işınları", "is_correct": True},
                    {"text": "X Işınları", "is_correct": False},
                    {"text": "Morötesi (UV)", "is_correct": False},
                    {"text": "Radyo Dalgaları", "is_correct": False}
                ]
            },
            {
                "text": "Bir cismin kütlesi ile yerçekimi ivmesinin çarpımı neyi verir?",
                "points": 10,
                "order": 11,
                "choices": [
                    {"text": "Ağırlık", "is_correct": True},
                    {"text": "Hacim", "is_correct": False},
                    {"text": "Yoğunluk", "is_correct": False},
                    {"text": "Basınç", "is_correct": False}
                ]
            },
            {
                "text": "Evrenin genişlediğini galaksilerin ışığındaki 'Kızıla Kayma' (Redshift) ile keşfeden gökbilimci kimdir?",
                "points": 10,
                "order": 12,
                "choices": [
                    {"text": "Edwin Hubble", "is_correct": True},
                    {"text": "Galileo Galilei", "is_correct": False},
                    {"text": "Johannes Kepler", "is_correct": False},
                    {"text": "Stephen Hawking", "is_correct": False}
                ]
            },
            {
                "text": "Atom çekirdeğinde yer alan ve elektriksel yükü nötr (yüksüz) olan parçacık hangisidir?",
                "points": 10,
                "order": 13,
                "choices": [
                    {"text": "Nötron", "is_correct": True},
                    {"text": "Proton", "is_correct": False},
                    {"text": "Elektron", "is_correct": False},
                    {"text": "Pozitron", "is_correct": False}
                ]
            },
            {
                "text": "Işığın hem dalga hem de parçacık özelliği göstermesi durumuna fizikte ne ad verilir?",
                "points": 10,
                "order": 14,
                "choices": [
                    {"text": "Dalga-Parçacık İkiliği (Wave-Particle Duality)", "is_correct": True},
                    {"text": "Kırılma (Refraction)", "is_correct": False},
                    {"text": "Girişim (Interference)", "is_correct": False},
                    {"text": "Kuantum Tünelleme", "is_correct": False}
                ]
            },
            {
                "text": "Manyetik alan içinden geçen iletkende gerilim indüklenmesini açıklayan temel yasa hangisidir?",
                "points": 10,
                "order": 15,
                "choices": [
                    {"text": "Faraday İndüksiyon Yasası", "is_correct": True},
                    {"text": "Coulomb Yasası", "is_correct": False},
                    {"text": "Ohm Yasası", "is_correct": False},
                    {"text": "Gauss Yasası", "is_correct": False}
                ]
            },
            {
                "text": "Maddenin katı, sıvı ve gaz dışındaki dördüncü iyonize hali nedir?",
                "points": 10,
                "order": 16,
                "choices": [
                    {"text": "Plazma", "is_correct": True},
                    {"text": "Bose-Einstein Yoğuşması", "is_correct": False},
                    {"text": "Süperiletken", "is_correct": False},
                    {"text": "Kristal", "is_correct": False}
                ]
            },
            {
                "text": "Evrendeki bir karadeliğin ışığın bile kaçamadığı sınır çizgisine ne ad verilir?",
                "points": 10,
                "order": 17,
                "choices": [
                    {"text": "Olay Ufku (Event Horizon)", "is_correct": True},
                    {"text": "Tekillik (Singularity)", "is_correct": False},
                    {"text": "Akkresyon Diski", "is_correct": False},
                    {"text": "Foton Küresi", "is_correct": False}
                ]
            },
            {
                "text": "Bir sistemdeki düzensizliğin veya rastgeleliğin ölçüsüne ne ad verilir?",
                "points": 10,
                "order": 18,
                "choices": [
                    {"text": "Entropi", "is_correct": True},
                    {"text": "Entalpi", "is_correct": False},
                    {"text": "Egzotermi", "is_correct": False},
                    {"text": "Özgül Isı", "is_correct": False}
                ]
            },
            {
                "text": "CERN'deki Büyük Hadron Çarpıştırıcısı'nda (LHC) 2012 yılında keşfedilen ve diğer parçacıklara kütle kazandıran bozon hangisidir?",
                "points": 10,
                "order": 19,
                "choices": [
                    {"text": "Higgs Bozonu", "is_correct": True},
                    {"text": "Foton", "is_correct": False},
                    {"text": "Gluon", "is_correct": False},
                    {"text": "Graviton", "is_correct": False}
                ]
            },
            {
                "text": "Kendi üzerine uygulanan kuvvet kaldırıldığında cismin eski şekline geri dönme özelliğine ne denir?",
                "points": 10,
                "order": 20,
                "choices": [
                    {"text": "Elastiklik", "is_correct": True},
                    {"text": "Plastiklik", "is_correct": False},
                    {"text": "Viskozite", "is_correct": False},
                    {"text": "Kırılganlık", "is_correct": False}
                ]
            }
        ]
    },
    {
        "name": "Futbol",
        "slug": "futbol",
        "icon": "Trophy",
        "color_theme": "rose",
        "music_url": "https://assets.mixkit.co/music/preview/mixkit-stadium-rock-beat-1122.mp3",
        "music_title": "Stadium Champions - Energetic Rock Beat",
        "questions": [
            {
                "text": "FIFA Dünya Kupası'nı 5 kez ile en çok kazanan ülke hangisidir?",
                "points": 10,
                "order": 1,
                "choices": [
                    {"text": "Brezilya", "is_correct": True},
                    {"text": "Almanya", "is_correct": False},
                    {"text": "İtalya", "is_correct": False},
                    {"text": "Arjantin", "is_correct": False}
                ]
            },
            {
                "text": "Futbol tarihinde 'Ballon d'Or' (Altın Top) ödülünü en çok kazanan futbolcu kimdir?",
                "points": 10,
                "order": 2,
                "choices": [
                    {"text": "Lionel Messi", "is_correct": True},
                    {"text": "Cristiano Ronaldo", "is_correct": False},
                    {"text": "Michel Platini", "is_correct": False},
                    {"text": "Johan Cruyff", "is_correct": False}
                ]
            },
            {
                "text": "UEFA Şampiyonlar Ligi'ni (ve eski adıyla Şampiyon Kulüpler Kupası'nı) en çok kazanan kulüp hangisidir?",
                "points": 10,
                "order": 3,
                "choices": [
                    {"text": "Real Madrid", "is_correct": True},
                    {"text": "AC Milan", "is_correct": False},
                    {"text": "Bayern Münih", "is_correct": False},
                    {"text": "Liverpool", "is_correct": False}
                ]
            },
            {
                "text": "Standart bir futbol maçında bir takım sahada kaç oyuncuyla yer alır?",
                "points": 10,
                "order": 4,
                "choices": [
                    {"text": "11", "is_correct": True},
                    {"text": "10", "is_correct": False},
                    {"text": "12", "is_correct": False},
                    {"text": "9", "is_correct": False}
                ]
            },
            {
                "text": "2000 yılında UEFA Kupası'nı (Avrupa Ligi) ve UEFA Süper Kupa'yı kazanan Türk futbol takımı hangisidir?",
                "points": 10,
                "order": 5,
                "choices": [
                    {"text": "Galatasaray", "is_correct": True},
                    {"text": "Fenerbahçe", "is_correct": False},
                    {"text": "Beşiktaş", "is_correct": False},
                    {"text": "Trabzonspor", "is_correct": False}
                ]
            },
            {
                "text": "Futbolda ofsayt kuralında kaleci dışında rakip kaleye en yakın en az kaç savunma oyuncusu bulunmalıdır?",
                "points": 10,
                "order": 6,
                "choices": [
                    {"text": "2 oyuncu (genelde kaleci + 1 savunmacı)", "is_correct": True},
                    {"text": "1 oyuncu", "is_correct": False},
                    {"text": "3 oyuncu", "is_correct": False},
                    {"text": "Hiç oyuncu gerekmez", "is_correct": False}
                ]
            },
            {
                "text": "Dünya Kupası tarihinde atılan en hızlı gol (11. saniyede) hangi futbolcuya aittir?",
                "points": 10,
                "order": 7,
                "choices": [
                    {"text": "Hakan Şükür (2002 Türkiye - G.Kore)", "is_correct": True},
                    {"text": "Ronaldo Nazario", "is_correct": False},
                    {"text": "Pele", "is_correct": False},
                    {"text": "Clint Dempsey", "is_correct": False}
                ]
            },
            {
                "text": "Premier Lig tarihinde 2003-2004 sezonunu hiç yenilgisiz ('The Invincibles') şampiyon tamamlayan takım hangisidir?",
                "points": 10,
                "order": 8,
                "choices": [
                    {"text": "Arsenal", "is_correct": True},
                    {"text": "Manchester United", "is_correct": False},
                    {"text": "Chelsea", "is_correct": False},
                    {"text": "Manchester City", "is_correct": False}
                ]
            },
            {
                "text": "Futbol oyun kurallarına göre standart bir penaltı noktasının kale çizgisine olan mesafesi kaç metredir?",
                "points": 10,
                "order": 9,
                "choices": [
                    {"text": "11 metre (12 yarda)", "is_correct": True},
                    {"text": "9.15 metre", "is_correct": False},
                    {"text": "12.5 metre", "is_correct": False},
                    {"text": "10 metre", "is_correct": False}
                ]
            },
            {
                "text": "Futbolda bir oyuncunun aynı maçta 3 gol atmasına ne ad verilir?",
                "points": 10,
                "order": 10,
                "choices": [
                    {"text": "Hat-trick", "is_correct": True},
                    {"text": "Duble", "is_correct": False},
                    {"text": "Poker", "is_correct": False},
                    {"text": "Trivela", "is_correct": False}
                ]
            },
            {
                "text": "2022 FIFA Dünya Kupası finalinde Fransa'yı penaltılarla mağlup ederek şampiyon olan ülke hangisidir?",
                "points": 10,
                "order": 11,
                "choices": [
                    {"text": "Arjantin", "is_correct": True},
                    {"text": "Hırvatistan", "is_correct": False},
                    {"text": "Fas", "is_correct": False},
                    {"text": "Brezilya", "is_correct": False}
                ]
            },
            {
                "text": "Futbolda 'Tiki-taka' pas oyun tarzı en çok hangi kulüp ve teknik direktör ile özdeşleşmiştir?",
                "points": 10,
                "order": 12,
                "choices": [
                    {"text": "Barcelona / Pep Guardiola", "is_correct": True},
                    {"text": "Real Madrid / Zinedine Zidane", "is_correct": False},
                    {"text": "Chelsea / Jose Mourinho", "is_correct": False},
                    {"text": "Liverpool / Jurgen Klopp", "is_correct": False}
                ]
            },
            {
                "text": "Futbolda ayağın dışıyla yapılan kavisli vuruş tekniğine ne ad verilir?",
                "points": 10,
                "order": 13,
                "choices": [
                    {"text": "Trivela", "is_correct": True},
                    {"text": "Rabona", "is_correct": False},
                    {"text": "Röveşata", "is_correct": False},
                    {"text": "Plase", "is_correct": False}
                ]
            },
            {
                "text": "EURO 2008 Avrupa Futbol Şampiyonası'nda Türkiye yarı finale yükselirken son dakika mucizeleriyle turnuvaya damga vuran teknik direktör kimdir?",
                "points": 10,
                "order": 14,
                "choices": [
                    {"text": "Fatih Terim", "is_correct": True},
                    {"text": "Mustafa Denizli", "is_correct": False},
                    {"text": "Şenol Güneş", "is_correct": False},
                    {"text": "Ersun Yanal", "is_correct": False}
                ]
            },
            {
                "text": "Uluslararası futbol kurallarını belirleyen ve düzenleyen tek yetkili kurul hangisidir?",
                "points": 10,
                "order": 15,
                "choices": [
                    {"text": "IFAB (International Football Association Board)", "is_correct": True},
                    {"text": "FIFA Executive Board", "is_correct": False},
                    {"text": "UEFA Referees Committee", "is_correct": False},
                    {"text": "CAS", "is_correct": False}
                ]
            },
            {
                "text": "Futbolda kalecinin ceza sahası içinde topu eliyle tutabildiği maksimum süre kuralı kaç saniyedir?",
                "points": 10,
                "order": 16,
                "choices": [
                    {"text": "6 saniye", "is_correct": True},
                    {"text": "10 saniye", "is_correct": False},
                    {"text": "4 saniye", "is_correct": False},
                    {"text": "Süre sınırı yoktur", "is_correct": False}
                ]
            },
            {
                "text": "1986 Dünya Kupası'nda Diego Maradona'nın İngiltere'ye elle attığı ve daha sonra 'Tanrı'nın Eli' olarak nitelendirdiği maçta attığı diğer efsanevi gol ne olarak anılır?",
                "points": 10,
                "order": 17,
                "choices": [
                    {"text": "Yüzyılın Golü (Goal of the Century)", "is_correct": True},
                    {"text": "Altın Gol", "is_correct": False},
                    {"text": "Akrep Vuruşu", "is_correct": False},
                    {"text": "Panenka Golü", "is_correct": False}
                ]
            },
            {
                "text": "Futbolda bir taç atışı doğrudan rakip kaleye girerse oyun nasıl başlar?",
                "points": 10,
                "order": 18,
                "choices": [
                    {"text": "Aut (Kale Vuruşu) ile", "is_correct": True},
                    {"text": "Gol geçerli sayılır", "is_correct": False},
                    {"text": "Taç atışı tekrarlanır", "is_correct": False},
                    {"text": "Korner ile", "is_correct": False}
                ]
            },
            {
                "text": "Futbolda 'Panenka' vuruş tekniği penaltıda nasıl uygulanır?",
                "points": 10,
                "order": 19,
                "choices": [
                    {"text": "Topun dibine hafifçe vurup aşırtarak kalenin ortasına göndermek", "is_correct": True},
                    {"text": "Çok sert ve 90'a doğru vurmak", "is_correct": False},
                    {"text": "Ters ayakla kaleciyi yanıltarak vurmak", "is_correct": False},
                    {"text": "Yerden köşeye plase bırakmak", "is_correct": False}
                ]
            },
            {
                "text": "FIFA tarafından her yıl dünyada yılın en estetik ve güzel golünü atan futbolcuya verilen ödül nedir?",
                "points": 10,
                "order": 20,
                "choices": [
                    {"text": "FIFA Puskás Ödülü", "is_correct": True},
                    {"text": "Altın Ayakkabı", "is_correct": False},
                    {"text": "Yashin Ödülü", "is_correct": False},
                    {"text": "Ballon d'Or", "is_correct": False}
                ]
            }
        ]
    },
    {
        "name": "Aşçılık",
        "slug": "ascilik",
        "icon": "ChefHat",
        "color_theme": "amber",
        "music_url": "https://assets.mixkit.co/music/preview/mixkit-cozy-lounge-bossa-nova-851.mp3",
        "music_title": "Bistro Gourmet - Cozy Kitchen Bossa Nova",
        "questions": [
            {
                "text": "Fransız mutfağında yemek yapımına başlamadan önce tüm malzemelerin doğranıp hazırlanması anlamına gelen terim nedir?",
                "points": 10,
                "order": 1,
                "choices": [
                    {"text": "Mise en place", "is_correct": True},
                    {"text": "Sous-vide", "is_correct": False},
                    {"text": "Flambe", "is_correct": False},
                    {"text": "Blanching", "is_correct": False}
                ]
            },
            {
                "text": "İtalyan mutfağında makarnanın aşırı yumuşamadan, hafif dişe gelecek kıvamda pişirilmesine ne ad verilir?",
                "points": 10,
                "order": 2,
                "choices": [
                    {"text": "Al dente", "is_correct": True},
                    {"text": "Al forno", "is_correct": False},
                    {"text": "Conchiglie", "is_correct": False},
                    {"text": "Antipasto", "is_correct": False}
                ]
            },
            {
                "text": "Beşamel sosun temelini oluşturan, eşit miktarda tereyağı ve unun kavrulmasıyla hazırlanan bağlayıcı karışıma ne denir?",
                "points": 10,
                "order": 3,
                "choices": [
                    {"text": "Meyane (Roux)", "is_correct": True},
                    {"text": "Ganaş (Ganache)", "is_correct": False},
                    {"text": "Marinasyon", "is_correct": False},
                    {"text": "Pesto", "is_correct": False}
                ]
            },
            {
                "text": "Sebzelerin 1-2 mm kalınlığında ve 4-5 cm uzunluğunda ince kibrit çöpü şeklinde doğranması tekniği hangisidir?",
                "points": 10,
                "order": 4,
                "choices": [
                    {"text": "Jülyen (Julienne)", "is_correct": True},
                    {"text": "Brunoise (Sıçandişi)", "is_correct": False},
                    {"text": "Chiffonade", "is_correct": False},
                    {"text": "Mirpua (Mirepoix)", "is_correct": False}
                ]
            },
            {
                "text": "Geleneksel İtalyan tatlısı Tiramisu’nun kremasında kullanılan temel peynir türü hangisidir?",
                "points": 10,
                "order": 5,
                "choices": [
                    {"text": "Mascarpone", "is_correct": True},
                    {"text": "Ricotta", "is_correct": False},
                    {"text": "Mozzarella", "is_correct": False},
                    {"text": "Parmesan", "is_correct": False}
                ]
            },
            {
                "text": "Geleneksel Türk mutfağında 'Hünkar Beğendi' yemeğinin altındaki közlenmiş püre hangi sebzeden yapılır?",
                "points": 10,
                "order": 6,
                "choices": [
                    {"text": "Patlıcan", "is_correct": True},
                    {"text": "Kabak", "is_correct": False},
                    {"text": "Kereviz", "is_correct": False},
                    {"text": "Kırmızı Biber", "is_correct": False}
                ]
            },
            {
                "text": "Çorbalara ve sulu yemeklere parlaklık, kıvam ve lezzet vermek için yumurta sarısı ve limonla yapılan işleme ne denir?",
                "points": 10,
                "order": 7,
                "choices": [
                    {"text": "Terbiye", "is_correct": True},
                    {"text": "Karamelize etme", "is_correct": False},
                    {"text": "Deklaze", "is_correct": False},
                    {"text": "Fermantasyon", "is_correct": False}
                ]
            },
            {
                "text": "Etin yüksek ısıda tava veya ızgarada hızla pişirilerek lezzet ve suyunu içine hapsetme tekniği hangisidir?",
                "points": 10,
                "order": 8,
                "choices": [
                    {"text": "Mühürleme (Searing)", "is_correct": True},
                    {"text": "Poşe etme (Poaching)", "is_correct": False},
                    {"text": "Haşlama (Boiling)", "is_correct": False},
                    {"text": "Fümeleme (Smoking)", "is_correct": False}
                ]
            },
            {
                "text": "Japon mutfağında suşi rulosu (maki) yapımında kullanılan preslenmiş kurutulmuş deniz yosununa ne ad verilir?",
                "points": 10,
                "order": 9,
                "choices": [
                    {"text": "Nori", "is_correct": True},
                    {"text": "Wakame", "is_correct": False},
                    {"text": "Kombu", "is_correct": False},
                    {"text": "Wasabi", "is_correct": False}
                ]
            },
            {
                "text": "Fransız mutfağında tereyağı ve yumurta sarısının emülsiyonu ile yapılan ünlü 5 temel ana sostan (Mother Sauces) biri hangisidir?",
                "points": 10,
                "order": 10,
                "choices": [
                    {"text": "Hollandez (Hollandaise)", "is_correct": True},
                    {"text": "Chimichurri", "is_correct": False},
                    {"text": "Guacamole", "is_correct": False},
                    {"text": "Tzatziki", "is_correct": False}
                ]
            },
            {
                "text": "Crocus sativus çiçeğinin tepeciklerinden toplanan, gramaj olarak dünyanın en pahalı baharatı hangisidir?",
                "points": 10,
                "order": 11,
                "choices": [
                    {"text": "Safran", "is_correct": True},
                    {"text": "Kakule", "is_correct": False},
                    {"text": "Vanilya Çubuğu", "is_correct": False},
                    {"text": "Muskat Cevizi", "is_correct": False}
                ]
            },
            {
                "text": "Yiyeceklerin vakumlu torbalarda su banyosu içinde düşük ve kontrollü sıcaklıkta pişirilmesi yöntemine ne ad verilir?",
                "points": 10,
                "order": 12,
                "choices": [
                    {"text": "Sous-vide", "is_correct": True},
                    {"text": "Braising", "is_correct": False},
                    {"text": "Broiling", "is_correct": False},
                    {"text": "Confit", "is_correct": False}
                ]
            },
            {
                "text": "İtalyan mutfağında Arborio pirinci ve et suyu kullanılarak kremsi dokuda pişirilen geleneksel pirinç yemeği hangisidir?",
                "points": 10,
                "order": 13,
                "choices": [
                    {"text": "Risotto", "is_correct": True},
                    {"text": "Paella", "is_correct": False},
                    {"text": "Polenta", "is_correct": False},
                    {"text": "Gnocchi", "is_correct": False}
                ]
            },
            {
                "text": "Ekmek yapımında un ve suyun yoğrulmadan önce bekletilerek glüten ağının kendiliğinden gelişmesini sağlayan dinlendirme aşaması nedir?",
                "points": 10,
                "order": 14,
                "choices": [
                    {"text": "Otoliz (Autolyse)", "is_correct": True},
                    {"text": "Fermantasyon", "is_correct": False},
                    {"text": "Mayalama", "is_correct": False},
                    {"text": "Taban pişirme", "is_correct": False}
                ]
            },
            {
                "text": "Geleneksel Meksika sosu Guacamole'nin ana maddesi olan yeşil tropikal meyve hangisidir?",
                "points": 10,
                "order": 15,
                "choices": [
                    {"text": "Avokado", "is_correct": True},
                    {"text": "Misket Limonu (Lime)", "is_correct": False},
                    {"text": "Kivi", "is_correct": False},
                    {"text": "Jalapeno Biberi", "is_correct": False}
                ]
            },
            {
                "text": "Soya sosu, mirin, sake ve şeker karışımından yapılan, ızgara et ve tavuklara parlaklık ve tatlı-tuzlu lezzet katan Japon sosu hangisidir?",
                "points": 10,
                "order": 16,
                "choices": [
                    {"text": "Teriyaki", "is_correct": True},
                    {"text": "Ponzu", "is_correct": False},
                    {"text": "Sriracha", "is_correct": False},
                    {"text": "Hoisin", "is_correct": False}
                ]
            },
            {
                "text": "Çikolatanın parlak görünmesi, oda sıcaklığında erimemesi ve kırıldığında net bir ses çıkarması için yapılan kristalleştirme işlemi nedir?",
                "points": 10,
                "order": 17,
                "choices": [
                    {"text": "Temperleme (Tempering)", "is_correct": True},
                    {"text": "Emülsiyon", "is_correct": False},
                    {"text": "Karamelizasyon", "is_correct": False},
                    {"text": "Homojenizasyon", "is_correct": False}
                ]
            },
            {
                "text": "Sebzelerin kaynayan tuzlu suya kısa süre daldırılıp hemen ardından buzlu suya atılarak renginin ve diriliğinin korunması işlemine ne denir?",
                "points": 10,
                "order": 18,
                "choices": [
                    {"text": "Blanching (Şok Haşlama)", "is_correct": True},
                    {"text": "Steaming (Buharda Pişirme)", "is_correct": False},
                    {"text": "Deep Frying (Derin Yağda Kızartma)", "is_correct": False},
                    {"text": "Soteleme (Sauteing)", "is_correct": False}
                ]
            },
            {
                "text": "Kırım Tatar mutfağı kökenli olup Türkiye'de özellikle Eskişehir ile özdeşleşen, içi kıymalı yarım ay şeklindeki börek hangisidir?",
                "points": 10,
                "order": 19,
                "choices": [
                    {"text": "Çiğ Börek (Çibörek)", "is_correct": True},
                    {"text": "Su Böreği", "is_correct": False},
                    {"text": "Kol Böreği", "is_correct": False},
                    {"text": "Boyoz", "is_correct": False}
                ]
            },
            {
                "text": "Pasta ve tatlılarda krema ve eritilmiş çikolatanın pürüzsüzce karıştırılmasıyla hazırlanan zengin dolgu ve kaplama kremasına ne ad verilir?",
                "points": 10,
                "order": 20,
                "choices": [
                    {"text": "Ganaş (Ganache)", "is_correct": True},
                    {"text": "Pralin", "is_correct": False},
                    {"text": "Mereng (Beze)", "is_correct": False},
                    {"text": "Krem Patissiere", "is_correct": False}
                ]
            }
        ]
    }
]


class Command(BaseCommand):
    help = "Populate initial categories and questions for Rapid Quiz"

    def handle(self, *args, **options):
        self.stdout.write(self.style.NOTICE("Seeding Rapid Quiz categories and questions..."))

        total_categories = 0
        total_questions = 0
        total_choices = 0

        with transaction.atomic():
            for cat_data in CATEGORIES_DATA:
                category, created = Category.objects.update_or_create(
                    slug=cat_data["slug"],
                    defaults={
                        "name": cat_data["name"],
                        "icon": cat_data["icon"],
                        "color_theme": cat_data["color_theme"],
                        "music_url": cat_data.get("music_url"),
                        "music_title": cat_data.get("music_title"),
                        "is_active": True,
                    }
                )
                if created:
                    self.stdout.write(self.style.SUCCESS(f"  + Kategori olusturuldu: {category.name}"))
                else:
                    self.stdout.write(self.style.WARNING(f"  * Kategori guncellendi: {category.name}"))

                total_categories += 1

                for q_data in cat_data["questions"]:
                    question, q_created = Question.objects.update_or_create(
                        category=category,
                        order=q_data["order"],
                        defaults={
                            "text": q_data["text"],
                            "points": q_data.get("points", 10),
                            "is_active": True,
                        }
                    )
                    total_questions += 1

                    # Reset choices and add new ones
                    question.choices.all().delete()
                    for ch_data in q_data["choices"]:
                        Choice.objects.create(
                            question=question,
                            text=ch_data["text"],
                            is_correct=ch_data["is_correct"],
                        )
                        total_choices += 1

        self.stdout.write(
            self.style.SUCCESS(
                f"Tamamlandi! {total_categories} Kategori, {total_questions} Soru ve {total_choices} Sik veritabanina eklendi."
            )
        )
