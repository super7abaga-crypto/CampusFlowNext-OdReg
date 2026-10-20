"""Interactive command-line interface for Campusflow-OdIna."""

from campusflow.reports import format_report, format_ticket
from campusflow.storage import DEFAULT_STORAGE_PATH, load_tickets, save_tickets
from campusflow.tickets import create_ticket, calculate_priority
from campusflow.notifications import (
    send_new_ticket_notification,
    send_assignment_notification,
    send_status_notification,
    send_feedback_note_notification,
)
from campusflow.staff import (
    STAFF_MEMBERS,
    recommend_staff_options,
    summarize_staff_workload,
)

from campusflow.quiz import quiz
from campusflow.notes import make_note_adder
from campusflow.workflow import (
    assign_ticket,
    update_ticket_status,
    search_tickets,
    get_priority_queue,
)


def ask_positive_integer(prompt):
    """Prompt until the user enters a positive whole number."""
    while True:
        raw = input(prompt).strip()
        try:
            value = int(raw)
        except ValueError:
            print("Please enter a whole number, such as 1 or 12.")
            continue

        if value <= 0:
            print("The number must be greater than zero.")
            continue

        return value


def show_tickets(tickets):
    if not tickets:
        print("No tickets have been created yet.")
        return

    for ticket in tickets:
        print(format_ticket(ticket))
        print("-" * 80)
        print()


def show_ticket_notes(tickets):
    """Display all notes attached to a selected ticket."""

    ticket_id = input("Enter ticket ID: ").strip().upper()

    ticket = next(
        (
            item
            for item in tickets
            if str(item.get("id", "")).strip().upper()
            == ticket_id
        ),
        None,
    )

    if ticket is None:
        print(f"Ticket {ticket_id} was not found.")
        return

    notes = ticket.get("notes", [])

    print("\n" + "=" * 60)
    print(f"NOTES FOR TICKET {ticket['id']}")
    print("=" * 60)

    if not notes:
        print("No notes have been added to this ticket yet.")
        print("=" * 60)
        return

    for note in notes:
        print(f"\nNote ID: {note.get('note_id', 'N/A')}")
        print(f"Author:  {note.get('author', 'Unknown')}")
        print(f"Message: {note.get('message', '')}")
        print("-" * 60)

    print(f"Total notes: {len(notes)}")
    print("=" * 60)


def show_priority_queue(tickets):
    """Display open tickets ordered by priority and numeric ID."""
    priority_queue = get_priority_queue(tickets)

    print("\n===== TICKET PRIORITY QUEUE =====")

    if not priority_queue:
        print("No open tickets in the priority queue.")
        return

    print(f"{'No.':<5} {'Ticket ID':<12} {'Priority':<12} "
          f"{'Category':<12} Title")
    print("-" * 80)

    for number, ticket in enumerate(priority_queue, start=1):
        ticket_id = ticket.get("id", "Unknown")
        priority = str(ticket.get("priority", "Unknown")).upper()
        category = ticket.get("category", "Other")
        title = ticket.get("title", "Untitled")

        print(
            f"{number:<5} "
            f"{ticket_id:<12} "
            f"{priority:<12} "
            f"{category:<12} "
            f"{title}"
        )

    print("-" * 80)
    print(f"Total open tickets: {len(priority_queue)}")


