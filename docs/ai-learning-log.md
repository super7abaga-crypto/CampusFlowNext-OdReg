# AI and Team Learning Log

Use this file to record how the team understood, checked, and adapted ideas
while building Campusflow-OdIna.

Keep entries honest: record what we actually asked, tested, changed, and learned.

## Entry 1 — Ticket Validation

- **Date:** October 9, 2026
- **Engineer(s):** Engineer A  ODEH ODEH
- **Problem or question:** How should invalid ticket inputs such as blank titles, invalid categories, invalid urgency values, and invalid affected-user counts be handled?
- **Explanation or resource used:** AI explanation of Python input validation and conditional checks.
- **What we understood in our own words:** Validation should happen before a ticket is added to the ticket list. This prevents invalid ticket data from entering the system.
- **What we changed:** Added validation checks for ticket title, category, urgency, and affected users.
- **How we tested it:** Ran unit tests using `python -m unittest discover -s tests -v` and tested invalid input cases.
- **What we would do differently next time:** Test additional unusual inputs earlier instead of waiting until the main implementation is complete.

## Entry 2 — Ticket Priority

- **Date:** October 9, 2026
- **Engineer(s):** Engineer A  ODEH ODEH
- **Problem or question:** How should ticket priority be calculated from urgency and the number of affected users?
- **Explanation or resource used:** AI explanation of conditional logic and `if`/`elif` evaluation order.
- **What we understood in our own words:** Python checks conditions in order and stops when it finds the first true condition. Therefore, the most specific priority rule needs to be checked before broader rules.
- **What we changed:** Ordered the priority conditions from critical to high, medium, and low.
- **How we tested it:** Created tests covering different urgency and affected-user combinations.
- **What we would do differently next time:** Write the priority rules down before implementing them so the expected behaviour is clear.

## Entry 3 — Storage

- **Date:** October 9, 2026
- **Engineer(s):** Engineer B  INALEGWU JULIET
- **Problem or question:** How can tickets be saved and loaded after the program closes?
- **Explanation or resource used:** AI explanation of JSON persistence using `json.dump()` and `json.load()`.
- **What we understood in our own words:** `json.dump()` writes Python data to a JSON file, while `json.load()` reads JSON data back into Python.
- **What we changed:** Implemented separate storage functions for saving and loading tickets.
- **How we tested it:** Saved sample tickets, loaded them again, and compared the loaded data with the original data.
- **What we would do differently next time:** Add tests for missing or invalid JSON files earlier.

## Entry 4 — Workflow

- **Date:** October 9, 2026
- **Engineer(s):** Engineer B  INALEGWU JULIET
- **Problem or question:** Why should workflow functions be tested separately from the CLI?
- **Explanation or resource used:** AI explanation of separation of concerns and unit testing.
- **What we understood in our own words:** Business logic can be tested independently from `input()` and `print()`. This makes the code easier to test and would make it easier to replace the CLI with a web interface later.
- **What we changed:** Kept ticket workflow operations separate from the CLI code.
- **How we tested it:** Tested assignment and status-change functions directly through unit tests.
- **What we would do differently next time:** Design the business logic and user interface as separate parts from the beginning.

# Team Reflection

- **Most useful concept learned:** Separating business logic from CLI input/output so the core ticket operations can be tested independently.
