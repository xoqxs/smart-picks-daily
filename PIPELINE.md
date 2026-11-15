# Smart Picks Daily – otomatik iş akışı

Sahip: Kadir Pars. Amazon US ortaklık (Associates) işi: ABD kitlesine İngilizce içerik.
Bu dosya zamanlanmış görevlerin tek kaynağıdır. Çelişki varsa en alttaki tarihli notlar geçerlidir.

## Hesaplar ve kimlikler
- Amazon Associates takip kodu: `desksetuppi07-20`. Link biçimi: `https://www.amazon.com/dp/<ASIN>?tag=desksetuppi07-20` (arama linki ASLA).
- Amazon sitesine girme (yapay zekâ ajanlarını engelliyor). Fiyat yazma; yalnızca resmi basın bülteninde geçen "launch list price" yazılabilir ve öyle etiketlenir.
- Blog: https://smartpicksdaily-reviews.blogspot.com (Blogger blog ID `6804187435880784901`, hesap akadirpars). Video Picks sayfası: `/p/video-picks.html` (sayfa ID `7010338707456657294`), kaynağı bu depoda `site/video-picks.html`.
- YouTube: "Smart Picks Daily" (@SmartPicksDailyShorts), kanal kimliği `UCxv_aGQCfArHi1rrwjBOPPw`. Aynı Google hesabında Döviz Radar (`UCETn8pkFCvCHQKpBAKnGXJw`), Belgesellerim, Baby Collective, PanEdit vb. var: YALNIZCA bu kanala yükle. İş bitince (hata/DUR dahil) Döviz Radar'a geri geç.
- Pinterest: @smartpicksdailyfinds (Business, site doğrulanmış). Panolar: Home & Kitchen Finds, Beauty & Skincare Picks, Tech Gadgets & Accessories.
- Depo: github.com/xoqxs/smart-picks-daily (public). Videolar `v/`, pin görselleri `pins/`, site HTML'leri `site/`, işler `jobs/<slug>/`. Raw URL: `https://raw.githubusercontent.com/xoqxs/smart-picks-daily/<commit>/<yol>` (önbellek sorunu olmasın diye commit SHA'sı kullan).
- Tarayıcı: kullanıcının bilgisayarındaki uygulama içi tarayıcı (mcp__remote-devices__Claude_Browser__*), kendi sekmen. Şifre yazma. Dar panelde düğmeler gizlenir: resize_window 1280x900 (Blogger editörü için 1400x900) kullan, iş bitince preset "desktop".

## Kurallar (kesin)
1. Ürün ASIN'i iki bağımsız kaynakta aynı ürün adıyla doğrulanmadan kullanılmaz (ör. arama sonucunda görünen amazon.com/dp/ASIN sayfası + camelcamelcamel/fiyat takip sitesi + marka sitesi/basın bülteni). Tutmazsa ürünü atla.
2. Görsel: yalnızca markanın resmi basın/medya kiti veya basın bülteni görselleri; her kartta "Image: <Marka>" atfı. Amazon görseli, rakip inceleme sitesi görseli, insan yüzü/ünlü YOK. Görsel bulunamazsa ürünü atla.
3. Özellikler yalnızca resmi kaynaktan; uydurma test/deneyim yok ("we tested" deme). Sağlık iddiası, takviye, ilaç, tıbbi cihaz, bebek güvenliği ürünü YOK. Market/grocery ve %1 komisyonlu kategorilerden kaçın.
4. Her içerikte açıklama: "As an Amazon Associate I earn from qualifying purchases." Videoda "#ad" köşede yazar (build.py otomatik).
5. Kopya içerik yok: son 10 videodan farklı ürün, farklı açılış cümlesi kalıbı. YouTube "özgün olmayan içerik" kuralına dikkat: her video gerçek bilgi (özellik, ipucu, kimin için uygun/değil) içermeli.
6. Shorts açıklamasındaki ve yorumlarındaki linkler tıklanamaz. Videonun son sahnesi her zaman `cta`: "Pick #N – link on our channel / Video Picks". Kanal profil linki Video Picks sayfasına gider.

