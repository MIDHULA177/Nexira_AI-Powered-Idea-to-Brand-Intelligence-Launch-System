NEXIRA — Detailed Project README

AI-Powered Multi-Agent Brand Building Web Application

1. Project Overview

NEXIRA is a web application that transforms a raw idea, product concept, startup concept, service, or detailed branding brief into a structured and coherent brand system.

NEXIRA uses a Supervisor-Orchestrated Multi-Agent Architecture rather than relying on a single generic AI prompt.

The system divides brand creation into specialized stages handled by dedicated AI agents. Each stage receives structured context from previously approved stages. The user remains in control throughout the process and can review, edit, regenerate, or approve every major AI-generated result before proceeding.

The complete workflow is:

Raw Idea
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

The core philosophy is:

NEXIRA should not simply generate a brand. It should guide the user through a structured AI-assisted brand-building process, challenge the resulting brand, validate consistency, and produce a coherent final brand system.

2. Core Product Concept

NEXIRA solves the problem of fragmented AI-assisted branding.

A typical AI interaction might produce:

a name
a tagline
some colors
a logo idea

but these outputs may not be strategically connected.

NEXIRA instead builds a chain of dependent decisions:

IDEA
 ↓
AUDIENCE + PROBLEM
 ↓
POSITIONING
 ↓
PERSONALITY
 ↓
NAMING + TAGLINE + VOICE
 ↓
VISUAL IDENTITY
 ↓
CRITIQUE
 ↓
CONSISTENCY CHECK
 ↓
LAUNCH CONTENT
 ↓
FINAL BRAND SYSTEM

Each stage uses information from previous approved stages.

3. Main Product Goals

NEXIRA must:

Transform incomplete ideas into structured brand strategies.
Use specialized AI agents for different branding responsibilities.
Pass structured context between agents.
Give the user control over every major AI-generated result.
Allow editing and regeneration.
Challenge generated branding rather than blindly accepting it.
Detect contradictions and inconsistencies.
Maintain persistent projects.
Allow completed projects to be edited later.
Produce a consolidated final brand system.
Generate launch-ready content.
Make the multi-agent workflow visible to users and judges.
Support two application roles: user and admin.
4. User Roles

NEXIRA has exactly two roles.

USER
ADMIN
4.1 User

A normal user can:

Register
Login
Create projects
Enter an initial prompt
View their projects
Open existing projects
Continue incomplete projects
Review AI-generated results
Edit AI results
Regenerate results
Approve results
Continue through workflow stages
Return to previous stages
Modify completed projects
View project history
Generate final brand content
View final brand system
Export/copy final information where supported

A user can only access their own projects.

5. Admin

The application must create a default admin account during initial project setup.

The default admin credentials may be hardcoded because this application is intended for an online hackathon/demo environment and judges need a known account for accessing administrative functionality.

The default admin account must still be stored in MongoDB Atlas.

Admin capabilities:

Login as admin
Access Admin Dashboard
View registered users
View user information relevant to administration
Change a user's role
Promote:
user → admin
Demote:
admin → user

There are no granular permission levels.

The only role values are:

user
admin

Admin users retain normal user/project capabilities in addition to administrative access.

Default Admin Initialization

The initialization process must be idempotent.

If the default admin already exists:

Do not create another admin.

If the default admin does not exist:

Create default admin in MongoDB Atlas.

The implementation should make the default credentials clearly discoverable for the hackathon judges without requiring external setup.

6. Homepage Entry Points

NEXIRA is a multi-page web application.

Users should have two primary ways to start a project.

6.1 Direct Homepage Prompt

The homepage contains a prominent prompt interface.

Example:

What are you building?

[ An app that helps college students find project teammates... ]

                              [ Start → ]

The user may enter either a simple idea:

An app that helps students find project teammates.

or a detailed brief:

I want to build a premium platform for university students to find teammates based on skills, personality and interests. The brand should feel energetic, trustworthy and approachable.

The prompt must support free-form input.

When submitted:

Homepage
   ↓
Create Project
   ↓
Save Prompt
   ↓
Start Discovery
   ↓
Project Workspace

If authentication is required before project creation, the user should be redirected through authentication and then returned to the project creation flow.

7. Create Project

Users can also create a project from their dashboard.

Required information:

Project Name
Initial Prompt / Brief

Example:

Project Name:
Aurora

What are you building?
A collaboration platform for university students...

When submitted:

Create project.
Associate it with authenticated user.
Store initial prompt.
Initialize workflow state.
Start or enable Discovery.
Redirect to project workspace.
8. Existing Projects

Every user should have access to a project dashboard.

The dashboard should show their existing projects.

Each project should expose information such as:

Project name
Status
Current stage
Progress
Last updated time
Completion state

Example:

Aurora
In Progress
Positioning

Nova
Completed
Brand Ready

CampusConnect
In Progress
Visualize

Users can open any project they own.

9. Project Lifecycle

Recommended logical states:

draft
discovering
discovery_review
positioning
positioning_review
shaping
shape_review
visualizing
visual_review
moodboard_optional
challenging
consistency_review
launch_generation
completed
archived

The implementation may simplify these states, but it must be possible to determine:

Current stage
Completed stages
Approved stages
Pending review
Regeneration status
Outdated downstream sections
Completion status
10. Human-in-the-Loop Workflow

NEXIRA must not automatically approve AI-generated results.

Each major stage follows:

AI Generates
     ↓
User Reviews
     ↓
 ┌───────────┬────────────┬─────────────┐
 │ Edit      │ Regenerate │ Approve     │
 └───────────┴────────────┴─────────────┘
                           ↓
                     Next Stage

The backend must persist the approval state.

Recommended stage states:

locked
available
generating
review
approved
needs_regeneration
outdated
11. Multi-Agent Architecture

NEXIRA uses a Supervisor-Orchestrated Multi-Agent Architecture.

Agent Architecture
                    SUPERVISOR
                   ORCHESTRATOR
                        │
        ┌───────────────┼────────────────┐
        │               │                │
        ▼               ▼                ▼
   Discovery       Positioning      Brand Shaper
      Agent           Agent             Agent
        │               │                │
        └───────────────┼────────────────┘
                        ▼
                   Visual Agent
                        │
                        ▼
                   Critic Agent
                        │
                        ▼
                Consistency Agent
                        │
                        ▼
                   Launch Agent

The Supervisor is responsible for workflow control, not for replacing every specialized agent.

12. Supervisor / Orchestrator

The Supervisor manages:

Workflow sequence
Agent invocation
Context passing
Stage dependencies
User approval gates
Regeneration
Targeted refinement
Error handling
Project state transitions
Dependency updates

The Supervisor should understand the current project state and determine which stage is available.

13. Discovery Agent
Purpose

Understand the user's idea before branding decisions are made.

The Discovery Agent extracts:

Core idea
Product/service description
Problem
Target audience
Audience segments
Audience needs
Context
User motivations
Constraints
Assumptions
Open questions

Example output:

{
  "core_idea": "...",
  "problem": "...",
  "target_audience": [
    {
      "segment": "...",
      "rationale": "..."
    }
  ],
  "needs": [],
  "context": "...",
  "constraints": [],
  "assumptions": [],
  "open_questions": []
}

