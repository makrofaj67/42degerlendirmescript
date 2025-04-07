import textwrap
import sys
import time

# --- Yapılandırılmış Evaluation Soruları (Kategori ve Anahtar Kelime ile) ---

# Değerlendiren (Evaluator) için Sorular
evaluator_questions_structured = {
    "Genel ve Fonksiyonellik": [
        ("Projenin adı ve değerlendirilen öğrencinin login'i nedir?", "Isınma turları.", "Proje Adı/Login"),
        ("Proje konusundaki (subject) tüm zorunlu (mandatory) kısımlar tamamlanmış mı? Eksikler var mı?", "Subject'i kutsal metin gibi inceledin mi?", "Zorunluluklar"),
        ("Program derleniyor mu? 'Makefile' sihirli değneğini doğru sallamış mı?", "'Warning'ler sadece birer öneri midir, yoksa dikkate alınmış mı?", "Derleme/Makefile"),
        ("Program çalışıyor mu? Beklenen temel işlevleri yerine getiriyor mu?", "Yoksa sadece terminalde güzel bir isim mi gösteriyor?", "Çalışma Durumu"),
        ("Hiç 'segmentation fault' (ya da başka bir crash) ile karşılaştın mı? Varsa, hangi durumlarda?", "Programın arada bir kestirme ihtiyacı oluyor mu?", "Çökme/Crash"),
        ("Kenar durumlar (edge cases) ve hatalı girdiler (error handling) nasıl ele alınmış? Program nazikçe mi uyarıyor, yoksa panik mi yapıyor?", "Kullanıcı 'abc' yazdığında programın ruh sağlığı bozuluyor mu?", "Hata Yönetimi/Edge Cases"),
    ],
    "Kod Kalitesi ve Anlaşılırlık": [
        ("Kod okunabilir mi? Değişken ve fonksiyon isimleri 'a', 'b', 'temp' üçgeninden çıkabilmiş mi?", "Kod şiir gibi mi akıyor, yoksa çözülmesi gereken bir bulmaca mı?", "Okunabilirlik/İsimlendirme"),
        ("Norminette (veya proje özelindeki stil rehberi) kurallarına ne kadar uyulmuş? Göz kanatan ihlaller var mı?", "Norminette'in ruhu şad olmuş mu?", "Norminette/Stil"),
        ("Kodda gereksiz karmaşıklık veya tekrar eden bloklar var mı? Daha basit/zarif çözümler olabilir miydi?", "'Kopyala-yapıştır' sanatının incelikleri mi sergilenmiş?", "Karmaşıklık/Tekrar"),
        ("Yorum satırları kullanılmış mı? Kullanıldıysa, kodu açıklıyor mu yoksa 'bu bir fonksiyondur' gibi bariz şeyleri mi söylüyor?", "Yorumlar yol gösterici mi, kafa karıştırıcı mı?", "Yorum Satırları"),
    ],
    "Anlama ve Problem Çözme": [
        ("Değerlendirilen kişi yazdığı kodu açıklayabiliyor mu? Mantığını ve neden o yolu seçtiğini anlatabiliyor mu?", "Kodu uzaylılar mı yazmış, yoksa kontrol kendisinde mi?", "Kod Açıklama"),
        ("Karşılaştığı zorlukları ve bunları nasıl aştığını anlatabiliyor mu? Hangi kaynakları kullanmış?", "Google ve Stack Overflow'a minnettar mı, yoksa kendi başına mı dağları devirmiş?", "Zorluklar/Kaynaklar"),
        ("Alternatif çözüm yolları düşünmüş mü? Neden mevcut çözümü tercih ettiğini açıklayabiliyor mu?", "Tek bir yola saplanıp kalmış mı, yoksa ufku geniş mi?", "Alternatif Çözümler"),
    ],
    "Akademik Dürüstlük ve İşbirliği": [
        ("Kodun özgün olduğuna dair bir şüphen var mı? İntihal (cheating) belirtisi gözlemledin mi?", "Kodun DNA'sı başkasına mı ait gibi duruyor? (Şüphe varsa, Bocal'a bildirmeyi unutma!)", "Özgünlük/İntihal Şüphesi"),
        ("Değerlendirme süreci nasıl geçti? İletişim açık ve yapıcı mıydı?", "Karşılıklı 'Aydınlanma Anları' yaşandı mı?", "Değerlendirme Süreci/İletişim"),
    ],
    "Sonuç ve Öneriler": [
        ("Projenin en güçlü yanı neydi?", "Nerede 'işte bu!' dedin?", "En Güçlü Yan"),
        ("Geliştirilebilecek en önemli alan nedir? Bir sonraki projede neye dikkat etmesini önerirsin?", "Yapıcı eleştiri kaslarımızı çalıştıralım.", "Geliştirilecek Alan/Öneri"),
        ("Genel bir puan (0-100 arası gibi düşünebilirsin, ama sadece referans amaçlı) veya his versen ne olurdu?", "İçindeki ses ne diyor?", "Genel İzlenim/Puan Hissi"),
    ]
}

