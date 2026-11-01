// איפה הכסף — demo data. SINGLE SOURCE OF TRUTH for every screen in design/v2
// and for the planted issues in scripts/generate_startup_data.py (data/startup/ground_truth.json).
// All company data is SYNTHETIC. Vendors are real services, invoices/amounts are invented.
window.DEMO = {
  company: {
    name: 'טכנוסיס בע״מ', nameEn: 'Technosis Ltd', domain: 'technosis.io', hp: '515873214',
    stage: 'Series B', employees: 112, active: 104, departed24m: 23, city: 'תל אביב',
    period: '11/2024–10/2026', fiscalCurrency: 'ILS', usdIls: 3.70,
    departments: { 'R&D': 61, 'Product': 9, 'Sales': 14, 'Marketing': 7, 'Customer Success': 9, 'G&A': 12 },
  },
  user: { name: 'מיכל לוי', role: 'CFO', initials: 'מל', email: 'michal@technosis.io' },

  // annual run-rate, ILS
  spend: {
    total: 71_400_000,
    byCategory: [
      { id: 'payroll', label: 'שכר ועלות מעביד', amount: 55_200_000 },
      { id: 'cloud',   label: 'ענן ותשתיות',      amount: 6_100_000 },
      { id: 'saas',    label: 'תוכנה ורישיונות',  amount: 3_400_000 },
      { id: 'office',  label: 'משרד, חשמל ורכבים', amount: 2_600_000 },
      { id: 'ai',      label: 'AI וטוקנים',       amount: 1_900_000 },
      { id: 'ap',      label: 'שירותים מקצועיים', amount: 1_200_000 },
      { id: 'finance', label: 'עמלות ומיסים',     amount: 700_000 },
      { id: 'telecom', label: 'תקשורת וסלולר',    amount: 300_000 },
    ],
    // monthly non-payroll spend, ILS, 11/2024 → 10/2026 (AI grows fastest)
    monthlyNonPayroll: [1031000,1044000,1058000,1062000,1079000,1091000,1105000,1118000,1126000,1149000,1163000,1172000,1188000,1205000,1219000,1236000,1251000,1262000,1290000,1311000,1324000,1342000,1361000,1383000],
    monthlyAi: [52000,55000,61000,66000,72000,79000,88000,94000,101000,112000,118000,126000,131000,138000,142000,147000,151000,156000,162000,168000,171000,176000,181000,188000],
  },

  kpi: {
    recurringSavings: 1_099_900,  // ₪/yr, recurring
    oneTimeRecovery: 139_600,     // ₪, refunds / credits to claim
    toReview: 96_000,             // ₪, needs human review, not counted as savings
    verifiedSaved: 284_300,       // ₪, already closed & verified (status fixed)
    openFindings: 27, vendors: 143, invoicesScanned: 1_608, rowsScanned: 155_263, sources: 11,
  },

  // kind: recurring = ₪/yr saving | recovery = one-time money back | review = check by a human
  // conf 0..1 · status: open | in_progress | fixed | reviewed_ok
  findings: [
    { id: 'F-1001', rule: 'AI_MODEL_OVERKILL', cat: 'ai', kind: 'recurring', amount: 214000, conf: .86, status: 'open', owner: 'אורי (Data)', vendor: 'Anthropic',
      title: 'צינור סיווג טיקטים רץ על מודל הדגל', why: '480K קריאות בחודש, ממוצע 380 טוקן פלט, משימת סיווג. מודל קטן מאותה משפחה עונה בדיוק דומה ב-20% מהמחיר.', action: 'להעביר את project "ticket-classifier" למודל קטן, לבדוק דיוק על 500 דוגמאות' },
    { id: 'F-1002', rule: 'CLOUD_NO_COMMITMENT', cat: 'cloud', kind: 'recurring', amount: 172000, conf: .91, status: 'in_progress', owner: 'רון (DevOps)', vendor: 'AWS',
      title: '68% מהמחשוב ב-On-Demand בלי Savings Plan', why: 'שימוש בסיסי יציב של 41 vCPU-שעות ממוצע ב-14 חודשים אחרונים, בלי התחייבות.', action: 'Compute Savings Plan לשנה, ללא מקדמה, על 75% מהבסיס' },
    { id: 'F-1003', rule: 'CLOUD_ZOMBIE', cat: 'cloud', kind: 'recurring', amount: 96000, conf: .95, status: 'open', owner: 'רון (DevOps)', vendor: 'AWS',
      title: 'אשכול EKS "staging-old" רץ 47 יום בלי תעבורה', why: '3 nodes m6i.xlarge + NAT + ALB. אפס בקשות ב-ALB מאז 15/09/2026.', action: 'לגבות ולמחוק את האשכול' },
    { id: 'F-1004', rule: 'SAAS_TIER_OVERKILL', cat: 'saas', kind: 'recurring', amount: 88000, conf: .78, status: 'open', owner: 'רון (DevOps)', vendor: 'Datadog',
      title: 'Datadog מאנדקס את כל לוגי ה-DEBUG', why: '61% מהלוגים המאונדקסים ברמת DEBUG, אף dashboard או monitor לא קורא אותם.', action: 'exclusion filter ל-DEBUG, לשמור ב-archive בלבד' },
    { id: 'F-1005', rule: 'AI_KEY_ORPHAN', cat: 'ai', kind: 'recurring', amount: 81600, conf: .93, status: 'open', owner: 'שי (CTO)', vendor: 'OpenAI',
      title: 'מפתח API של עובד שעזב ממשיך לצרוך', why: 'המפתח "dan-experiments" נוצר ע״י עובד שעזב ב-07/2026. cron יומי ממשיך, ~1,840$ בחודש.', action: 'לבטל את המפתח אחרי בדיקה שאין תלות בפרודקשן' },
    { id: 'F-1006', rule: 'CLOUD_DEV_ALWAYS_ON', cat: 'cloud', kind: 'recurring', amount: 63000, conf: .88, status: 'open', owner: 'רון (DevOps)', vendor: 'AWS',
      title: 'סביבות dev רצות לילות וסופי שבוע', why: '14 instances בסביבת dev עם CPU מתחת ל-3% בין 21:00 ל-07:00 ובשישי-שבת.', action: 'Instance Scheduler: כיבוי 21:00–07:00 ובסופ״ש' },
    { id: 'F-1007', rule: 'AI_NO_PROMPT_CACHE', cat: 'ai', kind: 'recurring', amount: 58000, conf: .82, status: 'open', owner: 'אורי (Data)', vendor: 'OpenAI',
      title: 'אותו system prompt נשלח 4.6M פעמים בלי caching', why: 'prefix זהה של 3,200 טוקן ב-92% מהקריאות של "support-copilot". 0% cached tokens.', action: 'להזיז את החלק הקבוע לתחילת הפרומפט ולהפעיל prompt caching' },
    { id: 'F-1008', rule: 'LICENSE_DUPLICATE_FUNC', cat: 'saas', kind: 'recurring', amount: 52000, conf: .80, status: 'open', owner: 'נועה (Ops)', vendor: 'Monday + Jira',
      title: 'שתי מערכות ניהול משימות: Jira ו-monday', why: 'Jira: 71 משתמשים (R&D). monday: 38 משתמשים (Sales, Marketing, CS). 12 משתמשים בשתיהן.', action: 'לאחד ל-Jira Work Management לצוותים העסקיים' },
    { id: 'F-1009', rule: 'AUTO_RENEWAL_JUMP', cat: 'saas', kind: 'recurring', amount: 47500, conf: .90, status: 'open', owner: 'מיכל (CFO)', vendor: 'HubSpot',
      title: 'HubSpot התחדש אוטומטית ב-34% יותר', why: 'חידוש 01/10/2026: מ-140,000 ₪ ל-187,500 ₪ לשנה, אותם 14 מושבים. אין הצעת מחיר בתיקייה.', action: 'לפנות למנהל הלקוח לפני תום 30 יום מהחידוש, לבקש מחיר קודם' },
    { id: 'F-1010', rule: 'CLOUD_EGRESS_SPIKE', cat: 'cloud', kind: 'recurring', amount: 44000, conf: .74, status: 'open', owner: 'רון (DevOps)', vendor: 'AWS',
      title: 'NAT Gateway: תעבורה פי 3 מאז אוגוסט', why: 'DataTransfer-Out דרך NAT קפץ מ-9TB ל-28TB בחודש. מקור: שירות ingest ששולף מ-S3 בלי VPC endpoint.', action: 'להוסיף S3 Gateway Endpoint (חינם)' },
    { id: 'F-1011', rule: 'LICENSE_UNUSED', cat: 'saas', kind: 'recurring', amount: 41000, conf: .87, status: 'open', owner: 'נועה (Ops)', vendor: 'Figma',
      title: 'Figma: 22 מושבי עורך, 9 פעילים', why: '13 מושבים בלי עריכה ב-90 יום. רובם צפייה בלבד, שזה חינם.', action: 'להוריד 13 מושבים ל-Viewer בחידוש' },
    { id: 'F-1012', rule: 'DUP_CROSS_CURRENCY', cat: 'ap', kind: 'recovery', amount: 38900, conf: .97, status: 'open', owner: 'יעל (Finance)', vendor: 'MongoDB',
      title: 'חשבונית MongoDB Atlas שולמה פעמיים: $ בכרטיס ו-₪ בהעברה', why: 'INV-ATL-88213, 10,450$ חויבו בכרטיס Cal ב-03/08/2026, ושוב 38,900 ₪ בהעברה בנקאית ב-11/08/2026.', action: 'לבקש מ-MongoDB זיכוי או קיזוז בחשבונית הבאה' },
    { id: 'F-1013', rule: 'CLOUD_ORPHAN_STORAGE', cat: 'cloud', kind: 'recurring', amount: 31200, conf: .92, status: 'fixed', owner: 'רון (DevOps)', vendor: 'AWS',
      title: '214 snapshots ו-38 דיסקים לא מחוברים', why: 'EBS volumes במצב available מעל 60 יום, snapshots של instances שנמחקו.', action: 'מחיקה אחרי lifecycle policy' },
    { id: 'F-1014', rule: 'PAYROLL_POST_TERMINATION', cat: 'payroll', kind: 'recovery', amount: 31500, conf: .96, status: 'in_progress', owner: 'יעל (Finance)', vendor: 'שכר',
      title: 'שכר אוקטובר שולם לעובד שסיים ב-30/09', why: 'עובד EMP-1047: תאריך סיום 30/09/2026 ב-HiBob, תלוש 10/2026 הופק ושולם.', action: 'לעצור, לבדוק מול HR, להסדיר החזר' },
    { id: 'F-1015', rule: 'LICENSE_DEPARTED', cat: 'saas', kind: 'recurring', amount: 28400, conf: .94, status: 'open', owner: 'נועה (Ops)', vendor: '6 כלים',
      title: '7 עובדים שעזבו עדיין תופסים מושבים ב-6 כלים', why: 'Slack, Google Workspace, GitHub, Notion, Zoom, 1Password. סיום העסקה לפי HiBob, המושב עדיין פעיל.', action: 'offboarding: לשחרר מושבים, להעביר בעלות על קבצים' },
    { id: 'F-1016', rule: 'FX_CARD_FEES', cat: 'finance', kind: 'recurring', amount: 27000, conf: .84, status: 'open', owner: 'מיכל (CFO)', vendor: 'Cal',
      title: 'עמלת המרה 2.5% על כל מנויי הדולר בכרטיס', why: '1.08M ₪ בשנה בחיובי USD בכרטיס Cal עם עמלת עסקה בחו״ל. יש לחברה חשבון דולרי.', action: 'להעביר ספקי USD גדולים לתשלום מהחשבון הדולרי' },
    { id: 'F-1017', rule: 'DUP_INVOICE_EXACT', cat: 'ap', kind: 'recovery', amount: 23400, conf: 1.0, status: 'open', owner: 'יעל (Finance)', vendor: 'שמיר-כהן עורכי דין',
      title: 'חשבונית 2026-0412 שולמה פעמיים', why: 'אותו מספר חשבונית, אותו סכום 23,400 ₪, שתי העברות בהפרש 9 ימים.', action: 'לבקש זיכוי מהמשרד' },
    { id: 'F-1018', rule: 'AI_SEAT_OVERLAP', cat: 'ai', kind: 'recurring', amount: 22300, conf: .76, status: 'open', owner: 'שי (CTO)', vendor: 'Cursor + Copilot',
      title: '31 מפתחים משלמים גם Cursor וגם GitHub Copilot', why: '31 משתמשים עם שימוש פעיל ב-Cursor ב-30 יום, ומושב Copilot Business בלי הצעות שהתקבלו.', action: 'לבחור כלי אחד לכל מפתח, לבטל 31 מושבי Copilot' },
    { id: 'F-1019', rule: 'PAYROLL_DUPLICATE_BANK', cat: 'payroll', kind: 'review', amount: 22000, conf: .70, status: 'open', owner: 'יעל (Finance)', vendor: 'שכר',
      title: 'שתי רשומות עובד עם אותו חשבון בנק', why: 'EMP-1033 ו-EMP-1088 מקבלים לאותו חשבון (hash זהה). ייתכן הסבר תקין, נדרשת בדיקה.', action: 'לבדוק עם HR. לא לפעול בלי אישור' },
    { id: 'F-1020', rule: 'INVOICE_NO_ALLOCATION', cat: 'finance', kind: 'recovery', amount: 19800, conf: .93, status: 'open', owner: 'יעל (Finance)', vendor: '6 ספקים',
      title: '6 חשבוניות מעל הסף בלי מספר הקצאה: מע״מ לא ניתן לקיזוז', why: 'חשבוניות מס מעל סף חובת מספר הקצאה של רשות המסים, בלי מספר. 18% מע״מ בסך 19,800 ₪.', action: 'לבקש מהספקים חשבונית מתוקנת עם מספר הקצאה' },
    { id: 'F-1021', rule: 'UTILITY_SPIKE', cat: 'office', kind: 'recurring', amount: 18000, conf: .72, status: 'open', owner: 'נועה (Ops)', vendor: 'חברת החשמל',
      title: 'חשבון החשמל קפץ ב-41% בלי שינוי בתפוסה', why: 'ספטמבר-אוקטובר 2026: 11,900 קוט״ש לעומת 8,400 בשנה שעברה. מיזוג חדר שרת פועל 24/7 מאז 07/2026.', action: 'לבדוק את מיזוג חדר השרת ולעבור לתעו״ז' },
    { id: 'F-1022', rule: 'DUP_CARD_AND_AP', cat: 'ap', kind: 'recovery', amount: 14200, conf: .91, status: 'open', owner: 'יעל (Finance)', vendor: 'Notion',
      title: 'Notion חויב בכרטיס וגם שולם בחשבונית', why: 'מנוי Business שנתי חויב בכרטיס ב-12/05/2026 וגם שולם בהעברה ע״פ חשבונית ב-20/05/2026.', action: 'לבקש החזר על אחד החיובים' },
    { id: 'F-1023', rule: 'CAR_LEASE_DEPARTED', cat: 'office', kind: 'recovery', amount: 11800, conf: .89, status: 'open', owner: 'נועה (Ops)', vendor: 'אלבר',
      title: 'ליסינג לרכב של עובד שעזב: חודשיים אחרי ההחזרה', why: 'הרכב הוחזר ב-31/07/2026, חיובי ליסינג 08 ו-09 עדיין שולמו.', action: 'לבקש זיכוי מחברת הליסינג' },
    { id: 'F-1024', rule: 'PHONE_LINE_DEPARTED', cat: 'telecom', kind: 'recurring', amount: 9600, conf: .95, status: 'open', owner: 'נועה (Ops)', vendor: 'פרטנר',
      title: '9 קווים סלולריים של עובדים שעזבו', why: '9 קווים בלי שיחות או גלישה 60 יום+, בעלים לא פעילים ב-HiBob. 89 ₪ לקו בחודש.', action: 'לנתק או להעביר לעובדים חדשים' },
    { id: 'F-1025', rule: 'PHONE_ROAMING', cat: 'telecom', kind: 'recurring', amount: 6300, conf: .68, status: 'reviewed_ok', owner: 'נועה (Ops)', vendor: 'פרטנר',
      title: 'חיובי נדידה בלי חבילת חו״ל', why: '4 קווים חויבו לפי שימוש בחו״ל במקום חבילה.', action: 'חבילת חו״ל קבועה לצוות המכירות' },
    { id: 'F-1026', rule: 'INVOICE_SPLITTING', cat: 'ap', kind: 'review', amount: 74000, conf: .64, status: 'open', owner: 'מיכל (CFO)', vendor: 'קוד-פלוס ייעוץ',
      title: '4 חשבוניות מתחת לסף האישור תוך 25 יום', why: 'כל חשבונית 18,500 ₪, סף אישור סמנכ״ל 20,000 ₪, סה״כ 74,000 ₪ לאותו פרויקט.', action: 'לבדוק אם היה צריך הזמנת רכש אחת מאושרת' },
  ],

  categories: {
    ai: 'AI וטוקנים', cloud: 'ענן', saas: 'תוכנה ורישיונות', ap: 'ספקים וחשבוניות',
    telecom: 'תקשורת', office: 'משרד ותפעול', payroll: 'שכר', finance: 'עמלות ומיסים',
  },

  // top vendors, ₪/yr
  vendors: [
    { name: 'AWS', cat: 'cloud', amount: 5_340_000, trend: .18, owner: 'רון', renewal: null, source: 'AWS CUR' },
    { name: 'OpenAI', cat: 'ai', amount: 1_020_000, trend: .64, owner: 'אורי', renewal: null, source: 'OpenAI Usage API' },
    { name: 'Anthropic', cat: 'ai', amount: 690_000, trend: .91, owner: 'אורי', renewal: null, source: 'Anthropic Admin API' },
    { name: 'Datadog', cat: 'cloud', amount: 410_000, trend: .22, owner: 'רון', renewal: '03/2027', source: 'חשבונית' },
    { name: 'Salesforce', cat: 'saas', amount: 388_000, trend: .04, owner: 'דנה', renewal: '02/2027', source: 'חשבונית' },
    { name: 'Google Workspace', cat: 'saas', amount: 246_000, trend: .03, owner: 'נועה', renewal: '06/2027', source: 'Google Admin' },
    { name: 'HubSpot', cat: 'saas', amount: 187_500, trend: .34, owner: 'דנה', renewal: '10/2027', source: 'חשבונית' },
    { name: 'GitHub', cat: 'saas', amount: 172_000, trend: .09, owner: 'שי', renewal: '01/2027', source: 'GitHub API' },
    { name: 'Atlassian', cat: 'saas', amount: 121_000, trend: .06, owner: 'שי', renewal: '04/2027', source: 'חשבונית' },
    { name: 'Slack', cat: 'saas', amount: 118_000, trend: .02, owner: 'נועה', renewal: '11/2026', source: 'Slack Admin' },
    { name: 'Cursor', cat: 'ai', amount: 99_000, trend: .55, owner: 'שי', renewal: '12/2026', source: 'כרטיס Cal' },
    { name: 'MongoDB Atlas', cat: 'cloud', amount: 182_000, trend: .12, owner: 'רון', renewal: null, source: 'חשבונית' },
    { name: 'Figma', cat: 'saas', amount: 69_000, trend: 0, owner: 'נועה', renewal: '05/2027', source: 'כרטיס Cal' },
    { name: 'monday.com', cat: 'saas', amount: 52_000, trend: .1, owner: 'דנה', renewal: '03/2027', source: 'כרטיס Cal' },
    { name: 'חברת החשמל', cat: 'office', amount: 112_000, trend: .41, owner: 'נועה', renewal: null, source: 'חשבון חודשי' },
    { name: 'פרטנר עסקים', cat: 'telecom', amount: 118_000, trend: .05, owner: 'נועה', renewal: '08/2027', source: 'חשבונית' },
    { name: 'אלבר ליסינג', cat: 'office', amount: 486_000, trend: .03, owner: 'נועה', renewal: null, source: 'חשבונית' },
    { name: 'שכירות משרד — מגדלי הים', cat: 'office', amount: 1_380_000, trend: .04, owner: 'מיכל', renewal: '12/2028', source: 'חוזה' },
  ],

  renewals: [
    { vendor: 'Slack', date: '15/11/2026', amount: 118000, seatsPaid: 112, seatsUsed: 97, autoRenew: true },
    { vendor: 'Cursor', date: '01/12/2026', amount: 99000, seatsPaid: 55, seatsUsed: 49, autoRenew: true },
    { vendor: 'GitHub Enterprise', date: '10/01/2027', amount: 172000, seatsPaid: 70, seatsUsed: 63, autoRenew: true },
    { vendor: 'Salesforce', date: '01/02/2027', amount: 388000, seatsPaid: 18, seatsUsed: 15, autoRenew: false },
    { vendor: 'Datadog', date: '01/03/2027', amount: 410000, seatsPaid: null, seatsUsed: null, autoRenew: true },
  ],

  ai: {
    monthlyUsd: 50800, models: [
      { name: 'claude-opus (Anthropic)', share: .34 }, { name: 'gpt-5 (OpenAI)', share: .27 },
      { name: 'claude-haiku (Anthropic)', share: .09 }, { name: 'gpt-5-mini (OpenAI)', share: .14 },
      { name: 'text-embedding-3-large', share: .06 }, { name: 'אחר', share: .10 },
    ],
    projects: [
      { name: 'support-copilot', team: 'Product', usd: 17200, cachedPct: 0 },
      { name: 'ticket-classifier', team: 'Data', usd: 15900, cachedPct: 12 },
      { name: 'search-rerank', team: 'R&D', usd: 7400, cachedPct: 61 },
      { name: 'dan-experiments', team: '— עובד שעזב', usd: 1840, cachedPct: 0 },
      { name: 'eval-harness', team: 'R&D', usd: 5100, cachedPct: 44 },
      { name: 'sales-email-drafts', team: 'Sales', usd: 3360, cachedPct: 8 },
    ],
  },

  integrations: [
    { id: 'google', name: 'Google Workspace', group: 'זהות ומשתמשים', status: 'connected', synced: 'לפני 12 דק׳' },
    { id: 'hibob', name: 'HiBob', group: 'זהות ומשתמשים', status: 'connected', synced: 'לפני שעה' },
    { id: 'okta', name: 'Okta', group: 'זהות ומשתמשים', status: 'available' },
    { id: 'priority', name: 'Priority ERP', group: 'הנהלת חשבונות', status: 'connected', synced: 'לפני 3 שעות' },
    { id: 'hashavshevet', name: 'חשבשבת', group: 'הנהלת חשבונות', status: 'available' },
    { id: 'sap', name: 'SAP Business One', group: 'הנהלת חשבונות', status: 'available' },
    { id: 'aws', name: 'AWS (CUR 2.0)', group: 'ענן', status: 'connected', synced: 'לפני 40 דק׳' },
    { id: 'gcp', name: 'Google Cloud Billing', group: 'ענן', status: 'available' },
    { id: 'openai', name: 'OpenAI', group: 'AI', status: 'connected', synced: 'לפני 8 דק׳' },
    { id: 'anthropic', name: 'Anthropic', group: 'AI', status: 'connected', synced: 'לפני 8 דק׳' },
    { id: 'cal', name: 'כרטיס אשראי Cal Business', group: 'בנק ואשראי', status: 'connected', synced: 'אתמול' },
    { id: 'leumi', name: 'בנק לאומי (בנקאות פתוחה)', group: 'בנק ואשראי', status: 'error', synced: 'נכשל: ההרשאה פגה' },
    { id: 'gmail', name: 'Gmail — תיבת חשבוניות', group: 'קבלות', status: 'connected', synced: 'לפני 5 דק׳' },
    { id: 'slack', name: 'Slack', group: 'פעולה והתראות', status: 'connected', synced: 'פעיל' },
    { id: 'jira', name: 'Jira', group: 'פעולה והתראות', status: 'connected', synced: 'פעיל' },
    { id: 'github', name: 'GitHub', group: 'כלי פיתוח', status: 'connected', synced: 'לפני שעה' },
    { id: 'datadog', name: 'Datadog', group: 'כלי פיתוח', status: 'available' },
    { id: 'mcp', name: 'MCP Server', group: 'סוכנים', status: 'connected', synced: '3 לקוחות מחוברים' },
  ],
};

// helpers
window.ils = (n) => '₪' + Math.round(n).toLocaleString('en-US');
window.ilsK = (n) => n >= 1e6 ? '₪' + (n / 1e6).toFixed(n >= 1e7 ? 0 : 1) + 'M' : n >= 1e3 ? '₪' + Math.round(n / 1e3) + 'K' : '₪' + n;