The output is shown to the user.

The user can:

Edit
Regenerate
Approve

Only approved Discovery information becomes authoritative context for Positioning.

14. Positioning Agent
Purpose

Convert discovery into strategic brand positioning.

The Positioning Agent generates:

Category
Value proposition
Core customer benefit
Differentiation
Positioning statement
Supporting rationale
Alternative positioning directions

Example:

{
  "category": "...",
  "value_proposition": "...",
  "core_benefit": "...",
  "differentiator": "...",
  "positioning_statement": "...",
  "rationale": "...",
  "alternatives": []
}

The user can:

Edit
Regenerate
Choose an alternative
Approve
15. Brand Shaper Agent

The Brand Shaper Agent handles the verbal and conceptual identity.

It contains several logical sub-processes.

15.1 Brand Personality

Generate:

Personality traits
Rationale
Traits to avoid
Relationship to audience
Relationship to positioning

Example:

{
  "traits": [
    {
      "name": "Energetic",
      "rationale": "..."
    },
    {
      "name": "Approachable",
      "rationale": "..."
    }
  ],
  "avoid_traits": [
    {
      "name": "Overly corporate",
      "reason": "..."
    }
  ]
}
16. Naming Territories

NEXIRA should not immediately dump a random list of names.

The system first generates conceptual naming territories.

Example:

Connection
Momentum
Discovery
Collaboration

Each territory should contain:

Name
Concept
Rationale
Keywords
Naming characteristics

The user selects a territory.

17. Name Generation

Names are generated using:

Approved positioning
Approved personality
Selected naming territory
Target audience
User-provided constraints

Each candidate should have useful information:

{
  "name": "SkillMesh",
  "concept": "...",
  "rationale": "...",
  "positioning_alignment": "...",
  "concerns": []
}

The system must not claim:

Trademark availability
Domain availability
Legal availability

unless an external verification system is actually implemented.

18. Tagline Generation

Generate taglines based on:

Positioning
Personality
Selected name

The user can:

Edit
Regenerate
Select
Approve
19. Brand Voice

Generate:

Voice description
Tone
Writing principles
Preferred words/phrases
Words/phrases to avoid
Example messaging

The voice must be consistent with approved positioning and personality.

20. Visual Agent

The Visual Agent develops the visual identity direction.

The output should include:

Visual concept
Color direction
Primary colors
Secondary colors
Accent colors
Typography direction
Heading characteristics
Body text characteristics
Imagery direction
Composition
Graphic language
Logo/symbol direction
Visual rules
Rationale

Example:

{
  "concept": "...",
  "color_direction": {
    "primary": "...",
    "secondary": [],
    "accent": [],
    "rationale": "..."
  },
  "typography": {
    "heading_character": "...",
    "body_character": "...",
    "rationale": "..."
  },
  "imagery": "...",
  "composition": "...",
  "logo_direction": "...",
  "visual_rules": {
    "do": [],
    "avoid": []
  }
}
21. Moodboard Generation

Moodboards are optional.

The workflow is:

Visual Direction
      ↓
User Approval
      ↓
Generate Moodboard?
    /       \
  No         Yes
  ↓           ↓
Continue    Image Generation

Moodboard generation should be implemented only if the selected OpenAI/image-generation capability is available for the deployed application.

If image generation is unavailable:

Do not pretend a moodboard exists.
Preserve the visual identity direction.
Allow the workflow to continue.
22. Critic Agent

The Critic Agent is a major differentiating feature.

Its purpose is to challenge the generated brand.

It should independently evaluate:

Generic/cliché naming
Weak differentiation
Audience mismatch
Positioning weakness
Personality inconsistency
Voice mismatch
Visual/personality mismatch
Visual/audience mismatch
Contradictions
Unclear value proposition
Weak tagline alignment
Ambiguity
Missing information

Example:

{
  "needs_revision": true,
  "issues": [
    {
      "category": "naming",
      "severity": "medium",
      "issue": "...",
      "evidence": "...",
      "suggested_action": "..."
    }
  ],
  "strengths": [],
  "overall_summary": "..."
}

The Critic should not automatically rewrite the entire brand.

The user should be able to choose:

Accept
Fix
Regenerate specific section
Edit manually
Continue despite warning
23. Refinement Loop

NEXIRA must support targeted refinement.

Example:

Brand Generated
      ↓
Critic
      ↓
Problem Found
      ↓
User Chooses Fix
      ↓
Relevant Agent Regenerates
      ↓
Critic Reviews Again
      ↓
User Approves

If only naming is problematic, do not unnecessarily regenerate:

Positioning
Personality
Visual identity

unless the user chooses to do so.

24. Consistency Agent

The Consistency Agent evaluates relationships between brand components.

It should check:

Name ↔ Positioning
Name ↔ Personality
Tagline ↔ Positioning
Tagline ↔ Personality
Voice ↔ Audience
Voice ↔ Personality
Visual ↔ Personality
Visual ↔ Audience
Visual ↔ Positioning
Launch Content ↔ Voice
Launch Content ↔ Positioning

Example:

{
  "score": 0.92,
  "checks": [
    {
      "relationship": "Visual ↔ Personality",
      "status": "warning",
      "explanation": "...",
      "recommendation": "..."
    }
  ]
}

The score is an AI consistency assessment and must not be represented as an objective measure of brand quality.

25. Launch Agent

The Launch Agent generates practical launch content using the final approved brand context.

Landing Page Content
Headline
Subheadline
CTA
Short description
Extended description
Social Content
Launch announcement
Short social post
Social caption
Platform-specific versions where useful
Brand Messaging
One-line pitch
Elevator pitch
Product description
Key messaging points

Launch content must use the approved:

Positioning
Brand personality
Brand voice
Audience
26. Deliver Stage

The final brand system should consolidate:

Original idea
Discovery
Audience
Problem
Positioning
Value proposition
Differentiation
Personality
Traits to avoid
Naming territory
Selected name
Tagline
Brand voice
Visual identity direction
Color direction
Typography
Imagery
Logo/symbol direction
Moodboard if generated
Critique results
Consistency results
Launch content
27. Brand Context Object

The project should maintain a central logical Brand Context Object.

{
  "project_id": "...",
  "idea": {},
  "discovery": {},
  "positioning": {},
  "brand": {},
  "visual": {},
  "critique": {},
  "consistency": {},
  "launch": {}
}

This is the conceptual context object.

The actual MongoDB document can use the finalized schema described below.

28. Database Architecture

Database:

MongoDB Atlas

Core collections:

users
projects
project_versions
agent_runs

The system should not create unnecessary collections unless a future requirement demands them.

29. Users Collection

Example:

{
  "_id": ObjectId,
  "first_name": "John",
  "last_name": "Doe",
  "email": "john@example.com",
  "password_hash": "...",
  "role": "user",
  "is_active": true,
  "created_at": ISODate,
  "updated_at": ISODate,
  "last_login_at": ISODate
}

Role:

user
admin
Index
email: unique
30. Projects Collection

