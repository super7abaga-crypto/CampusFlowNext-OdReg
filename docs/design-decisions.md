# CampusFlow Design Decisions

## 1. Ticket Collection
Tickets will be stored in a Python list of dictionaries while
the application is running. The collection will be passed to
functions that need to access or modify tickets. Every ticket
will have a unique ID.

## 2. Error Handling
Functions will raise appropriate exceptions, such as ValueError,
when input is invalid. The CLI will catch these exceptions and
display clear, user-friendly error messages. Invalid input must
not corrupt or partially create a ticket.

## 3. Function Return Values
Ticket creation will return the newly created ticket dictionary.
Successful assignment and status-update operations will modify
the existing ticket and return the updated dictionary. Functions
that return collections will return lists. Invalid operations
will raise appropriate exceptions.

## 4. JSON Persistence
The storage.py module will own all JSON loading and saving.
Tickets will be stored in data/tickets.json. The application
will load tickets at startup and save changes through the storage
module. A missing file will allow a fresh start. Malformed JSON
will produce a clear error without silently discarding existing
data. Runtime ticket data will be excluded from Git.

## 5. Automated Testing
CampusFlow will use Python's built-in unittest framework.
Business-logic functions will accept arguments and return results
or raise exceptions without requesting interactive input. Tests
will cover valid inputs, invalid inputs, priority rules, edge cases,
and relevant workflow and persistence behaviour. 



# CampusFlowNext Design Decsions

### `add_note(ticket_id, author, message)`

Engineer A provides the note-creation function for Engineer B to use.

The function is created from the ticket collection using:

```python
from campusflow.notes import make_note_adder

add_note = make_note_adder(tickets)
```

Engineer B can then add a note with:

```python
add_note("T001", "Engineer B", "Checked the network connection.")
```

The function accepts:

- `ticket_id` — ID of the ticket receiving the note.
- `author` — person adding the note.
- `message` — note text, between 5 and 300 characters.

Notes can only be added to tickets with status `open` or `in_progress`.

The function automatically generates the next unique note ID, such as `N001`, `N002`, `N003`, etc.

If the input is invalid, the function raises `ValueError` and does not modify the ticket collection.


CampusFlowNext — New Feature Design Decisions (Engineer B - REGINA CHIJIOKE)
1. Ticket Notes
Notes will be stored inside each ticket as a list of dictionaries. Each note will contain a unique note ID, an author, and a message. The make_note_adder(tickets) function will create an add_note(ticket_id, author, message) function that can be used to add notes to tickets.

Notes can only be added to tickets with open or in_progress status. Note messages must contain between 5 and 300 characters after trimming whitespace. Invalid note attempts will raise ValueError without modifying the ticket collection or consuming a note ID.
2. Staff Recommendation
The staff recommendation feature will suggest suitable staff members based on the ticket category, staff availability, and current workload. Available staff members with the appropriate speciality will be considered for recommendation. Staff members who are unavailable or have reached the busy threshold will not be recommended.

Recommendations will prioritize eligible staff members with lower active workloads. This helps distribute tickets more effectively and prevents already busy staff members from receiving additional recommendations.
3. Staff Workload Dashboard
The staff workload dashboard will summarize each staff member's current workload using the existing ticket collection. It will display staff names, specialities, availability status, active ticket counts and IDs, and resolved or closed ticket counts and IDs.

The dashboard will also show the number of unassigned active tickets. It will provide a read-only overview of workload distribution without modifying tickets or assignments.
4. Ticket Search
The ticket search feature will allow users to find tickets by title keyword and optionally filter the results by status, priority, category, and assignee.

Title matching will be case-insensitive. When multiple filters are provided, they will be combined using AND logic, meaning a ticket must satisfy every selected filter to appear in the results. Empty optional filters will be ignored, while invalid filter values will be rejected.

The search feature will return matching tickets without modifying the original ticket collection.
5. CampusFlow Quiz
The CampusFlow quiz feature will provide an interactive way for users to check their understanding of the application's concepts and behaviour. It will be accessible through a dedicated CLI menu option and will operate separately from the core ticket-management workflow.

Keeping the quiz in its own module makes it easier to maintain and update without unnecessarily changing the ticket-management logic.
