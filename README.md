# MiniPlayer

مصغّر مشغّل فيديو لسطح المكتب، مكتوب ببايثون وPySide6.

## التشغيل من المصدر

```bash
pip install -r requirements.txt
python main.py
```

أو افتح ملف `dist/MiniPlayer.exe` بعد البناء.

## الاستخدام

- زر **فتح** أو `Ctrl+O`
- اسحب ملف فيديو إلى النافذة
- مسافة: تشغيل / إيقاف
- `F`: ملء الشاشة
- `Esc`: الخروج من ملء الشاشة
- شريط التقدم لتقديم الفيديو، وشريط الصوت على اليمين

الصيغ المدعومة تعتمد على ويندوز: MP4, MKV, AVI, MOV, WEBM, WMV.

## بناء ملف EXE

```bash
pyinstaller --noconfirm --noconsole --onefile --name MiniPlayer main.py
```

الملف يظهر في مجلد `dist`.

## المتطلبات

- Python 3.10+
- PySide6