# Değerlendirilen (Evaluated - Kendi Kendine) için Sorular
evaluated_self_reflection_questions_structured = {
    "Proje ve Süreç": [
        ("Projenin adı ve kendi login'in nedir?", "Hafıza tazeleme.", "Proje Adı/Login"),
        ("Bu projede öğrenmeyi hedeflediğin ana konu(lar) neydi ve ne kadarını başardığını düşünüyorsun?", "Beklentiler ve gerçekler masaya yatırılsın.", "Öğrenme Hedefleri"),
        ("Projeyi yaparken en çok zorlandığın kısım hangisiydi?", "Hangi noktada 'ben ne yapıyorum?' diye sordun?", "En Zor Kısım"),
        ("Bu zorlukların üstesinden nasıl geldin? Hangi kaynaklar (internet, arkadaşlar, manual'lar) sana yol gösterdi?", "'Aha!' anını ne tetikledi?", "Zorlukları Aşma/Kaynaklar"),
        ("Proje üzerinde ne kadar zaman harcadığını tahmin ediyorsun?", "Zaman göreceli midir, yoksa sadece Intra logları mı kesindir?", "Harcanan Zaman"),
    ],
    "Kod ve Çözüm": [
        ("Yazdığın koddan memnun musun? 'İşte bu benim eserim!' diyebiliyor musun?", "Gurur mu duyuyorsun, yoksa 'geçmiş olsun' mu diyorsun?", "Kod Memnuniyeti"),
        ("Şimdi tekrar başlasan, neyi farklı yapardın?", "Gelecekteki kendine bir not bırak.", "Farklı Yapılacaklar"),
        ("Kodunun en güçlü ve en zayıf yönleri neler sence?", "Kendine karşı acımasızca dürüst olma vakti.", "Güçlü/Zayıf Yönler"),
        ("Projedeki tüm kod satırlarını gerçekten anladığını düşünüyor musun? Rastgele bir satırı açıklaman istense yapabilir misin?", "Kopyala-yapıştır'ın karanlık tarafına geçtin mi?", "Kod Anlayışı"),
        ("Norminette veya stil kurallarına uymak ne kadar zordu/kolaydı?", "Norminette ile aran nasıl?", "Norminette Uyumu"),
    ],
    "Öğrenme ve Gelişim": [
        ("Bu projeden öğrendiğin en önemli 1-2 teknik veya kavram nedir?", "Beynindeki hangi yeni nöron bağlantıları aktive oldu?", "Öğrenilen Teknikler"),
        ("'Öğrenmeyi öğrenme' konusunda bu proje sana ne kattı?", "Balık tutmayı mı öğrendin, yoksa sadece balık mı yedin?", "Öğrenmeyi Öğrenme Katkısı"),
        ("Bilgiye ulaşma ve doğrulama (verification) sürecinde nelere dikkat ettin?", "İnternetteki her bilgiye hemen inandın mı, yoksa şüpheci mi yaklaştın?", "Bilgi Doğrulama"),
    ],
    "Değerlendirmeye Hazırlık": [
        ("Değerlendirmede hangi soruların gelmesini bekliyorsun?", "Kristal kürene baktın mı?", "Beklenen Sorular"),
        ("Kodunun hangi kısımlarını açıklamaktan çekiniyorsun (varsa)?", "Saklanan iskeletler var mı?", "Açıklamaktan Çekinilen Kısımlar"),
        ("Değerlendirenin hangi potansiyel hataları bulmasından endişe ediyorsun?", "Umarım görmez dediğin yerler...", "Endişe Edilen Hatalar"),
    ],
    "Sonuç": [
        ("Bu projeyi bitirmiş olmak sana ne hissettiriyor?", "Rahatlama mı, zafer mi, yoksa 'bir sonrakine geçelim' mi?", "Proje Bitirme Hissi"),
        ("Bir sonraki projeye başlarken bu deneyimden hangi dersi yanında götüreceksin?", "Geleceğe yatırım.", "Alınan Dersler"),
    ]
}

