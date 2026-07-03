// In-memory "database" standing in for the future Django backend.
// Shape mirrors what the real API is expected to return.

let nextId = 7

export const notesStore = [
  {
    id: 1,
    title: 'Apple',
    subject: 'Apple',
    type: 'food',
    conditions: ['High cholesterol', 'Constipation', 'Type 2 diabetes'],
    summary:
      'Rich in soluble fiber (pectin) and polyphenols. Supports healthy cholesterol levels and digestion; low glycemic load makes it suitable for diabetic diets.',
    content:
      'Apples contain pectin, a soluble fiber shown to help lower LDL cholesterol. Their polyphenol content is associated with improved insulin sensitivity. The skin carries most of the fiber and antioxidants, so recommend eating unpeeled where tolerated. One medium apple (~95 kcal) makes a suitable snack for patients managing blood sugar.',
    source: 'pdf',
    createdAt: '2026-06-18T09:12:00.000Z',
  },
  {
    id: 2,
    title: 'Ginger',
    subject: 'Ginger',
    type: 'food',
    conditions: ['Nausea', 'Morning sickness', 'Inflammation', 'Indigestion'],
    summary:
      'Well-evidenced for nausea relief (including pregnancy-related) and mild anti-inflammatory effects. Typically taken as tea, capsule, or raw root.',
    content:
      'Ginger (Zingiber officinale) has consistent clinical support for reducing nausea and vomiting, including chemotherapy- and pregnancy-related cases, at doses around 1g/day. Gingerols are believed to contribute anti-inflammatory and mild analgesic effects. Caution in patients on anticoagulants due to a mild antiplatelet effect.',
    source: 'pdf',
    createdAt: '2026-06-20T14:30:00.000Z',
  },
  {
    id: 3,
    title: 'Turmeric',
    subject: 'Turmeric',
    type: 'food',
    conditions: ['Inflammation', 'Joint pain', 'Osteoarthritis'],
    summary:
      'Curcumin has anti-inflammatory properties comparable to some OTC options in mild-to-moderate joint pain; absorption improves markedly with black pepper (piperine).',
    content:
      'Curcumin, the active compound in turmeric, has demonstrated anti-inflammatory effects in several trials for osteoarthritis-related joint pain, with some studies showing benefit comparable to low-dose ibuprofen. Bioavailability is poor alone; pairing with black pepper (piperine) increases absorption significantly. Typical supplemental doses range 500-1000mg curcumin/day.',
    source: 'manual',
    createdAt: '2026-06-22T11:05:00.000Z',
  },
  {
    id: 4,
    title: 'Honey',
    subject: 'Honey',
    type: 'food',
    conditions: ['Sore throat', 'Cough', 'Wound healing'],
    summary:
      'Demonstrated to reduce cough frequency/severity, soothes sore throat, and has mild antibacterial properties useful in topical wound dressings.',
    content:
      'Honey has been shown in pediatric studies to reduce nocturnal cough frequency and severity comparably to some OTC cough suppressants. Its viscosity soothes throat irritation, and its low water activity plus hydrogen peroxide production give it mild antibacterial properties, supporting use in medical-grade wound dressings. Not recommended for children under 1 year due to botulism risk.',
    source: 'manual',
    createdAt: '2026-06-25T08:47:00.000Z',
  },
  {
    id: 5,
    title: 'Oats',
    subject: 'Oats',
    type: 'food',
    conditions: ['High cholesterol', 'Type 2 diabetes', 'Constipation'],
    summary:
      'Beta-glucan fiber lowers LDL cholesterol and blunts post-meal blood sugar spikes; a reliable staple recommendation for cardiometabolic patients.',
    content:
      'Oats are a strong source of beta-glucan, a soluble fiber with well-documented LDL-cholesterol-lowering effects (~5-10% reduction with regular intake). Beta-glucan also slows gastric emptying, blunting post-prandial glucose spikes, which benefits patients managing type 2 diabetes. Recommend plain/rolled oats over instant flavored varieties to avoid added sugar.',
    source: 'pdf',
    createdAt: '2026-06-27T16:20:00.000Z',
  },
  {
    id: 6,
    title: 'Fatty Fish (Salmon, Mackerel, Sardines)',
    subject: 'Fatty fish',
    type: 'food',
    conditions: ['High cholesterol', 'Hypertension', 'Inflammation', 'Depression'],
    summary:
      'Omega-3s (EPA/DHA) support cardiovascular health, help lower triglycerides and blood pressure, and are linked to reduced inflammatory markers.',
    content:
      'Fatty fish are a primary dietary source of long-chain omega-3 fatty acids (EPA and DHA), which reduce triglycerides, modestly lower blood pressure, and are associated with reduced systemic inflammation. Observational and some interventional evidence also links regular intake to improved mood outcomes in mild-to-moderate depression. Recommend 2 servings/week per general cardiology guidance.',
    source: 'manual',
    createdAt: '2026-06-29T10:00:00.000Z',
  },
]

export function generateId() {
  return nextId++
}