The project is the central persistent Brand Context Object.

Example:

{
  "_id": ObjectId,

  "user_id": ObjectId,

  "name": "Aurora",

  "initial_prompt": "An app that helps students find project teammates...",

  "status": "in_progress",

  "current_stage": "positioning",

  "progress": 33,

  "stages": {

    "discovery": {
      "status": "approved",
      "version": 2,
      "data": {},
      "generated_at": ISODate,
      "approved_at": ISODate,
      "source": "ai",
      "approved_by": ObjectId
    },

    "positioning": {
      "status": "review",
      "version": 1,
      "data": {},
      "generated_at": ISODate,
      "approved_at": null
    },

    "shape": {
      "status": "locked",
      "version": 0,
      "data": null
    },

    "visualize": {
      "status": "locked",
      "version": 0,
      "data": null
    },

    "challenge": {
      "status": "locked",
      "data": null
    },

    "consistency": {
      "status": "locked",
      "data": null
    },

    "launch": {
      "status": "locked",
      "data": null
    }
  },

  "created_at": ISODate,
  "updated_at": ISODate
}
31. Stage Data Strategy

Stage data should be embedded inside the project document because the stages represent one evolving brand system.

Conceptually:

Project
│
├── Discovery
├── Positioning
├── Shape
├── Visualize
├── Challenge
├── Consistency
└── Launch

This makes project retrieval straightforward.

32. Project Versions Collection

Meaningful project states should be stored as snapshots.

Example:

{
  "_id": ObjectId,
  "project_id": ObjectId,
  "version_number": 4,
  "trigger": "positioning_updated",

  "snapshot": {
    "discovery": {},
    "positioning": {},
    "shape": {},
    "visualize": {},
    "challenge": {},
    "consistency": {},
    "launch": {}
  },

  "created_by": {
    "type": "user",
    "user_id": ObjectId
  },

  "created_at": ISODate
}

Possible triggers:

project_created
discovery_approved
positioning_approved
shape_approved
visual_approved
finalized
manual_edit
33. Agent Runs Collection

Every meaningful AI execution should be tracked.

Example:

{
  "_id": ObjectId,

  "project_id": ObjectId,

  "agent": "discovery",

  "stage": "discover",

  "status": "completed",

  "trigger": "initial_generation",

  "input_context": {
    "project_prompt": "...",
    "previous_stage_version": null
  },

  "output": {},

  "model": "...",

  "started_at": ISODate,

  "completed_at": ISODate,

  "error": null
}

Failed run:

{
  "agent": "visual",
  "status": "failed",
  "error": {
    "code": "IMAGE_GENERATION_FAILED",
    "message": "..."
  }
}

Full execution logging is intentional because the multi-agent workflow is a major technical feature of NEXIRA.

34. Database Relationships
                  USERS
                    │
                    │ 1
                    │
                    │ N
                 PROJECTS
                 /      \
                /        \
               N          N
              /            \
             /              \
PROJECT_VERSIONS        AGENT_RUNS
35. Database Indexes
Users
email: unique
Projects
user_id
status
user_id + updated_at

Recommended compound index:

{
  "user_id": 1,
  "updated_at": -1
}
Project Versions
project_id + version_number
Agent Runs
project_id + created_at
project_id + stage
project_id + status
36. Project Dependency Management

Earlier stages influence later stages.

Example:

Discovery
   ↓
Positioning
   ↓
Shape
   ↓
Visualize
   ↓
Challenge
   ↓
Consistency
   ↓
Launch

If the user changes an earlier approved stage, downstream data must not be automatically deleted.

Example:

Positioning → changed

Then:

Name          → outdated
Tagline       → outdated
Voice         → outdated
Visual        → outdated
Challenge     → outdated
Consistency   → outdated
Launch        → outdated

Existing data remains available.

The user decides what to regenerate.

37. Approved vs AI-Generated Data

The system should logically distinguish:

AI generated
User edited
User approved

Example:

{
  "data": {},
  "status": "approved",
  "source": "ai",
  "approved_by": ObjectId,
  "approved_at": ISODate
}

If edited:

{
  "source": "user_edited"
}
38. Naming Candidate Storage

Naming candidates should be retained where useful.

Example:

{
  "naming": {
    "territories": [],
    "candidates": [
      {
        "name": "SkillMesh",
        "selected": true
      },
      {
        "name": "Teamly",
        "selected": false
      }
    ],
    "selected_name": "SkillMesh"
  }
}

This allows users to revisit previous naming decisions.

39. Moodboard Data

If moodboard generation is used:

{
  "moodboard": {
    "status": "generated",
    "images": [
      {
        "url": "...",
        "prompt": "...",
        "type": "imagery"
      }
    ],
    "created_at": ISODate
  }
}

If not requested:

{
  "moodboard": {
    "status": "not_requested"
  }
}
40. Authentication

Authentication uses:

JWT

Required functionality:

POST /api/auth/register
POST /api/auth/login
GET  /api/auth/me

Registration requires:

first_name
last_name
email
password

Passwords must be securely hashed.

Plaintext passwords must never be stored.

41. Default Admin Initialization

During initial application setup:

Check MongoDB
      ↓
Does default admin exist?
      │
   ┌──┴──┐
  YES    NO
   │      │
   │      ↓
   │   Create admin
   │      │
   └──────┘
      ↓
Continue application

The operation must be idempotent.

Default admin credentials may be hardcoded for the hackathon environment so judges can access the Admin Dashboard.

42. REST API
Authentication
POST /api/auth/register
POST /api/auth/login
GET  /api/auth/me
Projects
GET    /api/projects
POST   /api/projects
GET    /api/projects/:projectId
PATCH  /api/projects/:projectId
DELETE /api/projects/:projectId
Workflow
GET /api/projects/:projectId/workflow

Discovery:

POST /api/projects/:projectId/stages/discovery/generate
POST /api/projects/:projectId/stages/discovery/regenerate
POST /api/projects/:projectId/stages/discovery/approve

Positioning:

POST /api/projects/:projectId/stages/positioning/generate
POST /api/projects/:projectId/stages/positioning/regenerate
POST /api/projects/:projectId/stages/positioning/approve

Shape:

POST /api/projects/:projectId/stages/shape/generate
POST /api/projects/:projectId/stages/shape/regenerate
POST /api/projects/:projectId/stages/shape/approve

Visual:

POST /api/projects/:projectId/stages/visual/generate
POST /api/projects/:projectId/stages/visual/regenerate
POST /api/projects/:projectId/stages/visual/approve

Challenge:

POST /api/projects/:projectId/stages/challenge/run

Consistency:

POST /api/projects/:projectId/stages/consistency/run

Launch:

POST /api/projects/:projectId/stages/launch/generate

The implementation can consolidate endpoints if appropriate, but all functionality must remain available.

43. Admin API

Example:

GET   /api/admin/users
PATCH /api/admin/users/:userId/role

The role endpoint accepts only:

user
admin

Only authenticated admins can access these endpoints.

The backend must verify the authenticated user's role on every admin request.

44. Frontend Routes

Functional routes:

