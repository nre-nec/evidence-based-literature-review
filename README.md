# Evidence-Based Literature Review Skill | مهارة المراجعة الأدبية القائمة على الأدلة

<!-- foundry:install:start -->
> **AI agents / وكلاء الذكاء الاصطناعي:** to install, read [INSTALL.md](https://raw.githubusercontent.com/nre-nec/evidence-based-literature-review/main/INSTALL.md) and follow the path for your environment.

## Install | التثبيت

**Easiest | الأسهل:** give this repository's link to your AI tool and ask it to install the skill. It will read [INSTALL.md](INSTALL.md).
أعطِ رابط هذا المستودع لأداة الذكاء الاصطناعي التي تستخدمها واطلب منها تثبيت المهارة، وستتبع ملف INSTALL.md.

| Your tool | What to do |
|---|---|
| Claude Code | Ask it to install from this link, or copy `skills/evidence-based-literature-review/` to `~/.claude/skills/` |
| Claude.ai | Download the zip below and upload it in Settings → Skills (if available on your plan) |
| ChatGPT / Gemini / others | Add the single-file text to a custom GPT, Gem, project or custom instructions |
| Your own app / API | Use the single-file text as the system prompt |

- `evidence-based-literature-review`: [zip](https://raw.githubusercontent.com/nre-nec/evidence-based-literature-review/main/install/evidence-based-literature-review.zip) · [single file](https://raw.githubusercontent.com/nre-nec/evidence-based-literature-review/main/install/evidence-based-literature-review.md)
<!-- foundry:install:end -->

A connector-agnostic, bilingual (Arabic/English) AI skill for producing **traceable, verified, critically appraised** academic literature reviews: narrative, critical, integrative, scoping, or genuinely systematic/PRISMA-aligned.

مهارة ذكاء اصطناعي ثنائية اللغة (عربي/إنجليزي) لإعداد مراجعات أدبية أكاديمية **قابلة للتتبع والتحقق وخاضعة للتقييم النقدي**، ولا ترتبط بموصل أو منصة محددة.

> **Protocol first, tools second | المنهج أولًا، والأداة ثانيًا**

## What it does | ماذا تفعل

**Define → Search → Deduplicate → Screen → Verify → Appraise → Extract → Code → Synthesize → Identify gaps → Audit citations → Report**

- Builds a search model and a layered search (broad, combinatorial, deep, citation chaining, saturation check).
- Verifies DOI and bibliographic metadata independently against a source hierarchy.
- Appraises each study with a design-appropriate tool (RoB 2, ROBINS-I, JBI, CASP, AMSTAR 2, QUADAS-2, NOS, GRADE).
- Builds an evidence matrix before drafting, synthesizes analytically, and classifies gaps using a 12-type taxonomy.
- Audits citations and refuses to fabricate sources, statistics, or PRISMA counts.
- Delivers **two files**: the review as Markdown and as an editable **Word (.docx)** file, with correct Arabic RTL / English LTR layout, tables (wide evidence matrices on landscape pages), lists, links and hanging-indent references. The converter (`scripts/md_to_docx.py`) needs only Python, no installs.

- تبني نموذج بحث وبحثًا متعدد الطبقات، وتتحقق من DOI والبيانات الببليوجرافية من مصادر مستقلة.
- تقيّم كل دراسة بأداة مناسبة لتصميمها، وتبني مصفوفة أدلة قبل الكتابة، وتصنّف الفجوات البحثية في 12 نوعًا.
- تدقق الاستشهادات، ولا تختلق مراجع أو إحصاءات أو أعداد PRISMA.
- تسلّم **ملفين**: المراجعة بصيغة Markdown، ونسخة **Word قابلة للتعديل** باتجاه صحيح للعربية والإنجليزية.

## Structure | الهيكل

```text
skills/evidence-based-literature-review/
├── SKILL.md                 # entry point (bilingual procedure and rules)
├── metadata.json            # name, description, triggers, reference index
├── scripts/md_to_docx.py    # Markdown -> editable Word, standard-library Python
├── references/
│   ├── integrity-rules.md
│   ├── tool-routing.md
│   ├── review-specification.md
│   ├── search-and-screening.md
│   ├── verification-and-appraisal.md
│   ├── synthesis-and-gaps.md
│   ├── systematic-prisma.md
│   └── writing-and-delivery.md
└── tests/                   # trigger test prompts + converter fixture
INSTALL.md                   # install guide for AI agents (generated)
install/                     # zip, single-file text, Cursor rule (generated)
```

## Verification status | حالة التحقق

| Check | Status |
|---|---|
| Structure validated with [skill-foundry](https://github.com/nre-nec/skill-foundry) `validate --strict` | Passed (2026-10-11) |
| Install from the repository link alone (fresh Claude Code agent, path A, sandbox home) | Passed (2026-10-11): installed files identical to source |
| Word output: `md_to_docx.py` on Arabic and English fixtures, opened in Microsoft Word 16 (Windows 11) | Passed (2026-10-11): RTL/LTR paragraphs, embedded citations in both directions, RTL table, lists, links, hanging references, landscape evidence matrix |
| Skill used in Cursor | Reported working by the user (2026-10-11), before the Word output was added |
| Trigger tests in `tests/triggers.json` run in a live environment | Not yet verified |
| Behaviour tested end-to-end on Claude Code / Claude.ai / other models | Not yet verified |

## License
MIT. See [LICENSE](LICENSE).
