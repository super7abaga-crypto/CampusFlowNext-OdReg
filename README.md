# CampusFlowNext-OdReg — Ticket Management CLI

A beginner-friendly Python command-line application for managing IT support requests at Learn2Earn campus. The system helps staff create tickets, calculate priorities, assign available specialists, track progress, record feedback notes, and monitor workloads.

## Features

### 1. Ticket Management
- Create tickets with automatically generated unique IDs (`T001`, `T002`, `T003`, ...).
- Validate ticket titles, categories, urgency levels, and affected-user counts.
- Automatically calculate ticket priority.
- Review ticket details and edit them before confirming creation.
- List all tickets and view their details.
- Search tickets by title keyword and optional filters.

### 2. Ticket Priority Queue
- View the queue of open tickets ordered by priority.
- Display tickets in the following order: `critical`, `high`, `medium`, then `low`.
- Sort tickets with the same priority by their numeric ticket ID, so `T002` appears before `T010`.
- Exclude tickets that are not open from the open-ticket priority queue.

### 3. Assignment and Workflow
- Assign tickets to recognized staff members.
- Reassign tickets with confirmation when they already have an assignee.
- Prevent assignment changes on resolved or closed tickets until they are reopened.
- Update ticket statuses through the supported workflow.
- Prevent unassigned tickets from progressing through the workflow.

### 4. Staff Recommendations
- Recommend qualified staff based on ticket category and staff availability.
- Account for active workloads when selecting staff.
- Apply a workload threshold so staff members with three or more active tickets are treated as busy and excluded from recommendations.
- Display multiple eligible specialists instead of recommending only one person.
- Identify the leading recommendation and show each candidate's speciality, active ticket count, and status.

### 5. Staff Workload Dashboard
- View staff members and their specialities.
- See whether each staff member is available, busy, or unavailable.
- Track active tickets and their IDs.
- View resolved and closed ticket counts and IDs.
- Count active tickets that have not yet been assigned.

### 6. Feedback Notes
- Add feedback notes to eligible tickets.
- Record the note ID, author, and message.
- Generate unique note IDs such as `N001`, `N002`, and `N003`.
- Validate note content and prevent invalid notes from being added.
- Restrict note creation to tickets whose status is `open` or `in_progress`.

### 7. Reports and Analytics
- Generate a ticket summary report.
- Summarize tickets by status, priority, and category.
- Review staff workload and ticket distribution.

### 8. Learning Quiz
- Take the built-in CampusFlow quiz to practise concepts related to the project.

### 9. Data Persistence
- Save ticket data in JSON format.
- Reload previously saved tickets.
- Validate saved data before accepting it.
- Handle missing or malformed JSON files without silently replacing existing data.
- Preserve ticket information across application sessions.

## Requirements

- Python 3.10 or newer.
- No third-party packages are required for the standard-library functionality described by the project.

## Getting Started

### 1. Clone the repository

```bash
git clone https://github.com/super7abaga-crypto/CampusFlowNext-OdReg.git
cd CampusFlowNext-OdReg
```

### 2. Run the application

From the project root directory, run:

```bash
python3 main.py
```

The application loads saved tickets from `data/tickets.json` when the file exists and passes validation.

### 3. Use the main menu

The current application menu provides the following options:

| Option | Action |
|---|---|
| 1 | Create a ticket |
| 2 | View ticket priority queue |
| 3 | List all tickets |
| 4 | Search tickets |
| 5 | Assign a ticket |
| 6 | Recommend a staff member |
| 7 | Update ticket status |
| 8 | Add a feedback note |
| 9 | View feedback notes |
| 10 | Show ticket report |
| 11 | Show staff workload dashboard |
| 12 | Take the CampusFlow quiz |
| 13 | Save tickets |
| 14 | Reload tickets |
| 0 | Save and exit |

Follow the prompts displayed by the application to complete each operation.

## Ticket Fields

Each ticket contains the following core fields:

| Field | Description |
|---|---|
| `id` | Automatically generated unique ticket ID. |
| `title` | Short description of the issue. |
| `category` | `Network`, `Hardware`, `Software`, or `Other`. |
| `urgency` | `low`, `medium`, or `high`. |
| `affected_users` | Positive whole number representing affected users. |
| `priority` | Automatically calculated as `low`, `medium`, `high`, or `critical`. |
| `status` | Current workflow status. |
| `assigned_to` | Assigned staff member's name, or `null` when unassigned. |
| `history` | Ticket events recorded by the workflow, where supported. |
| `notes` | Feedback notes associated with the ticket. |

Additional fields may be maintained by the application to support timestamps, workflow history, and other implemented functionality.

## Priority Rules

Ticket priority is calculated using the following rules, in order:

