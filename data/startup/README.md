# data/startup: נתוני הוצאות סינתטיים של טכנוסיס בע״מ

> **כל הנתונים סינתטיים.** החברה, העובדים, החשבוניות, חשבונות הבנק, מספרי הטלפון והסכומים בדויים לחלוטין.
> שמות ספקי הענן/SaaS/AI הם שירותים אמיתיים כדי שהדוגמה תהיה מוחשית, אבל כל עסקה וסכום מומצאים.
> משרדי עורכי הדין, רואי החשבון והייעוץ (שמיר-כהן, ברגר-אלון, קוד-פלוס וכו׳) בדויים. אין כאן מידע אישי אמיתי.

**החברה:** טכנוסיס בע״מ, סטארט-אפ Series B בתל אביב. 112 עובדים היום, 23 עזבו בתקופה.
**תקופה:** 01/11/2024 עד 31/10/2026 (24 חודשים). **שער:** USD/ILS סביב 3.70 עם תנודה קלה; כל סכום "שנתי" בממצאים מחושב לפי 3.70.
**מע״מ:** 17% עד 31/12/2024, 18% מ-01/01/2025. **מספר הקצאה:** חובה מעל ₪25,000 (2024), ₪20,000 (2025), ₪10,000 (01–05/2026), ₪5,000 (מ-06/2026), לפני מע״מ. ספקים זרים פטורים.
**מקור אמת:** `design/v2/assets/demo-data.js`. 26 הממצאים F-1001..F-1026 נשתלו בנתונים בסכומים שלו (±3%).

## הרצה

```bash
python scripts/generate_startup_data.py          # כותב את כל data/startup (דטרמיניסטי, seed 42)
python scripts/generate_startup_data.py --no-png # בלי צילומי מסך של הקבלות
python scripts/check_startup_data.py             # מחשב מחדש כל ממצא מהשורות הגולמיות ובודק ±3%
```

## קבצים

כל ה-CSV ב-UTF-8 עם BOM (אקסל מציג עברית), כותרות באנגלית snake_case.

| קובץ | מחקה את הפורמט של | תוכן | שורות | גודל |
|---|---|---|---:|---:|
| `employees.csv` | ייצוא עובדים בסגנון HiBob | עובד לשורה כולל 23 שעזבו. שם פרטי בלבד, חשבון בנק כ-hash | 135 | 16 KB |
| `payroll.csv` | תלוש שכר ישראלי (רכיבים כמו בחילן) | עובד × חודש: ברוטו, הפרשות מעביד 6.5%/8.33%/7.5%, ב״ל מדורג, מס, נטו | 2,587 | 373 KB |
| `vendors.csv` | כרטיס ספק ב-Priority ERP | 140 ספקים: ענן/SaaS/AI אמיתיים + ספקים מקומיים. משרדי עו״ד/רו״ח/ייעוץ בדויים | 140 | 10 KB |
| `invoices.csv` | כותרות חשבוניות ספקים (AP), שדות חשבונית מס | מספר הקצאה, מע״מ 17%/18%, הזמנת רכש, סטטוס ותשלום | 1,608 | 258 KB |
| `invoice_lines.csv` | שורות חשבונית | AWS לפי שירות, Datadog לפי רכיב, פרטנר לפי קו, אלבר/פז לפי רכב | 5,950 | 398 KB |
| `bank_transactions.csv` | דף חשבון עסקי בסגנון בנק לאומי (ILS + USD) | תאריך, תאריך ערך, תיאור, אסמכתא, חובה, זכות, יתרה | 2,226 | 271 KB |
| `card_transactions.csv` | פירוט כרטיס Cal Business | סכום מקורי, מטבע, חיוב בש״ח, עמלת עסקה בחו״ל 2.5%, מועד חיוב | 6,125 | 718 KB |
| `aws_cur.csv` | AWS Cost & Usage Report 2.0, יומי | line_item_*, pricing_term, תגיות env/team/owner/cluster | 59,926 | 13,451 KB |
| `ai_usage.csv` | OpenAI usage export + Anthropic Console usage, יומי | פרויקט, מפתח API, בעלים, מודל, טוקנים (כולל cached), עלות $ משוערת | 47,341 | 4,730 KB |
| `saas_seats.csv` | תמונת מצב חודשית של מושבי SaaS (כמו Torii/Productiv) | כלי × משתמש: סוג מושב, מחיר, פעילות אחרונה, פעולות ב-30 יום | 26,298 | 1,557 KB |
| `telecom.csv` | חשבון פרטנר עסקים, פירוט לפי קו | מספר מוסתר 05X-XXX-1234, מסלול, דקות, GB, נדידה | 2,657 | 188 KB |
| `utilities.csv` | חשבון חשמל חודשי של חברת החשמל | קוט״ש, תעריף כללי, תשלום קבוע, מע״מ | 24 | 3 KB |
| `car_leases.csv` | חיובי ליסינג אלבר + כרטיס דלק פז | רכב × חודש: לוחית מוסתרת, דגם, ליסינג, דלק, ק״מ, תאריך החזרה | 246 | 15 KB |
| **סה״כ** | | | **155,263** | |

