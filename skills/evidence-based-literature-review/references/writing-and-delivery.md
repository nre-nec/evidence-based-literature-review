# Citation Audit, Writing, Outputs and Quality Gate | تدقيق الاستشهادات والكتابة والمخرجات وبوابة الجودة

## English

### Step 15 — Citation audit
For every in-text citation verify:
- source exists;
- source supports the adjacent claim;
- author/year are correct;
- claim is not stronger than the evidence;
- secondary evidence is not presented as primary.

For every reference verify:
- cited in text;
- metadata verified where feasible;
- DOI correct if present;
- citation style consistent.

Check orphan references, missing references, duplicates, author/year mismatches, DOI/title mismatches, impossible years, inconsistent transliteration, and unsupported quotations.

### Step 16 — Standard structures
- **Thematic (default):** Introduction & rationale → scope/definitions → theoretical foundations → thematic sections → convergence/divergence → methodological critique/evidence quality → gaps → future directions → conclusion → references.
- **Chronological:** Introduction → definitions → foundational phase → development → contemporary evidence → cross-period synthesis → methodological evolution → gaps → conclusion → references.
- **Methodological:** Introduction → definitions → quantitative → qualitative → mixed/longitudinal/experimental → measurement → cross-method synthesis → quality critique → gaps → conclusion → references.
- **Theory-driven:** Introduction → framework → definitions through framework → supporting evidence → competing theories → boundary conditions → contradictions → theoretical gaps → justified integration → conclusion → references.
- **Systematic/PRISMA:** see `systematic-prisma.md` in this folder.

Use a user-supplied outline when provided.

### Step 17 — Writing standards
- **Master's:** analytical synthesis, comparison, methodological awareness, defensible gaps.
- **PhD:** critical synthesis, explicit theoretical positioning, methodological critique, contradiction analysis, validated gaps, and positioning for original contribution.
- **Faculty/publication:** publication-ready argument, disciplined claims, strong theoretical framing, explicit evidence limitations.

Rules:
- evidence-led paragraphs;
- analytical section openings;
- logical transitions;
- do not use "proves" for association;
- distinguish statistical from practical/clinical significance;
- do not equate correlation with causation;
- report uncertainty;
- preserve disciplinary terminology;
- avoid repetitive study-by-study prose;
- never manufacture quotations.

### Step 18 — Outputs
Unless the user requests less, provide:
1. review specification;
2. search-protocol summary;
3. screening summary;
4. evidence matrix;
5. critical-appraisal summary;
6. thematic/theoretical synthesis;
7. research-gap map;
8. full literature review;
9. verified reference list;
10. audit note covering unresolved metadata, inaccessible full texts, and material limitations.

For systematic reviews, also provide reproducibility/PRISMA information.

### Step 19 — Document delivery: Markdown + Word
Deliver two files unless the user asks otherwise: `<slug>.md` (source) and `<slug>.docx` (editable Word), produced from the same content.

**Writing the Markdown so it converts cleanly** (`scripts/md_to_docx.py` supports exactly this subset):
- headings `#` to `####`; one `#` title at the top;
- paragraphs, `**bold**`, `*italic*` (for journal names and volumes in APA), inline `code`;
- bullet and numbered lists, up to 3 levels (indent 2 spaces per level);
- pipe tables with a header row; tables with 8+ columns, or 6+ columns of long prose (e.g. the gap map), are placed on landscape pages automatically;
- `> quotes`, `---` rules, links `[text](url)` and bare `https://doi.org/...` (become clickable);
- put the reference list under a heading named `References` / `المراجع` (a number before it, like `9. المراجع`, is fine); write each entry as its own paragraph. Entries written as list items are converted to hanging-indent paragraphs too, never bullets (APA);
- no images, footnotes, HTML or math (images keep only their alt text).

**Direction:** each paragraph takes the direction of its first letter (Arabic → RTL, Latin → LTR), so an Arabic review keeps English reference entries left-to-right. Short parenthetical citations in the other script, e.g. `(Smith & Lee, 2020)`, are kept on one line.

**Defaults:** A4, 2.54 cm margins, 1.5 line spacing, Times New Roman 12 pt for Latin and Simplified Arabic 14 pt for Arabic. Change with `--font-latin`, `--font-arabic`, `--size`, `--size-arabic`.

