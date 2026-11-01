# איפה הכסף: אפיון מסכים מלא + Prompts לבנייה

*1 בנובמבר 2026. Web app + Mobile PWA. RTL עברית. Dark mode כברירת מחדל לארגונים, Light לבית.*

---

## עקרונות עיצוב גלובליים

| עיקרון | פירוט |
|---|---|
| **כסף במרכז** | מספר אחד גדול בכל מסך — לא גרפים |
| **אמון לפני הכל** | לכל מספר יש "למה?" ולחיצה לשורות מקור |
| **פעולה אחת ברורה** | כל מסך מוביל לפעולה אחת — לא תפריט של אפשרויות |
| **RTL מלא** | עברית, סכומים ב-₪, תאריכים DD/MM/YYYY |
| **צבעי ממצאים** | כתום = חשד, ירוק = חיסכון שבוצע, אפור = נבדק תקין. לא אדום |
| **Mobile-first** | כל מסך עובד על מסך 390px ומעלה |

### פלטת צבעים
```
רקע ראשי:   #0F1117  (כהה כמעט שחור)
רקע כרטיס:  #1A1D27
גבול:        #2A2D3A
טקסט ראשי:  #F0F2F8
טקסט משני:  #8B8FA8
כתום ממצא:  #F59E0B
ירוק חיסכון:#10B981
כחול פעולה: #3B82F6
אדום סיכון: #EF4444  (רק לסיכון עסקי גבוה)
```

---

## מסך 0 — Splash / Landing (אתר שיווקי)

### תיאור
דף נחיתה לכניסה ראשונה. מסביר ב-3 שניות מה הכלי עושה. CTA אחד: "התחל בחינם".

### מבנה
```
[Header] לוגו | כניסה | שפה
[Hero]   "מצא איפה הארגון שלך מפסיד כסף"
         "תוך 5 דקות, בלי מומחה BI"
         [CTA: התחל בחינם]
[Social proof] "₪2.6M חיסכון ממוצע לחברת 100 עובדים"
[3 בעיות] כלים שלא בשימוש | תשלומים כפולים | מנויים שהתחדשו
[איך עובד] 3 שלבים: העלה → מצא → חסוך
[CTA תחתון]
```

### Prompt לבנייה
```
Build a Hebrew RTL dark-mode landing page for "איפה הכסף" (Where Is the Money).
Stack: single HTML file, Tailwind CDN, vanilla JS.
Layout (RTL, dark #0F1117 bg):
- Sticky header: logo right, "כניסה" button left
- Hero: large headline "מצא איפה הארגון שלך מפסיד כסף",
  subheadline "תוך 5 דקות, בלי מומחה BI",
  orange CTA button "התחל בחינם — חינם לחודש הראשון"
- Stats bar: 3 numbers: "₪2.6M חיסכון ממוצע", "47 ממצאים ממוצע לארגון", "5 דקות להתחלה"
- 3-card section: כלים שלא בשימוש / תשלומים כפולים / מנויים שהתחדשו
- How it works: 3 steps with icons: העלה קבצים → המנוע מנתח → קבל רשימה
- Footer: "נבנה עם IBM Bob"
Fonts: system-ui. Colors: bg #0F1117, cards #1A1D27, orange #F59E0B, text #F0F2F8.
```

---

## מסך 1 — Onboarding: בחירת עולם

### תיאור
משתמש חדש בוחר מי הוא. 3 כרטיסים. בחירה מובילה ישירות להעלאה.

### מבנה
```
"מי אתם?" — כותרת גדולה

[כרטיס 1] 🏢 ארגון / רשות
           "מבקר פנים, גזבר, מנהל כספים"
           "ספקים, שכר, מכרזים"

[כרטיס 2] 💻 חברת הייטק          ← מומלץ
           "CFO, מנהל IT, מנהל תפעול"
           "כלים, ענן, ספקים, רישיונות"

[כרטיס 3] 🏠 משק בית
           "זוג, הורה"
           "מנויים, ביטוחים, בנק"

[קישור קטן] "רוצה לראות דמו קודם? ←"
```