/
 /login
 /register

 /dashboard
 /projects/new
 /projects/:projectId

 /projects/:projectId/discover
 /projects/:projectId/position
 /projects/:projectId/shape
 /projects/:projectId/visualize
 /projects/:projectId/challenge
 /projects/:projectId/consistency
 /projects/:projectId/deliver

 /admin

The project stages may alternatively be implemented within a single project workspace route.

45. Frontend Technology

Confirmed:

React.js
CSS

The frontend must support:

Homepage
Authentication
Dashboard
Project creation
Project list
Project workspace
Stage navigation
AI output display
Editing
Regeneration
Approval
Workflow status
Agent activity
Final brand presentation
Admin dashboard

The exact visual design system is intentionally not defined in this README.

46. Backend Technology

Confirmed:

Python
Flask
REST API

Backend responsibilities:

Authentication
Authorization
User management
Project CRUD
Workflow state
Agent orchestration
OpenAI API integration
Structured output validation
MongoDB Atlas operations
Version management
Agent execution tracking
Error handling
47. AI Technology

Use the OpenAI API.

AI functionality should use:

Role-specific prompting
Structured outputs
Explicit schemas
Context passing
Agent-specific instructions
Validation
Critique
Refinement
Regeneration
Optional image generation

OpenAI credentials must remain server-side.

The frontend must never contain the OpenAI API key.

48. Structured Output Validation

Every agent response must be validated before being stored.

Validation should check:

Required fields
Correct data types
Arrays
Nested objects
Enum values
Stage-specific structure

If invalid:

AI Output
    ↓
Validation
    ↓
Invalid?
  /    \
Yes     No
 ↓       ↓
Retry   Save

The system must not blindly store arbitrary LLM output as structured state.

49. Error Handling

Handle:

OpenAI failures
Rate limits
Invalid AI output
MongoDB errors
Authentication failures
Unauthorized project access
Network errors
Agent timeouts
Image-generation failures
Invalid user input

Failed operations must not overwrite the last successful approved state.

Example:

Existing Approved Output
        ↓
Regeneration
        ↓
FAILURE
        ↓
Keep Existing Output
50. Security

Minimum security requirements:

Password hashing
JWT authentication
Role-based authorization
Project ownership checks
Environment variables for sensitive secrets
HTTPS in production
CORS restriction
Input validation
API rate limiting where appropriate
OpenAI key only on backend
MongoDB credentials only on backend
No sensitive credentials in frontend
No hidden chain-of-thought exposure
51. AI Reasoning Visibility

NEXIRA should make its workflow visible, not its private reasoning.

The UI may show:

Discovery Agent
Analyzing audience and problem

Positioning Agent
Building positioning directions

Critic Agent
Checking differentiation

It must not expose hidden chain-of-thought.

Only concise results, explanations, issues, recommendations, and status information should be shown.

52. Agent Activity Tracking

Agent execution status can be represented as:

Discovery Agent       Complete
Positioning Agent     Complete
Brand Shaper          Running
Visual Agent          Waiting
Critic Agent          Waiting
Consistency Agent     Waiting
Launch Agent          Waiting

This should be backed by agent_runs where practical.

53. Regeneration Rules

Regeneration must:

Preserve upstream approved context.
Respect user edits.
Preserve unrelated approved sections.
Generate alternatives.
Avoid overwriting successful data until the new result is accepted.

Example:

Name A
Name B
Name C

[Choose A]
[Choose B]
[Choose C]
[Generate More]
54. Versioning

Meaningful changes should create project versions.

A version should contain:

Project ID
Version number
Trigger
Snapshot
Creator
Timestamp

Version history allows the application to preserve the evolution of the brand.

55. Recommended Repository Structure
nexira/
│
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   ├── pages/
│   │   ├── layouts/
│   │   ├── hooks/
│   │   ├── services/
│   │   ├── context/
│   │   ├── utils/
│   │   └── App.jsx
│   ├── public/
│   └── package.json
│
├── backend/
│   ├── app/
│   │   ├── routes/
│   │   ├── models/
│   │   ├── agents/
│   │   │   ├── supervisor.py
│   │   │   ├── discovery.py
│   │   │   ├── positioning.py
│   │   │   ├── brand_shaper.py
│   │   │   ├── visual.py
│   │   │   ├── critic.py
│   │   │   ├── consistency.py
│   │   │   └── launch.py
│   │   ├── services/
│   │   ├── schemas/
│   │   ├── auth/
│   │   ├── db/
│   │   └── utils/
│   ├── tests/
│   ├── requirements.txt
│   └── run.py
│
├── docs/
├── .env.example
├── .gitignore
└── README.md

The implementing AI may adjust the structure if functionality and architecture are preserved.

56. Environment Variables

Example:

OPENAI_API_KEY=
MONGODB_URI=
JWT_SECRET=
FLASK_ENV=
FRONTEND_URL=

For the hackathon's default admin, the credentials may be defined directly in the initialization configuration/source as previously specified.

No production secrets should be committed.

57. Performance

The application should:

Avoid unnecessary AI calls.
Persist successful results.
Avoid regenerating unchanged sections.
Provide loading states.
Provide retry mechanisms.
Keep MongoDB queries scoped to the authenticated user.
Avoid blocking long-running Flask requests where practical.

The initial implementation may use synchronous generation endpoints if acceptable, but the architecture should allow asynchronous processing later.

58. Testing
Authentication

Test:

Registration
Login
Invalid credentials
JWT validation
User role
Admin role
Admin authorization
Projects

Test:

Create
Read
Update
Delete
Ownership
Unauthorized access
Project listing
Agents

Test:

Valid output
Invalid output
Context passing
Regeneration
Critique
Consistency
Failure handling
Workflow

Test:

Stage locking
Stage generation
Approval
Regeneration
Editing
Progression
Upstream changes
Outdated downstream stages
Preservation of previous successful state
Admin

Test:

Admin can access dashboard
User cannot access dashboard
Admin can promote user
Admin can demote admin
Invalid roles are rejected
59. MVP Priorities
Priority 1
Authentication
User database
Default admin
Admin dashboard
Project database
Project creation
Prompt entry
Project dashboard
Discovery Agent
Approval/edit/regenerate
Priority 2
Positioning Agent
Brand Shaper Agent
Workflow state
Context passing
Persistent project state
Priority 3
Visual Agent
Critic Agent
Consistency Agent
Priority 4
Launch Agent
Final brand presentation
Version history
Export
Priority 5
Moodboard/image generation
Advanced admin features
Advanced animations
Additional integrations
60. Definition of Done

A user should be able to:

Register.
Login.
Create a project.
Enter a simple or detailed idea.
Run Discovery.
Review Discovery.
Edit Discovery.
Regenerate Discovery.
Approve Discovery.
Run Positioning.
Review Positioning.
Edit/regenerate Positioning.
Approve Positioning.
Generate brand personality.
Generate naming territories.
Generate names.
Select a name.
Generate tagline.
Generate brand voice.
Review/edit/regenerate Brand Shape.
Approve Brand Shape.
Generate visual identity direction.
Review/edit/regenerate visual direction.
Optionally generate a moodboard if image generation is available.
Run Critic Agent.
Review critique.
Perform targeted refinement.
Run Consistency Agent.
Generate launch content.
View the complete brand system.
Save the project.
Leave and return later.
Modify an earlier section after completion.
Receive downstream review/outdated indicators.
View project history.
Export/copy final brand information where implemented.
Access only their own projects.
Allow an admin to manage user roles.
61. Final Technical Stack
Layer	Technology
Frontend	React.js
Styling	CSS
Backend	Python
API Framework	Flask
AI	OpenAI API
AI Architecture	Supervisor-Orchestrated Multi-Agent System
Database	MongoDB Atlas
Authentication	JWT
Data Format	JSON / Structured Outputs
Repository	Git + GitHub

A dedicated multi-agent framework such as LangChain or LangGraph is not required. A custom Python supervisor/orchestrator is sufficient and preferred if it keeps the architecture simple and transparent.

62. Deployment Architecture
                    USER
                      │
                      ▼
              React Frontend
                      │
                      ▼
                Flask REST API
                      │
          ┌───────────┴───────────┐
          │                       │
          ▼                       ▼
    OpenAI API              MongoDB Atlas
          │                       │
          ▼                       ▼
     AI Agents              Persistent State

Recommended deployment:

Frontend → Vercel
Backend  → Render / Railway
Database → MongoDB Atlas

Deployment providers may be changed without changing the architecture.

63. Frontend Visual Design 
.1 Frontend Design Direction

NEXIRA uses a Hybrid UI/UX system combining four visual approaches according to the user's context.

Public/Home Experience

Use the Creative Intelligence direction.

The homepage should feel:

Creative
Premium
Modern
Brand-focused
Spacious
Visually engaging
Professional

The homepage should not look like a conventional administrative dashboard.

Project Workspace

Use the Intelligent Minimal direction.

Once users begin working on a project, the interface should prioritize:

Clarity
Focus
Information hierarchy
Easy editing
Clear workflow progression
Minimal visual distraction
Agent Visualization

Use the AI Canvas direction for showing NEXIRA's multi-agent workflow.

The interface should visually communicate:

Discovery
    ↓
Positioning
    ↓
Brand Shaper
    ↓
Visual
    ↓
Critic
    ↓
Consistency
    ↓
Launch
Final Brand Presentation

Use the Dynamic Brand Studio direction.

Once the brand is complete, the final presentation should feel like a polished representation of the generated brand rather than a normal dashboard.

The approved brand's:

Name
Colors
Typography
Personality
Visual direction
Imagery

should influence the final presentation.

68. Frontend Technology

Use:

React.js
CSS

The frontend should be component-based and structured for maintainability.

Recommended supporting frontend concepts:

React Router
React Context or equivalent state management where appropriate
Fetch/Axios for REST API communication
Reusable UI components
Protected routes
Responsive layouts

Do not introduce a large UI framework unless necessary.

69. Frontend Application Structure

Recommended structure:

frontend/
│
├── src/
│   ├── components/
│   │   ├── common/
│   │   ├── navigation/
│   │   ├── project/
│   │   ├── workflow/
│   │   ├── agents/
│   │   ├── stages/
│   │   ├── brand/
│   │   └── admin/
│   │
│   ├── pages/
│   │   ├── Home/
│   │   ├── Login/
│   │   ├── Register/
│   │   ├── Dashboard/
│   │   ├── CreateProject/
│   │   ├── Project/
│   │   └── Admin/
│   │
│   ├── layouts/
│   │   ├── PublicLayout/
│   │   ├── AppLayout/
│   │   └── AdminLayout/
│   │
│   ├── services/
│   │   ├── api.js
│   │   ├── auth.js
│   │   ├── projects.js
│   │   ├── workflow.js
│   │   └── admin.js
│   │
│   ├── context/
│   │   ├── AuthContext.jsx
│   │   └── ProjectContext.jsx
│   │
│   ├── hooks/
│   ├── utils/
│   ├── styles/
│   ├── App.jsx
│   └── main.jsx
│
└── package.json

The structure may be modified if an equivalent architecture is maintained.

70. Main Frontend Routes

The application should support the following logical routes:

/
 /login
 /register

 /dashboard
 /projects/new

 /projects/:projectId
 /projects/:projectId/discover
 /projects/:projectId/position
 /projects/:projectId/shape
 /projects/:projectId/visualize
 /projects/:projectId/challenge
 /projects/:projectId/consistency
 /projects/:projectId/deliver

 /admin

The workflow may also be implemented using one project route with internal stage navigation.

71. Public Homepage

The homepage is both a marketing/product introduction and a direct entry point into NEXIRA.

The user must be able to start a project directly from the homepage.

Homepage structure

Recommended sections:

Hero
 ↓
How NEXIRA Works
 ↓
AI Agent Workflow
 ↓
Idea → Brand Transformation
 ↓
Brand Showcase
 ↓
Feature Overview
 ↓
Final CTA
72. Homepage Hero

The hero is the primary interaction point.

It should communicate:

Turn an idea into a brand.

or equivalent messaging.

The exact copy can be refined during implementation, but the concept must remain clear.

Hero elements
NEXIRA branding/navigation
Main headline
Supporting description
Large prompt input
Submit/start button
Example prompts
Optional visual/image area
Subtle motion

Example structure:

┌──────────────────────────────────────────────────────┐
│ NEXIRA                              Login / Start     │
│                                                      │
│              TURN AN IDEA INTO A BRAND               │
│                                                      │
│       From an incomplete idea to a coherent          │
│                    brand system.                     │
│                                                      │
│ ┌──────────────────────────────────────────────────┐ │
│ │ Tell NEXIRA what you're building...             │ │
│ │                                                  │ │
│ │                                         [ → ]    │ │
│ └──────────────────────────────────────────────────┘ │
│                                                      │
│ [ Startup ] [ Product ] [ Service ] [ Brand ]       │
│                                                      │
└──────────────────────────────────────────────────────┘

The screenshot supplied by the user is only a reference for the direct-prompt interaction pattern. Do not copy its visual theme or layout.

73. Hero Prompt Behavior

The prompt must support:

Simple prompts
An app that helps students find project teammates.
Detailed prompts
I want to build a premium platform for university students
to find teammates based on skills, personality and interests.
The brand should feel energetic and trustworthy.

The input should be a flexible multiline field.

The user should be able to:

Type
Paste
Edit
Submit

Example prompts can be clickable and populate the prompt field.

74. Homepage Prompt Submission

When an authenticated user submits:

Prompt
 ↓
Create project
 ↓
Save prompt
 ↓
Initialize workflow
 ↓
Open Discovery

If the user is not authenticated:

Prompt
 ↓
Login/Register
 ↓
Create project using saved prompt
 ↓
Open Discovery

The user's original prompt must not be lost during authentication.

75. Homepage How-It-Works Section

Show the NEXIRA workflow visually.

DISCOVER
    ↓
POSITION
    ↓
SHAPE
    ↓
VISUALIZE
    ↓
CHALLENGE
    ↓