def create_ticket_from_prompt(tickets):
    """Collect ticket details, allow corrections, and create on confirmation."""

    valid_categories = {
        "network": "Network",
        "hardware": "Hardware",
        "software": "Software",
        "other": "Other",
    }

    valid_urgencies = {
        "low": "low",
        "medium": "medium",
        "high": "high",
    }

    # Step 1: Collect the initial ticket details.
    while True:
        title = input("Ticket title: ").strip()

        if title:
            break

        print("Error: Ticket title cannot be empty. Please try again.")

    while True:
        category_input = input(
            "Category (Network/Hardware/Software/Other): "
        ).strip()

        category = valid_categories.get(category_input.casefold())

        if category is not None:
            break

        print("Error: Choose Network, Hardware, Software, or Other.")

    while True:
        urgency_input = input(
            "Urgency (low/medium/high): "
        ).strip()

        urgency = valid_urgencies.get(urgency_input.casefold())

        if urgency is not None:
            break

        print("Error: Choose low, medium, or high.")

    affected_users = ask_positive_integer("Number of affected users: ")

    # Step 2: Review, edit, confirm, or cancel.
    while True:
        priority = calculate_priority(urgency, affected_users)

        print("\n" + "=" * 45)
        print("          TICKET REVIEW")
        print("=" * 45)
        print(f"Title:          {title}")
        print(f"Category:       {category}")
        print(f"Urgency:        {urgency.title()}")
        print(f"Affected users: {affected_users}")
        print(f"Priority:       {priority.upper()}")
        print("=" * 45)

        print("1. Create ticket")
        print("2. Edit title")
        print("3. Edit category")
        print("4. Edit urgency")
        print("5. Edit affected users")
        print("6. Cancel ticket creation")

        choice = input("Choose an option: ").strip()

        
        if choice == "1":
            try:
                ticket = create_ticket(
                    tickets,
                    title,
                    category,
                    urgency,
                    affected_users,
                )
            except ValueError as exc:
                print(f"Could not create ticket: {exc}")
                return

            # Save the ticket before attempting email notification.
            try:
                save_tickets(tickets, DEFAULT_STORAGE_PATH)
            except Exception as exc:
                print(
                    "\nWarning: The ticket was created in memory, "
                    "but saving it to disk failed."
                )
                print(f"Save error: {exc}")
                print(
                    "Do not close the application until the ticket "
                    "has been saved successfully."
                )
                return

            print("\nTicket created and saved successfully!")
            print("-" * 60)
            print(format_ticket(ticket))
            print("-" * 60)

            # Email failure must not undo ticket creation.
            try:
                send_new_ticket_notification(ticket)
            except Exception as exc:
                print(
                    "\nWARNING: The ticket was saved, but the "
                    "email notification could not be sent."
                )
                print(f"Reason: {exc}")
            else:
                print("Email notification sent to the support inbox.")

            return


        elif choice == "2":
            while True:
                new_title = input("Enter the new title: ").strip()

                if new_title:
                    title = new_title
                    break

                print("Error: Ticket title cannot be empty.")

        elif choice == "3":
            while True:
                category_input = input(
                    "New category (Network/Hardware/Software/Other): "
                ).strip()

                new_category = valid_categories.get(
                    category_input.casefold()
                )

                if new_category is not None:
                    category = new_category
                    break

                print(
                    "Error: Choose Network, Hardware, Software, or Other."
                )

        elif choice == "4":
            while True:
                urgency_input = input(
                    "New urgency (low/medium/high): "
                ).strip()

                new_urgency = valid_urgencies.get(
                    urgency_input.casefold()
                )

                if new_urgency is not None:
                    urgency = new_urgency
                    break

                print("Error: Choose low, medium, or high.")

        elif choice == "5":
            affected_users = ask_positive_integer(
                "Enter the new number of affected users: "
            )

        elif choice == "6":
            print("Ticket creation cancelled. No ticket was created.")
            return

        else:
            print("Invalid option. Please choose from 1 to 6.")


def print_menu():
    """Display the main menu with bold headings and clear sections."""

    BOLD = "\033[1m"
    RESET = "\033[0m"

    print()
    print("=" * 60)
    print(BOLD + "         OD_REG CAMPUSFLOWNEXT TICKET MANAGER" + RESET)
    print("=" * 60)

    print()
    print(BOLD +"  TICKET MANAGEMENT" + RESET)
    print("  " + "-" * 56)
    print("   1.  Create a ticket")
    print("   2.  View ticket priority queue")
    print("   3.  List all tickets")
    print("   4.  Search tickets")

    print()
    print(BOLD +"  TICKET OPERATIONS" + RESET)
    print("  " + "-" * 56)
    print("   5.  Assign a ticket")
    print("   6.  Recommend a staff member")
    print("   7.  Update ticket status")

    print()
    print(BOLD +"  FEEDBACK NOTES" + RESET)
    print("  " + "-" * 56)
    print("   8.  Add a feedback note")
    print("   9.  View feedback notes")

    print()
    print(BOLD +"  REPORTS AND ANALYTICS" + RESET)
    print("  " + "-" * 56)
    print("  10.  Show ticket report")
    print("  11.  Show staff workload dashboard")

    print()
    print(BOLD +"  LEARNING" + RESET)
    print("  " + "-" * 56)
    print("  12.  Take the CampusFlow quiz")

    print()
    print(BOLD +"  DATA MANAGEMENT" + RESET)
    print("  " + "-" * 56)
    print("  13.  Save tickets")
    print("  14.  Reload tickets")

    print()
    print("-" * 60)
    print("   0.  SAVE AND EXIT" + RESET)
    print("=" * 60)


