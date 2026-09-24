# NEXIRA — Development Implementation Plan

NEXIRA is an AI-powered workflow that turns an incomplete product idea into a clear, launch-ready brand system. The product follows a staged approach that preserves context between stages rather than relying on a single giant prompt.

## 1. Overall Architecture

```text
                         NEXIRA
                           │
                           ▼
                  ┌─────────────────┐
                  │   React + Vite  │
                  │    Frontend     │
                  └────────┬────────┘
                           │
                       REST API
                           │
                           ▼
                  ┌─────────────────┐
                  │ Flask Backend   │
                  │ Workflow Engine │
                  └────────┬────────┘
                           │
              ┌────────────┼────────────┐
              ▼            ▼            ▼
          LLM API       MongoDB      Export
              │
              ▼
       AI WORKFLOW ENGINE
              │
     ┌────────┼─────────┐
     ▼        ▼         ▼
 Discover  Position   Shape
     │        │         │
     └────────┼─────────┘
              ▼
          Visualize
              │
              ▼
          Challenge
              │
              ▼
        Consistency
              │
              ▼
           Deliver
```

The key recommendation is a staged processing workflow where each stage produces structured JSON and passes context forward to the next stage.

---

## 2. Technology Stack

### Frontend

- React
- Vite
- React Router
- Axios
- Plain CSS

### Backend

- Python
- Flask
- REST API

### AI

- LLM API
- Structured JSON responses
- Prompt chaining

### Database

- MongoDB

### Export

- PDF / downloadable JSON

### Optional

- Image-generation API for visual concepts

The product should focus on prompt chaining, structured JSON, staged reasoning, and human review rather than overengineering the stack.

---

## 3. Folder Structure

```text
NEXIRA/
│
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   ├── pages/
│   │   ├── services/
│   │   ├── hooks/
│   │   └── App.jsx
│   │
│   └── package.json
│
├── backend/
│   ├── app.py
│   ├── routes/
│   ├── services/
│   │   ├── llm_service.py
│   │   ├── workflow.py
│   │   └── evaluator.py
│   │
│   ├── prompts/
│   │   ├── discover.txt
│   │   ├── position.txt
│   │   ├── shape.txt
│   │   ├── visualize.txt
│   │   ├── challenge.txt
│   │   ├── consistency.txt
│   │   └── launch.txt
│   │
│   ├── models/
│   └── requirements.txt
│
├── README.md
└── .env
```

---

## 4. Frontend Screens

### Screen 1 — Landing

```text
NEXIRA

From raw idea
to launch-ready brand.

[ Start Building ]
```

### Screen 2 — Idea Input

```text
Project / Product Idea

┌────────────────────────────────────────┐
│ Describe your idea...                  │
│                                        │
│                                        │
└────────────────────────────────────────┘

Target Audience
[ Optional ]

Industry
[ Optional ]

                    [ Build My Brand ]
```

The user may optionally provide audience and industry, since the AI should be able to make sense of incomplete ideas and uncover open questions.

---

## 5. Workflow Engine

The heart of NEXIRA is a workflow engine with staged AI reasoning:

```text
Idea
 ↓
Discover
 ↓
Position
 ↓
Shape
 ↓
Visualize
 ↓
Challenge
 ↓
Consistency
 ↓
Deliver
```

This directly avoids the one-prompt trap and ensures that each stage builds on the previous stage's output.

---

## 6. Stage 1 — DISCOVER

### Input

```json
{
  "idea": "...",
  "audience": "...",
  "industry": "..."
}
```

### AI task

Extract:

- Core problem
- Target users
- User needs
- Context
- Constraints
- Open questions

### JSON output

```json
{
  "core_problem": "",
  "target_users": [],
  "user_needs": [],
  "context": "",
  "constraints": [],
  "open_questions": []
}
```

### Frontend

Display:

```text
DISCOVER

🎯 Target Users
...

⚠ Core Problem
...

💡 User Needs
...

❓ Open Questions
...
```

---

## 7. Stage 2 — POSITION

The whole Discover output is passed into Position. The AI generates:

```json
{
  "category": "",
  "value_proposition": "",
  "differentiator": "",
  "competitive_angle": "",
  "positioning_statement": ""
}
```

This stage clarifies where the product sits in the market and why it is valuable.