### מקרי קצה
- לחצו "אחורה" אחרי בחירה → חזרה לבחירה בלי לאבד קבצים
- מובייל → כרטיסים אנכיים, לא רוחביים

### Prompt לבנייה
```
Build a Hebrew RTL onboarding screen "בחירת עולם" (Choose Domain).
3 large clickable cards in a row (mobile: stacked):
1. ארגון / רשות — icon: 🏢, subtitle: "ספקים, שכר, מכרזים"
2. חברת הייטק — icon: 💻, badge: "מומלץ" in orange, subtitle: "כלים, ענן, רישיונות"
3. משק בית — icon: 🏠, subtitle: "מנויים, ביטוחים, בנק"
Hover: card border turns orange (#F59E0B), slight scale-up.
Selected: filled orange border + checkmark.
Below cards: small link "רוצה לראות דמו קודם? ←"
Dark bg #0F1117, card bg #1A1D27, border #2A2D3A.
```

---

## מסך 2 — העלאת קבצים

### תיאור
Drag & drop. מזהה אוטומטי סוג קובץ. מראה מה זוהה ומה חסר. מתחיל ניתוח.

### מבנה
```
[Progress] בחירת עולם ✓ → העלאה → מיפוי → ניתוח

"העלו את הנתונים שלכם"

[Drop Zone גדול]
  "גררו קבצים לכאן, או לחצו לבחירה"
  "CSV, Excel, JSON — עד 50MB לקובץ"

[קבצים שהועלו — לפי סוג:]
  ✅ חשבוניות_2026.xlsx   (2,847 שורות) — זוהה
  ✅ עובדים.csv            (143 שורות)   — זוהה
  ⚠️ שכר.csv              — זוהה חלקית, צריך אישור עמודות
  ❌ קובץ_רכבים           — חסר (אופציונלי)

[בנר] "יש לנו 2/3 קבצים נדרשים — נוכל להריץ ניתוח חלקי"

[כפתור] "התחל ניתוח ←" (פעיל גם עם קבצים חלקיים)
[קישור] "חבר ל-Priority / BigQuery במקום"
```

### Prompt לבנייה
```
Build a Hebrew RTL file upload screen.
- Large dashed drop zone (border #2A2D3A, hover border #F59E0B)
  text: "גררו קבצים לכאן, או לחצו לבחירה" + "CSV, Excel, JSON — עד 50MB"
- Below drop zone: file list with status icons:
  ✅ green = detected & mapped
  ⚠️ orange = detected, needs column confirmation
  ❌ gray = missing (optional)
  Each row: filename, row count, status badge
- Info banner (blue): "יש לנו 2/3 קבצים נדרשים — נוכל להריץ ניתוח חלקי"
- Primary button: "התחל ניתוח ←" always enabled
- Secondary link: "חבר ל-Priority / BigQuery במקום"
- Progress bar at top: 3 steps — בחירת עולם ✓ | העלאה (active) | ניתוח
```

---

## מסך 3 — מיפוי עמודות (AI Column Mapping)

### תיאור
AI הציע מיפוי. משתמש רואה הצעה ומאשר/מתקן. מוצג רק כשיש ספק.

### מבנה
```
"בדקו את המיפוי"
"זיהינו אוטומטית את עמודות הקובץ — אשרו או תקנו"

[טבלה:]
עמודה בקובץ          | מה זיהינו    | ביטחון | פעולה
"סכום_כולל_כולל_מע"מ" | סכום         | 98%    | ✅ אשר
"תאריך_חשבונית"       | תאריך        | 95%    | ✅ אשר
"שם_ספק_מלא"          | ספק          | 91%    | ✅ אשר
"מס_חשבונית"          | מספר מסמך   | 72%    | ⚠️ בדוק ▾
"הערות_פנימיות"        | להתעלם      | —      | [בחר] ▾

[בנר] "3 עמודות זוהו בביטחון גבוה ✓ — נדרש אישורך ל-1"

[כפתור] "אשר ותתחיל ←"
[קישור] "הצג את כל העמודות (12)"
```

