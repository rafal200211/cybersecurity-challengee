"""Intentionally vulnerable, local-only classroom CTF. Uses synthetic data."""
import html
import json
import os
import sqlite3
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import parse_qs, urlparse

FLAGS = {"1": "FLAG{hidden_files_are_not_private}",
         "2": "FLAG{check_the_record_owner}",
         "3": "FLAG{use_parameterized_queries}"}

STYLE = """
:root{color-scheme:dark}*{box-sizing:border-box}body{margin:0;background:#0b1220;color:#e6edf7;font:18px/1.8 Tahoma,Arial,sans-serif}main{max-width:1050px;margin:45px auto;padding:24px}a{color:#66d9cf}h1{font-size:38px;line-height:1.4}h2{font-size:25px}p{color:#b7c4d8}.tag{color:#66d9cf;font-size:14px;letter-spacing:1px}.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(250px,1fr));gap:18px}.card{background:#142136;border:1px solid #293b55;border-radius:18px;padding:25px;margin:18px 0}input,button{font:inherit;border-radius:9px;padding:10px 16px;border:1px solid #405570}input{background:#0b1220;color:white;max-width:100%;width:420px}button,.button{background:#66d9cf;color:#092224;cursor:pointer;border:0;font-weight:bold}.button{display:inline-block;padding:8px 20px;border-radius:9px;text-decoration:none}code,pre{direction:ltr;unicode-bidi:embed;overflow-wrap:anywhere}pre{white-space:pre-wrap;background:#0b1220;padding:18px;border-radius:10px}.hint{font-size:15px}footer{font-size:14px;color:#8c9eb8;margin-top:35px}
"""

def page(title, body):
    return f'''<!doctype html><html lang="ar" dir="rtl"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{html.escape(title)} | مختبر الثغرات</title><style>{STYLE}</style></head><body><main><a href="/">مختبر الثغرات / الرئيسية</a><p class="tag">LOCAL SECURITY LAB · 3 LEVELS</p><h1>{title}</h1>{body}<footer>مختبر تعليمي • بيانات وهمية • ثغرات مقصودة • تشغيل محلي فقط</footer></main></body></html>'''

def flag_form(level):
    return f'''<section class="card"><h2>تحقق من الحل</h2><form action="/check" method="post"><input type="hidden" name="level" value="{level}"><input name="flag" aria-label="رمز النجاح" placeholder="FLAG{{...}}" dir="ltr" required> <button>تحقق</button></form></section>'''

def search(query):
    # LEVEL 3: deliberately concatenated SQL. Never copy this pattern into real apps.
    with sqlite3.connect(":memory:") as db:
        db.executescript("CREATE TABLE products(name TEXT); INSERT INTO products VALUES ('Notebook'),('Keyboard'),('Mouse'); CREATE TABLE vault(secret TEXT);")
        db.execute("INSERT INTO vault VALUES (?)", (FLAGS["3"],))
        return db.execute("SELECT name FROM products WHERE name LIKE '%" + query + "%'").fetchall()