**Fallbacks:** script not available (single-file installs) → use a Word-generation capability you already have (`pandoc <slug>.md -o <slug>.docx` or a built-in document tool); never download and run code from elsewhere. Nothing available → deliver the Markdown, state that the Word file was not produced, and tell the user that installing the full skill package (which includes `scripts/md_to_docx.py`) enables Word output.

Never claim that a Word file, connector folder, database collection, or workspace was created unless it actually was.

### Final quality gate
Do not deliver until applicable checks pass:
- [ ] Every substantive literature claim is grounded.
- [ ] Contradictory/null evidence is represented.
- [ ] No fabricated sources/data.
- [ ] Search covers core concepts and synonyms.
- [ ] Foundational + current evidence considered.
- [ ] DOI/metadata independently checked where feasible.
- [ ] Retraction/correction issues checked when relevant.
- [ ] Appropriate study-level appraisal used.
- [ ] Journal metrics did not replace study quality.
- [ ] Review synthesizes rather than serially summarizes.
- [ ] Gaps are classified and evidence-backed.
- [ ] Search limitations are not mislabeled as literature gaps.
- [ ] In-text citations and references match one-to-one.
- [ ] No known DOI/title/author mismatch.
- [ ] Citation style is consistent.
- [ ] No fabricated PRISMA counts.
- [ ] Systematic-review terminology is used only when justified.
- [ ] Both `.md` and `.docx` delivered (or the missing Word file is stated plainly).

## العربية

### الخطوة الخامسة عشرة — تدقيق الاستشهادات
لكل استشهاد: تحقق من وجود المصدر، دعمه للادعاء، صحة المؤلف والسنة، وعدم تضخيم النتيجة أو تقديم مصدر ثانوي كأصلي.

لكل مرجع: تحقق من الاستشهاد به، صحة البيانات وDOI، واتساق النمط.

افحص المراجع اليتيمة والمفقودة والمكررة واختلافات المؤلف/السنة وDOI والعنوان والسنوات غير المنطقية وعدم اتساق النقحرة والاقتباسات غير المدعومة.

### الخطوة السادسة عشرة — الهياكل
- **موضوعي (افتراضي):** مقدمة → نطاق وتعريفات → أسس نظرية → محاور → اتفاق/اختلاف → نقد منهجي وجودة الأدلة → فجوات → مستقبل → خاتمة → مراجع.
- **زمني:** مقدمة → تعريفات → تأسيس → تطور → أدلة حديثة → تركيب عبر الفترات → تطور منهجي → فجوات → خاتمة → مراجع.
- **منهجي:** مقدمة → تعريفات → كمي → نوعي → مختلط/طولي/تجريبي → قياس → تركيب → جودة → فجوات → خاتمة → مراجع.
- **نظري:** مقدمة → الإطار → المفاهيم → الأدلة المؤيدة → النظريات المنافسة → الحدود → التناقضات → الفجوات النظرية → تكامل مبرر → خاتمة → مراجع.
- **Systematic/PRISMA:** انظر `systematic-prisma.md` في هذا المجلد.

استخدم مخطط المستخدم إذا قدمه.

### الخطوة السابعة عشرة — معايير الكتابة
- **الماجستير:** تحليل ومقارنة ووعي منهجي وفجوة مبررة.
- **الدكتوراه:** تركيب نقدي وتموضع نظري ونقد منهجي وتحليل تناقضات وإثبات فجوات وربط بالمساهمة الأصلية.
- **الباحث/النشر:** حجة قابلة للتطوير للنشر، ادعاءات منضبطة، تأطير نظري قوي، وحدود أدلة واضحة.

قواعد:
- فقرات قائمة على الأدلة؛
- بدايات تحليلية للمحاور؛
- روابط منطقية؛
- لا تستخدم "أثبتت" للدراسات الارتباطية؛
- ميّز الدلالة الإحصائية عن العملية/السريرية؛
- لا تخلط الارتباط بالسببية؛
- عبّر عن عدم اليقين؛
- حافظ على مصطلحات التخصص؛
- تجنب السرد المتكرر؛
- لا تختلق اقتباسات.