# Değerlendirilenin Değerlendireni Değerlendirmesi için Sorular
evaluated_reviewing_evaluator_questions_structured = {
    "Hazırlık ve Anlayış": [
        ("Değerlendirenin adı/login'i nedir?", "Kime geri bildirim veriyoruz?", "Değerlendiren Kimliği"),
        ("Değerlendiren, projeyi (subject) önceden incelemiş gibi miydi, yoksa ilk defa mı görüyordu?", "Hazırlıklı bir savaşçı mıydı, yoksa konuya Fransız mıydı?", "Subject Hazırlığı"),
        ("Kodunu ve çözümünü genel olarak anladığını düşünüyor musun? Mantığını takip edebildi mi?", "Aynı dili konuşabildiniz mi?", "Kodu Anlama"),
    ],
    "Süreç ve Yaklaşım": [
        ("Değerlendirme sırasında konuya (subject) sadık kalındı mı? Yoksa kişisel tercihler veya konu dışı beklentiler mi ön plana çıktı?", "Kutsal subject'in sınırları içinde kalındı mı?", "Subject'e Sadakat"),
        ("Sorulan sorular adil, ilgili ve düşünmeye teşvik edici miydi?", "Sorular ufuk açıcı mıydı, yoksa sadece 'çalışıyor mu?' seviyesinde miydi?", "Soru Kalitesi/Adilliği"),
        ("Projenin farklı yönlerini (Makefile, Norminette, hatalar, kenar durumlar vb.) yeterince ve dengeli bir şekilde inceledi mi?", "Sadece sevdiği kısımlara mı baktı?", "İnceleme Kapsamı"),
        ("Zaman yönetimi nasıldı? Değerlendirme süresi verimli kullanıldı mı?", "Süre yetti mi, yoksa aceleye mi geldi?", "Zaman Yönetimi"),
    ],
    "İletişim ve Tutum": [
        ("Değerlendirenin soruları ve geri bildirimleri net ve anlaşılır mıydı?", "Kristal küreye ihtiyaç duydun mu, yoksa meramını anlatabildi mi?", "İletişim Netliği"),
        ("İletişim tarzı saygılı, sabırlı ve yapıcı mıydı?", "Ego savaşları mı yaşandı, yoksa öğrenme odaklı bir diyalog muydu?", "İletişim Tarzı/Saygı"),
        ("Açıklamalarını ve cevaplarını dikkatle dinlediğini hissettin mi?", "Sözünü kesip durdu mu, yoksa sana alan tanıdı mı?", "Dinleme Becerisi"),
        ("Geri bildirim verirken hem olumlu yönleri hem de geliştirilebilecek alanları belirtti mi?", "Sadece hataları mı saydı, yoksa iyi yapılanları da takdir etti mi?", "Geri Bildirim Dengesi"),
    ],
    "Genel Deneyim ve Sonuç": [
        ("Bu değerlendirme süreci genel olarak sana ne kattı? Yeni bir şey öğrendin mi veya farklı bir bakış açısı kazandın mı?", "Sadece bir 'geçti/kaldı' anı mıydı, yoksa öğretici miydi?", "Öğrenme Katkısı"),
        ("Değerlendirme sonucunda verilen puan veya geri bildirim sence adil miydi? Neden?", "İçine sindi mi?", "Sonuç Adilliği"),
        ("Değerlendirenin yaptığı en iyi şey/en olumlu yaklaşım neydi?", "Neyi özellikle takdir ettin?", "En Olumlu Yaklaşım"),
        ("Gelecekteki değerlendirmeleri için değerlendirene (yapıcı bir dille) bir tavsiyen olsa ne olurdu?", "Peer-learning ruhuyla bir iyilik yap.", "Gelişim Tavsiyesi"),
    ]
}

# --- Yardımcı Fonksiyonlar ---

def print_slow(text):
    """Yazıyı yavaşça yazdırır."""
    for char in text:
        print(char, end='', flush=True)
        time.sleep(0.01) # Hızı ayarlayabilirsiniz
    print()

def wrap_text(text, width=80):
    """Metni belirtilen genişliğe göre sarar."""
    return '\n'.join(textwrap.wrap(text, width))

# --- Ana Script ---

