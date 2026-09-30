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
        "questions": [
            {
                "text": "Python dilinde değiştirilemez (immutable) veri tipi hangisidir?",
                "points": 10,
                "order": 1,
                "choices": [
                    {"text": "Tuple", "is_correct": True},
                    {"text": "List", "is_correct": False},
                    {"text": "Dictionary", "is_correct": False},
                    {"text": "Set", "is_correct": False},
                ],
            },
            {
                "text": "JavaScript'te '===' operatörünün '==' den farkı nedir?",
                "points": 10,
                "order": 2,
                "choices": [
                    {"text": "Değer ile birlikte veri tipini de kontrol eder", "is_correct": True},
                    {"text": "Sadece string ifadeleri karşılaştırır", "is_correct": False},
                    {"text": "Tipleri otomatik olarak birbirine dönüştürür", "is_correct": False},
                    {"text": "Referans adreslerini karşılaştırmaz", "is_correct": False},
                ],
            },
            {
                "text": "Git'te yerel değişiklikleri commit yapmadan geçici olarak saklamak için hangi komut kullanılır?",
                "points": 10,
                "order": 3,
                "choices": [
                    {"text": "git stash", "is_correct": True},
                    {"text": "git save", "is_correct": False},
                    {"text": "git cache", "is_correct": False},
                    {"text": "git pause", "is_correct": False},
                ],
            },
            {
                "text": "REST mimarisinde bir kaynağı tamamen güncellemek için kullanılan standart idempotent HTTP metodu hangisidir?",
                "points": 10,
                "order": 4,
                "choices": [
                    {"text": "PUT", "is_correct": True},
                    {"text": "POST", "is_correct": False},
                    {"text": "PATCH", "is_correct": False},
                    {"text": "CONNECT", "is_correct": False},
                ],
            },
            {
                "text": "Nesne Yönelimli Programlamada (OOP) bir sınıfın başka bir sınıfın özellik ve metotlarını devralması ne olarak adlandırılır?",
                "points": 10,
                "order": 5,
                "choices": [
                    {"text": "Inheritance (Kalıtım)", "is_correct": True},
                    {"text": "Polymorphism (Çok Biçimlilik)", "is_correct": False},
                    {"text": "Encapsulation (Kapsülleme)", "is_correct": False},
                    {"text": "Abstraction (Soyutlama)", "is_correct": False},
                ],
            },
            {
                "text": "SQL'de tablodan çekilen verilerdeki tekrar eden kayıtları tekilleştirmek için hangi anahtar kelime kullanılır?",
                "points": 10,
                "order": 6,
                "choices": [
                    {"text": "DISTINCT", "is_correct": True},
                    {"text": "UNIQUE", "is_correct": False},
                    {"text": "GROUP", "is_correct": False},
                    {"text": "SINGLE", "is_correct": False},
                ],
            },
            {
                "text": "CSS Flexbox yapısında elemanları ana eksende (main-axis) ortalamak için hangi özellik kullanılır?",
                "points": 10,
                "order": 7,
                "choices": [
                    {"text": "justify-content: center;", "is_correct": True},
                    {"text": "align-items: center;", "is_correct": False},
                    {"text": "text-align: center;", "is_correct": False},
                    {"text": "flex-direction: center;", "is_correct": False},
                ],
            },
            {
                "text": "Web tarayıcılarında istemci depolaması için kullanılan ve tarayıcı sekmesi kapatıldığında silinen yapı hangisidir?",
                "points": 10,
                "order": 8,
                "choices": [
                    {"text": "sessionStorage", "is_correct": True},
                    {"text": "localStorage", "is_correct": False},
                    {"text": "IndexedDB", "is_correct": False},
                    {"text": "Cookies", "is_correct": False},
                ],
            },
            {
                "text": "Hangi veri yapısı LIFO (Last In First Out - Son Giren İlk Çıkar) prensibine göre çalışır?",
                "points": 10,
                "order": 9,
                "choices": [
                    {"text": "Stack (Yığıt)", "is_correct": True},
                    {"text": "Queue (Kuyruk)", "is_correct": False},
                    {"text": "LinkedList (Bağlı Liste)", "is_correct": False},
                    {"text": "Tree (Ağaç)", "is_correct": False},
                ],
            },
            {
                "text": "Docker container imajlarının katmanlarını ve yapılandırmasını tanımlayan temel dosya nedir?",
                "points": 10,
                "order": 10,
                "choices": [
                    {"text": "Dockerfile", "is_correct": True},
                    {"text": "docker-compose.yml", "is_correct": False},
                    {"text": "container.json", "is_correct": False},
                    {"text": "manifest.yaml", "is_correct": False},
                ],
            },
            {
                "text": "JSON veri formatında diziler (array) hangi parantez karakteri ile tanımlanır?",
                "points": 10,
                "order": 11,
                "choices": [
                    {"text": "Köşeli Parantez [ ]", "is_correct": True},
                    {"text": "Süslü Parantez { }", "is_correct": False},
                    {"text": "Yay Ayraç ( )", "is_correct": False},
                    {"text": "Açılı Ayraç < >", "is_correct": False},
                ],
            },
            {
                "text": "TypeScript, JavaScript ekosistemine temelde hangi kritik yeteneği kazandırır?",
                "points": 10,
                "order": 12,
                "choices": [
                    {"text": "Statik Tip Denetimi (Static Typing)", "is_correct": True},
                    {"text": "Dahili CSS Derleyicisi", "is_correct": False},
                    {"text": "Doğrudan Veritabanı Bağlantısı", "is_correct": False},
                    {"text": "İşletim Sistemi Çekirdek Erişimi", "is_correct": False},
                ],
            },
            {
                "text": "Bir fonksiyonun kendi kendini doğrudan veya dolaylı olarak çağırması mekanizmasına ne ad verilir?",
                "points": 10,
                "order": 13,
                "choices": [
                    {"text": "Recursion (Özyineleme)", "is_correct": True},
                    {"text": "Iteration (Yineleme)", "is_correct": False},
                    {"text": "Memoization", "is_correct": False},
                    {"text": "Currying", "is_correct": False},
                ],
            },
            {
                "text": "Linux işletim sisteminde dosya veya dizin erişim izinlerini (read/write/execute) değiştiren komut hangisidir?",
                "points": 10,
                "order": 14,
                "choices": [
                    {"text": "chmod", "is_correct": True},
                    {"text": "chown", "is_correct": False},
                    {"text": "chgrp", "is_correct": False},
                    {"text": "touch", "is_correct": False},
                ],
            },
            {
                "text": "HTTP durum kodu 404 ne anlama gelir?",
                "points": 10,
                "order": 15,
                "choices": [
                    {"text": "Not Found (Kaynak Bulunamadı)", "is_correct": True},
                    {"text": "Unauthorized (Yetkisiz Erişim)", "is_correct": False},
                    {"text": "Internal Server Error (Sunucu Hatası)", "is_correct": False},
                    {"text": "Bad Request (Hatalı İstek)", "is_correct": False},
                ],
            },
            {
                "text": "CSS'te z-index özelliğinin çalışabilmesi için elemanın position değeri aşağıdakilerden hangisi OLMAMALIDIR?",
                "points": 10,
                "order": 16,
                "choices": [
                    {"text": "static", "is_correct": True},
                    {"text": "relative", "is_correct": False},
                    {"text": "absolute", "is_correct": False},
                    {"text": "fixed", "is_correct": False},
                ],
            },
            {
                "text": "CORS (Cross-Origin Resource Sharing) mekanizması web geliştirmede temel olarak neyi denetler?",
                "points": 10,
                "order": 17,
                "choices": [
                    {"text": "Farklı kaynaklar (origin) arası API istek izinlerini", "is_correct": True},
                    {"text": "Veritabanı indeksleme performansını", "is_correct": False},
                    {"text": "HTML sayfalarının yüklenme hızını", "is_correct": False},
                    {"text": "CSS dosyalarının sıkıştırılmasını", "is_correct": False},
                ],
            },
            {
                "text": "Yazılım geliştirmedeki DRY prensibinin açılımı ve temel kuralı nedir?",
                "points": 10,
                "order": 18,
                "choices": [
                    {"text": "Don't Repeat Yourself (Kendini Tekrar Etme)", "is_correct": True},
                    {"text": "Do Right Yesterday (Dünü Doğru Yap)", "is_correct": False},
                    {"text": "Dynamic Resource Yield (Dinamik Kaynak Verimi)", "is_correct": False},
                    {"text": "Data Redundancy Yield (Veri Artıklığı)", "is_correct": False},
                ],
            },
            {
                "text": "İlişkisel veritabanlarında iki veya daha fazla tabloyu ortak bir sütun üzerinden birleştirmek için ne kullanılır?",
                "points": 10,
                "order": 19,
                "choices": [
                    {"text": "JOIN", "is_correct": True},
                    {"text": "MERGE", "is_correct": False},
                    {"text": "COMBINE", "is_correct": False},
                    {"text": "ATTACH", "is_correct": False},
                ],
            },
            {
                "text": "Python'da bir listenin elemanlarını orijinal listeyi değiştirerek (in-place) sıralayan metot hangisidir?",
                "points": 10,
                "order": 20,
                "choices": [
                    {"text": "list.sort()", "is_correct": True},
                    {"text": "sorted(list)", "is_correct": False},
                    {"text": "list.order()", "is_correct": False},
                    {"text": "list.arrange()", "is_correct": False},
                ],
            },
        ],
    },
    {
        "name": "Yapay Zeka",
        "slug": "yapay-zeka",
        "icon": "Bot",
        "color_theme": "purple",
        "questions": [
            {
                "text": "Makine öğreniminde etiketlenmiş (labeled) veriler kullanılarak modelin eğitildiği öğrenme türü nedir?",
                "points": 10,
                "order": 1,
                "choices": [
                    {"text": "Denetimli Öğrenme (Supervised Learning)", "is_correct": True},
                    {"text": "Denetimsiz Öğrenme (Unsupervised Learning)", "is_correct": False},
                    {"text": "Pekiştirmeli Öğrenme (Reinforcement Learning)", "is_correct": False},
                    {"text": "Kendi Kendine Denetimli Öğrenme", "is_correct": False},
                ],
            },
            {
                "text": "Derin öğrenmede aşırı öğrenmeyi (overfitting) engellemek amacıyla nöronların rastgele kapatılması tekniğine ne denir?",
                "points": 10,
                "order": 2,
                "choices": [
                    {"text": "Dropout", "is_correct": True},
                    {"text": "Backpropagation", "is_correct": False},
                    {"text": "Batch Normalization", "is_correct": False},
                    {"text": "Gradient Clipping", "is_correct": False},
                ],
            },
            {
                "text": "Büyük Dil Modellerinde (LLM) devrim yaratan Transformer mimarisinin temel yapı taşı olan mekanizma nedir?",
                "points": 10,
                "order": 3,
                "choices": [
                    {"text": "Self-Attention (Öz-Dikkat) Mekanizması", "is_correct": True},
                    {"text": "Convolutional Filters (Evrişim Filtreleri)", "is_correct": False},
                    {"text": "Recurrent Loops (Yinelemeli Döngüler)", "is_correct": False},
                    {"text": "Decision Trees (Karar Ağaçları)", "is_correct": False},
                ],
            },
            {
                "text": "Görüntü işleme, nesne tanıma ve piksel analizi görevlerinde en başarılı yapay sinir ağı mimarisi hangisidir?",
                "points": 10,
                "order": 4,
                "choices": [
                    {"text": "CNN (Convolutional Neural Network)", "is_correct": True},
                    {"text": "RNN (Recurrent Neural Network)", "is_correct": False},
                    {"text": "MLP (Multilayer Perceptron)", "is_correct": False},
                    {"text": "SOM (Self-Organizing Map)", "is_correct": False},
                ],
            },
            {
                "text": "Bir modelin eğitim verisini aşırı ezberleyip yeni/görülmemiş verilerde düşük performans göstermesi durumuna ne ad verilir?",
                "points": 10,
                "order": 5,
                "choices": [
                    {"text": "Overfitting (Aşırı Öğrenme)", "is_correct": True},
                    {"text": "Underfitting (Eksik Öğrenme)", "is_correct": False},
                    {"text": "Data Drift", "is_correct": False},
                    {"text": "Gradient Explosion", "is_correct": False},
                ],
            },
            {
                "text": "Pekiştirmeli öğrenmede (Reinforcement Learning) bir ajanın aksiyonları sonucu çevreden aldığı sinyal nedir?",
                "points": 10,
                "order": 6,
                "choices": [
                    {"text": "Ödül / Ceza (Reward / Penalty)", "is_correct": True},
                    {"text": "Doğruluk Oranı (Accuracy)", "is_correct": False},
                    {"text": "Kayıp Değeri (Loss)", "is_correct": False},
                    {"text": "Token Sayısı", "is_correct": False},
                ],
            },
            {
                "text": "Doğal Dil İşlemede (NLP) metinlerin kelime, kök veya karakter parçalarına bölünmesi işlemine ne ad verilir?",
                "points": 10,
                "order": 7,
                "choices": [
                    {"text": "Tokenization (Jetonlama)", "is_correct": True},
                    {"text": "Lemmatization", "is_correct": False},
                    {"text": "Stemming", "is_correct": False},
                    {"text": "Embedding", "is_correct": False},
                ],
            },
            {
                "text": "GAN (Üretken Çekişmeli Ağlar) mimarisinde birbirine karşı yarışarak öğrenen iki ana ağ hangileridir?",
                "points": 10,
                "order": 8,
                "choices": [
                    {"text": "Generator (Üreteç) & Discriminator (Ayırt Edici)", "is_correct": True},
                    {"text": "Encoder (Kodlayıcı) & Decoder (Kod Çözücü)", "is_correct": False},
                    {"text": "Actor (Aktör) & Critic (Eleştirmen)", "is_correct": False},
                    {"text": "Feedforward & Feedback", "is_correct": False},
                ],
            },
            {
                "text": "Yapay sinir ağlarında modelin tahmin hatasını ölçen ve eğitimde minimize edilmeye çalışılan fonksiyon nedir?",
                "points": 10,
                "order": 9,
                "choices": [
                    {"text": "Kayıp Fonksiyonu (Loss Function)", "is_correct": True},
                    {"text": "Aktivasyon Fonksiyonu", "is_correct": False},
                    {"text": "Öğrenme Oranı (Learning Rate)", "is_correct": False},
                    {"text": "Optimizasyon Adımı", "is_correct": False},
                ],
            },
            {
                "text": "Yapay sinir ağı katmanlarına doğrusal olmayan (non-linear) özellik kazandıran fonksiyonlara ne ad verilir?",
                "points": 10,
                "order": 10,
                "choices": [
                    {"text": "Aktivasyon Fonksiyonu", "is_correct": True},
                    {"text": "Kayıp Fonksiyonu", "is_correct": False},
                    {"text": "Ağırlık Fonksiyonu", "is_correct": False},
                    {"text": "Türev Fonksiyonu", "is_correct": False},
                ],
            },
            {
                "text": "Derin öğrenmede sıkça kullanılan 'ReLU' aktivasyon fonksiyonunun açılımı nedir?",
                "points": 10,
                "order": 11,
                "choices": [
                    {"text": "Rectified Linear Unit", "is_correct": True},
                    {"text": "Recurrent Linear Utility", "is_correct": False},
                    {"text": "Radial Error Logistic Unit", "is_correct": False},
                    {"text": "Reduced Linear Universal", "is_correct": False},
                ],
            },
            {
                "text": "Vektör veritabanları (Vector DB) yapay zeka uygulamalarında temelde ne için kullanılır?",
                "points": 10,
                "order": 12,
                "choices": [
                    {"text": "Embedding vektörleri arasında anlamsal (semantik) benzerlik araması için", "is_correct": True},
                    {"text": "SQL sorgularını önbelleğe almak için", "is_correct": False},
                    {"text": "Resim dosyalarını sıkıştırmak için", "is_correct": False},
                    {"text": "Kullanıcı parolalarını şifrelemek için", "is_correct": False},
                ],
            },
            {
                "text": "LLM'lerin harici veri kaynaklarıyla desteklenmesini sağlayan RAG kavramının açılımı nedir?",
                "points": 10,
                "order": 13,
                "choices": [
                    {"text": "Retrieval-Augmented Generation", "is_correct": True},
                    {"text": "Recurrent-Attention Generator", "is_correct": False},
                    {"text": "Random-Automated Gradient", "is_correct": False},
                    {"text": "Realtime-Adaptive Graph", "is_correct": False},
                ],
            },
            {
                "text": "Büyük Dil Modellerinde (LLM) 'Temperature' (Sıcaklık) parametresi neyi kontrol eder?",
                "points": 10,
                "order": 14,
                "choices": [
                    {"text": "Model yanıtlarındaki rastgelelik ve yaratıcılık derecesini", "is_correct": True},
                    {"text": "Modelin çalıştığı GPU'nun donanım sıcaklığını", "is_correct": False},
                    {"text": "Üretilen metnin maksimum token sayısını", "is_correct": False},
                    {"text": "Modelin cevap verme hızını", "is_correct": False},
                ],
            },
            {
                "text": "Yapay sinir ağlarında hatanın çıkıştan geriye doğru aktarılarak ağırlıkların güncellenmesi sürecine ne denir?",
                "points": 10,
                "order": 15,
                "choices": [
                    {"text": "Backpropagation (Geri Yayılım)", "is_correct": True},
                    {"text": "Forward Pass (İleri Geçiş)", "is_correct": False},
                    {"text": "Hebbian Learning", "is_correct": False},
                    {"text": "Feature Extraction", "is_correct": False},
                ],
            },
            {
                "text": "Gözetimsiz öğrenmede benzer özelliklere sahip verilerin otomatik olarak gruplandırılması işlemine ne denir?",
                "points": 10,
                "order": 16,
                "choices": [
                    {"text": "Clustering (Kümeleme)", "is_correct": True},
                    {"text": "Classification (Sınıflandırma)", "is_correct": False},
                    {"text": "Regression (Regresyon)", "is_correct": False},
                    {"text": "Dimensionality Reduction", "is_correct": False},
                ],
            },
            {
                "text": "K-Means algoritması hangi makine öğrenimi alanına aittir?",
                "points": 10,
                "order": 17,
                "choices": [
                    {"text": "Denetimsiz Öğrenme (Kümeleme)", "is_correct": True},
                    {"text": "Denetimli Öğrenme (Sınıflandırma)", "is_correct": False},
                    {"text": "Pekiştirmeli Öğrenme", "is_correct": False},
                    {"text": "Zaman Serisi Tahmini", "is_correct": False},
                ],
            },
            {
                "text": "Turing Testi temel olarak neyi sınamak için tasarlanmıştır?",
                "points": 10,
                "order": 18,
                "choices": [
                    {"text": "Bir makinenin insandan ayırt edilemez düzeyde akıllı davranıp davranamayacağını", "is_correct": True},
                    {"text": "Bir bilgisayarın işlemci saat hızını", "is_correct": False},
                    {"text": "Bir algoritmanın bellek verimliliğini", "is_correct": False},
                    {"text": "Veri tabanının sorgu yanıt süresini", "is_correct": False},
                ],
            },
            {
                "text": "NLP'de kelimelerin ve cümlelerin çok boyutlu sayısal vektörlerle ifade edilmesine ne ad verilir?",
                "points": 10,
                "order": 19,
                "choices": [
                    {"text": "Word Embedding (Kelime Gömme)", "is_correct": True},
                    {"text": "Word Parsing", "is_correct": False},
                    {"text": "Word Tokenizing", "is_correct": False},
                    {"text": "Word Hashing", "is_correct": False},
                ],
            },
            {
                "text": "Derin öğrenme eğitiminde tüm veri setinin sinir ağından tam bir tur geçmesine ne ad verilir?",
                "points": 10,
                "order": 20,
                "choices": [
                    {"text": "Epoch", "is_correct": True},
                    {"text": "Batch", "is_correct": False},
                    {"text": "Iteration", "is_correct": False},
                    {"text": "Step", "is_correct": False},
                ],
            },
        ],
    },
    {
        "name": "Bilgisayar Mühendisliği",
        "slug": "bilgisayar-muhendisligi",
        "icon": "Cpu",
        "color_theme": "blue",
        "questions": [
            {
                "text": "Merkezi İşlem Biriminin (CPU) saat frekansını ölçmek için kullanılan temel birim nedir?",
                "points": 10,
                "order": 1,
                "choices": [
                    {"text": "Hertz (GHz / MHz)", "is_correct": True},
                    {"text": "Byte (GB / MB)", "is_correct": False},
                    {"text": "Flops", "is_correct": False},
                    {"text": "Watt", "is_correct": False},
                ],
            },
            {
                "text": "Bir algoritmanın girdi boyutu büyüdükçe gereken çalışma süresini ifade eden gösterim nedir?",
                "points": 10,
                "order": 2,
                "choices": [
                    {"text": "Big-O Notasyonu", "is_correct": True},
                    {"text": "Shannon Entropisi", "is_correct": False},
                    {"text": "Moore Yasası", "is_correct": False},
                    {"text": "Boolean İfadesi", "is_correct": False},
                ],
            },
            {
                "text": "İşletim sisteminde iki veya daha fazla sürecin birbirinin kaynağını beklemesiyle oluşan kilitlenme durumuna ne ad verilir?",
                "points": 10,
                "order": 3,
                "choices": [
                    {"text": "Deadlock (Ölümcül Kilitlenme)", "is_correct": True},
                    {"text": "Race Condition", "is_correct": False},
                    {"text": "Starvation", "is_correct": False},
                    {"text": "Thrashing", "is_correct": False},
                ],
            },
            {
                "text": "İşlemci (CPU) çekirdeği içerisindeki en hızlı ve doğrudan erişilebilen bellek birimi hangisidir?",
                "points": 10,
                "order": 4,
                "choices": [
                    {"text": "Register (Yazmaç)", "is_correct": True},
                    {"text": "L1 Cache", "is_correct": False},
                    {"text": "RAM", "is_correct": False},
                    {"text": "ROM", "is_correct": False},
                ],
            },
            {
                "text": "Ağ protokolleri olan TCP ile UDP arasındaki en temel fark nedir?",
                "points": 10,
                "order": 5,
                "choices": [
                    {"text": "TCP bağlantı temelli ve garantilidir, UDP bağlantısız ve hızlıdır", "is_correct": True},
                    {"text": "UDP hata kontrolü yapar, TCP yapmaz", "is_correct": False},
                    {"text": "TCP sadece yerel ağda çalışır, UDP internette çalışır", "is_correct": False},
                    {"text": "UDP şifreli veri taşır, TCP taşımaz", "is_correct": False},
                ],
            },
            {
                "text": "İkili (Binary) sayı sistemindeki '1011' sayısının onluk (Decimal) karşılığı kaçtır?",
                "points": 10,
                "order": 6,
                "choices": [
                    {"text": "11", "is_correct": True},
                    {"text": "9", "is_correct": False},
                    {"text": "13", "is_correct": False},
                    {"text": "15", "is_correct": False},
                ],
            },
            {
                "text": "İşlemci mimarisinde komut işleme adımlarını donanım katmanında örtüştürerek hızlandıran teknik nedir?",
                "points": 10,
                "order": 7,
                "choices": [
                    {"text": "Pipelining (Boru Hattı)", "is_correct": True},
                    {"text": "Caching", "is_correct": False},
                    {"text": "Branch Prediction", "is_correct": False},
                    {"text": "Overclocking", "is_correct": False},
                ],
            },
            {
                "text": "OSI referans modelinde IP adresleme ve yönlendirme (routing) işlemleri hangi katmanda gerçekleşir?",
                "points": 10,
                "order": 8,
                "choices": [
                    {"text": "Ağ Katmanı (Network Layer - Katman 3)", "is_correct": True},
                    {"text": "Veri Bağı Katmanı (Data Link Layer)", "is_correct": False},
                    {"text": "Taşıma Katmanı (Transport Layer)", "is_correct": False},
                    {"text": "Fiziksel Katman (Physical Layer)", "is_correct": False},
                ],
            },
            {
                "text": "CPU ile ana bellek (RAM) arasındaki hız farkını dengelemek amacıyla kullanılan yüksek hızlı ara bellek türü nedir?",
                "points": 10,
                "order": 9,
                "choices": [
                    {"text": "Cache (Önbellek)", "is_correct": True},
                    {"text": "Sanal Bellek (Virtual Memory)", "is_correct": False},
                    {"text": "Flash Bellek", "is_correct": False},
                    {"text": "ROM Bellek", "is_correct": False},
                ],
            },
            {
                "text": "Moore Yasası (Moore's Law) yaklaşık her 2 yılda bir neyin iki katına çıkacağını öngörmüştür?",
                "points": 10,
                "order": 10,
                "choices": [
                    {"text": "Entegre devre üzerindeki transistör sayısının", "is_correct": True},
                    {"text": "İnternet bant genişliği hızının", "is_correct": False},
                    {"text": "Sabit disk depolama kapasitesinin", "is_correct": False},
                    {"text": "Programlama dillerinin sayısının", "is_correct": False},
                ],
            },
            {
                "text": "Binary Search (İkili Arama) algoritmasının çalışabilmesi için arama yapılacak dizide aranan zorunlu şart nedir?",
                "points": 10,
                "order": 11,
                "choices": [
                    {"text": "Dizinin sıralı (sorted) olması", "is_correct": True},
                    {"text": "Elemanların sayısal olması", "is_correct": False},
                    {"text": "Eleman sayısının çift olması", "is_correct": False},
                    {"text": "Tüm elemanların pozitif olması", "is_correct": False},
                ],
            },
            {
                "text": "Birden fazla işlemin aynı paylaşılan veriye eşzamanlı erişerek tutarsız sonuç üretmesi riskine ne ad verilir?",
                "points": 10,
                "order": 12,
                "choices": [
                    {"text": "Race Condition (Yarış Durumu)", "is_correct": True},
                    {"text": "Deadlock (Kilitlenme)", "is_correct": False},
                    {"text": "Context Switch", "is_correct": False},
                    {"text": "Page Fault", "is_correct": False},
                ],
            },
            {
                "text": "RAM tükendiğinde işletim sisteminin geçici olarak disk üzerinde kullandığı bellek alanına ne ad verilir?",
                "points": 10,
                "order": 13,
                "choices": [
                    {"text": "Sanal Bellek / Takas Alanı (Swap)", "is_correct": True},
                    {"text": "L3 Önbellek", "is_correct": False},
                    {"text": "CMOS", "is_correct": False},
                    {"text": "BIOS ROM", "is_correct": False},
                ],
            },
            {
                "text": "Bilgisayarlarda negatif tam sayıları ikili sistemde göstermek için en yaygın kullanılan yöntem hangisidir?",
                "points": 10,
                "order": 14,
                "choices": [
                    {"text": "Two's Complement (İkiye Tümleyen)", "is_correct": True},
                    {"text": "One's Complement (Bire Tümleyen)", "is_correct": False},
                    {"text": "Sign and Magnitude", "is_correct": False},
                    {"text": "Hexadecimal Offset", "is_correct": False},
                ],
            },
            {
                "text": "İkili Arama Ağacında (Binary Search Tree) bir düğümün sol alt çocuğunun değeri kök düğüme göre nasıldır?",
                "points": 10,
                "order": 15,
                "choices": [
                    {"text": "Kök düğümden daima küçüktür", "is_correct": True},
                    {"text": "Kök düğümden daima büyüktür", "is_correct": False},
                    {"text": "Kök düğümle eşit olmak zorundadır", "is_correct": False},
                    {"text": "Rastgele büyüklüktedir", "is_correct": False},
                ],
            },
            {
                "text": "Bilgisayar başlatıldığında donanımları test eden (POST) ve işletim sistemini yükleyen firmware yazılımı nedir?",
                "points": 10,
                "order": 16,
                "choices": [
                    {"text": "BIOS / UEFI", "is_correct": True},
                    {"text": "İşletim Sistemi Çekirdeği (Kernel)", "is_correct": False},
                    {"text": "Aygıt Sürücüsü (Driver)", "is_correct": False},
                    {"text": "Sistem Daemon'ı", "is_correct": False},
                ],
            },
            {
                "text": "RAID 0 disk yapılandırmasının temel amacı nedir?",
                "points": 10,
                "order": 17,
                "choices": [
                    {"text": "Okuma/yazma hızını artırmak (Striping)", "is_correct": True},
                    {"text": "Veri yedekliliği sağlamak (Mirroring)", "is_correct": False},
                    {"text": "Hata düzeltme paritesi oluşturmak", "is_correct": False},
                    {"text": "Diski donanımsal olarak şifrelemek", "is_correct": False},
                ],
            },
            {
                "text": "Tüm girişleri 1 (True) olduğunda çıkışı 1 veren mantık kapısı hangisidir?",
                "points": 10,
                "order": 18,
                "choices": [
                    {"text": "AND (VE) Kapısı", "is_correct": True},
                    {"text": "OR (VEYA) Kapısı", "is_correct": False},
                    {"text": "XOR Kapısı", "is_correct": False},
                    {"text": "NOT Kapısı", "is_correct": False},
                ],
            },
            {
                "text": "En kötü durumda (Worst-case) bile O(n log n) zaman karmaşıklığı sunan sıralama algoritması hangisidir?",
                "points": 10,
                "order": 19,
                "choices": [
                    {"text": "Merge Sort", "is_correct": True},
                    {"text": "Quick Sort", "is_correct": False},
                    {"text": "Bubble Sort", "is_correct": False},
                    {"text": "Insertion Sort", "is_correct": False},
                ],
            },
            {
                "text": "İşletim sisteminde çalışmakta olan bir programın bellekteki ve işlemcideki aktif çalışma örneğine ne ad verilir?",
                "points": 10,
                "order": 20,
                "choices": [
                    {"text": "Process (Süreç)", "is_correct": True},
                    {"text": "Thread (İş Parçacığı)", "is_correct": False},
                    {"text": "Routine", "is_correct": False},
                    {"text": "Microservice", "is_correct": False},
                ],
            },
        ],
    },
    {
        "name": "Ülkeler",
        "slug": "ulkeler",
        "icon": "Globe",
        "color_theme": "emerald",
        "questions": [
            {
                "text": "Dünyanın yüzölçümü bakımından en büyük ülkesi hangisidir?",
                "points": 10,
                "order": 1,
                "choices": [
                    {"text": "Rusya", "is_correct": True},
                    {"text": "Kanada", "is_correct": False},
                    {"text": "Çin", "is_correct": False},
                    {"text": "Amerika Birleşik Devletleri", "is_correct": False},
                ],
            },
            {
                "text": "Avustralya'nın başkenti neresidir?",
                "points": 10,
                "order": 2,
                "choices": [
                    {"text": "Kanberra", "is_correct": True},
                    {"text": "Sidney", "is_correct": False},
                    {"text": "Melbourne", "is_correct": False},
                    {"text": "Brisbane", "is_correct": False},
                ],
            },
            {
                "text": "Toprakları hem Asya hem de Avrupa kıtasında yer alan kıtalararası mega şehir hangisidir?",
                "points": 10,
                "order": 3,
                "choices": [
                    {"text": "İstanbul", "is_correct": True},
                    {"text": "Kahire", "is_correct": False},
                    {"text": "Bakü", "is_correct": False},
                    {"text": "Tiflis", "is_correct": False},
                ],
            },
            {
                "text": "Nüfus bakımından şu an dünyanın en kalabalık ülkesi hangisidir?",
                "points": 10,
                "order": 4,
                "choices": [
                    {"text": "Hindistan", "is_correct": True},
                    {"text": "Çin", "is_correct": False},
                    {"text": "ABD", "is_correct": False},
                    {"text": "Endonezya", "is_correct": False},
                ],
            },
            {
                "text": "Japonya'nın resmi para birimi nedir?",
                "points": 10,
                "order": 5,
                "choices": [
                    {"text": "Yen", "is_correct": True},
                    {"text": "Yuan", "is_correct": False},
                    {"text": "Won", "is_correct": False},
                    {"text": "Baht", "is_correct": False},
                ],
            },
            {
                "text": "Dünyanın en uzun nehri kabul edilen Nil Nehri hangi kıtadadır?",
                "points": 10,
                "order": 6,
                "choices": [
                    {"text": "Afrika", "is_correct": True},
                    {"text": "Güney Amerika", "is_correct": False},
                    {"text": "Asya", "is_correct": False},
                    {"text": "Kuzey Amerika", "is_correct": False},
                ],
            },
            {
                "text": "Güney Amerika kıtasında resmi dili Portekizce olan ülke hangisidir?",
                "points": 10,
                "order": 7,
                "choices": [
                    {"text": "Brezilya", "is_correct": True},
                    {"text": "Arjantin", "is_correct": False},
                    {"text": "Şili", "is_correct": False},
                    {"text": "Kolombiya", "is_correct": False},
                ],
            },
            {
                "text": "İsviçre'nin fiili (de facto) federal başkenti neresidir?",
                "points": 10,
                "order": 8,
                "choices": [
                    {"text": "Bern", "is_correct": True},
                    {"text": "Zürih", "is_correct": False},
                    {"text": "Cenevre", "is_correct": False},
                    {"text": "Basel", "is_correct": False},
                ],
            },
            {
                "text": "Dünyanın hem yüzölçümü hem de nüfus bakımından en küçük bağımsız devleti hangisidir?",
                "points": 10,
                "order": 9,
                "choices": [
                    {"text": "Vatikan", "is_correct": True},
                    {"text": "Monako", "is_correct": False},
                    {"text": "San Marino", "is_correct": False},
                    {"text": "Lihtenştayn", "is_correct": False},
                ],
            },
            {
                "text": "Aşağıdaki ülkelerden hangisi İskandinavya / Kuzey Avrupa ülkesi DEĞİLDİR?",
                "points": 10,
                "order": 10,
                "choices": [
                    {"text": "Portekiz", "is_correct": True},
                    {"text": "Norveç", "is_correct": False},
                    {"text": "İsveç", "is_correct": False},
                    {"text": "Finlandiya", "is_correct": False},
                ],
            },
            {
                "text": "Eyfel Kulesi hangi ülkenin başkentinde yer alır?",
                "points": 10,
                "order": 11,
                "choices": [
                    {"text": "Fransa (Paris)", "is_correct": True},
                    {"text": "İtalya (Roma)", "is_correct": False},
                    {"text": "İspanya (Madrid)", "is_correct": False},
                    {"text": "Almanya (Berlin)", "is_correct": False},
                ],
            },
            {
                "text": "Dünyanın en yüksek zirvesi olan Everest Tepesi hangi dağ sırasındadır?",
                "points": 10,
                "order": 12,
                "choices": [
                    {"text": "Himalayalar", "is_correct": True},
                    {"text": "Alpler", "is_correct": False},
                    {"text": "And Dağları", "is_correct": False},
                    {"text": "Ural Dağları", "is_correct": False},
                ],
            },
            {
                "text": "Kanada ulusal bayrağında simge olarak hangi ağacın yaprağı yer alır?",
                "points": 10,
                "order": 13,
                "choices": [
                    {"text": "Akçaağaç (Maple)", "is_correct": True},
                    {"text": "Meşe Yaprağı", "is_correct": False},
                    {"text": "Çam İğnesi", "is_correct": False},
                    {"text": "Zeytin Dalı", "is_correct": False},
                ],
            },
            {
                "text": "Akdeniz ile Kızıldeniz'i birbirine bağlayan yapay deniz kanalı hangisidir?",
                "points": 10,
                "order": 14,
                "choices": [
                    {"text": "Süveyş Kanalı", "is_correct": True},
                    {"text": "Panama Kanalı", "is_correct": False},
                    {"text": "Korint Kanalı", "is_correct": False},
                    {"text": "Kiel Kanalı", "is_correct": False},
                ],
            },
            {
                "text": "Afrika kıtasının en yüksek dağı olan Kilimanjaro hangi ülkededir?",
                "points": 10,
                "order": 15,
                "choices": [
                    {"text": "Tanzanya", "is_correct": True},
                    {"text": "Kenya", "is_correct": False},
                    {"text": "Güney Afrika", "is_correct": False},
                    {"text": "Uganda", "is_correct": False},
                ],
            },
            {
                "text": "Dünyada 260 binden fazla ada ile en çok adaya sahip olan ülke hangisidir?",
                "points": 10,
                "order": 16,
                "choices": [
                    {"text": "İsveç", "is_correct": True},
                    {"text": "Norveç", "is_correct": False},
                    {"text": "Filipinler", "is_correct": False},
                    {"text": "Endonezya", "is_correct": False},
                ],
            },
            {
                "text": "Güney Amerika'da Peru sınırları içinde yer alan ünlü antik İnka şehri hangisidir?",
                "points": 10,
                "order": 17,
                "choices": [
                    {"text": "Machu Picchu", "is_correct": True},
                    {"text": "Chichen Itza", "is_correct": False},
                    {"text": "Petra", "is_correct": False},
                    {"text": "Tikal", "is_correct": False},
                ],
            },
            {
                "text": "İzlanda'nın başkenti neresidir?",
                "points": 10,
                "order": 18,
                "choices": [
                    {"text": "Reykjavik", "is_correct": True},
                    {"text": "Oslo", "is_correct": False},
                    {"text": "Helsinki", "is_correct": False},
                    {"text": "Kopenhag", "is_correct": False},
                ],
            },
            {
                "text": "Dünyanın en derin ve en eski tatlı su gölü olan Baykal Gölü hangi ülkededir?",
                "points": 10,
                "order": 19,
                "choices": [
                    {"text": "Rusya", "is_correct": True},
                    {"text": "Moğolistan", "is_correct": False},
                    {"text": "Kanada", "is_correct": False},
                    {"text": "Kazakistan", "is_correct": False},
                ],
            },
            {
                "text": "Hem Atlas Okyanusu'na hem de Akdeniz'e kıyısı bulunan Afrika ülkesi hangisidir?",
                "points": 10,
                "order": 20,
                "choices": [
                    {"text": "Fas", "is_correct": True},
                    {"text": "Cezayir", "is_correct": False},
                    {"text": "Tunus", "is_correct": False},
                    {"text": "Libya", "is_correct": False},
                ],
            },
        ],
    },
    {
        "name": "Fizik",
        "slug": "fizik",
        "icon": "Atom",
        "color_theme": "orange",
        "questions": [
            {
                "text": "Boşlukta ışığın yayılma hızı yaklaşık olarak saniyede kaç kilometredir?",
                "points": 10,
                "order": 1,
                "choices": [
                    {"text": "300.000 km/s", "is_correct": True},
                    {"text": "150.000 km/s", "is_correct": False},
                    {"text": "1.000.000 km/s", "is_correct": False},
                    {"text": "30.000 km/s", "is_correct": False},
                ],
            },
            {
                "text": "Albert Einstein'ın ünlü kütle-enerji eşdeğerliği bağıntısı hangisidir?",
                "points": 10,
                "order": 2,
                "choices": [
                    {"text": "E = mc²", "is_correct": True},
                    {"text": "F = m * a", "is_correct": False},
                    {"text": "V = I * R", "is_correct": False},
                    {"text": "PV = nRT", "is_correct": False},
                ],
            },
            {
                "text": "SI birim sisteminde kuvvetin (Force) standart birimi nedir?",
                "points": 10,
                "order": 3,
                "choices": [
                    {"text": "Newton (N)", "is_correct": True},
                    {"text": "Joule (J)", "is_correct": False},
                    {"text": "Pascal (Pa)", "is_correct": False},
                    {"text": "Watt (W)", "is_correct": False},
                ],
            },
            {
                "text": "Termodinamiğin birinci yasası temel olarak hangi korunum ilkesini ifade eder?",
                "points": 10,
                "order": 4,
                "choices": [
                    {"text": "Enerjinin Korunumu", "is_correct": True},
                    {"text": "Momentumun Korunumu", "is_correct": False},
                    {"text": "Kütlenin Korunumu", "is_correct": False},
                    {"text": "Elektriksel Yükün Korunumu", "is_correct": False},
                ],
            },
            {
                "text": "Elektrik akım şiddetinin SI birim sistemindeki birimi nedir?",
                "points": 10,
                "order": 5,
                "choices": [
                    {"text": "Amper (A)", "is_correct": True},
                    {"text": "Volt (V)", "is_correct": False},
                    {"text": "Ohm (Ω)", "is_correct": False},
                    {"text": "Coulomb (C)", "is_correct": False},
                ],
            },
            {
                "text": "Işığın farklı yoğunluktaki bir ortama geçerken hız ve doğrultu değiştirmesi olayına ne denir?",
                "points": 10,
                "order": 6,
                "choices": [
                    {"text": "Kırılma (Refraction)", "is_correct": True},
                    {"text": "Yansıma (Reflection)", "is_correct": False},
                    {"text": "Kırınım (Diffraction)", "is_correct": False},
                    {"text": "Girişim (Interference)", "is_correct": False},
                ],
            },
            {
                "text": "Dünya yüzeyinde yerçekimi ivmesi (g) yaklaşık olarak kaç m/s² kabul edilir?",
                "points": 10,
                "order": 7,
                "choices": [
                    {"text": "9.8 m/s²", "is_correct": True},
                    {"text": "3.14 m/s²", "is_correct": False},
                    {"text": "12.4 m/s²", "is_correct": False},
                    {"text": "6.67 m/s²", "is_correct": False},
                ],
            },
            {
                "text": "Bir cismin mevcut hareket veya durma durumunu koruma eğilimine ne ad verilir?",
                "points": 10,
                "order": 8,
                "choices": [
                    {"text": "Eylemsizlik (Inertia)", "is_correct": True},
                    {"text": "Sürtünme", "is_correct": False},
                    {"text": "İtme (Impulse)", "is_correct": False},
                    {"text": "Tork", "is_correct": False},
                ],
            },
            {
                "text": "Ses dalgaları ile ilgili aşağıdaki fiziksel gerçeklerden hangisi doğrudur?",
                "points": 10,
                "order": 9,
                "choices": [
                    {"text": "Ses dalgaları mekanik dalgadır ve boşlukta yayılamaz", "is_correct": True},
                    {"text": "Ses dalgaları ışıktan daha hızlı yayılır", "is_correct": False},
                    {"text": "Ses sadece katılarda yayılır", "is_correct": False},
                    {"text": "Sesin yayılma hızı ortam yoğunluğundan bağımsızdır", "is_correct": False},
                ],
            },
            {
                "text": "Kuantum fiziğinde ışığın ve parçacıkların hem dalga hem tanecik davranışı sergilemesine ne denir?",
                "points": 10,
                "order": 10,
                "choices": [
                    {"text": "Dalga-Parçacık İkiliği (Wave-Particle Duality)", "is_correct": True},
                    {"text": "Kuantum Dolanıklığı (Entanglement)", "is_correct": False},
                    {"text": "Kuantum Tünelleme", "is_correct": False},
                    {"text": "Süperpozisyon İlkesi", "is_correct": False},
                ],
            },
            {
                "text": "SI birim sisteminde frekansın (saniyedeki titreşim sayısı) standart birimi nedir?",
                "points": 10,
                "order": 11,
                "choices": [
                    {"text": "Hertz (Hz)", "is_correct": True},
                    {"text": "Desibel (dB)", "is_correct": False},
                    {"text": "Radyan", "is_correct": False},
                    {"text": "Candela", "is_correct": False},
                ],
            },
            {
                "text": "Newton'ın ikinci hareket yasasının temel matematiksel formülü nedir?",
                "points": 10,
                "order": 12,
                "choices": [
                    {"text": "F = m * a", "is_correct": True},
                    {"text": "W = F * d", "is_correct": False},
                    {"text": "P = F / A", "is_correct": False},
                    {"text": "p = m * v", "is_correct": False},
                ],
            },
            {
                "text": "Elektrik devrelerinde Gerilim (V), Akım (I) ve Direnç (R) ilişkisini veren temel yasa hangisidir?",
                "points": 10,
                "order": 13,
                "choices": [
                    {"text": "Ohm Yasası (V = I * R)", "is_correct": True},
                    {"text": "Faraday İndüksiyon Yasası", "is_correct": False},
                    {"text": "Lenz Yasası", "is_correct": False},
                    {"text": "Coulomb Yasası", "is_correct": False},
                ],
            },
            {
                "text": "Maddenin katı, sıvı ve gaz halleri dışındaki iyonlaşmış gaz formundaki dördüncü hali nedir?",
                "points": 10,
                "order": 14,
                "choices": [
                    {"text": "Plazma", "is_correct": True},
                    {"text": "Bose-Einstein Yoğuşması", "is_correct": False},
                    {"text": "Süperiletken", "is_correct": False},
                    {"text": "Sıvı Kristal", "is_correct": False},
                ],
            },
            {
                "text": "Birim yüzeye dik olarak etki eden net kuvvet miktarına ne ad verilir?",
                "points": 10,
                "order": 15,
                "choices": [
                    {"text": "Basınç (Pressure)", "is_correct": True},
                    {"text": "Güç (Power)", "is_correct": False},
                    {"text": "İş (Work)", "is_correct": False},
                    {"text": "Gerilme (Tension)", "is_correct": False},
                ],
            },
            {
                "text": "Sabit süratle dairesel yörüngede dönen bir cismin ivmesi neden sıfırdan farklıdır?",
                "points": 10,
                "order": 16,
                "choices": [
                    {"text": "Hız vektörünün yönü sürekli değiştiği için (Merkezcil İvme)", "is_correct": True},
                    {"text": "Kütlesi sürekli arttığı için", "is_correct": False},
                    {"text": "Sürtünme sıfır olduğu için", "is_correct": False},
                    {"text": "Enerji kaybettiği için", "is_correct": False},
                ],
            },
            {
                "text": "Termodinamikte bir sistemin düzensizliğinin veya rastgeleliğinin ölçüsü olan kavram nedir?",
                "points": 10,
                "order": 17,
                "choices": [
                    {"text": "Entropi", "is_correct": True},
                    {"text": "Entalpi", "is_correct": False},
                    {"text": "İç Enerji", "is_correct": False},
                    {"text": "Isı Kapasitesi", "is_correct": False},
                ],
            },
            {
                "text": "Kuantum mekaniğinde bir parçacığın konumu ile momentumunun aynı anda kesin olarak ölçülemeyeceğini belirten ilke nedir?",
                "points": 10,
                "order": 18,
                "choices": [
                    {"text": "Heisenberg Belirsizlik İlkesi", "is_correct": True},
                    {"text": "Pauli Dışarlama İlkesi", "is_correct": False},
                    {"text": "Schrödinger Dalga Denklemi", "is_correct": False},
                    {"text": "Planck Yasası", "is_correct": False},
                ],
            },
            {
                "text": "Güneş ve yıldızların merkezinde hidrojen atomlarının birleşerek helyuma dönüşmesiyle devasa enerji üreten reaksiyon nedir?",
                "points": 10,
                "order": 19,
                "choices": [
                    {"text": "Nükleer Füzyon (Çekirdek Kaynaşması)", "is_correct": True},
                    {"text": "Nükleer Fisyon (Çekirdek Bölünmesi)", "is_correct": False},
                    {"text": "Kimyasal Yanma", "is_correct": False},
                    {"text": "Radyoaktif Bozunma", "is_correct": False},
                ],
            },
            {
                "text": "Elektromanyetik spektrumda dalga boyu en kısa ve enerjisi en yüksek olan ışın türü hangisidir?",
                "points": 10,
                "order": 20,
                "choices": [
                    {"text": "Gama Işınları", "is_correct": True},
                    {"text": "X Işınları (Röntgen)", "is_correct": False},
                    {"text": "Morötesi (UV) Işınlar", "is_correct": False},
                    {"text": "Radyo Dalgaları", "is_correct": False},
                ],
            },
        ],
    },
    {
        "name": "Futbol",
        "slug": "futbol",
        "icon": "Trophy",
        "color_theme": "rose",
        "questions": [
            {
                "text": "Futbol tarihinde FIFA Dünya Kupası'nı en çok kazanan ülke hangisidir?",
                "points": 10,
                "order": 1,
                "choices": [
                    {"text": "Brezilya", "is_correct": True},
                    {"text": "Almanya", "is_correct": False},
                    {"text": "İtalya", "is_correct": False},
                    {"text": "Arjantin", "is_correct": False},
                ],
            },
            {
                "text": "UEFA Şampiyonlar Ligi kupasını müzesine en çok götüren kulüp hangisidir?",
                "points": 10,
                "order": 2,
                "choices": [
                    {"text": "Real Madrid", "is_correct": True},
                    {"text": "AC Milan", "is_correct": False},
                    {"text": "Bayern Münih", "is_correct": False},
                    {"text": "Liverpool", "is_correct": False},
                ],
            },
            {
                "text": "2022 FIFA Dünya Kupası finalinde şampiyon olan milli takım hangisidir?",
                "points": 10,
                "order": 3,
                "choices": [
                    {"text": "Arjantin", "is_correct": True},
                    {"text": "Fransa", "is_correct": False},
                    {"text": "Hırvatistan", "is_correct": False},
                    {"text": "Fas", "is_correct": False},
                ],
            },
            {
                "text": "Kariyerinde en çok Ballon d'Or (Altın Top) ödülü kazanan futbolcu kimdir?",
                "points": 10,
                "order": 4,
                "choices": [
                    {"text": "Lionel Messi", "is_correct": True},
                    {"text": "Cristiano Ronaldo", "is_correct": False},
                    {"text": "Johan Cruyff", "is_correct": False},
                    {"text": "Michel Platini", "is_correct": False},
                ],
            },
            {
                "text": "Futbolda aşağıdaki durumlardan hangisinde doğrudan ofsayt kuralı GEÇERSİZDİR?",
                "points": 10,
                "order": 5,
                "choices": [
                    {"text": "Taç Atışı", "is_correct": True},
                    {"text": "Direkt Serbest Vuruş", "is_correct": False},
                    {"text": "Endirekt Serbest Vuruş", "is_correct": False},
                    {"text": "Hakem Atışı", "is_correct": False},
                ],
            },
            {
                "text": "2000 yılında UEFA Kupası ve UEFA Süper Kupa'yı kazanan Türk futbol kulübü hangisidir?",
                "points": 10,
                "order": 6,
                "choices": [
                    {"text": "Galatasaray", "is_correct": True},
                    {"text": "Fenerbahçe", "is_correct": False},
                    {"text": "Beşiktaş", "is_correct": False},
                    {"text": "Trabzonspor", "is_correct": False},
                ],
            },
            {
                "text": "Standart bir futbol kalesinde iki direk arasındaki içten içe mesafe kaç metredir?",
                "points": 10,
                "order": 7,
                "choices": [
                    {"text": "7.32 metre", "is_correct": True},
                    {"text": "7.50 metre", "is_correct": False},
                    {"text": "6.80 metre", "is_correct": False},
                    {"text": "8.00 metre", "is_correct": False},
                ],
            },
            {
                "text": "Bir futbol karşılaşmasında normal sürede her bir yarı kaçar dakikadır?",
                "points": 10,
                "order": 8,
                "choices": [
                    {"text": "45 Dakika", "is_correct": True},
                    {"text": "40 Dakika", "is_correct": False},
                    {"text": "50 Dakika", "is_correct": False},
                    {"text": "35 Dakika", "is_correct": False},
                ],
            },
            {
                "text": "Takım arkadaşının bilerek ayakla verdiği geri pası kaleci eliyle tutarsa hakem ne kararı verir?",
                "points": 10,
                "order": 9,
                "choices": [
                    {"text": "Endirekt Serbest Vuruş (Çift Vuruş)", "is_correct": True},
                    {"text": "Penaltı", "is_correct": False},
                    {"text": "Direkt Serbest Vuruş", "is_correct": False},
                    {"text": "Sarı Kart & Taç Atışı", "is_correct": False},
                ],
            },
            {
                "text": "Futbol tarihinde 'Siyah İnci' ve 'Kral' lakabıyla anılan efsanevi futbolcu kimdir?",
                "points": 10,
                "order": 10,
                "choices": [
                    {"text": "Pelé", "is_correct": True},
                    {"text": "Diego Maradona", "is_correct": False},
                    {"text": "Ronaldinho", "is_correct": False},
                    {"text": "Romário", "is_correct": False},
                ],
            },
            {
                "text": "Almanya'da düzenlenen EURO 2024 Avrupa Futbol Şampiyonası'nda kupayı kim kazandı?",
                "points": 10,
                "order": 11,
                "choices": [
                    {"text": "İspanya", "is_correct": True},
                    {"text": "İngiltere", "is_correct": False},
                    {"text": "Almanya", "is_correct": False},
                    {"text": "Fransa", "is_correct": False},
                ],
            },
            {
                "text": "Futbol sahasında penaltı noktası kale çizgisinden tam olarak kaç metre uzaklıktadır?",
                "points": 10,
                "order": 12,
                "choices": [
                    {"text": "11 Metre", "is_correct": True},
                    {"text": "9.15 Metre", "is_correct": False},
                    {"text": "12 Metre", "is_correct": False},
                    {"text": "10 Metre", "is_correct": False},
                ],
            },
            {
                "text": "Bir takımda kaç oyuncu kırmızı kart görürse (takım 6 kişiye düşerse) maç tatil edilir?",
                "points": 10,
                "order": 13,
                "choices": [
                    {"text": "5 Oyuncu", "is_correct": True},
                    {"text": "4 Oyuncu", "is_correct": False},
                    {"text": "3 Oyuncu", "is_correct": False},
                    {"text": "6 Oyuncu", "is_correct": False},
                ],
            },
            {
                "text": "Dünyaca ünlü 'El Clásico' derbisi hangi iki takım arasında oynanır?",
                "points": 10,
                "order": 14,
                "choices": [
                    {"text": "Real Madrid - Barcelona", "is_correct": True},
                    {"text": "Real Madrid - Atlético Madrid", "is_correct": False},
                    {"text": "Barcelona - Sevilla", "is_correct": False},
                    {"text": "Inter - AC Milan", "is_correct": False},
                ],
            },
            {
                "text": "Süper Lig tarihinde sezonu namağlup (yenilgisiz) şampiyon tamamlayan tek takım hangisidir?",
                "points": 10,
                "order": 15,
                "choices": [
                    {"text": "Beşiktaş (1991-92)", "is_correct": True},
                    {"text": "Galatasaray", "is_correct": False},
                    {"text": "Fenerbahçe", "is_correct": False},
                    {"text": "Trabzonspor", "is_correct": False},
                ],
            },
            {
                "text": "Futbolda 'Hat-trick' terimi hangi başarıyı ifade eder?",
                "points": 10,
                "order": 16,
                "choices": [
                    {"text": "Bir oyuncunun aynı maçta 3 gol atmasını", "is_correct": True},
                    {"text": "Bir oyuncunun 3 asist yapmasını", "is_correct": False},
                    {"text": "Kalecinin 3 penaltı kurtarmasını", "is_correct": False},
                    {"text": "Bir takımın 3 maç üst üste kazanmasını", "is_correct": False},
                ],
            },
            {
                "text": "2003-2004 Premier Lig sezonunu hiç yenilmeden tamamlayıp 'The Invincibles' unvanını alan takım hangisidir?",
                "points": 10,
                "order": 17,
                "choices": [
                    {"text": "Arsenal", "is_correct": True},
                    {"text": "Manchester United", "is_correct": False},
                    {"text": "Chelsea", "is_correct": False},
                    {"text": "Manchester City", "is_correct": False},
                ],
            },
            {
                "text": "FIFA Dünya Kupası finalleri tarihinde toplam 16 golle en çok gol atan oyuncu rekoru kime aittir?",
                "points": 10,
                "order": 18,
                "choices": [
                    {"text": "Miroslav Klose", "is_correct": True},
                    {"text": "Ronaldo Nazário", "is_correct": False},
                    {"text": "Gerd Müller", "is_correct": False},
                    {"text": "Kylian Mbappé", "is_correct": False},
                ],
            },
            {
                "text": "Futbolda 'Panenka' vuruş tekniği penaltıda nasıl uygulanır?",
                "points": 10,
                "order": 19,
                "choices": [
                    {"text": "Topun dibine hafifçe vurup aşırtarak kalenin ortasına göndermek", "is_correct": True},
                    {"text": "Çok sert ve 90'a doğru vurmak", "is_correct": False},
                    {"text": "Ters ayakla kaleciyi yanıltarak vurmak", "is_correct": False},
                    {"text": "Yerden köşeye plase bırakmak", "is_correct": False},
                ],
            },
            {
                "text": "FIFA tarafından her yıl dünyada yılın en estetik ve güzel golünü atan futbolcuya verilen ödül nedir?",
                "points": 10,
                "order": 20,
                "choices": [
                    {"text": "FIFA Puskás Ödülü", "is_correct": True},
                    {"text": "Altın Ayakkabı", "is_correct": False},
                    {"text": "Yashin Ödülü", "is_correct": False},
                    {"text": "Ballon d'Or", "is_correct": False},
                ],
            },
        ],
    },
]


class Command(BaseCommand):
    help = "Populate initial 5 categories and 100 questions (20 per category) for Rapid Quiz"

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

