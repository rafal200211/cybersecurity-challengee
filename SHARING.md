# مشاركة مؤقتة عبر الإنترنت

الإعداد الافتراضي محلي. ملف compose.public.yaml اختياري ويضيف Cloudflare Quick Tunnel لمشاركة المختبر التعليمي مع الزملاء. الرابط عام لكل من يحصل عليه ولا يحتوي حماية دخول. لا تستخدم بيانات حقيقية.

من مجلد المشروع:

```powershell
docker compose -f compose.yaml -f compose.public.yaml up -d
docker compose -f compose.yaml -f compose.public.yaml logs tunnel
```

انسخ رابط https الذي ينتهي بـ trycloudflare.com من السجل. أبقِ جهازك مستيقظًا وDocker والإنترنت شغالين. الرابط مؤقت وقد يتغير عند إعادة تشغيل النفق.

لإيقاف الوصول عبر الإنترنت مع إبقاء المختبر المحلي:

```powershell
docker compose -f compose.yaml -f compose.public.yaml stop tunnel
```

لإيقاف المختبر والنفق معًا:

```powershell
docker compose -f compose.yaml -f compose.public.yaml down
```

GitHub مناسب لحفظ ملفات المشروع؛ GitHub Pages لا يشغّل خادم Python. كذلك نشر المصدر يكشف رموز الحلول، لذا احتفظ بالمستودع خاصًا إذا أردت اختبار زملائك دون اطلاعهم على الحلول.

المراجع:
- https://developers.cloudflare.com/tunnel/get-started/quick-tunnels/
- https://docs.github.com/en/pages/getting-started-with-github-pages/creating-a-github-pages-site