`ground_truth.json`: רשימת הממצאים שנשתלו (מזהה, כלל, קבצים ומפתחות שורה שמוכיחים, סכום צפוי) ורשימת מלכודות הרעש.

## 26 הממצאים שנשתלו

| ממצא | כלל | סכום DEMO | סוג | קבצים | איך מזהים ואיך מחושב הסכום |
|---|---|---:|---|---|---|
| F-1001 | `AI_MODEL_OVERKILL` | ₪214,000 | recurring | ai_usage.csv | classification route on the flagship model, avg 380 output tokens. amount = Oct-2026 cost × 0.80 (haiku-4-5 is 1/5 the price) × 12 × 3.70. |
| F-1002 | `CLOUD_NO_COMMITMENT` | ₪172,000 | recurring | aws_cur.csv | prod EC2 BoxUsage with pricing_term=OnDemand (9 nodes, flat for 24 months) ≈ 68% of all EC2 compute. amount = last-12m prod On-Demand compute USD × 0.75 (cover 75% of base) × 0.28 (1y no-upfront Compute SP discount) × 3.70. |
| F-1003 | `CLOUD_ZOMBIE` | ₪96,000 | recurring | aws_cur.csv | all resources tagged cluster=staging-old; LCUUsage usage_amount = 0 from 2026-09-15. amount = avg daily cost 15/09–31/10 × 365 × 3.70. |
| F-1004 | `SAAS_TIER_OVERKILL` | ₪88,000 | recurring | invoices.csv, invoice_lines.csv | 61% of indexed log spend is DEBUG level. amount = last-12m 'status:debug' invoice lines USD × 3.70. |
| F-1005 | `AI_KEY_ORPHAN` | ₪81,600 | recurring | ai_usage.csv, employees.csv | key owner EMP-1061 end_date 2026-07-14; daily cron continues at the same volume. amount = Oct-2026 cost × 12 × 3.70. |
| F-1006 | `CLOUD_DEV_ALWAYS_ON` | ₪63,000 | recurring | aws_cur.csv | 14 env=dev instances bill 24h every day incl. Fri/Sat. amount = last-12m dev BoxUsage USD × 98/168 off-hours share (21:00–07:00 Sun–Thu + weekend) × 3.70. |
| F-1007 | `AI_NO_PROMPT_CACHE` | ₪58,000 | recurring | ai_usage.csv | cached_input_tokens = 0 on every row. amount = last-12m requests × 0.92 (share with the shared 3,200-token prefix) × 3,200 × (1.25−0.125)$/1M × 3.70. |
| F-1008 | `LICENSE_DUPLICATE_FUNC` | ₪52,000 | recurring | saas_seats.csv, card_transactions.csv | Jira (R&D+Product) and monday.com (Sales/Marketing/CS + 8 Product) both in use, 12 users in both. amount = last-12m monday.com card spend (charged_ils). |
| F-1009 | `AUTO_RENEWAL_JUMP` | ₪47,500 | recurring | invoices.csv, vendors.csv | auto_renew=TRUE; renewal 01/10/2026 ₪187,500 vs ₪140,000 a year earlier, 14 seats both years. amount = difference. |
| F-1010 | `CLOUD_EGRESS_SPIKE` | ₪44,000 | recurring | aws_cur.csv | NatGateway-Bytes on the ingest NAT: 9,000 GB/month until 07/2026, 28,000 GB/month from 08/2026. amount = (avg monthly Aug–Oct 2026 − avg monthly Jan–Jul 2026) × 12 × 3.70. |
| F-1011 | `LICENSE_UNUSED` | ₪41,000 | recurring | saas_seats.csv | Oct-2026 snapshot: 22 Figma editor seats, 13 with last_active_date > 90 days and 0 actions. amount = 13 × seat_cost_usd_month × 12 × 3.70. |
| F-1012 | `DUP_CROSS_CURRENCY` | ₪38,900 | recovery | invoices.csv, card_transactions.csv, bank_transactions.csv | same Atlas invoice charged $10,450 on the Cal card (03/08/2026) and paid again ₪38,900 by bank transfer (11/08/2026). amount = the bank debit. |
| F-1013 | `CLOUD_ORPHAN_STORAGE` | ₪31,200 | recurring | aws_cur.csv | EBS volumes/snapshots of terminated instances. amount = Oct-2026 cost × 12 × 3.70. (DEMO status: fixed — rows kept so the evidence exists.) |
| F-1014 | `PAYROLL_POST_TERMINATION` | ₪31,500 | recovery | employees.csv, payroll.csv | end_date 2026-09-30, payslip period 2026-10 generated & paid (payment_date 2026-10-29). amount = total_employer_cost of that payslip. |
| F-1015 | `LICENSE_DEPARTED` | ₪28,400 | recurring | saas_seats.csv, employees.csv | Oct-2026 snapshot rows of 7 terminated employees in Slack, Google Workspace, GitHub, Notion, Zoom, 1Password. amount = Σ seat_cost_usd_month × 12 × 3.70. |
| F-1016 | `FX_CARD_FEES` | ₪27,000 | recurring | card_transactions.csv | ≈₪1.08M/yr of USD subscriptions on the Cal card, each with a 2.5% foreign-transaction fee, while a USD account exists. amount = last-12m Σ fx_fee_ils. |
| F-1017 | `DUP_INVOICE_EXACT` | ₪23,400 | recovery | invoices.csv, bank_transactions.csv | same vendor + invoice_number 2026-0412 + same total ₪23,400, two separate AP entries and two bank transfers 9–10 days apart. amount = one total. |
| F-1018 | `AI_SEAT_OVERLAP` | ₪22,300 | recurring | saas_seats.csv | Oct-2026: 31 users with Cursor actions_30d>0 and Copilot actions_30d=0. amount = Σ copilot seat_cost × 12 × 3.70. |
| F-1019 | `PAYROLL_DUPLICATE_BANK` | ₪22,000 | review | employees.csv, payroll.csv | two active employees share one bank_account_hash. amount = Oct-2026 net paid to the second record (EMP-1088). |
| F-1020 | `INVOICE_NO_ALLOCATION` | ₪19,800 | recovery | invoices.csv | Israeli tax invoices with amount_before_vat above the Tax Authority threshold for their issue_date and an empty allocation_number. VAT is not deductible. amount = Σ vat_amount. |
| F-1021 | `UTILITY_SPIKE` | ₪18,000 | recurring | utilities.csv | Sep–Oct 2026 11,900 kWh/month vs 8,400 a year earlier (+41%). amount = excess kWh × 2026 kwh_rate × 6 (annualize 2 months). |
| F-1022 | `DUP_CARD_AND_AP` | ₪14,200 | recovery | card_transactions.csv, invoices.csv | annual Notion renewal charged on card 12/05/2026 and the same invoice paid by bank transfer 20/05/2026. amount = card charged_ils. |
| F-1023 | `CAR_LEASE_DEPARTED` | ₪11,800 | recovery | car_leases.csv, employees.csv | car returned 2026-07-31 (returned_date) yet lease charged for 08 and 09/2026, km=0. amount = Σ monthly_fee after returned_date. |
| F-1024 | `PHONE_LINE_DEPARTED` | ₪9,600 | recurring | telecom.csv, employees.csv | 9 lines whose owner is terminated in HiBob, 0 minutes / 0 GB for 60+ days, still billed ₪89. amount = 9 × 89 × 12. |
| F-1025 | `PHONE_ROAMING` | ₪6,300 | recurring | telecom.csv | 4 lines on plan 'עסקי 89' (no abroad package) with per-use roaming_charges. amount = last-12m roaming_charges. (DEMO status: reviewed_ok) |
| F-1026 | `INVOICE_SPLITTING` | ₪74,000 | review | invoices.csv | 4 invoices of ₪18,500 pre-VAT from one vendor within 25 days, each just under the ₪20,000 VP-approval threshold, no PO. amount = sum pre-VAT. |