def main():
    """Run the CampusFlow ticket manager CLI."""
    try:
        tickets = load_tickets()
    except ValueError as exc:
        print(f"Could not load saved tickets: {exc}")
        print(
            "Fix the data file before starting so saved data "
            "is not overwritten."
        )
        return

    add_note = make_note_adder(tickets)

    print(
        f"Loaded {len(tickets)} ticket(s) from "
        f"{DEFAULT_STORAGE_PATH} (if the file existed)."
    )

    while True:
        print_menu()
        choice = input("Choose an option: ").strip()

        # 1. Create a ticket
        if choice == "1":
            create_ticket_from_prompt(tickets)
            
        # 2. View ticket priority queue
        elif choice == "2":
            show_priority_queue(tickets)

        # 3. List all tickets
        elif choice == "3":
            show_tickets(tickets)

        # 4. Search tickets
        elif choice == "4":
            valid_statuses = {
                "open", "in_progress", "resolved", "closed",
            }
            valid_priorities = {
                "critical", "high", "medium", "low",
            }
            valid_categories = {
                "network", "hardware", "software", "other",
            }

            title_keyword = input("Input ticket title: ").strip()

            if not title_keyword:
                print("No keyword detected. Please enter a keyword.")
                continue

            input_status = input(
                "Input preferred status (press Enter to skip): "
            ).strip().casefold()

            if input_status and input_status not in valid_statuses:
                print(
                    "Invalid status. Choose open, in_progress, "
                    "resolved, or closed."
                )
                continue

            input_priority = input(
                "Input preferred priority (press Enter to skip): "
            ).strip().casefold()

            if input_priority and input_priority not in valid_priorities:
                print(
                    "Invalid priority. Choose critical, high, "
                    "medium, or low."
                )
                continue

            input_category = input(
                "Input preferred category (press Enter to skip): "
            ).strip().casefold()

            if input_category and input_category not in valid_categories:
                print(
                    "Invalid category. Choose network, hardware, "
                    "software, or other."
                )
                continue

            input_assignee = input(
                "Input assignee (press Enter to skip): "
            ).strip()

            if input_assignee:
                valid_assignees = {
                    member["name"].strip().casefold()
                    for member in STAFF_MEMBERS
                }

                if input_assignee.casefold() not in valid_assignees:
                    print(
                        "Invalid assignee. Choose a recognized "
                        "staff member."
                    )
                    continue

                input_assignee = input_assignee.casefold()
            else:
                input_assignee = None

            searched_tickets = search_tickets(
                tickets,
                title_keyword,
                input_status or None,
                input_priority or None,
                input_category or None,
                input_assignee,
            )

            if searched_tickets:
                show_tickets(searched_tickets)
            else:
                print(
                    f"No tickets found matching '{title_keyword}'."
                )

        # 5. Assign a ticket
        elif choice == "5":
            ticket_id = input("Ticket ID: ").strip()

            ticket = next(
                (
                    item for item in tickets
                    if str(item.get("id", "")).strip().upper()
                    == ticket_id.upper()
                ),
                None,
            )

            if ticket is None:
                print(f"Ticket {ticket_id.upper()} was not found.")
                continue

            status = str(
                ticket.get("status", "")
            ).strip().lower()

            if status in {"resolved", "closed"}:
                print(
                    f"Ticket {ticket['id']} cannot be reassigned "
                    f"because its status is {status}."
                )
                print("Reopen the ticket before changing its assignment.")
                continue

            current_assignee = str(
                ticket.get("assigned_to") or ""
            ).strip()

            if current_assignee:
                print(
                    f"\nTicket {ticket['id']} is already assigned "
                    f"to {current_assignee}."
                )

                answer = input(
                    "Do you want to reassign this ticket? (y/N): "
                ).strip().casefold()

                if answer not in {"y", "yes"}:
                    print(
                        f"Assignment unchanged. {ticket['id']} "
                        f"remains assigned to {current_assignee}."
                    )
                    continue

            assignee = input("Assign to (name): ").strip()

            
            try:
                ticket = assign_ticket(tickets, ticket_id, assignee)

                if current_assignee:
                    if ticket["assigned_to"] == current_assignee:
                        print(
                            f"{ticket['id']} remains assigned to "
                            f"{ticket['assigned_to']}."
                        )
                    else:
                        print(
                            f"Successfully reassigned {ticket['id']} "
                            f"from {current_assignee} to "
                            f"{ticket['assigned_to']}."
                        )
                else:
                    print(
                        f"Successfully assigned {ticket['id']} "
                        f"to {ticket['assigned_to']}."
                    )

                try:
                    save_tickets(tickets)
                except OSError as exc:
                    print(
                        f"Warning: assignment could not be saved: {exc}"
                    )

                try:
                    send_assignment_notification(ticket)
                    print("Assignment email sent to the staff member.")
                except Exception as exc:
                    print(
                        f"Warning: assignment email was not sent: {exc}"
                    )

            except ValueError as exc:
                print(exc)

        # 6. Recommend a staff member
        elif choice == "6":
            ticket_id = input(
                "Enter the ticket ID: "
            ).strip().upper()

            ticket = next(
                (
                    item for item in tickets
                    if str(item.get("id", "")).strip().upper()
                    == ticket_id
                ),
                None,
            )

            if ticket is None:
                print(f"Ticket {ticket_id} was not found.")
                continue

            if str(ticket.get("status", "")).lower() in {
                "resolved", "closed",
            }:
                print("This ticket is already resolved or closed.")
                continue

            try:
                recommendations = recommend_staff_options(
                    ticket,
                    tickets,
                )
            except ValueError as exc:
                print(f"Could not recommend staff: {exc}")
                continue

            if not recommendations:
                print(
                    f"No available specialist found for the "
                    f"{ticket['category']} category."
                )
            else:
                print("\nStaff Recommendation")
                print("--------------------")

                for index, staff in enumerate(
                    recommendations,
                    start=1,
                ):
                    print(f"{index}. \033[1m{staff['name']}\033[0m")
                    print(f"   Speciality: {staff['speciality']}")
                    print(f"   Active Tickets: {staff['active']}")
                    print(f"   Status: {staff['status']}")

                    if index == 1:
                        print("   ★ Recommended")

                    print()

                print(
                    "To assign a staff member, select menu option 5."
                )
        
        # 7. Update ticket status
        elif choice == "7":
            ticket_id = input("Ticket ID: ").strip()
            status = input(
                "New status (open/in_progress/resolved/closed): "
            ).strip()

            ticket_before = next(
                (
                    item for item in tickets
                    if str(item.get("id", "")).strip().upper()
                    == ticket_id.upper()
                ),
                None,
            )

            if ticket_before is None:
                print(f"Ticket {ticket_id.upper()} was not found.")
                continue

            previous_status = ticket_before.get("status", "unknown")

            try:
                ticket = update_ticket_status(
                    tickets,
                    ticket_id,
                    status,
                )

                print(
                    f"{ticket['id']} status is now "
                    f"{ticket['status']}."
                )

                if ticket["status"] != previous_status:
                    try:
                        save_tickets(tickets)
                    except OSError as exc:
                        print(
                            f"Warning: status change could not be saved: {exc}"
                        )

                    try:
                        send_status_notification(
                            ticket,
                            previous_status,
                        )
                        print(
                            "Status notification sent to central support."
                        )
                    except Exception as exc:
                        print(
                            f"Warning: status email was not sent: {exc}"
                        )

            except ValueError as exc:
                print(exc)

                # 8. Add a feedback note
        elif choice == "8":
            ticket_id = input("Enter ticket ID: ").strip()
            author = input("Enter your name: ").strip()
            message = input("Enter feedback note: ")

            try:
                new_note = add_note(ticket_id, author, message)

                print(
                    f"Feedback note added successfully! "
                    f"Note ID: {new_note['note_id']}"
                )

                try:
                    save_tickets(tickets)
                except OSError as exc:
                    print(
                        f"Warning: feedback note could not be saved: {exc}"
                    )

                try:
                    ticket = next(
                        item for item in tickets
                        if str(item.get("id", "")).strip().upper()
                        == ticket_id.upper()
                    )

                    send_feedback_note_notification(ticket, new_note)
                    print(
                        "Feedback notification sent to central support."
                    )

                except Exception as exc:
                    print(
                        f"Warning: feedback email was not sent: {exc}"
                    )

            except ValueError as exc:
                print(f"Error: {exc}")

        # 9. View feedback notes
        elif choice == "9":
            show_ticket_notes(tickets)
        # 10. Show ticket report
        elif choice == "10":
            print(format_report(tickets))
        # 11. Show staff workload dashboard    
        elif choice == "11":
            summary = summarize_staff_workload(tickets)

            print("\n" + "=" * 70)
            print("       STAFF WORKLOAD & PERFORMANCE DASHBOARD")
            print("=" * 70)

            for staff in summary["staff"]:
                active_ids = ", ".join(
                    staff["active_ticket_ids"]
                )
                resolved_ids = ", ".join(
                    staff["resolved_closed_ticket_ids"]
                )

                
                print(f"\nStaff Member: \033[1m{staff['name']}\033[0m")
                print(f"{'Speciality:':<16} {staff['speciality']}")
                print(f"{'Availability:':<16} {staff['status']}")

                print("-" * 50)
                print(f"{'Active Tickets:':<20} {staff['active']}")
                print(f"{'Open:':<20} {staff['open']}")
                print(f"{'In Progress:':<20} {staff['in_progress']}")
                print(f"{'Ticket IDs:':<20} {active_ids or 'None'}")

                print(
                    f"{'Completed Tickets:':<20} "
                    f"{staff['resolved_closed']}"
                )
                print(f"{'Ticket IDs:':<20} {resolved_ids or 'None'}")
                print("-" * 50)


            print("\n" + "=" * 70)
            print(
                "UNASSIGNED ACTIVE TICKETS: "
                f"{summary['unassigned']}"
            )
            print("=" * 70)

            for ticket in summary["unassigned_tickets"]:
                print(
                    f"\n{ticket.get('id', 'Unknown')} | "
                    f"{ticket.get('title', 'Untitled')}"
                )
                print(
                    f"  Category: {ticket.get('category', 'Unknown')}"
                )
                print(
                    f"  Priority: {ticket.get('priority', 'Unknown')}"
                )
                print(
                    f"  Status: {ticket.get('status', 'Unknown')}"
                )
        # 12. Take the CampusFlow quiz
        elif choice == "12":
            quiz()
        # 13. Save tickets
        elif choice == "13":
            try:
                save_tickets(tickets)
                print(
                    f"Saved {len(tickets)} ticket(s) "
                    f"to {DEFAULT_STORAGE_PATH}."
                )
            except OSError as exc:
                print(f"Could not save tickets: {exc}")
        # 14. Reload tickets
        elif choice == "14":
            try:
                reloaded = load_tickets()
            except ValueError as exc:
                print(f"Could not reload tickets: {exc}")
            else:
                tickets = reloaded
                add_note = make_note_adder(tickets)
                print(
                    f"Reloaded {len(tickets)} ticket(s). "
                    "Unsaved changes, if any, were discarded."
                )
        # 0. Save and exit
        elif choice == "0":
            try:
                save_tickets(tickets)
            except OSError as exc:
                print(f"Could not save tickets: {exc}")

                answer = input(
                    "Exit anyway without saving? (y/N): "
                ).strip().lower()

                if answer != "y":
                    continue
            else:
                print(
                    f"Saved {len(tickets)} ticket(s). "
                    "Thank You and Goodbye!"
                )

            break

        else:
            print("Unknown option. Choose one of the menu numbers.")


if __name__ == "__main__":
    main()