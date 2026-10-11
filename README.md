# Evidence-Based Literature Review Skill | مهارة المراجعة الأدبية القائمة على الأدلة

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

- تبني نموذج بحث وبحثًا متعدد الطبقات، وتتحقق من DOI والبيانات الببليوجرافية من مصادر مستقلة.
- تقيّم كل دراسة بأداة مناسبة لتصميمها، وتبني مصفوفة أدلة قبل الكتابة، وتصنّف الفجوات البحثية في 12 نوعًا.
- تدقق الاستشهادات، ولا تختلق مراجع أو إحصاءات أو أعداد PRISMA.

## Structure | الهيكل

```text
skills/evidence-based-literature-review/
├── SKILL.md                 # entry point (bilingual procedure and rules)
├── metadata.json            # name, description, triggers, reference index
├── references/
│   ├── integrity-rules.md
│   ├── tool-routing.md
│   ├── review-specification.md
│   ├── search-and-screening.md
│   ├── verification-and-appraisal.md
│   ├── synthesis-and-gaps.md
│   ├── systematic-prisma.md
│   └── writing-and-delivery.md
└── tests/triggers.json      # manual trigger test prompts
```

## Install | التثبيت

### Claude Code
Copy the skill folder into your personal skills directory (`~/.claude/skills/`):

```bash
git clone https://github.com/nre-nec/evidence-based-literature-review.git
cp -r evidence-based-literature-review/skills/evidence-based-literature-review ~/.claude/skills/
```

On Windows (PowerShell):

```powershell
git clone https://github.com/nre-nec/evidence-based-literature-review.git
Copy-Item -Recurse "evidence-based-literature-review\skills\evidence-based-literature-review" "$env:USERPROFILE\.claude\skills\"
```

### Claude.ai / other models
Zip the `skills/evidence-based-literature-review` folder and upload it as a skill where supported, or paste `SKILL.md` plus the needed `references/` files as system instructions for any model.

## Verification status | حالة التحقق

| Check | Status |
|---|---|
| Structure validated with [skill-foundry](https://github.com/nre-nec/skill-foundry) `validate --strict` | Passed (2026-10-11) |
| Trigger tests in `tests/triggers.json` run in a live environment | Not yet verified |
| Behaviour tested end-to-end on Claude Code / Claude.ai / other models | Not yet verified |

## License
MIT. See [LICENSE](LICENSE).