### Prompt לבנייה
```
Build a Hebrew RTL column mapping screen.
Table with 4 columns: "עמודה בקובץ" | "מה זיהינו" | "ביטחון" | "פעולה"
Rows:
- High confidence (>90%): show green checkmark, "אשר" button pre-checked
- Medium confidence (70-90%): show orange warning, dropdown to select correct mapping
- Unknown: show gray "להתעלם" with dropdown override option
Confidence shown as % badge: green >90%, orange 70-90%, gray <70%.
Info banner: "3 עמודות זוהו בביטחון גבוה ✓ — נדרש אישורך ל-1"
Primary CTA: "אשר ותתחיל ←"
Secondary link: "הצג את כל העמודות (12)"
```

---

## מסך 4 — ניתוח בתהליך (Loading / Processing)

### תיאור
מסך ביניים. מראה מה קורה. לא spinner ריק — כל שלב עם הסבר.

### מבנה
```
"מנתח את הנתונים שלכם..."

[Progress steps animated:]
  ✅ טוען 2,847 חשבוניות
  ✅ מאחד שמות ספקים (מצאנו 3 כפילויות)
  ⟳ בודק תשלומים כפולים...
  ○ בודק חריגות שכר
  ○ בודק רישיונות
  ○ מחשב חיסכון אפשרי

[Teaser — מתחת לרשימה:]
  "כבר מצאנו:
   💰 2 חשבוניות כפולות — ₪8,400
   ⏳ עוד כמה שניות..."

[זמן משוער:] "עוד ~30 שניות"
```

### Prompt לבנייה
```
Build a Hebrew RTL processing/loading screen.
Animated step list (top to bottom):
- Completed steps: green ✅ with step name + brief result ("מצאנו 3 כפילויות שמות")
- Current step: spinning orange ⟳ with step name
- Pending steps: gray ○ with step name
Steps: טוען נתונים | מאחד ספקים | בודק כפילויות | בודק שכר | בודק רישיונות | מחשב חיסכון
"Teaser" card that appears after first finding: orange border card showing "כבר מצאנו: 2 חשבוניות כפולות — ₪8,400"
Progress bar at top showing % complete.
Estimated time remaining: "עוד ~30 שניות"
Auto-redirect to dashboard when complete.
```

---

## מסך 5 — לוח הבקרה הראשי (Dashboard)

### תיאור
המסך המרכזי. מספר אחד גדול. פילוח לפי קטגוריה. 5 ממצאים גדולים.

### מבנה
```
[Header] לוגו | שם חברה | התראות 3 | פרופיל

[Hero card — גדול:]
  "חיסכון אפשרי השנה"
  ₪ 340,200
  [Progress bar] מתוך ₪340K — 0 טופל עד כה
  "מבוסס על 47 ממצאים פתוחים"

[4 כרטיסי קטגוריה:]
  💳 תשלומים כפולים    ₪94,000   12 ממצאים  →
  💻 רישיונות לא בשימוש ₪127,000  8 ממצאים  →
  ☁️ ענן               ₪73,200   5 ממצאים   →
  👤 שכר               ₪46,000   3 ממצאים   →

[טבלת 5 ממצאים גדולים:]
  # | כותרת | קטגוריה | ₪ בסיכון | ביטחון | סטטוס | →
  1   חשבונית כפולה — מילגם    תשלומים  ₪23,400  98%  פתוח  →
  2   14 רישיונות Figma לא בשימוש  רישיונות ₪19,600 94%  פתוח  →
  ...

[כפתור] "הצג את כל 47 הממצאים"
[כרטיס סוכן] "שאל את הסוכן: 'כמה שילמנו לספקים חדשים השנה?'" →
```