class Handler(BaseHTTPRequestHandler):
    def send(self, content, status=200, content_type="text/html; charset=utf-8"):
        data = content.encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(data)))
        self.send_header("Cache-Control", "no-store")
        self.send_header("X-Content-Type-Options", "nosniff")
        self.end_headers()
        self.wfile.write(data)

    def do_GET(self):
        url = urlparse(self.path)
        args = parse_qs(url.query, keep_blank_values=True)
        if url.path == "/":
            cards = "".join(f'<section class="card"><span class="tag">LEVEL 0{n}</span><h2>{title}</h2><p>{desc}</p><a class="button" href="/level/{n}">ابدأ المرحلة</a></section>' for n, title, desc in [
                (1, "كشف المعلومات", "سهل · اكتشف ملفًا لا يظهر في قوائم الموقع."),
                (2, "خلل الصلاحيات", "متوسط · اختبر من يستطيع قراءة الفواتير."),
                (3, "حقن SQL", "أصعب · افحص طريقة بحث الموقع في قاعدة البيانات.")])
            return self.send(page("ثلاث مراحل. ثلاث ثغرات.", '<p>أنت تختبر متجرًا تجريبيًا. ابحث عن رمز النجاح في كل مرحلة وأدخله للتحقق. المراحل مستقلة ويمكن لعبها بأي ترتيب.</p><div class="grid">'+cards+'</div>'))
        if url.path == "/robots.txt":
            return self.send("User-agent: *\nDisallow: /backup/site-notes.txt\n", content_type="text/plain; charset=utf-8")
        if url.path == "/backup/site-notes.txt":
            return self.send("Demo deployment notes\nDo not publish internal backup files.\n"+FLAGS["1"]+"\n", content_type="text/plain; charset=utf-8")
        if url.path == "/level/1":
            return self.send(page("01 / كشف المعلومات", '<section class="card"><p>ترك المطور ملف ملاحظات احتياطيًا على خادم الموقع. اكتشف مساره واقرأ محتواه.</p><details><summary>تلميح</summary><p>أي ملف يخبر محركات البحث بالمسارات التي يُفضّل عدم فهرستها؟</p></details></section>'+flag_form(1)))
        if url.path == "/level/2":
            return self.send(page("02 / خلل الصلاحيات — IDOR", '<section class="card"><p>هويتك التجريبية ثابتة: المستخدم 7. فاتورتك رقم 1001. يجب أن تكون فواتير المستخدمين الآخرين خاصة.</p><a href="/invoice?id=1001">عرض فاتورتي</a><details><summary>تلميح</summary><p>راقب رقم الفاتورة في عنوان الصفحة. هل يتحقق الخادم من مالك السجل؟</p></details></section>'+flag_form(2)))
        if url.path == "/invoice":
            invoices = {"1001": {"owner": 7, "item": "Notebook", "note": "Your demo invoice"}, "1002": {"owner": 8, "item": "Keyboard", "note": FLAGS["2"]}}
            # LEVEL 2: intentionally missing ownership authorization for user 7.
            invoice = invoices.get(args.get("id", [""])[0])
            if invoice is None:
                return self.send(page("الفاتورة غير موجودة", '<a href="/level/2">عودة للمرحلة</a>'), 404)
            return self.send(page("الفاتورة", '<p>المستخدم الحالي: 7</p><pre dir="ltr">'+html.escape(json.dumps(invoice, indent=2))+'</pre><a href="/level/2">عودة للمرحلة الثانية</a>'))
        if url.path == "/level/3":
            query = args.get("q", [""])[0]
            result = ""
            if "q" in args:
                try:
                    result = '<pre dir="ltr">'+html.escape("\n".join(str(row[0]) for row in search(query)) or "No results")+'</pre>'
                except sqlite3.Error as error:
                    result = '<pre dir="ltr">SQLite error: '+html.escape(str(error))+'</pre>'
            body = '<section class="card"><p>ابحث في منتجات المتجر. هدفك قراءة رمز مخفي في جدول آخر.</p><form method="get"><input name="q" aria-label="بحث المنتجات" dir="ltr" value="'+html.escape(query, quote=True)+'" placeholder="Notebook"> <button>بحث</button></form>'+result+'<details><summary>تلميح</summary><p>الاستعلام يعيد عمودًا واحدًا. جدول الأسرار اسمه <code>vault</code> وعموده <code>secret</code>. جرّب فهم أثر علامة الاقتباس ثم UNION SELECT.</p></details></section>'
            return self.send(page("03 / حقن SQL", body+flag_form(3)))
        self.send(page("الصفحة غير موجودة", '<a href="/">عودة للرئيسية</a>'), 404)

    def do_POST(self):
        if self.path != "/check":
            return self.send("Not found", 404, "text/plain")
        try:
            length = int(self.headers.get("Content-Length", "0"))
        except ValueError:
            return self.send("Invalid length", 400, "text/plain")
        if not 0 <= length <= 4096:
            return self.send("Request too large", 413, "text/plain")
        args = parse_qs(self.rfile.read(length).decode("utf-8", errors="replace"))
        level = args.get("level", [""])[0]
        flag = args.get("flag", [""])[0].strip()
        if level not in FLAGS:
            return self.send("Unknown level", 400, "text/plain")
        correct = flag == FLAGS[level]
        self.send(page("أحسنت! تم حل المرحلة" if correct else "الرمز غير صحيح", f'<p>{"اكتشفت الثغرة واستخرجت رمز النجاح." if correct else "ارجع للمرحلة وجرّب مرة ثانية."}</p><a class="button" href="/level/{level}">عودة للمرحلة</a> <a href="/">جميع المراحل</a>'))

if __name__ == "__main__":
    host = os.environ.get("LAB_HOST", "127.0.0.1")
    print("Open http://127.0.0.1:8000 — Ctrl+C to stop", flush=True)
    ThreadingHTTPServer((host, 8000), Handler).serve_forever()
