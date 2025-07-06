# Ürün İsmi


**PostuRek** – Gerçek Zamanlı Postür Analiz ve Duruş Takip Asistanı
  

---
| Fotoğraf         | İsim                     | Görevler             | LinkedIn Profili                          |  Durum |
| ---------------- | ------                   | -------------------- | ------------------------------------------| ----- |
| ![Hasan](link1)  | Hasan Barış Sunar        | Scrum Master         | https://www.linkedin.com/in/hasan-bar%C4%B1%C5%9F-sunar-48b26a174/ | Aktif |
| ![Ayşe](link2)   | Kayra Semercioğlu        | Product Owner        | [LinkedIn](https://linkedin.com/in/ayse)  | Aktif |
| ![Mehmet](link3) | Hatice Aygül             | Developer            | [LinkedIn](https://linkedin.com/in/mehmet)| Aktif |
| ![Elif](link4)   | Eda Mete                 | Developer            | https://www.linkedin.com/in/edamete       | Aktif |
| ![Can](link5)    | Yusuf Yaşar              | Developer            | [LinkedIn](https://linkedin.com/in/can)   | Pasif |
---
 # Proje Açıklaması:

PostuRek, kullanıcıların duruşlarını gerçek zamanlı olarak analiz eden ve yanlış pozisyonlarda anında uyarı veren yenilikçi bir mobil sağlık uygulamasıdır. Uygulama, MediaPipe teknolojisi sayesinde vücuttaki iskelet noktalarını hassas şekilde tespit eder ve boyun, omuz, sırt ile bel açılarını temel geometrik yöntemlerle değerlendirir. Özellikle uzun süre masa başında çalışan bireylerde sıkça görülen duruş bozukluklarının önüne geçmeyi ve kullanıcıda ergonomik farkındalık oluşturmayı hedefler. Böylece PostuRek, daha sağlıklı bir yaşam ve iş ortamı için etkin bir destek sağlar.


---

 # Kullanılan Teknolojiler:

- **Yazılım Dili:** Python (AI Modülü), JavaScript (React Native)

- **Geliştirme Ortamı:** Visual Studio Code

- **Mobil Geliştirme:** React Native (Android ve iOS)

- **Yapay Zeka Çekirdeği:** MediaPipe Pose

- **Backend & Veritabanı:** Firebase (veri saklama, kullanıcı giriş/çıkış, analiz geçmişi)

- **Model Tipi:** Kurala dayalı duruş açısı sınıflandırma (geometrik açı hesabı)



---

# Hedef Kitle

- **Masa başında uzun süre çalışan beyaz yakalılar:**  
  Ofis ortamında bilgisayar başında çalışan bireylerde zamanla duruş bozuklukları gelişebilir. Uygulama, bu kişilere ergonomik farkındalık kazandırarak daha sağlıklı bir çalışma düzeni oluşturmayı hedefler.

- **Öğrenciler:**  
  Özellikle çevrim içi eğitim sürecinde uzun süre oturan öğrencilerde yaygın görülen kambur duruş ve baş öne eğik pozisyon gibi postür sorunlarının önüne geçmek için tasarlanmıştır.

- **Fizyoterapi desteği alan bireyler:**  
  Rehabilitasyon sürecinde olan veya sırt, boyun ve bel ağrısı yaşayan bireyler, PostuRek aracılığıyla evde kendi duruşlarını izleyip düzeltici geri bildirimler alabilir.

- **Spor yapanlar / Fitness kullanıcıları (Gym):**  
  Egzersiz sırasında doğru postür hayati önem taşır. Uygulama, spor esnasında yapılan hareketlerde omurga ve duruş pozisyonlarının korunmasına yardımcı olabilir. Özellikle ağırlık çalışmaları sırasında omuz ve bel hizasının korunması için anlık uyarılar sunabilir.

- **Genel kullanıcılar:**  
  Günlük yaşamda daha sağlıklı ve estetik bir duruşa sahip olmak isteyen herkes, PostuRek’i bir rehber olarak kullanabilir.



---

# Ürün Özellikleri

- **Kameradan gerçek zamanlı duruş tespiti:**  
  Cihaz kamerası aracılığıyla kullanıcının vücut duruşu analiz edilir. MediaPipe teknolojisi ile omuz, boyun ve bel hizası gibi kritik noktalar gerçek zamanlı takip edilir.

- **Kötü postür algılandığında anlık uyarı bildirimi:**  
  Tanımlanan açı limitleri dışına çıkıldığında kullanıcıya görsel veya sesli uyarılar gönderilir. Bu sayede kullanıcı farkında olmadan yaptığı duruş hatalarını anında düzeltebilir.

- **Kullanıcıya günlük rapor sunumu:**  
  Gün içinde ne kadar süre doğru ya da yanlış postürde durulduğu gibi bilgiler analiz edilerek kullanıcıya sade bir rapor halinde sunulur.

- **Firebase ile bulut tabanlı kullanıcı geçmişi saklama:**  
  Kullanıcıların duruş analiz geçmişi, Firebase veritabanı üzerinden güvenli bir şekilde saklanır. Bu veriler daha sonra istatistiksel takip ve ilerleme değerlendirmesi için kullanılabilir.

- **Mobil arayüz ile kolay kullanım:**  
  React Native ile geliştirilen kullanıcı arayüzü; hem Android hem de iOS cihazlarda sorunsuz çalışacak şekilde tasarlanmıştır. Temiz ve sezgisel ekranlar sayesinde kullanım kolaylığı sağlar.

- **Kullanıcı dostu, minimal tasarım:**  
  Gereksiz karmaşadan uzak, sade ve modern bir arayüz sunularak uygulamanın hem estetik hem de fonksiyonel olması hedeflenmiştir.



---

**Product Backlog URL**

Product backlog’u Trello üzerinde yönetiyoruz.  
Trello panosuna erişim için [URL buraya eklenecek].

---

<details>
  <summary><strong> SPRİNT 1 </strong></summary>

###  Sprint 1 - Planlama ve Teknoloji Kararları

####  Sprint Notları  
- Proje kapsamında kullanılacak ana teknolojiler belirlendi:  
 - Yapay Zeka için MediaPipe Pose  
 - Mobil uygulama geliştirme için React Native  
- Backend ve veri saklama için Firebase  
- Proje hedefleri ve öncelikli modüller üzerinde ekip içinde fikir birliğine varıldı.  
- Uygulamanın temel işlevleri, kullanıcı ihtiyaçları ve teknik gereksinimler detaylandırıldı.  
- Hangi modüllere öncelik verileceği ve sprint sonu hedefleri netleştirildi.

---

####  Sprint Puanlaması (Toplam 200 Puan)

Proje toplamda 200 puan üzerinden değerlendirilecektir.

###  Sprint İçerisinde Tamamlanması Gereken 50 Puan

Sprint 1, projenin planlama, temel altyapı ve teknoloji seçim aşamalarını kapsar.  
Bu sprintin başarıyla tamamlanması için toplam 50 puan alınması hedeflenmiştir.

####  Planlanan Ana Görevler ve Puanlama 
-  Teknoloji araştırması ve seçimi (15 puan)  
-  Proje mimarisi ve veri akışının tasarlanması (15 puan)  
-  Kullanıcı ihtiyaçları ve önceliklerin belirlenmesi (10 puan)  
-  UI/UX için ilk fikirlerin toplanması ve eskizler (10 puan)  

---

####  Daily Scrum  
- Günlük toplantılar **WhatsApp** ve **Google Meet** üzerinden gerçekleştirilmiştir.  
- Toplantı notları ve tartışmalar **Google Drive** üzerinde paylaşılmıştır.
 <details>
<summary><strong> Konuşma ve Toplantı Kayıtları</strong></summary>

![Toplantı 1](images/resim1.jpg)
![Toplantı 2](images/resim2.jpg) 
![Toplantı 1](images/resim3.jpg)
![Toplantı 2](images/resim4.jpg)
![Toplantı 1](images/resim5.jpg)
</details>

---

####  Sprint Review (Planlama Sonrası)  
- Ana teknolojiler ve araçlar seçildi.  
- Proje hedefleri ekipçe netleştirildi ve görev dağılımı yapıldı.  
- İlk UI/UX fikirleri toplandı ve ön taslaklar oluşturuldu.  
- Veri modeli ve temel mimari için ilk yol haritası çizildi.

---

####  Sprint Retrospective  
- Planlama aşaması verimli geçti, ekip üyeleri teknoloji seçiminde hem fikir oldu.  
- Bazı modüller için daha detaylı araştırma gerekliliği ortaya çıktı.  
- İletişim ve koordinasyonun artırılması konusunda fikirler oluştu.  
- Bir sonraki sprintte kodlama ve prototip geliştirme aşamasına geçilecek.

---


</details>