def main():
    print_slow("🚀 42 İstanbul Değerlendirme Asistanına Hoş Geldin! 🚀")
    print_slow("Amacımız, değerlendirme sürecini daha yapılandırılmış ve (belki) biraz daha eğlenceli hale getirmek.")
    print("-" * 60)

    questions_structured = None # Seçilen soru setini tutacak değişken
    role = ""
    role_description = ""

    while True:
        print("\nHangi roldesin?")
        print("1. Değerlendiren (Evaluator) - Başkasının projesini değerlendiriyorum.")
        print("2. Değerlendirilen (Self-Reflection) - Kendi projem üzerine düşünüyorum / hazırlanıyorum.")
        print("3. Değerlendirilen (Evaluator Feedback) - Beni değerlendiren kişi hakkında geri bildirim veriyorum.")
        print("4. Çıkış")
        choice = input("Seçimin (1, 2, 3 veya 4): ")

        if choice == '1':
            questions_structured = evaluator_questions_structured
            role = "Değerlendiren (Evaluator)"
            role_description = "Harika! 'Değerlendiren' modundasın. Projeyi dikkatlice incele ve yapıcı olmaya çalış."
            break
        elif choice == '2':
            questions_structured = evaluated_self_reflection_questions_structured
            role = "Değerlendirilen (Kendi Kendine Değerlendirme)"
            role_description = "Süper! 'Kendi Kendine Değerlendirme' modundasın. Bu, öğrenme sürecini anlamak için harika bir fırsat."
            break
        elif choice == '3':
            questions_structured = evaluated_reviewing_evaluator_questions_structured
            role = "Değerlendirilen (Değerlendiren Geri Bildirimi)"
            role_description = "Çok iyi! 'Değerlendiren Geri Bildirimi' modundasın. Bu geri bildirimler peer-learning sistemini geliştirmek için çok önemli. Lütfen dürüst ve yapıcı ol."
            break
        elif choice == '4':
            print_slow("\nAnlaşıldı, başka sefere görüşmek üzere. İyi kodlamalar! 👋")
            sys.exit()
        else:
            print("\n❌ Geçersiz seçim. Lütfen 1, 2, 3 veya 4 girin.")

    print(f"\n{role_description}")
    print("Şimdi sana bazı sorular soracağım.")
    print("Cevaplarını düşünerek yaz. Sonunda hepsini bir arada görebileceksin.")
    print("-" * 60)

    # Cevapları saklamak için yapılandırılmış bir sözlük
    evaluation_results = {}
    question_counter = 0
    total_questions = sum(len(q_list) for q_list in questions_structured.values())

    # Kategorilere ve sorulara göre döngü
    for category, questions_in_category in questions_structured.items():
        print(f"\n--- KATEGORİ: {category} ---")
        evaluation_results[category] = [] # Her kategori için boş liste başlat
        for question, hint, keyword in questions_in_category:
            question_counter += 1
            print(f"\n--- Soru {question_counter}/{total_questions} ({keyword}) ---")
            print(wrap_text(f"❓ {question}"))
            if hint:
                print(wrap_text(f"   ({hint})"))

            answer = input("\n💬 Cevabın: ")
            # Sonuçları kategoriye göre sakla (anahtar kelime ve cevap olarak)
            evaluation_results[category].append((keyword, answer))
            print("-" * 40) # Sorular arası ayırıcı


    print("\n✨🎉 İşte Formatlanmış Değerlendirme Özetin! 🎉✨")
    print("Aşağıdaki metni kopyalayıp Intra'daki değerlendirme yorumuna veya ilgili yere yapıştırabilirsin.")
    print("(Markdown formatındadır, **Kalın** anahtar kelimeler içerir.)")
    if role == "Değerlendirilen (Değerlendiren Geri Bildirimi)":
         print("(Not: Değerlendiren Geri Bildirimi veriyorsan, bu özeti Intra'daki ana değerlendirme yorumuna değil, varsa ayrı bir geri bildirim mekanizmasına veya kişisel notlarına eklemen daha uygun olabilir.)")
    print("=" * 60)

    # Formatlanmış çıktıyı oluştur
    output_lines = [f"# Değerlendirme Özeti ({role})\n"]
    for category, results in evaluation_results.items():
        output_lines.append(f"## {category}") # Kategori başlığı (Markdown H2)
        for keyword, answer in results:
            # Cevap boşsa veya sadece boşluk içeriyorsa "Belirtilmedi" yaz
            formatted_answer = answer.strip() if answer.strip() else "*Belirtilmedi*"
            # Markdown: * **AnahtarKelime:** Cevap
            output_lines.append(f"  * **{keyword}:** {formatted_answer}")
        output_lines.append("") # Kategoriler arası boşluk

    # Tüm çıktıyı yazdır
    for line in output_lines:
        print(line)

    print("=" * 60)
    print_slow("\nUmarım işine yaramıştır! Başarılar! 💪")

if __name__ == "__main__":
    main()