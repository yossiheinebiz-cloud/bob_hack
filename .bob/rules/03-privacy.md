# כלל פרטיות — תיקון 13 (חל על כל המצבים)

## קו אדום — לעולם לא לכתוב קוד שעושה אחד מאלה:
- שומר תעודת זהות, מספר דרכון, או פרטי BAN (חשבון בנק) בטקסט ברור
- כותב שם עובד אמיתי לתוך ממצא — רק hash
- שומר קבצים גולמיים מעבר ל-24 שעות
- מאפשר גישה לנתוני שכר ללא RBAC
- שולח נתוני עובדים למודלים חיצוניים (Gemini/OpenAI) ללא Pseudonymisation קודם

## לפני כל פיצ'ר שנוגע בנתוני עובדים — בדוק:
1. האם אפשר לעשות את אותו הדבר בלי לאחסן שם אמיתי?
2. האם יש Retention policy מוגדרת?
3. האם יש Audit log?

## Pseudonymisation — תמיד לפני שמירה
```python
from engine.privacy import pseudonymise
# כל DataFrame עם עמודות PII עובר pseudonymise לפני:
# - שמירה ב-DB
# - שליחה ל-AI model
# - הצגה בממשק (אלא אם role == "admin" | "dpo")
```

## עמודות שהכלי מסרב לאחסן
ראה: engine/privacy.py → FORBIDDEN_COLUMNS

## מסמך מלא
ראה: 07-privacy-compliance.md