### מקרי קצה
- אין ממצאים → "לא מצאנו חריגות — הנתונים שהועלו נראים תקינים. ייתכן שחסרים קבצים."
- ממצא אחד שהוא 94% מהסכום → banner: "ממצא אחד מהווה 94% מהסכום — בדוק אותו קודם"
- נתונים ישנים → banner כתום: "הנתונים מ-2023 — ממצאים עשויים שלא לשקף מצב נוכחי"

### Prompt לבנייה
```
Build a Hebrew RTL dark-mode financial dashboard.
Layout (max-width 1280px, centered):
1. Top header: logo right, company name, notification bell (badge 3), avatar
2. Hero KPI card (full width, dark card #1A1D27):
   - Label: "חיסכון אפשרי השנה" (small gray text)
   - Number: "₪340,200" (huge, white, 64px)
   - Progress bar: 0% resolved (orange fill)
   - Subtext: "מבוסס על 47 ממצאים פתוחים"
3. 4 category cards in a row (mobile: 2x2 grid):
   Each: icon, category name, total ₪, finding count, arrow →
   Categories: תשלומים כפולים (₪94K), רישיונות (₪127K), ענן (₪73K), שכר (₪46K)
4. Top findings table (5 rows):
   Columns: rank, title, category badge, ₪ amount (bold orange), confidence %, status badge, →
5. "הצג את כל 47 הממצאים" button (outline style)
6. Agent teaser card at bottom: "שאל את הסוכן" with example question
Dark theme throughout. Orange accents. Responsive.
```

---

## מסך 6 — רשימת ממצאים

### תיאור
כל הממצאים. סינון, מיון, חיפוש. ממוין לפי ₪.

### מבנה
```
[Filters bar:]
  [חיפוש] | קטגוריה ▾ | סטטוס ▾ | ביטחון ▾ | [מיין: לפי סכום ▾]

[Summary bar:]
  47 ממצאים | ₪340,200 סה"כ | 12 טופלו | 35 פתוחים

[כרטיס לכל ממצא:]
  ┌─────────────────────────────────────────┐
  │ 🔶 חשבונית כפולה — מילגם בע"מ          │
  │ תשלומים כפולים  •  98% ביטחון  •  פתוח │
  │ ₪23,400 בסיכון                          │
  │ "אותו ספק ואותה חשבונית שולמה פעמיים" │
  │ [נבדק, תקין] [בטיפול] [הצג פירוט →]    │
  └─────────────────────────────────────────┘

[Pagination] 1 2 3 ... 5
```

### Prompt לבנייה
```
Build a Hebrew RTL findings list screen.
Filter bar at top: search input, dropdowns for קטגוריה/סטטוס/ביטחון, sort by dropdown.
Summary strip: "47 ממצאים | ₪340,200 סה"כ | 35 פתוחים"
Finding cards (one per finding):
- Header: orange 🔶 icon, finding title (bold), category badge, confidence badge, status badge
- Amount: large orange "₪23,400 בסיכון"
- One-line description of why it was flagged
- Action buttons: "נבדק, תקין" (gray outline) | "בטיפול" (blue outline) | "הצג פירוט →" (filled orange)
Card hover: slight border highlight.
Pagination at bottom.
Empty state: "אין ממצאים בסינון זה — נסה לנקות סינונים"
```

---

## מסך 7 — פירוט ממצא

### תיאור
מה מצאנו. הכלל. השורות המקוריות. פעולה מומלצת. מעקב.