1. High urgency **and** 10 or more affected users → `critical`
2. High urgency **or** 10 or more affected users → `high`
3. Medium urgency **or** 3 or more affected users → `medium`
4. Otherwise → `low`

The first matching rule determines the ticket's priority.

## Ticket Status Workflow

The application supports these statuses:

- `open`
- `in_progress`
- `resolved`
- `closed`

The intended workflow is:

```text
open → in_progress → resolved → closed
           ↑             |
           └─────────────┘
```

An open ticket must first move to `in_progress` before it can be resolved. An in-progress ticket must be resolved before it can be closed. Resolved or closed tickets must be reopened to `open` before they can be worked on again or reassigned.

Tickets must be assigned before progressing through the workflow to an assigned-work status.

## Staff Recommendation Rules

The staff recommendation system considers:

- The ticket's category.
- The staff member's speciality.
- Manual staff availability.
- The number of active tickets assigned to each person.
- A workload threshold of three active tickets.

Staff with fewer active tickets are preferred. Staff at or above the workload threshold are excluded from recommendations, allowing the application to suggest other qualified staff when someone is busy.

A staff member who supports more than one speciality has a shared workload across those specialities. For example, assignments to Mr. Kingsley (HOC) in both Network and Software support contribute to his overall active workload.

Recommendations do not automatically assign tickets. Use **option 5 — Assign a ticket** to complete an assignment from the current menu.

## Feedback Notes

Feedback notes contain:

- `note_id` — unique note identifier.
- `author` — name of the person adding the note.
- `message` — feedback text between 5 and 300 characters.

Notes can be added only to tickets with status `open` or `in_progress`. Invalid input must not modify the ticket collection.

## Data Storage

The default storage file is:

```text
data/tickets.json
```

Use option **13** to save tickets and option **14** to reload them.

The JSON file allows ticket data to be stored between sessions. Missing files are treated as a fresh start. Malformed JSON or invalid saved ticket data should produce a clear error rather than silently replacing the existing data.

The `.gitignore` configuration should prevent local ticket data from being committed unintentionally. Keep `data/.gitkeep` tracked when needed to preserve the directory in Git.

## Running the Tests

Run the automated test suite from the project root:

```bash
python3 -m unittest discover -s tests -v
```

The tests cover implemented functionality such as ticket creation, validation, workflow transitions, assignment, staff recommendations, notes, reporting, and persistence.

Run the complete test suite after modifying application logic and before submitting a pull request.

## Project Structure

```text
CampusFlowNext-OdReg/
├── README.md
├── LICENSE
├── .gitignore
├── main.py
├── campusflow/
│   ├── __init__.py
│   ├── tickets.py
│   ├── workflow.py
│   ├── storage.py
│   ├── reports.py
│   ├── staff.py
│   ├── notes.py
│   └── quiz.py
├── data/
│   ├── .gitkeep
│   └── tickets.json
├── docs/
│   ├── ai-learning-log.md
│   ├── baseline-check.md
│   └── design-decisions.md
└── tests/
    ├── test_tickets.py
    ├── test_workflow.py
    ├── test_storage.py
    ├── test_reports.py
    ├── test_notes.py
    ├── test_staff.py
    ├── test_assign_ticket.py
    ├── test_staff_availability_reassignment.py
    ├── test_staff_recommendation_edges.py
    └── test_ticket_persistence.py
```

*Note: The test filenames shown above reflect files present in the recent development context. Check the repository's current directory before treating this tree as exhaustive.*

## Main Modules

| Module | Responsibility |
|---|---|
| `main.py` | Interactive menu and user input. |
| `campusflow/tickets.py` | Ticket creation, validation, IDs, and priority calculation. |
| `campusflow/workflow.py` | Ticket lookup, assignment, status transitions, searching, filtering, and priority queue logic. |
| `campusflow/staff.py` | Staff records, recommendations, and workload summaries. |
| `campusflow/notes.py` | Feedback note creation and validation. |
| `campusflow/storage.py` | JSON saving, loading, and stored-data validation. |
| `campusflow/reports.py` | Ticket formatting and summary reports. |
| `campusflow/quiz.py` | Interactive learning quiz. |

## Suggested Team Workflow

1. Create a feature branch for each new improvement.
2. Implement the change in the appropriate module.
3. Add or update automated tests.
4. Run the full test suite.
5. Open a pull request against `main`.
6. Ask the other engineer to review the implementation and tests.
7. Address review feedback before merging.
8. Keep `docs/design-decisions.md` and `docs/ai-learning-log.md` updated when required by the assignment.


## Project Status

CampusFlowNext-OdReg is an evolving educational project. Features and test coverage may change as development continues. The README should be updated whenever menu options, module names, workflow rules, or other user-facing behaviour changes.

## License

See the [`LICENSE`](LICENSE) file for the project's licensing terms.