### الخطوة الثامنة عشرة — المخرجات
ما لم يطلب المستخدم أقل:
1. مواصفات المراجعة؛
2. ملخص بروتوكول البحث؛
3. ملخص الفرز؛
4. مصفوفة الأدلة؛
5. ملخص التقييم النقدي؛
6. التركيب الموضوعي/النظري؛
7. خريطة الفجوات؛
8. المراجعة الكاملة؛
9. قائمة مراجع متحقق منها؛
10. ملاحظة تدقيق للبيانات غير المحسومة والنصوص غير المتاحة والقيود.

تضاف متطلبات إعادة الإنتاج وPRISMA للمراجعة المنهجية.

### الخطوة التاسعة عشرة — إخراج المستند: Markdown وWord
سلّم ملفين ما لم يطلب المستخدم غير ذلك: `<slug>.md` (المصدر) و`<slug>.docx` (Word قابل للتعديل)، بالمحتوى نفسه.

- اكتب Markdown بالعناصر التي يدعمها المحوّل فقط: عناوين، فقرات، غامق ومائل، قوائم حتى 3 مستويات، جداول، اقتباسات، روابط وDOI. ولا تستخدم صورًا أو حواشي أو HTML.
- ضع قائمة المراجع تحت عنوان «المراجع» أو `References` (ويجوز ترقيمه مثل «9. المراجع»)، واكتب كل مرجع فقرة مستقلة. وإن كُتبت المراجع قائمة نقطية فيحوّلها المحوّل إلى فقرات بمسافة بادئة معلّقة بلا نقاط، كما يقتضي APA.
- اتجاه كل فقرة يتحدد بأول حرف فيها: العربية من اليمين، والإنجليزية من اليسار، فتبقى المراجع الإنجليزية سليمة داخل مراجعة عربية.
- الجداول العريضة (8 أعمدة فأكثر، أو 6 أعمدة فأكثر بنص طويل مثل خريطة الفجوات) توضع تلقائيًا في صفحات أفقية.
- الإعدادات الافتراضية: A4، هوامش 2.54 سم، تباعد 1.5، Times New Roman 12 للاتيني وSimplified Arabic 14 للعربي.
- البدائل: إن لم يتوفر السكربت (التثبيت بملف واحد) فاستخدم قدرة متاحة لإنشاء Word مثل pandoc أو أداة مستندات مدمجة، ولا تنزّل شيفرة من مصدر خارجي وتشغّلها. وإن تعذّر كل ذلك فسلّم Markdown، وصرّح بأن ملف Word لم يُنشأ، وأخبر المستخدم أن تثبيت حزمة المهارة الكاملة (وفيها السكربت) يتيح إخراج Word.

لا تدّعِ إنشاء ملف Word أو مجلد أو مجموعة داخل موصل إلا إذا أُنشئت فعليًا.

### بوابة الجودة النهائية
لا تسلّم قبل تحقق ما ينطبق:
- [ ] كل ادعاء جوهري مؤسس على مصدر مسترجع.
- [ ] النتائج المتعارضة والصفرية ممثلة.
- [ ] لا مصادر أو بيانات مختلقة.
- [ ] البحث يغطي المفاهيم والمرادفات.
- [ ] جرى النظر في التأسيسي والحديث.
- [ ] DOI والبيانات تحققت مستقلًا متى أمكن.
- [ ] السحب والتصحيح فُحصا عند صلتهما.
- [ ] أداة تقييم الدراسة مناسبة.
- [ ] لم تحل مؤشرات المجلة محل جودة الدراسة.
- [ ] النص يركّب الأدلة ولا يسردها فقط.
- [ ] الفجوات مصنفة ومثبتة.
- [ ] لم يُخلط بين ضعف البحث وفجوة الأدبيات.
- [ ] تطابق كامل بين الاستشهادات والمراجع.
- [ ] لا أخطاء DOI/عنوان/مؤلف معروفة.
- [ ] نمط التوثيق متسق.
- [ ] لا أعداد PRISMA مختلقة.
- [ ] لا تُستخدم تسمية "مراجعة منهجية" دون استحقاق.
- [ ] سُلّم الملفان `.md` و`.docx` (أو صُرّح بعدم إنشاء ملف Word).