### מבנה
```
← חזרה לרשימה

[כותרת] 🔶 חשבונית כפולה — מילגם בע"מ
[badges] תשלומים כפולים | ₪23,400 | 98% ביטחון | פתוח

[3 tabs:] הסבר | ראיות | היסטוריה

--- tab: הסבר ---
"מה מצאנו:"
אותו ספק (מילגם בע"מ) ואותו מספר חשבונית (INV-2024-4471)
שולמו פעמיים — ב-12/03/2026 וב-15/03/2026.
הסכום הכפול: ₪23,400.

"הכלל:"
כלל DUP_INVOICE_EXACT — אותו ספק + אותו מספר חשבונית + יותר מתשלום אחד.

"פעולה מומלצת:"
פנה למילגם ובקש החזר על תשלום כפול. צרף את מספר החשבונית.

--- tab: ראיות ---
[טבלה: 2 שורות מקוריות:]
תאריך      | ספק         | חשבונית       | סכום    | ערוץ
12/03/2026 | מילגם בע"מ  | INV-2024-4471 | ₪23,400 | העברה
15/03/2026 | מילגם בע"מ  | INV-2024-4471 | ₪23,400 | העברה

[כפתור] "הורד ראיות כ-CSV"

--- tab: היסטוריה ---
01/11/2026 12:03 — נמצא אוטומטית
[ריק — לא טופל עדיין]

[Footer actions:]
[נבדק, תקין — הוסף הערה] [בטיפול] [✅ הוחזר כסף — סמן ₪23,400]
```

### Prompt לבנייה
```
Build a Hebrew RTL finding detail screen.
Header: back arrow, finding title, badges (category, amount in orange, confidence, status).
3 tabs: הסבר | ראיות | היסטוריה
Tab 1 - הסבר:
  - "מה מצאנו" section with plain Hebrew explanation
  - "הכלל" section: rule ID + description
  - "פעולה מומלצת" section: actionable text in blue card
Tab 2 - ראיות:
  - Data table showing original rows that triggered the rule
  - Highlighted cells that match (same invoice number)
  - "הורד ראיות כ-CSV" button
Tab 3 - היסטוריה:
  - Timeline of status changes with timestamp and user
Footer action bar (sticky):
  - "נבדק, תקין" button (gray)
  - "בטיפול" button (blue)
  - "הוחזר כסף ₪23,400" button (green, triggers confetti animation)
```

---

## מסך 8 — הסוכן (Agent Chat)

### תיאור
חלון צד או מסך מלא. שאלות בעברית. תשובות עם הפניה לשורה.

### מבנה
```
[Header] 🤖 סוכן איפה הכסף  [X סגור]

[שאלות מוצעות:]
  "כמה שילמנו לספקים חדשים השנה?"
  "אילו רישיונות לא נפתחו 60 יום?"
  "מה השתנה מהרבעון הקודם?"

[Chat area:]
  [User] "כמה שילמנו לספקים שלא עבדנו איתם לפני 2026?"

  [Bot] "מצאתי 7 ספקים חדשים מ-2026:
         סה"כ: ₪347,200
         הגדול: טכנוסיס בע"מ — ₪89,400 (3 עסקאות)

         [הצג ממצא: ספקים חדשים →]"

[Input] "שאל שאלה בעברית..." [שלח →]

[Footer] "הסוכן עונה רק מתוך הנתונים שהועלו"
```

### מקרי קצה
- שאלה ללא נתון → "הנתון הזה לא קיים בקבצים שהועלו"
- שאלה על אדם בשם → אזהרה לפני תשובה
- שאלה חוצה גבול → "אני יכול לענות רק על נתוני הארגון"

### Prompt לבנייה
```
Build a Hebrew RTL AI chat interface (side panel, 420px wide).
Header: robot emoji + "סוכן איפה הכסף" title + close X button.
Suggested questions chips (horizontal scroll): 3 example questions as clickable pills.
Chat area (scrollable):
  - User messages: right-aligned, orange background bubble
  - Bot messages: left-aligned, dark card #1A1D27, with:
    - Plain text answer in Hebrew
    - Highlighted number/amount in orange
    - Optional "הצג ממצא →" link card at bottom of message
  - Typing indicator: 3 animated dots
Input bar at bottom: text input + send button (orange arrow).
Disclaimer footer: small gray text "הסוכן עונה רק מתוך הנתונים שהועלו"
```

---

## מסך 9 — דוח PDF (Preview)

### תיאור
תצוגה מקדימה של הדוח לפני הפקה. אפשרות להסתיר שמות.