## Kategori dönüşümü (ilk 6–8 hafta)
Sırayla: Beauty (cilt bakımı, saç aletleri; lüks güzellik markaları öncelikli) → Home & Kitchen (pratik mutfak/ev ürünleri) → Tech (şarj, kulaklık, masa aksesuarı). picks.json'daki son kaydın kategorisinden sonrakini seç. Ürün: Amazon'da çok satan, markanın basın kiti olan, 15–150 $ bandında.

## Günlük Short (her gün)
0. HAZIRLIK: `git clone https://github.com/xoqxs/smart-picks-daily /home/claude/smart-picks-daily` (varsa `git pull`). `pip install --break-system-packages -q kokoro-onnx soundfile pillow`. Model yoksa: `mkdir -p /tmp/kokoro && cd /tmp/kokoro && curl -sLO https://github.com/thewh1teagle/kokoro-onnx/releases/download/model-files-v1.0/kokoro-v1.0.onnx && curl -sLO https://github.com/thewh1teagle/kokoro-onnx/releases/download/model-files-v1.0/voices-v1.0.bin`. picks.json'da bugünün tarihli kaydı varsa DUR (mesajsız).
1. ÜRÜN: kategoriye göre aday bul (WebSearch). Kural 1–3'ü uygula. Basın görselini `jobs/<YYYY-MM-DD>-<kısa-ad>/img/` altına indir: önce `curl -sL -o` dene (kabuğun ağ izin listesi çoğu siteyi engeller). Olmazsa tarayıcıda görselin KENDİ URL'sine navigate et (aynı köken olsun) → javascript_tool ile `fetch(location.href)` → base64'e çevir → 40 KB'lık parçalar halinde döndür (büyük çıktılar /tmp/claude-tool-results altına dosya olarak düşer) → parçaları python ile birleştirip decode et; boyutu/sha'yı doğrula. Elle base64 kopyalama YAPMA (bozuluyor). Görsel en az 1200 px genişlikte olmalı; indirilemiyorsa başka ürün seç.
2. METİN: 5 sahne, toplam 25–35 sn. 1) merak uyandıran açılış (rakam/şaşırtıcı fayda), 2) ürün adı + ana özellik (badge), 3) kimin için / ne ile çalışır (chips), 4) ipucu veya dikkat edilecek nokta (tip kutuları ya da card), 5) cta: "It's pick number N. Find the link on our channel, under Video Picks." Sayıları seslendirme için yazıyla yaz (sixty-five). `video.json` biçimi tools/build.py başındaki açıklamada; örnek: jobs/2026-11-15-ugreen-nexode-air-65w. `name` alanını da doldur.
3. KONTROL: `python3 tools/build.py jobs/<slug> --stills` → 5 kareyi Read ile aç: görselde basın kitinin yazısı/kesik metin olmasın, badge doğru ürünü göstersin, yazı taşmasın. Düzelt, tekrar kontrol.
4. ÜRET: `python3 tools/build.py jobs/<slug>` → `v/<slug>.mp4`. Süre 20–40 sn olmalı.
5. PIN GÖRSELLERİ (3 adet): video.json'a `pin` bloğu ve 2 öğeli `pin_variants` ekle (biçim tools/pin.py başında; varyantlardan biri `"style":"light"`, biri ipucu/dikkat başlıklı; farklı kırpım ve buton yazısı) → `python3 tools/pin.py jobs/<slug>` , `... 1` , `... 2` → `pins/<slug>.jpg`, `-v1.jpg`, `-v2.jpg`. Üçünü de Read ile kontrol et (basın kiti yazısı görünmesin, rozet doğru ürünü göstersin). v1 ve v2'yi pins.json kuyruğuna ekle (posted:null; v1 link = blog yazısı, v2 link = `.../p/video-picks.html#pick-N`; her birine ≤450 karakterlik FARKLI açıklama + "#affiliate As an Amazon Associate I earn from qualifying purchases.").
6. BLOG YAZISI: `site/post-<slug>.html` (örnek: site/post-2026-11-15-ugreen.html yapısı: giriş paragrafı, .dsp-disclosure, .dsp-hero görsel + atıf, .dsp-product kartı (özellikler, artı/eksi, Amazon butonu rel="nofollow sponsored"), 2–3 bilgi başlığı, .dsp-check kontrol listesi). Görsel URL'si = raw GitHub görseli.
7. VIDEO PICKS: `site/video-picks.html` içinde en üste yeni `.dsp-product` bloğu (id="pick-N", rozet "PICK #N · KATEGORİ", Amazon butonu, yazı + Short linkleri).
8. COMMIT + PUSH (git -c user.name="Smart Picks Daily" -c user.email="noreply@anthropic.com"; mesaj sonuna oturumun atıf satırları). SHA'yı not et; raw URL'leri curl ile 200 doğrula.
9. BLOGGER: (a) Yeni yayın: blogger.com/blog/posts/6804187435880784901 → "Yeni Yayın" (görünmüyorsa 1400x900) → HTML görünümü → `document.querySelector('.CodeMirror').CodeMirror.setValue(await fetch(RAW).then(r=>r.text()))` → başlığa GERÇEK tıkla + yaz → sağ panel Etiketler: kategori adı (Electronics / Beauty / Home & Kitchen) + "Buying Guides" (etiket kutusu kaydetmiyorsa yayından sonra Yayınlar listesi → YÖNET → kutucuk → etiket simgesi ile ekle) → Yayınla → ONAYLA. (b) Video Picks: blogger.com/blog/page/edit/6804187435880784901/7010338707456657294 → CodeMirror'a raw `site/video-picks.html` → Güncelle (ref ile; görünmüyorsa 1400x900). Canlıda ?nc= ile doğrula.
10. YOUTUBE: kanala geç (studio.youtube.com → sağ üst avatar → Hesap değiştir → "Smart Picks Daily" / @SmartPicksDailyShorts; adres `/channel/UCxv_aGQCfArHi1rrwjBOPPw` olmalı, değilse DUR). `.../videos/upload?d=ud` → javascript_tool: `const b=await (await fetch(RAW_MP4)).blob(); const f=new File([b],'<slug>.mp4',{type:'video/mp4'}); const inp=document.querySelector('ytcp-uploads-dialog input[type=file]'); const dt=new DataTransfer(); dt.items.add(f); inp.files=dt.files; inp.dispatchEvent(new Event('change',{bubbles:true}));` → başlık/açıklama kutuları `ytcp-uploads-dialog #textbox[contenteditable=true]` (click, focus, execCommand selectAll + insertText; textContent ile doğrula). Başlık ≤70 karakter + " #shorts". Açıklama ilk satırı: `🔗 Amazon link: Pick #N → tap our channel name → "Video Picks"`; sonra 2 cümle özet, düz yazı Amazon linki, blog yazısı linki, açıklama cümlesi, "Product images: <Marka> press kit.", 3–5 hashtag. Radyo: VIDEO_MADE_FOR_KIDS_NOT_MFK, "Daha fazla göster" → ücretli tanıtım Evet (VIDEO_PAID_PRODUCT_PLACEMENT_NOTIFY), VIDEO_HAS_ALTERED_CONTENT_NO, etiketler 6–10 (chip bar input'a virgüllü yaz + Enter). Uzun await'li script yazma (45 sn sınırı); adımları ayrı çağrılara böl. Görünürlük: önce kontrolleri bekle ("Sorun bulunmadı"); telif/kısıtlama varsa Gizli bırak ve bildir. Sonra PUBLIC → done-button. Studio'da video düzenleme sayfasında "Herkese açık" doğrula. O haftanın uzun videosu varsa "İlgili video" olarak onu seç.
11. PINTEREST: `https://www.pinterest.com/pin/create/button/?url=<blog yazısı>&media=<raw pin jpg>&description=<≤450 karakter, sonunda "#affiliate As an Amazon Associate I earn from qualifying purchases.">` aç (1280x900) → görselin üstüne hover → kategoriye uygun pano satırına tıkla → "panosuna kaydedildi" doğrula. (pin-creation-tool bu tarayıcıda boş açılıyor, kullanma.)
12. KAYIT: ana pini pins.json'a posted:<bugün> ve pin_url ile yaz; picks.json'a yeni kayıt (pick, date, category, name, asin, asin_sources, amazon, post, short, pin, job, in_weekly:false) → commit + push.
13. GERİ DÖN: YouTube'da Döviz Radar'a geç; viewport'ları "desktop" yap.
14. RAPOR (SendUserMessage, ≤4 satır, Türkçe): "🛒 Pick #N: <ürün> – <Short linki>" / blog + pin linkleri / ASIN kaynakları / "Döviz Radar kanalına geri dönüldü ✓".

## Ek pinler (günde 2 kez × 2 pin; ana pinle birlikte günde 5 pin)
- Hedef: günde toplam 5 pin, gün içine yayılmış. Aynı görsel iki kez pinlenmez.
- pins.json'da posted:null olan en eski 2 kaydı al. Kuyrukta 2'den az varsa eksik kadarını ESKİ bir pick için yeni varyantla üret: picks.json'dan son 30 günde en az pinlenmiş pick'i seç, onun video.json'una yeni bir `pin_variants` öğesi ekle (yeni başlık açısı: kimin için, hangi sorunu çözer, ipucu, karşılaştırma; farklı kırpım/stil), `tools/pin.py jobs/<slug> <n>` ile üret, Read ile kontrol et, kuyruğa ekle. Uydurma özellik yok; yalnızca o ürünün yazısındaki doğrulanmış bilgiler.
- Commit + push → raw URL'yi commit SHA ile kur, curl 200.
- Her pin için Günlük Short 11. adımdaki create/button yöntemi (1280x900, görsel üstüne hover, pano satırına tıkla, "panosuna kaydedildi" doğrula). İki pin arasında en az 2 dk bekle.
- pins.json'u posted:<bugün> ve pin_url ile güncelle, commit + push. Viewport "desktop".
- Rapor yalnızca hata olursa (başarıda mesaj gönderme; günde bir kez, ikinci çalışmada tek satır "📌 Bugün <n> pin atıldı" yazılabilir).

## Haftalık uzun video (pazar)
- picks.json'da `in_weekly:false` olan ve bu hafta yayınlanan pick sayısı 4'ten azsa yapma; raporda nedenini yaz.
- `python3 tools/build_long.py <YYYY-MM-DD>-weekly "<Başlık>" jobs/<a> jobs/<b> ...` (sıra: yayın sırası). Başlık örn. "5 Smart Amazon Finds This Week (Tech, Beauty, Home)". Çıktı: v/<slug>.mp4 + -chapters.txt.
- YouTube: normal video (Short değil). Açıklama: 2 cümle özet + boş satır + chapters + her ürün için "Name – https://www.amazon.com/dp/ASIN?tag=desksetuppi07-20" (uzun videoda TIKLANABİLİR) + Video Picks linki + açıklama cümlesi + görsel atıfları. Küçük resim: build_long ara karesi (intro) yeterli. Oynatma listesi "Weekly Smart Picks". Yayından sonra sabit yorum: en çok merak edilen ürünün linki + soru.
- O haftanın Short'larında (Studio → video → İlgili video) bu uzun videoyu seç.
- picks.json'da ilgili kayıtları in_weekly:true yap, commit.

## DUR koşulları
Captcha, kimlik doğrulama, giriş isteme, telif/politika uyarısı, yükleme sınırı, ASIN doğrulanamadı ve yedek ürün de bulunamadı, Blogger/YouTube başka görevce kullanılıyor (studio.youtube.com başka kanalda açık ve işlem sürüyorsa 10 dk bekle, en fazla 3 kez). Ne olduğunu ve Kadir Bey'in ne yapması gerektiğini bildir.

## Notlar
- 15 Kasım 2026: Kanal adı Smart Picks Daily, ses Kokoro af_heart (kadın, Kadir Bey seçti). İlk Short (Pick #1 UGREEN) yayında. Video Picks sayfası açıldı, kanal linki ona çevrildi. Pinterest kuruldu, ilk pin atıldı. Pazar uzun videosu 22 Kasım'dan itibaren. Kadir Bey günde 5 pin istedi: ana pin + günde 2 ek pin çalışması × 2 pin (pins.json kuyruğu).
