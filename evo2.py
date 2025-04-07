import textwrap
import sys
import time

# --- Evaluation Soruları ---

# Değerlendiren (Evaluator) için Sorular
evaluator_questions = [
    # --- Genel ve Fonksiyonellik ---
    ("Projenin adı ve değerlendirilen öğrencinin login'i nedir?", "Başlangıç için ısınma turları."),
    ("Proje konusundaki (subject) tüm zorunlu (mandatory) kısımlar tamamlanmış mı? Eksikler var mı?", "Subject'i kutsal metin gibi inceledin mi?"),
    ("Program derleniyor mu? 'Makefile' sihirli değneğini doğru sallamış mı?", "'Warning'ler sadece birer öneri midir, yoksa dikkate alınmış mı?"),
    ("Program çalışıyor mu? Beklenen temel işlevleri yerine getiriyor mu?", "Yoksa sadece terminalde güzel bir isim mi gösteriyor?"),
    ("Hiç 'segmentation fault' (ya da başka bir crash) ile karşılaştın mı? Varsa, hangi durumlarda?", "Programın arada bir kestirme ihtiyacı oluyor mu?"),
    ("Kenar durumlar (edge cases) ve hatalı girdiler (error handling) nasıl ele alınmış? Program nazikçe mi uyarıyor, yoksa panik mi yapıyor?", "Kullanıcı 'abc' yazdığında programın ruh sağlığı bozuluyor mu?"),

    # --- Kod Kalitesi ve Anlaşılırlık ---
    ("Kod okunabilir mi? Değişken ve fonksiyon isimleri 'a', 'b', 'temp' üçgeninden çıkabilmiş mi?", "Kod şiir gibi mi akıyor, yoksa çözülmesi gereken bir bulmaca mı?"),
    ("Norminette (veya proje özelindeki stil rehberi) kurallarına ne kadar uyulmuş? Göz kanatan ihlaller var mı?", "Norminette'in ruhu şad olmuş mu?"),
    ("Kodda gereksiz karmaşıklık veya tekrar eden bloklar var mı? Daha basit/zarif çözümler olabilir miydi?", "'Kopyala-yapıştır' sanatının incelikleri mi sergilenmiş?"),
    ("Yorum satırları kullanılmış mı? Kullanıldıysa, kodu açıklıyor mu yoksa 'bu bir fonksiyondur' gibi bariz şeyleri mi söylüyor?", "Yorumlar yol gösterici mi, kafa karıştırıcı mı?"),

    # --- Anlama ve Problem Çözme ---
    ("Değerlendirilen kişi yazdığı kodu açıklayabiliyor mu? Mantığını ve neden o yolu seçtiğini anlatabiliyor mu?", "Kodu uzaylılar mı yazmış, yoksa kontrol kendisinde mi?"),
    ("Karşılaştığı zorlukları ve bunları nasıl aştığını anlatabiliyor mu? Hangi kaynakları kullanmış?", "Google ve Stack Overflow'a minnettar mı, yoksa kendi başına mı dağları devirmiş?"),
    ("Alternatif çözüm yolları düşünmüş mü? Neden mevcut çözümü tercih ettiğini açıklayabiliyor mu?", "Tek bir yola saplanıp kalmış mı, yoksa ufku geniş mi?"),

    # --- Akademik Dürüstlük ve İşbirliği ---
    ("Kodun özgün olduğuna dair bir şüphen var mı? İntihal (cheating) belirtisi gözlemledin mi?", "Kodun DNA'sı başkasına mı ait gibi duruyor? (Şüphe varsa, Bocal'a bildirmeyi unutma!)"),
    ("Değerlendirme süreci nasıl geçti? İletişim açık ve yapıcı mıydı?", "Karşılıklı 'Aydınlanma Anları' yaşandı mı?"),

    # --- Sonuç ---
    ("Projenin en güçlü yanı neydi?", "Nerede 'işte bu!' dedin?"),
    ("Geliştirilebilecek en önemli alan nedir? Bir sonraki projede neye dikkat etmesini önerirsin?", "Yapıcı eleştiri kaslarımızı çalıştıralım."),
    ("Genel bir puan (0-100 arası gibi düşünebilirsin, ama sadece referans amaçlı) veya his versen ne olurdu?", "İçindeki ses ne diyor?"),
]