## מלכודות רעש (אסור שיסומנו)

| מלכודת | למה זה תקין |
|---|---|
| `cancelled_and_reissued_invoice` | 2025-1187 status=cancelled, reissued as 2025-1188 with a corrected amount; only one payment. Not a duplicate. |
| `card_refund` | Zoom Webinar add-on charged by mistake and refunded 4 days later (transaction_type=זיכוי). Net zero, not a duplicate. |
| `recurring_identical_saas_charges` | fixed-seat subscriptions bill the same amount every month on the same day — different months, not duplicates. |
| `departed_lines_disconnected` | properly offboarded lines stop billing — must not be flagged. |
| `seasonal_august_electricity` | August is the yearly peak (AC); Aug-2026 is +4% YoY like the rest of the year — seasonal, not a spike. |
| `car_returned_properly` | EMP-1029 left 2025-05-31; car returned and charges stopped the same month. |
| `departed_seats_released` | EMP-1092 left 2026-06-30; every seat disappears from the next snapshot (and 15 more departed employees behave the same). |
| `prorated_final_payslip` | EMP-1055 left 2026-10-15; the October payslip is prorated to 15 days — legitimate final pay. |
| `revoked_personal_api_keys` | personal dev keys of departed engineers stop on their end_date — revoked correctly. |
| `vendor_refund_credit` | event-production vendor refunded a cancelled date — a credit, not a payment. |

