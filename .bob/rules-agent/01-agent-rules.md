# Rules — Agent mode (general)

## סדר עבודה בכל משימת קוד
1. קרא את קובץ ה-plan הרלוונטי מ-`plans/` לפני שכותב שורה
2. בדוק אם יש בדיקות קיימות — אל תשבור אותן
3. כתוב קוד מינימלי שפותר את הבעיה — לא יותר
4. הרץ בדיקות לפני סיום
5. עדכן `AGENTS.md` אם שינית ארכיטקטורה

## Finding model — תמיד לייבא
```python
from engine.models import Finding  # לא להגדיר מחדש
```

## API endpoints — תקן
```
POST /api/upload          → העלאת קבצים
POST /api/run             → הרצת כל הכללים על dataset
GET  /api/findings        → רשימת ממצאים (query params: status, category, min_amount)
GET  /api/findings/{id}   → פירוט + evidence
PATCH /api/findings/{id}  → עדכון סטטוס {status: "reviewed_ok"|"in_progress"|"fixed"}
GET  /api/report          → PDF דוח
POST /api/agent/query     → שאלה לסוכן {question: str, dataset_id: str}
```

## סביבה
```
Python 3.11+
DuckDB 0.10+
FastAPI 0.110+
pandas 2.0+
pytest 8.0+
```

## לפני כל commit
- [ ] `pytest engine/tests/` — כל הבדיקות עוברות
- [ ] אין API keys בקוד
- [ ] שמות קבצים באנגלית