### מבנה
```
[Toolbar] הורד PDF | שלח במייל | [הסתר שמות: OFF/ON]

[Preview — A4 מסוגנן:]
  [Logo + שם ארגון]              [תאריך: 01/11/2026]

  דוח ממצאים — סיכום מנהלים
  ─────────────────────────────
  חיסכון אפשרי: ₪340,200
  ממצאים: 47 | טופלו: 12 | פתוחים: 35

  ממצאים לפי קטגוריה:
  [bar chart קצר]

  5 ממצאים מובילים:
  [טבלה מסוגננת]

  נספח: כל הממצאים עם ראיות
  ─────────────────────────────
  [Footer] הופק ע"י "איפה הכסף" | IBM Bob Hackathon 2026
```

### Prompt לבנייה
```
Build a Hebrew RTL PDF report preview screen.
Toolbar at top: "הורד PDF" primary button, "שלח במייל" secondary, toggle "הסתר שמות".
A4-sized preview card (shadow, white bg, padding):
  - Header: logo placeholder left, company name + date right
  - Title: "דוח ממצאים — סיכום מנהלים" centered
  - 3 KPI numbers in a row: חיסכון אפשרי ₪340K | ממצאים 47 | טופלו 12
  - Small horizontal bar chart: 4 categories with ₪ amounts
  - Top 5 findings table: rank, title, ₪ amount, status
  - Footer: "הופק ע"י איפה הכסף | 01/11/2026"
Outside preview: page navigation (1/3, 2/3, 3/3).
```

---

## מסך 10 — הגדרות + אינטגרציות

### תיאור
חיבור למקורות נתונים חיצוניים. ניהול ספי התראות. ניהול משתמשים.

### מבנה
```
[Tabs:] חיבורים | התראות | משתמשים | חשבון

--- tab: חיבורים ---
[כרטיסי connector:]
  ✅ Priority ERP        מחובר — עודכן לפני שעה    [נתק]
  ⬜ Google BigQuery     לא מחובר                  [חבר]
  ⬜ AWS Cost Explorer   לא מחובר                  [חבר]
  ⬜ Slack               לא מחובר                  [חבר]
  ⬜ Gmail               לא מחובר                  [חבר]
  ✅ CSV Upload          תמיד פעיל                 —

--- tab: התראות ---
  ספק חדש מעל: [___₪] → התראה ל: [Slack / מייל]
  חשבונית כפולה: [תמיד] → [מיידי / יומי / שבועי]
  ממצא פתוח מעל: [7] ימים → תזכורת ל: [מנהל כספים]
```

### Prompt לבנייה
```
Build a Hebrew RTL settings screen with 4 tabs: חיבורים | התראות | משתמשים | חשבון.
Tab 1 - חיבורים (Integrations):
  Grid of connector cards (2 columns, mobile: 1 column):
  Each card: connector logo/icon, name, status badge (מחובר=green / לא מחובר=gray),
  last sync time if connected, connect/disconnect button.
  Connectors: Priority, BigQuery, AWS, Slack, Gmail, CSV (always active).
Tab 2 - התראות (Alerts):
  Form rows with label + input + destination selector:
  - "ספק חדש מעל ₪___" → channel dropdown
  - "חשבונית כפולה" → frequency dropdown
  - "ממצא פתוח מעל ___ ימים" → recipient input
  Save button.
```

---

## סדר בנייה מומלץ

| שלב | מסכים | מה מוכן אחרי |
|---|---|---|
| 1 | 5 (Dashboard) | הדגמה בסיסית — מספר + ממצאים |
| 2 | 6+7 (רשימה + פירוט) | flow מלא: ממצא → פירוט → טיפול |
| 3 | 2+3 (העלאה + מיפוי) | onboarding עובד |
| 4 | 8 (סוכן) | שאלות בעברית |
| 5 | 9 (דוח) | PDF לועדת ביקורת |
| 6 | 0+1 (Landing + בחירה) | אתר שלם |
| 7 | 4+10 (Loading + הגדרות) | מוצר מלא |