CONSISTENCY
    ↓
DELIVER

Each stage should have a concise description.

Example:

Discover
Understand the idea, audience and problem.

Position
Define the value proposition and differentiation.

Shape
Build personality, naming, tagline and voice.

Visualize
Create the visual identity direction.

Challenge
Critique the brand and identify weaknesses.

Consistency
Validate relationships between brand components.

Deliver
Create the final brand system and launch content.
76. Homepage Agent Section

Show the specialized agents as part of NEXIRA's architecture.

Example:

Discovery Agent
Positioning Agent
Brand Shaper
Visual Agent
Critic Agent
Consistency Agent
Launch Agent

Hovering/clicking an agent should reveal a short description.

The purpose is to communicate that NEXIRA is a coordinated multi-agent system rather than a generic chatbot.

77. Idea-to-Brand Transformation Section

Show an example transformation.

Concept:

RAW IDEA

"An app for students to find project teammates."

        ↓

DISCOVERY

Audience
Problem
Needs

        ↓

POSITIONING

Value Proposition
Differentiation

        ↓

BRAND

Name
Personality
Voice
Tagline

        ↓

VISUAL

Colors
Typography
Imagery

        ↓

FINAL BRAND

The section should use animation or progressive visual transitions where appropriate.

78. Brand Showcase

The homepage should include examples of completed/generated brand systems.

Each card can display:

Brand name
Short description
Industry/category
Visual preview

Clicking a showcase item can open a detailed presentation if showcase data exists.

The showcase should use sample/demo projects and must not expose private user projects.

79. Homepage Final CTA

End the homepage with a strong action:

Ready to build your brand?

[ Start with an idea → ]

This button should focus the homepage prompt or navigate to project creation.

80. Authentication Pages
Login

Required fields:

Email
Password

Actions:

Login
Forgot password
Register
Register

Required:

First Name
Last Name
Email
Password
Confirm Password

After successful registration, redirect to the dashboard.

81. Dashboard

The dashboard uses the Intelligent Minimal direction.

It should prioritize projects rather than marketing content.

Structure:

NEXIRA

Dashboard

[ + Create Project ]

Your Projects

┌────────────────────┐
│ Aurora             │
│ In Progress        │
│ Positioning        │
│ 33%                │
└────────────────────┘

┌────────────────────┐
│ Nova               │
│ Completed          │
│ Brand Ready        │
│ 100%               │
└────────────────────┘
82. Dashboard Functionality

Users can:

Create project
Search projects
Open projects
Continue projects
View completion status
View current stage
Delete projects
Sort/filter projects
View last updated time

Do not add unnecessary dashboard functionality.

83. Create Project Page

The Create Project page should be simple.

Required:

Project Name
Initial Idea / Prompt

Example:

Create your brand

Project name
[ Aurora ]

Tell NEXIRA what you're building
[                                      ]
[                                      ]

              [ Start Building → ]

After submission:

Create
 ↓
Discovery
84. Project Workspace

The project workspace is the primary application interface.

Use the Intelligent Minimal design philosophy.

The workspace must prioritize:

Current task
AI output
User editing
Approval
Regeneration
Workflow status
85. Workspace Layout

Recommended conceptual layout:

┌────────────────────────────────────────────────────────────┐
│ NEXIRA       Aurora                    Save     Export     │
├────────────────────────────────────────────────────────────┤
│                                                            │
│ DISCOVER → POSITION → SHAPE → VISUALIZE → CHALLENGE →     │
│ CONSISTENCY → DELIVER                                      │
│                                                            │
├───────────────┬────────────────────────────────────────────┤
│               │                                            │
│ Stage Info    │              Current Stage                 │
│               │                                            │
│ AI Agents     │              AI Output                     │
│               │                                            │
│ Progress      │              [ Edit ] [ Regenerate ]       │
│               │                                            │
│               │                       [ Approve → ]         │
└───────────────┴────────────────────────────────────────────┘

Exact layout can be adapted responsively.

86. Workflow Navigation

The workflow navigation must always show:

Discover
Position
Shape
Visualize
Challenge
Consistency
Deliver

Use visual states:

Completed
Current
Available
Locked
Outdated

Example:

✓ Discover
✓ Position
● Shape
○ Visualize
○ Challenge
○ Consistency
○ Deliver
87. Stage Access Rules

The frontend must respect backend stage status.

Examples:

Locked

User cannot enter the stage.

Available

User can begin generation.

Review

User can inspect/edit/regenerate.

Approved

Stage is complete.

Outdated

Previous output exists but upstream changes require review.

88. Stage Output Interface

Every stage should have a consistent interaction model.

Stage Title

AI-generated result

────────────────────────

[ Edit ]

[ Regenerate ]

[ Approve & Continue → ]

If the user edits:

Save Changes
Cancel

If regeneration is running:

Generating...

The user must not accidentally approve a result that is still generating.

89. Discovery UI

Display structured cards/sections:

Core Idea
Problem
Target Audience
Needs
Context
Constraints
Assumptions
Open Questions

Each section should be independently editable where practical.

Example:

Target Audience

College students
Students working on academic projects

[ Edit ]
90. Positioning UI

Display:

Category
Value Proposition
Core Benefit
Differentiator
Positioning Statement

Alternative positioning directions can appear as selectable cards.

Example:

Positioning Direction A
...

Positioning Direction B
...

[ Select ]
91. Shape UI

The Shape stage should have tabs/sections for:

Personality
Naming
Tagline
Voice
Personality

Use visually distinct trait cards.

Energetic
Approachable
Collaborative

Each should display its rationale.

Naming

Show naming territories first.

Connection
Momentum
Discovery
Collaboration

After selecting a territory, show candidates.

SkillMesh
Teamly
CrewSync

The user selects a preferred name.

Tagline

Show multiple options.

Voice

Show:

Voice description
Tone
Writing rules
Do
Don't
Example messaging
92. Visualize UI

The Visualize stage should clearly separate:

Visual Direction

from:

Optional Moodboard

Visual direction should include:

Color
Typography
Imagery
Composition
Graphic Language
Logo Direction
Visual Rules

The user first reviews this.

After approval:

Generate Moodboard?

If supported:

[ Generate Moodboard ]

Otherwise:

Continue with Visual Direction
93. Moodboard UI

If image generation is available, display generated images in a visual grid.

Each image can have:

Preview
Generation prompt/description
Regenerate
Remove
Select/favorite

The system should not require moodboard generation for project completion.

94. Challenge UI

The Challenge stage should feel visually distinct from normal generation.

Display:

NEXIRA CRITIC

Potential Issues

⚠ Naming
The name may be too generic.

✓ Audience
Strong alignment.

⚠ Visual Direction
The visual tone may conflict with the intended personality.

Each issue should include:

Category
Severity
Explanation
Suggested action

Actions:

[ Fix ]
[ Ignore ]
[ Regenerate Section ]

Do not expose internal chain-of-thought.

95. Consistency UI

Use a visual relationship/canvas representation.

Example:

             POSITIONING
                  │
                  │