# Değerlendirilen (Evaluated - Kendi Kendine) için Sorular
evaluated_self_reflection_questions = [
    # --- Proje ve Süreç ---
    ("Projenin adı ve kendi login'in nedir?", "Hafıza tazeleme."),
    ("Bu projede öğrenmeyi hedeflediğin ana konu(lar) neydi ve ne kadarını başardığını düşünüyorsun?", "Beklentiler ve gerçekler masaya yatırılsın."),
    ("Projeyi yaparken en çok zorlandığın kısım hangisiydi?", "Hangi noktada 'ben ne yapıyorum?' diye sordun?"),
    ("Bu zorlukların üstesinden nasıl geldin? Hangi kaynaklar (internet, arkadaşlar, manual'lar) sana yol gösterdi?", "'Aha!' anını ne tetikledi?"),
    ("Proje üzerinde ne kadar zaman harcadığını tahmin ediyorsun?", "Zaman göreceli midir, yoksa sadece Intra logları mı kesindir?"),

    # --- Kod ve Çözüm ---
    ("Yazdığın koddan memnun musun? 'İşte bu benim eserim!' diyebiliyor musun?", "Gurur mu duyuyorsun, yoksa 'geçmiş olsun' mu diyorsun?"),
    ("Şimdi tekrar başlasan, neyi farklı yapardın?", "Gelecekteki kendine bir not bırak."),
    ("Kodunun en güçlü ve en zayıf yönleri neler sence?", "Kendine karşı acımasızca dürüst olma vakti."),
    ("Projedeki tüm kod satırlarını gerçekten anladığını düşünüyor musun? Rastgele bir satırı açıklaman istense yapabilir misin?", "Kopyala-yapıştır'ın karanlık tarafına geçtin mi?"),
    ("Norminette veya stil kurallarına uymak ne kadar zordu/kolaydı?", "Norminette ile aran nasıl?"),

    # --- Öğrenme ve Gelişim ---
    ("Bu projeden öğrendiğin en önemli 1-2 teknik veya kavram nedir?", "Beynindeki hangi yeni nöron bağlantıları aktive oldu?"),
    ("'Öğrenmeyi öğrenme' konusunda bu proje sana ne kattı?", "Balık tutmayı mı öğrendin, yoksa sadece balık mı yedin?"),
    ("Bilgiye ulaşma ve doğrulama (verification) sürecinde nelere dikkat ettin?", "İnternetteki her bilgiye hemen inandın mı, yoksa şüpheci mi yaklaştın?"),

    # --- Değerlendirmeye Hazırlık ---
    ("Değerlendirmede hangi soruların gelmesini bekliyorsun?", "Kristal kürene baktın mı?"),
    ("Kodunun hangi kısımlarını açıklamaktan çekiniyorsun (varsa)?", "Saklanan iskeletler var mı?"),
    ("Değerlendirenin hangi potansiyel hataları bulmasından endişe ediyorsun?", "Umarım görmez dediğin yerler..."),

    # --- Sonuç ---
    ("Bu projeyi bitirmiş olmak sana ne hissettiriyor?", "Rahatlama mı, zafer mi, yoksa 'bir sonrakine geçelim' mi?"),
    ("Bir sonraki projeye başlarken bu deneyimden hangi dersi yanında götüreceksin?", "Geleceğe yatırım."),
]