## מסמכים לדוגמה

12 קבלות וחשבוניות HTML שתואמות שורות בנתונים, עם סימן מים "SYNTHETIC · דוגמה" ובלי לוגואים אמיתיים (שם טקסטואלי בלבד), וצילום PNG ברוחב 900px לכל אחת:

- `receipts/receipt_aws_2026-10.html` + `receipt_aws_2026-10.png`
- `receipts/receipt_openai_2026-10.html` + `receipt_openai_2026-10.png`
- `receipts/receipt_anthropic_2026-10.html` + `receipt_anthropic_2026-10.png`
- `receipts/receipt_law_2026-0187.html` + `receipt_law_2026-0187.png`
- `receipts/receipt_partner_2026-10.html` + `receipt_partner_2026-10.png`
- `receipts/receipt_iec_2026-10.html` + `receipt_iec_2026-10.png`
- `receipts/receipt_albar_2026-09.html` + `receipt_albar_2026-09.png`
- `receipts/receipt_mongodb_INV-ATL-88213.html` + `receipt_mongodb_INV-ATL-88213.png`
- `receipts/receipt_hubspot_2026-10.html` + `receipt_hubspot_2026-10.png`
- `receipts/receipt_cal_2026-08.html` + `receipt_cal_2026-08.png`
- `receipts/receipt_payslip_EMP-1047_2026-10.html` + `receipt_payslip_EMP-1047_2026-10.png`
- `receipts/receipt_notion_2026-05.html` + `receipt_notion_2026-05.png`

## פישוטים ידועים

- מחירי הטוקנים ב-`ai_usage.csv` הם **מחירון ציבורי משוער** ל-1M טוקנים (gpt-5 $1.25/$10, claude-opus-4-5 $5/$25 וכו׳), לא חשבון אמיתי.
- תעריפי AWS ב-CUR משוערים (eu-central-1) וחלקם מכוילים כדי שהממצאים ייצאו בסכום של ה-DEMO. שורות Savings Plan מוצגות בעלות האפקטיבית, בלי שורת SavingsPlanRecurringFee נפרדת.
- התגיות ב-CUR שטוחות (`resource_tags_user_env`) כמו ב-CUR הוותיק, במקום עמודת המפה `resource_tags` של CUR 2.0.
- תעריף החשמל (כ-0.43 ₪ לקוט״ש לפני מע״מ) ותשלום הקיבולת הקבוע משוערים.
- מס הכנסה וביטוח לאומי בתלוש מחושבים בקירוב לפי מדרגות 2025 (2.25 נקודות זיכוי, בלי תקרות הפקדה). מספיק לסדר גודל של נטו.
- כמה פרטים בטקסט ה-DEMO לא מתיישבים עם המחירון ולכן הותאמו: ב-F-1001 יש כ-480 אלף קריאות בחודש (לא 2.1M) כדי שעלות מודל הדגל תתאים ל-₪214K; ב-F-1007 נספרו 4.73M קריאות ב-12 חודשים, 92% מהן עם ה-prefix. סכומי חלק מהספקים בטבלת ה-vendors של ה-DEMO (חשמל, monday) שונים מעט מהנתונים.