---

## 8. Stage 3 — SHAPE

The identity is now established.

### Personality

```json
[
  {
    "trait": "Trustworthy",
    "reason": "..."
  },
  {
    "trait": "Energetic",
    "reason": "..."
  }
]
```

### Avoid

```json
[
  "Overly corporate",
  "Generic",
  "Childish"
]
```

### Naming

Instead of generating 20 random names, the system should generate naming territories and rationale.

```text
Territory A
Human-centered

Territory B
Technology-centered

Territory C
Purpose-centered
```

Then generate names under each territory.

This follows the requirement for naming directions with rationale and personality traits with justification.

---

## 9. Stage 4 — VISUALIZE

The brand strategy becomes a visual design brief.

```json
{
  "color_mood": [],
  "typography": "",
  "composition": "",
  "imagery": "",
  "symbol_direction": "",
  "visual_concepts_to_avoid": []
}
```

Display:

```text
VISUAL DIRECTION

Color Mood
● Modern
● Energetic
● Trustworthy

Typography
Modern geometric sans-serif

Imagery
...

Symbol Direction
...

Avoid
...
```

---

## 10. Stage 5 — CHALLENGE

This is one of NEXIRA's major differentiators.

The system uses a critic prompt to find:

- Clichés
- Generic ideas
- Contradictions
- Audience mismatch
- Weak naming
- Weak positioning
- Visual inconsistencies

Output:

```json
{
  "issues": [
    {
      "type": "Cliche",
      "severity": "medium",
      "description": "...",
      "alternative": "..."
    }
  ]
}
```

This aligns with the recommendation to challenge clichés, contradictions, bias, and audience mismatch.

---

## 11. Stage 6 — CONSISTENCY

Now the system checks whether all generated elements align.

Input:

```text
Positioning
+
Personality
+
Name
+
Tagline
+
Visual direction
+
Brand voice
```

Question:

> Does this feel like one coherent brand?

Output:

```json
{
  "checks": [
    {
      "element": "Name ↔ Positioning",
      "status": "PASS",
      "reason": "..."
    },
    {
      "element": "Visual ↔ Audience",
      "status": "WARNING",
      "reason": "..."
    }
  ]
}
```

---

## 12. Stage 7 — DELIVER

Finally, generate launch materials:

```json
{
  "one_line_pitch": "",
  "landing_headline": "",
  "product_description": "",
  "social_post": "",
  "launch_message": ""
}
```

This is the final output stage for practical launch content.

---

## 13. Final Brand Kit

The final product should render a single, polished page that presents the full brand system.

```text
╔══════════════════════════════════════╗
║             NEXIRA                   ║
║          YOUR BRAND KIT              ║
╠══════════════════════════════════════╣
║                                      ║
║  BRAND NAME                          ║
║  ──────────                          ║
║  ________                            ║
║                                      ║
║  TAGLINE                             ║
║  ________                            ║
║                                      ║
║  🎯 AUDIENCE                         ║
║                                      ║
║  💡 PROBLEM                          ║
║                                      ║
║  📍 POSITIONING                      ║
║                                      ║
║  🧠 PERSONALITY                      ║
║                                      ║
║  ✨ NAMING                           ║
║                                      ║
║  🎨 VISUAL IDENTITY                 ║
║                                      ║
║  💬 BRAND VOICE                      ║
║                                      ║
║  🔍 AI CRITIQUE                      ║
║                                      ║
║  ✓ CONSISTENCY                       ║
║                                      ║
║  🚀 LAUNCH KIT                       ║
║                                      ║
║       [ EXPORT BRAND KIT ]           ║
╚══════════════════════════════════════╝
```

---

## 14. Backend Workflow

The Flask backend can implement one main workflow function:

```text
run_nexira_workflow()
        │
        ├── discover()
        │
        ├── position(discover)
        │
        ├── shape(discover, position)
        │
        ├── visualize(position, shape)
        │
        ├── challenge(all_previous)
        │
        ├── consistency(all_previous)
        │
        └── deliver(all_previous)
```

The important requirement is context preservation. Each stage should use outputs from prior stages and not restart from scratch.

Examples:

```text
Position Agent
       ↑
       │
Discover Output
```

