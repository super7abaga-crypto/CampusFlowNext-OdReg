# CampusFlow Baseline Check

## 1. Audited Commit

- Commit SHA: 8da12ecd3ece3b21a5861c11c624adb7e2abd934
- Project: OdIna-Campusflow — Ticket Management CLI
- Language: Python
- Minimum Python version: Python 3.10
- Dependencies: Python standard library; no third-party packages required.

## 2. Application Run

- Run command: `python3 main.py`
- Working directory: Project root directory.
- Expected behavior: The command starts the ticket management CLI.
- Actual result: Not yet verified.

## 3. Automated Tests

- Test framework: Python `unittest`
- Command from README: `python3 -m unittest discover -s tests -v`
- Previously observed test command: `python3 -m unittest discover -s tests -p "test_*.py" -v`
- Baseline test result: 41 tests passed; 0 failures or errors.
- Test command: `python3 -m unittest discover -s tests -p "test_*.py" -v`
- Actual result: `Ran 41 tests in 0.006s — OK`.

## 4. Features Documented in README

The baseline application is documented as supporting:

- Ticket creation with automatic IDs such as T001 and T002.
- Validation of ticket titles, categories, urgency, and affected-user counts.
- Automatic priority calculation.
- Listing and finding tickets.
- Assigning tickets to team members.
- Updating ticket statuses.
- Summary reports.
- Saving and loading tickets through JSON.
- Automated unit tests.

## 5. Ticket Rules Documented in README

### Categories
- Network
- Hardware
- Software
- Other

### Urgency
- Low
- Medium
- High

### Priority
1. High urgency and 10 or more affected users: Critical.
2. High urgency or 10 or more affected users: High.
3. Medium urgency or 3 or more affected users: Medium.
4. Otherwise: Low.

### Statuses
- Open
- In progress
- Resolved
- Closed

### Assignment
- An assigned staff member's name is stored in `assigned_to`.
- Unassigned tickets use `null`.

## 6. Manual Input Tests

### Test 1: Valid ticket creation
- Planned input: A ticket with a non-empty title, valid category, valid urgency, and a positive whole number of affected users.
- Expected result: The ticket is created and receives an ID and calculated priority.
- Actual result: Not yet tested.

### Test 2: Invalid ticket input
- Planned input: A blank title or zero affected users.
- Expected result: Invalid input is rejected.
- Actual result: Not yet tested.

### Test 3: Workflow validation
- Planned input: Attempt to move an unassigned ticket to resolved or closed.
- Expected result: To be verified against the baseline application.
- Actual result: Not yet tested.

## 7. Audit Improvements

## 3. Automated Tests

- Test framework: Python `unittest`
- Command from README: `python3 -m unittest discover -s tests -v`
- Baseline test command executed: `python3 -m unittest discover -s tests -p "test_*.py" -v`
- Baseline commit tested: `8da12ecd3ece3b21a5861c11c624adb7e2abd934`
- Baseline test result: 41 tests passed; 0 failures or errors.
- Actual result: `Ran 41 tests in 0.006s — OK`.
- Note: These results apply to the original baseline version, not the updated feature branch.

Potential areas to investigate include:
- Input validation and boundary cases.
- Status transition restrictions.
- Assignment rules.
- Ticket ID uniqueness after loading saved data.
- JSON loading and error handling.
- Search, filtering, sorting, and report accuracy.
- Regression tests for any confirmed defects.

These are investigation areas, not confirmed bugs.

## 8. Conclusion

The README documents a Python command-line ticket management application with ticket creation, assignment, workflow management, reporting, and JSON persistence.

The application run, automated baseline test results, manual test outcomes, and confirmed audit improvements must still be verified.