NAME ───────── BRAND ───────── VISUAL
                  │
                  │
                VOICE
                  │
                  │
               AUDIENCE

Then provide a detailed consistency report:

Name ↔ Positioning       ✓
Name ↔ Personality       ✓
Tagline ↔ Positioning    ✓
Visual ↔ Personality     ⚠
Voice ↔ Audience         ✓

A consistency summary can display an AI-generated score, but it must be clearly described as an AI assessment.

96. Deliver UI

The Deliver page transitions from workspace into the Dynamic Brand Studio direction.

The completed brand should feel like a finished creative system.

Display:

BRAND NAME

Tagline

Brand Personality

Positioning

Voice

Visual Identity

Color System

Typography

Imagery

Logo Direction

Consistency

Launch Content
97. Dynamic Brand Studio

The final presentation should use the approved brand information to influence its visual presentation.

For example:

Approved Brand Colors
       ↓
Final Brand Background/Accents

Approved Typography
       ↓
Brand Headings

Approved Personality
       ↓
Presentation Tone

Approved Imagery
       ↓
Visual Sections

The final brand page should feel like a brand presentation, not a database record.

98. Final Brand Navigation

The final brand presentation can use sections such as:

Overview
Strategy
Personality
Naming
Voice
Visual Identity
Moodboard
Challenge
Consistency
Launch

Users should be able to navigate directly to sections.

99. Editing a Completed Brand

Completed projects remain editable.

The user can select:

Edit Brand

Then choose:

Positioning
Personality
Name
Tagline
Voice
Visual Identity
Launch Content

If an earlier component changes, the UI should clearly show affected downstream sections.

Example:

Positioning changed

Name
Review recommended

Tagline
Review recommended

Voice
Review recommended

Visual Identity
Review recommended
100. Agent Visualization

The Agent Activity UI uses the AI Canvas concept.

It should visually represent:

                  SUPERVISOR
                      │
        ┌─────────────┼─────────────┐
        │             │             │
        ▼             ▼             ▼
   DISCOVERY      POSITIONING     SHAPER
        │             │             │
        └─────────────┼─────────────┘
                      ▼
                   VISUAL
                      │
                      ▼
                    CRITIC
                      │
                      ▼
                 CONSISTENCY
                      │
                      ▼
                   LAUNCH
101. Agent States

Each agent should have a visual state:

waiting
running
completed
failed
needs_review

Example:

✓ Discovery Agent
✓ Positioning Agent
● Brand Shaper
○ Visual Agent
○ Critic Agent
○ Consistency Agent
○ Launch Agent
102. Agent Activity Details

Clicking an agent can show:

Agent
Brand Shaper

Status
Completed

Stage
Shape

Output
Personality, naming, tagline and voice generated.

Completed
2 minutes ago

Do not display hidden chain-of-thought.

103. Global Project Status

Every project workspace should show:

Project name
Current stage
Overall progress
Last saved time
Current approval state

Example:

Aurora

Brand Progress
████████░░ 80%

Current Stage
Challenge

Last saved
2 minutes ago
104. Global Command Interaction

The application may include a command interface such as:

⌘ K

or a visible AI action bar.

Possible actions:

Regenerate this section
Give me alternative names
Change the personality
Challenge the positioning
Generate another visual direction

These actions must operate on the current project context.

They must not bypass approval/dependency rules.

105. Notifications

Use lightweight notifications for:

Generation completed
Regeneration completed
Save completed
Project created
Approval completed
Agent failure
Moodboard generation completed
Export completed

Avoid excessive notifications.

106. Loading States

AI generation requires clear loading states.

Example:

Brand Shaper is working...

Generating:
✓ Personality
● Naming
○ Tagline
○ Voice

If exact subtask progress cannot be determined, do not fabricate progress.

Instead:

Brand Shaper
Generating...
107. Empty States

Dashboard:

You haven't created a brand yet.

[ Create your first project → ]

No moodboard:

No moodboard generated yet.

[ Generate Moodboard ]

No projects:

Your brand workspace is empty.
Start with an idea.
108. Error States

Errors should be understandable.

Instead of:

500 Internal Server Error

display:

NEXIRA couldn't generate this section.

Your previous version is safe.

[ Try Again ]

Backend error details can be logged internally but should not expose sensitive implementation information.

109. Responsive Design

The application must work on:

Desktop
Tablet
Mobile

Desktop is the primary experience because the product is a creative workspace.

On smaller screens:

Workflow navigation can become horizontally scrollable or collapsible.
Agent canvas can become a vertical pipeline.
Multi-column layouts become single-column.
Large visual cards become stacked.
Prompt input remains easily accessible.
Editing controls remain usable.

Do not simply shrink desktop layouts.

110. Accessibility

The frontend should support:

Keyboard navigation
Visible focus states
Semantic HTML
Accessible buttons
Accessible form labels
Sufficient text contrast
Screen-reader-friendly status information
Non-color indicators for workflow status
Reduced-motion consideration

Do not rely solely on color to communicate:

approved
warning
error
locked
111. Animation Principles

Animation should communicate state and progression rather than exist purely for decoration.

Useful animations:

Agent activation
Workflow progression
Stage transitions
Card reveal
Prompt submission
Brand transformation
Final brand presentation
Loading/generation states

Avoid:

Constant movement
Excessive parallax
Distracting animations
Long transitions that slow the user down
112. Visual System Direction

The exact color palette and typography can be finalized during implementation, but the Hybrid system follows these principles.

Homepage

Creative:

Large typography
Strong whitespace
High-quality imagery/visuals
Editorial composition
Strong hero
Premium presentation
Workspace

Minimal:

Neutral foundation
Clear hierarchy
Structured cards/panels
Strong spacing
Focused content
Limited decoration
Agent System

Canvas-like:

Connected nodes
Status indicators
Relationship lines
Subtle motion
Interactive agent states
Final Brand

Dynamic:

Uses approved brand identity
Visual identity becomes part of the interface
Presentation-oriented
Rich visual sections
Brand-first composition
113. Component System

Create reusable components rather than building each page independently.

Recommended components:

Navbar
Footer
PromptInput
ProjectCard
ProjectGrid
WorkflowStepper
StageHeader
StageCard
AIOutputCard
EditableField
RegenerateButton
ApproveButton
AgentStatus
AgentPipeline
AgentNode
CritiqueCard
ConsistencyGraph
ConsistencyCheck
NamingCard
NamingTerritoryCard
PersonalityCard
ColorPalette
TypographyPreview
MoodboardGrid
BrandPresentation
ProgressIndicator
Modal
ConfirmDialog
Toast
LoadingState
ErrorState
EmptyState
114. State Management

Frontend state should distinguish:

Authentication state
user
role
token
isAuthenticated
Project state
project
currentStage
stageStatuses
progress
UI state
loading
editing
regenerating
modal state
notifications

The backend remains the source of truth for persistent project state.

Do not rely solely on frontend state for approvals or workflow progression.

115. API Integration

Frontend service layer should handle:

authService
projectService
workflowService
adminService

Example:

projectService.createProject()
projectService.getProjects()
projectService.getProject()
projectService.updateProject()
projectService.deleteProject()