```text
Challenge Agent
       ↑
       │
Discover
Position
Shape
Visual
```

---

## 15. MongoDB Structure

Store one project like this:

```json
{
  "_id": "...",

  "idea": {
    "description": "...",
    "audience": "..."
  },

  "discover": {},
  "position": {},
  "shape": {},
  "visual": {},
  "challenge": {},
  "consistency": {},
  "launch": {},
  "final_brand": {}
}
```

This makes the workflow persistent and allows individual stages to be regenerated later.

---

## 16. Add Human Control

The user should remain in the loop. A few examples:

```text
AI generated 6 directions

○ Name A
● Name B
○ Name C

        [ Continue ]
```

The selected name is then used in the next stage.

Similarly:

```text
Personality

☑ Innovative
☑ Trustworthy
☐ Playful
☐ Luxury
```

This ensures the product allows users to shape the direction while still benefiting from AI acceleration.

---

## 17. API Design

For the MVP:

```text
POST /api/project
```

Create project.

```text
POST /api/workflow/discover
POST /api/workflow/position
POST /api/workflow/shape
POST /api/workflow/visualize
POST /api/workflow/challenge
POST /api/workflow/consistency
POST /api/workflow/deliver
GET /api/project/:id
```

---

## 18. Development Order

Follow this order carefully:

### Phase 1 — Foundation

```text
React
  +
Flask
  +
MongoDB
  +
LLM API
```

Get one API call working first.

### Phase 2 — Core AI

```text
Discover
   ↓
Position
   ↓
Shape
```

### Phase 3 — Brand generation

```text
Visualize
   ↓
Launch
```

### Phase 4 — Differentiation

```text
Challenge
   ↓
Consistency
```

### Phase 5 — UI

Build the polished dashboard around the already-working AI.

### Phase 6 — Export

Generate the final Brand Kit.

### Phase 7 — Testing

Use different ideas and verify that the workflow adapts.

---

## 19. Demo Narrative for Judges

Use one realistic idea throughout the demo, for example:

> An AI platform that helps college students find teammates for hackathons based on skills and interests.

Then show:

```text
00:00  Problem
00:20  Enter idea
00:35  Discover
00:55  Position
01:15  Shape
01:35  Visualize
01:55  🔥 AI Challenge
02:15  Consistency
02:30  Final Brand Kit
02:50  Original feature
```

The recommended demo length is 2–4 minutes and should show real product usage, realistic input, and the workflow with the strongest original feature.

---

## 20. MVP Priority

If time becomes tight, prioritize the following:

```text
                 MUST WORK
                     │
          ┌──────────┴──────────┐
          ▼                     ▼
      Idea Input          AI Workflow
                              │
                 ┌────────────┼────────────┐
                 ▼            ▼            ▼
              Discover     Position      Shape
                 │
                 ▼
              Visual
                 │
                 ▼
              Challenge ⭐
                 │
                 ▼
             Final Kit ⭐
```

The handbook emphasizes that AI workflow and prompt engineering are high-value judging areas.

The strongest technical story becomes:

> NEXIRA does not just generate a brand. It progressively reasons about the idea, preserves context between stages, challenges its own output, validates consistency, and then produces a launch-ready brand system.

---

## 21. Recommended Local Setup

### Backend

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python app.py
```

### Frontend

```bash
cd frontend
npm install
npm run dev -- --host 0.0.0.0
```

### Environment

```env
OPENAI_API_KEY=
FLASK_ENV=development
PORT=5000
```

The frontend can talk to the backend through the Flask API at:

```text
http://localhost:5000
```

---

## 22. Run the project

From the repository root:

```bash
# terminal 1
cd backend
python app.py

# terminal 2
cd frontend
npm install
npm run dev -- --host 0.0.0.0
```

Open the UI in the browser at:

```text
http://localhost:5173
```

---

## 23. Summary

NEXIRA is designed to demonstrate a practical, working AI brand-generation product under a short hackathon timeline. The key to success is not a complicated toolchain; it is a structured workflow that reasons progressively, keeps context alive, actively challenges its own output, and creates a coherent final brand kit.

This project is intentionally built to be:

- useful,
- demo-friendly,
- grounded in a real AI workflow,
- and aligned with the handbook's emphasis on structured reasoning and launch-ready outputs.