# Değerlendirilenin Değerlendireni Değerlendirmesi için Sorular
evaluated_reviewing_evaluator_questions = [
    # --- Hazırlık ve Anlayış ---
    ("Değerlendirenin adı/login'i nedir?", "Kime geri bildirim veriyoruz?"),
    ("Değerlendiren, projeyi (subject) önceden incelemiş gibi miydi, yoksa ilk defa mı görüyordu?", "Hazırlıklı bir savaşçı mıydı, yoksa konuya Fransız mıydı?"),
    ("Kodunu ve çözümünü genel olarak anladığını düşünüyor musun? Mantığını takip edebildi mi?", "Aynı dili konuşabildiniz mi?"),

    # --- Süreç ve Yaklaşım ---
    ("Değerlendirme sırasında konuya (subject) sadık kalındı mı? Yoksa kişisel tercihler veya konu dışı beklentiler mi ön plana çıktı?", "Kutsal subject'in sınırları içinde kalındı mı?"),
    ("Sorulan sorular adil, ilgili ve düşünmeye teşvik edici miydi?", "Sorular ufuk açıcı mıydı, yoksa sadece 'çalışıyor mu?' seviyesinde miydi?"),
    ("Projenin farklı yönlerini (Makefile, Norminette, hatalar, kenar durumlar vb.) yeterince ve dengeli bir şekilde inceledi mi?", "Sadece sevdiği kısımlara mı baktı?"),
    ("Zaman yönetimi nasıldı? Değerlendirme süresi verimli kullanıldı mı?", "Süre yetti mi, yoksa aceleye mi geldi?"),

    # --- İletişim ve Tutum ---
    ("Değerlendirenin soruları ve geri bildirimleri net ve anlaşılır mıydı?", "Kristal küreye ihtiyaç duydun mu, yoksa meramını anlatabildi mi?"),
    ("İletişim tarzı saygılı, sabırlı ve yapıcı mıydı?", "Ego savaşları mı yaşandı, yoksa öğrenme odaklı bir diyalog muydu?"),
    ("Açıklamalarını ve cevaplarını dikkatle dinlediğini hissettin mi?", "Sözünü kesip durdu mu, yoksa sana alan tanıdı mı?"),
    ("Geri bildirim verirken hem olumlu yönleri hem de geliştirilebilecek alanları belirtti mi?", "Sadece hataları mı saydı, yoksa iyi yapılanları da takdir etti mi?"),

    # --- Genel Deneyim ve Sonuç ---
    ("Bu değerlendirme süreci genel olarak sana ne kattı? Yeni bir şey öğrendin mi veya farklı bir bakış açısı kazandın mı?", "Sadece bir 'geçti/kaldı' anı mıydı, yoksa öğretici miydi?"),
    ("Değerlendirme sonucunda verilen puan veya geri bildirim sence adil miydi? Neden?", "İçine sindi mi?"),
    ("Değerlendirenin yaptığı en iyi şey/en olumlu yaklaşım neydi?", "Neyi özellikle takdir ettin?"),
    ("Gelecekteki değerlendirmeleri için değerlendirene (yapıcı bir dille) bir tavsiyen olsa ne olurdu?", "Peer-learning ruhuyla bir iyilik yap."),
]


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

    while True:
        print("\nHangi roldesin?")
        print("1. Değerlendiren (Evaluator) - Başkasının projesini değerlendiriyorum.")
        print("2. Değerlendirilen (Self-Reflection) - Kendi projem üzerine düşünüyorum / hazırlanıyorum.")
        print("3. Değerlendirilen (Evaluator Feedback) - Beni değerlendiren kişi hakkında geri bildirim veriyorum.")
        print("4. Çıkış")
        choice = input("Seçimin (1, 2, 3 veya 4): ")

        if choice == '1':
            questions = evaluator_questions
            role = "Değerlendiren (Evaluator)"
            role_description = "Harika! 'Değerlendiren' modundasın. Projeyi dikkatlice incele ve yapıcı olmaya çalış."
            break
        elif choice == '2':
            questions = evaluated_self_reflection_questions
            role = "Değerlendirilen (Kendi Kendine Değerlendirme)"
            role_description = "Süper! 'Kendi Kendine Değerlendirme' modundasın. Bu, öğrenme sürecini anlamak için harika bir fırsat."
            break
        elif choice == '3':
            questions = evaluated_reviewing_evaluator_questions
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

    evaluation_summary = [f"--- DEĞERLENDİRME ÖZETİ ({role}) ---"] # Başlık ekleyelim
    total_questions = len(questions)

    for i, (question, hint) in enumerate(questions):
        print(f"\n--- Soru {i+1}/{total_questions} ---")
        print(wrap_text(f"❓ {question}"))
        if hint:
            print(wrap_text(f"   ({hint})")) # Küçük ipucu

        answer = input("\n💬 Cevabın: ")
        evaluation_summary.append(f"❓ Soru: {question}\n💬 Cevap: {answer}\n" + "-"*40)
        print("-" * 60)


    print("\n✨🎉 İşte Değerlendirme Özetin! 🎉✨")
    print("Aşağıdaki metni kopyalayıp Intra'daki değerlendirme yorumuna veya ilgili yere yapıştırabilirsin.")
    print("(Eğer Değerlendiren Geri Bildirimi veriyorsan, bu özeti not alıp belki daha sonra anonim bir geri bildirim mekanizması varsa orada kullanabilirsin veya sadece kendi düşüncelerini netleştirmek için kullan.)")
    print("=" * 60)
    for entry in evaluation_summary:
        print(entry)
    print("=" * 60)
    print_slow("\nUmarım işine yaramıştır! Başarılar! 💪")

if __name__ == "__main__":
    main()