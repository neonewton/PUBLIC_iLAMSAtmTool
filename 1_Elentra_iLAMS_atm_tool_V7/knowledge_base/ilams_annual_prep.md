Knowledge Base: LAMS Annual Preparation (iLAMS SSO)
KB-META-001 — Document Overview

Title: LAMS Annual Preparation – Courses, Users & Groupings
Prepared by: Nelton Tan
Last updated: 28 Nov 2025
Applies from: June 2024 onwards

Purpose:
To document the annual operational steps required to prepare iLAMS (SSO-enabled) for a new Academic Year, including course creation, user mapping, groupings, and lesson deployment.

KB-META-002 — Systems & URLs

Systems involved:

LKCMedicine Learn (Elentra): https://ntu.elentra.cloud

LAMS Production (SSO): https://ilams.lamsinternational.com

KB-CONCEPT-001 — High-Level Workflow

Annual Preparation Workflow Order:

Import Courses

Import Users

Import Groupings

Add Lessons & Conduct UAT

Important rule:
Each step depends on the completion of the previous step. Course IDs must exist before users or groupings are imported.

KB-CONCEPT-002 — Staff vs Student Mapping Model
Staff Mapping Logic

One staff email can map to multiple courses

Roles can differ per course

Roles include: Monitor, Author, Group Manager, Learner

Mapping is individual-based

Student Mapping Logic

Many student emails mapped to cohort courses

Students receive Learner role only

Mapping is course-based and bulk

KB-STEP-001 — Step 1: Import Courses (Overview)

Objective:
Create or update courses in LAMS for the upcoming Academic Year.

Dependency:
None (first step)

Output:
Courses created with assigned Course IDs

KB-STEP-001A — Import Courses: Template Download

Navigation Path:
LAMS Admin → Import Courses

Template:
lams_groups_template_.xls

KB-STEP-001B — Import Courses: Preparation Rules

Only populate course name

Leave all other columns empty

Include:

Existing courses

New courses for upcoming AY

KB-STEP-001C — Extracting Course IDs

Navigation Path:
LAMS → Course Management

Action:
Extract and record Course ID for each imported course.

Usage:
Course IDs are required for:

User imports

Group imports

Lesson deployment

KB-STEP-002 — Step 2: Import Users (Overview)

Objective:
Map users (staff or students) to courses with correct roles.

Dependency:
Courses and Course IDs must exist.

KB-STEP-002A — User Import Templates

Templates used:

lams_role_template.xls → Role mapping

lams_users_template.xls → New user creation (Y1 only)

KB-STAFF-001 — Staff User Import Rules

Key rules:

One Excel file per staff email

One staff email can map to multiple courses

Do not bulk multiple staff into one file

Roles are configurable per course.

KB-STAFF-002 — Staff Import File Naming Convention

Recommended format:

CE_AD_<staff_name>_YYYYMMDD.xls


Example:

CE_AD_andrea.pavesi_20260105.xls

KB-STAFF-003 — Staff Import Template Fields

Required fields:

organisation → Course ID

login → Staff email

roles → Assigned role(s)

add to lessons → yes / no

KB-STUDENT-001 — Student Categories

Students are handled in two groups:

Y1: New users (account creation required)

Y2–Y5: Existing users (role mapping only)

KB-STUDENT-002 — Academic Year Operational Timeline

Typical period: Mid-July to August

Key risks:

Late exam result processing

LOA changes

Last-minute additions/removals

Operational advice:
Avoid taking leave during this period.

KB-STUDENT-003 — Y1 Student User Creation

When required:
For new Year 1 students only.

Template:
lams_users_template.xls

Mandatory fields:

login

password

first_name

last_name

email

country = Australia

KB-STUDENT-004 — Y1 User Creation File Naming

Format:

lams_users_template_Y1_YYYYMMDD.xls


Example:

lams_users_template_Y1_20260801.xls

KB-STUDENT-005 — Y2–Y5 Student Course Mapping

Template:
lams_role_template.xls

Rules:

One Excel file per Course ID

Contains all students for that course

Role = Learner only

KB-STUDENT-006 — Student Mapping File Naming

Recommended format:

Cohort_<YearOfEntry>Y<Year>_CID<CourseID>_YYYYMMDD_<StudentCount>students.xls


Example:

Cohort_2023Y3_CID40215_20250721_280students.xls

KB-STEP-003 — Step 3: Import Groupings (Teams)

Objective:
Assign students into teams/groups within a course.

Dependency:
Users must already be mapped to the course.

KB-STEP-003A — Groupings Navigation

Path:
LAMS Index Page → ⋮ (kebab menu) → Groupings
→ Create New → Course Group View
→ Import teams from template

KB-STEP-003B — Grouping Template Rules

Required fields:

Email

Team name

Team naming format:

Team_01
Team_02

KB-STEP-003C — Cohort Grouping Notes

Y1 & Y2: Mainstream groups only

Y3: Sub-teams exist but usually ignored in LAMS

Y4 & Y5: Streams (A/B/C/D) must be respected

KB-STEP-004 — Step 4: Lesson Deployment & UAT

Performed after:

Courses imported

Users mapped

Groupings created

Activities include:

Lesson creation

iRAT / TBL setup

Access validation

User Acceptance Testing (UAT)

KB-OPS-001 — Operational Best Practices

Always verify Course IDs before imports

Use dated, descriptive filenames

Expect multiple student list revisions

Never bulk-import staff users

Document all mid-AY changes