Workflow:

workflowService.generateStage()
workflowService.regenerateStage()
workflowService.approveStage()
workflowService.runCritic()
workflowService.runConsistency()
116. Authentication UI Behavior

Unauthenticated user:

Homepage
   ↓
Prompt
   ↓
Login/Register

Authenticated user:

Homepage
   ↓
Prompt
   ↓
Create Project
   ↓
Workspace

Protected pages:

Dashboard
Projects
Admin

must redirect unauthenticated users to Login.

117. Admin Dashboard UI

The Admin Dashboard should use the same overall product language but remain functionally minimal.

Display:

Admin Dashboard

Users

┌──────────────┬─────────────────────┬────────┐
│ Name         │ Email               │ Role   │
├──────────────┼─────────────────────┼────────┤
│ John Doe     │ john@example.com    │ user   │
│ Jane Smith   │ jane@example.com    │ admin  │
└──────────────┴─────────────────────┴────────┘

Actions:

Change Role

Role selector:

user
admin

No additional permission system is required.

118. Admin Protection

The frontend must hide admin navigation from normal users.

However, hiding the UI is not sufficient.

The backend must independently enforce:

authenticated && role === "admin"

for every admin API request.

119. Project Ownership UI

If a user attempts to access a project they do not own:

Project not found

Do not reveal whether another user owns the project.

120. Final User Journey

The complete intended experience is:

                    HOME
                      │
                      ▼
              Enter an idea
                      │
             ┌────────┴────────┐
             │                 │
        Authenticated      Not logged in
             │                 │
             │              Login/Register
             │                 │
             └────────┬────────┘
                      ▼
                CREATE PROJECT
                      │
                      ▼
                  DISCOVER
                      │
             Review / Edit / Regenerate
                      │
                   Approve
                      ▼
                 POSITION
                      │
             Review / Edit / Regenerate
                      │
                   Approve
                      ▼
                    SHAPE
                      │
             Review / Edit / Regenerate
                      │
                   Approve
                      ▼
                 VISUALIZE
                      │
             Review / Edit / Regenerate
                      │
                   Approve
                      ▼
                 CHALLENGE
                      │
                  Fix Issues
                      │
                      ▼
                CONSISTENCY
                      │
                      ▼
                   DELIVER
                      │
                      ▼
              FINAL BRAND STUDIO
                      │
                      ▼
              Edit Anytime Later
121. Frontend Definition of Done

The frontend is considered complete when:

Homepage allows direct prompting.
Users can register/login.
Users can create projects.
Users can view existing projects.
Users can open and continue projects.
Workflow stages are clearly visible.
Locked/current/completed/outdated states are represented.
AI results are displayed clearly.
Users can edit results.
Users can regenerate results.
Users can approve results.
Users cannot accidentally bypass workflow approval.
Agent activity is visible.
Critique is clearly displayed.
Consistency results are clearly displayed.
Visual identity is presented effectively.
Optional moodboards are supported when available.
Completed brands have a polished final presentation.
Completed projects can be edited.
Downstream affected sections are clearly marked.
Admins can access the Admin Dashboard.
Admins can change user roles.
Normal users cannot access admin functionality.
The application is responsive.
Loading/error/empty states exist.
Keyboard/accessibility basics are implemented.
No OpenAI API key is exposed in frontend code.
122. Frontend Design Constraint

The frontend implementation must preserve the following Hybrid design identity:

PUBLIC EXPERIENCE
       │
       ▼
CREATIVE INTELLIGENCE
       │
       ▼
PROJECT WORKSPACE
       │
       ▼
INTELLIGENT MINIMAL
       │
       ▼
AGENT EXECUTION
       │
       ▼
AI CANVAS
       │
       ▼
FINAL BRAND
       │
       ▼
DYNAMIC BRAND STUDIO

The frontend should feel like one coherent product, not four unrelated designs.

The transitions between these modes should be subtle and intentional.

64. Implementation Instructions for an AI Coding Agent

If this README is provided to another AI coding agent, the agent must:

Read the entire README before implementation.
Preserve the stated architecture.
Build frontend and backend as separate applications.
Use React.js and CSS for the frontend.
Use Python and Flask for the backend.
Use MongoDB Atlas.
Implement JWT authentication.
Implement exactly two roles: user and admin.
Automatically initialize the default admin account.
Store the admin account in MongoDB.
Provide an Admin Dashboard.
Allow admins to promote/demote users.
Ensure normal users cannot access admin routes.
Implement the Supervisor-Orchestrated Multi-Agent Architecture.
Keep each agent modular.
Use structured outputs.
Persist project state after meaningful operations.
Require user approval between major stages.
Support editing and regeneration.
Preserve previous successful outputs when regeneration fails.
Support completed-project editing.
Detect downstream dependencies when earlier sections change.
Implement Critic and Consistency functionality as actual system features.
Track agent runs.
Maintain project versions.
Keep OpenAI API keys on the backend.
Never expose hidden chain-of-thought.
Validate AI outputs before persistence.
Provide .env.example.
Provide database setup instructions.
Provide API documentation.
Provide local development instructions.
Provide automated tests for core functionality.
Do not invent a frontend visual style.
Keep the frontend architecture flexible enough for a separate UI/UX specification.
Do not replace MongoDB Atlas with another database.
Do not replace Flask unless explicitly instructed.
Do not replace the multi-agent architecture with a single generic AI call.
Do not automatically overwrite approved user content.
Treat user approval as a first-class part of the workflow.
65. Core Product Principle

NEXIRA's core differentiator is:

SPECIALIZED AI
      +
STRUCTURED CONTEXT
      +
USER CONTROL
      +
CRITIQUE
      +
CONSISTENCY VALIDATION
      =
COHERENT BRAND SYSTEM

NEXIRA is therefore not simply:

"AI generates your brand."

It is:

An AI-powered staged brand-building system that transforms an idea into a brand through specialized agents, user-controlled refinement, critique, consistency validation, and final delivery.

66. Final Architecture Summary
                              NEXIRA
                                │
                                ▼
                       ┌────────────────┐
                       │ React.js + CSS │
                       └───────┬────────┘
                               │
                            REST API
                               │
                       ┌───────▼────────┐
                       │ Flask Backend  │
                       └───────┬────────┘
                               │
                   ┌───────────▼───────────┐
                   │ Supervisor /           │
                   │ Agent Orchestrator     │
                   └───────────┬───────────┘
                               │
        ┌──────────────┬───────┼────────┬──────────────┐
        │              │       │        │              │
        ▼              ▼       ▼        ▼              ▼
   Discovery      Position   Brand    Visual        Critic
     Agent          Agent    Shaper    Agent         Agent
                               │
                               ▼
                        Consistency Agent
                               │
                               ▼
                          Launch Agent
                               │
                               ▼
                     Final Brand System
                               │
                     ┌─────────┴─────────┐
                     │                   │
                     ▼                   ▼
                MongoDB Atlas       Optional Image
                                   / Moodboard Gen.

This document defines the functional, technical, architectural, database, AI, authentication, workflow, and implementation requirements for NEXIRA.

