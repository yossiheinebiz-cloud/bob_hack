# Plan 01 — מחולל נתונים סינתטיים

## מה בונים
Script Python שמייצר 5 קבצי CSV לחברת הייטק "טכנוסיס בע"מ" עם 10 בעיות שתולות.

## קלט / פלט
- **קלט:** אין — הכל נוצר בקוד
- **פלט:** `data/synthetic/*.csv` — 5 קבצים

## קבצים שייווצרו
```
data/synthetic/
├── invoices.csv      ← חשבוניות ספקים (500 שורות, 3 כפילויות שתולות)
├── employees.csv     ← עובדים (87 עובדים, 2 בעיות שכר)
├── payroll.csv       ← תלושי שכר (87×12 = 1,044 שורות, 2 חריגות)
├── licenses.csv      ← רישיונות תוכנה (23 כלים, 4 בעיות)
└── cloud_costs.csv   ← עלויות ענן (24 חודשים × 8 שירותים, 1 זומבי)
```

## 10 בעיות שתולות

| # | קובץ | סוג | תיאור | סכום בסיכון |
|---|---|---|---|---|
| 1 | invoices | DUP_INVOICE_EXACT | מילגם INV-4471 שולמה פעמיים | ₪23,400 |
| 2 | invoices | DUP_AMOUNT_WINDOW | AWS $12,000 ב-₪ וב-$ | ₪44,200 |
| 3 | invoices | INVOICE_SPLITTING | 4 חשבוניות מטריקס מתחת לסף | ₪48,000 |
| 4 | employees+payroll | PAYROLL_POST_TERMINATION | עובד 47 — שכר 3 חודשים אחרי סיום | ₪28,500 |
| 5 | employees+payroll | PAYROLL_OVERTIME_SPIKE | עובד 12 — 94 שעות נוספות | ₪4,200 |
| 6 | licenses | LICENSE_UNUSED | Figma — 14 רישיונות, 6 בשימוש | ₪19,600/שנה |
| 7 | licenses | LICENSE_DEPARTED | Slack Pro — 5 עובדים שעזבו | ₪3,600/שנה |
| 8 | licenses | LICENSE_DUPLICATE | Jira + Monday — כפולים | ₪24,000/שנה |
| 9 | licenses | AUTO_RENEWAL_JUMP | HubSpot +32% בחידוש | ₪14,400/שנה |
| 10 | cloud | CLOUD_ZOMBIE | staging-old — 45 יום ללא תעבורה | ₪8,400/שנה |

**סה"כ שתול:** ₪218,300

## בדיקות הצלחה
- כל 5 קבצים נוצרו ✓
- כל קובץ עם עמודות נכונות ✓
- 10 בעיות קיימות בדיוק ✓
- סכומים מסתכמים נכון ✓

## תלויות
- Python 3.11+, pandas, faker
- אין תלות בשום רכיב אחר — רץ עצמאי
