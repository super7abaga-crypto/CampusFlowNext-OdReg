"""Interactive command-line interface for Campusflow-OdIna."""

from campusflow.reports import format_report, format_ticket
from campusflow.storage import DEFAULT_STORAGE_PATH, load_tickets, save_tickets
from campusflow.tickets import create_ticket, calculate_priority
from campusflow.staff import (
    recommend_staff,
    recommend_staff_options,
    summarize_staff_workload,
)

from campusflow.notes import make_note_adder
from campusflow.workflow import assign_ticket, update_ticket_status, search_tickets


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

            print("\nTicket created successfully!")
            print("-" * 60)
            print(format_ticket(ticket))
            print("-" * 60)
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
    """Display the main menu."""
    print("\n===== OD_REG CAMPUSFLOWNEXT TICKET MANAGER =====")
    print("1. Create a ticket")
    print("2. List all tickets")
    print("3. Assign a ticket")
    print("4. Update ticket status")
    print("5. Show ticket report")
    print("6. Save tickets")
    print("7. Reload tickets")
    print("8. Recommend staff")
    print("9. Search tickets")
    print("10. Show staff workload dashboard")
    print("0. Save and exit")


def main():
    try:
        tickets = load_tickets()
    except ValueError as exc:
        print(f"Could not load saved tickets: {exc}")
        print(
            "Fix the data file before starting so saved data is not overwritten."
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

        if choice == "1":
            create_ticket_from_prompt(tickets)

        elif choice == "2":
            show_tickets(tickets)

        elif choice == "3":
            ticket_id = input("Ticket ID: ").strip()

            # Find the ticket before asking for a staff member.
            ticket = next(
                (
                    item
                    for item in tickets
                    if str(item.get("id", "")).strip().upper()
                    == ticket_id.upper()
                ),
                None,
            )

            if ticket is None:
                print(f"Ticket {ticket_id.upper()} was not found.")
                continue

            # Resolved and closed tickets cannot be reassigned.
            status = str(ticket.get("status", "")).strip().lower()

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

            # Ask for confirmation if a staff member is already assigned.
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
                        f"Assignment unchanged. "
                        f"{ticket['id']} remains assigned to "
                        f"{current_assignee}."
                    )
                    continue

            # Ask for the staff member only when assignment is proceeding.
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

            except ValueError as exc:
                print(exc)

        elif choice == "4":
            ticket_id = input("Ticket ID: ")
            status = input(
                "New status (open/in_progress/resolved/closed): "
            )

            try:
                ticket = update_ticket_status(
                    tickets,
                    ticket_id,
                    status,
                )
                print(f"{ticket['id']} status is now {ticket['status']}.")
            except ValueError as exc:
                print(exc)

        elif choice == "5":
            print(format_report(tickets))

        elif choice == "6":
            try:
                save_tickets(tickets)
                print(
                    f"Saved {len(tickets)} ticket(s) "
                    f"to {DEFAULT_STORAGE_PATH}."
                )
            except OSError as exc:
                print(f"Could not save tickets: {exc}")

        elif choice == "7":
            try:
                reloaded = load_tickets()
            except ValueError as exc:
                print(f"Could not reload tickets: {exc}")
            else:
                tickets = reloaded
                print(
                    f"Reloaded {len(tickets)} ticket(s). "
                    "Unsaved changes, if any, were discarded."
                )

        elif choice == "8":
            ticket_id = input("Enter the ticket ID: ").strip().upper()

            ticket = next(
                (
                    item
                    for item in tickets
                    if str(item.get("id", "")).upper() == ticket_id
                ),
                None,
            )

            if ticket is None:
                print(f"Ticket {ticket_id} was not found.")
                continue

            if ticket.get("status") in {"resolved", "closed"}:
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
                    print(f"{index}. {staff['name']}")
                    print(f"   Speciality: {staff['speciality']}")
                    print(f"   Active Tickets: {staff['active']}")
                    print(f"   Status: {staff['status']}")

                    if index == 1:
                        print("   ★ Recommended")

                    print()

                print(
                    "To assign a staff member, select menu option 3."
                )

        elif choice == "9":
            valid_statuses = {
                "open",
                "in_progress",
                "resolved",
                "closed",
            }

            valid_priorities = {
                "critical",
                "high",
                "medium",
                "low",
            }

            valid_categories = {
                "network",
                "hardware",
                "software",
                "other",
            }

            title_keyword = input("Input ticket title: ").strip()

            if not title_keyword:
                print("No keyword detected. Please enter a keyword.")
                continue

            input_status = input(
                "Input preferred status (press Enter to skip): "
            ).strip()

            if input_status:
                input_status = input_status.casefold()

                if input_status not in valid_statuses:
                    print(
                        "Invalid status. Choose open, in_progress, "
                        "resolved, or closed."
                    )
                    continue
            else:
                input_status = None

            input_priority = input(
                "Input preferred priority (press Enter to skip): "
            ).strip()

            if input_priority:
                input_priority = input_priority.casefold()

                if input_priority not in valid_priorities:
                    print(
                        "Invalid priority. Choose critical, high, "
                        "medium, or low."
                    )
                    continue
            else:
                input_priority = None

            input_category = input(
                "Input preferred category (press Enter to skip): "
            ).strip()

            if input_category:
                input_category = input_category.casefold()

                if input_category not in valid_categories:
                    print(
                        "Invalid category. Choose network, hardware, "
                        "software, or other."
                    )
                    continue
            else:
                input_category = None

            input_assignee = input(
                "Input assignee (press Enter to skip): "
            ).strip()

            if input_assignee:
                from campusflow.staff import STAFF_MEMBERS

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
                input_status,
                input_priority,
                input_category,
                input_assignee,
            )

            if searched_tickets:
                show_tickets(searched_tickets)
            else:
                print(
                    f"No tickets found matching '{title_keyword}'."
                )

        elif choice == "10":
            summary = summarize_staff_workload(tickets)

            print(
                "\n===== STAFF WORKLOAD & PERFORMANCE DASHBOARD ====="
            )

            print(
                f"{'Staff Member':<25} "
                f"{'Speciality':<12} "
                f"{'Status':<15} "
                f"{'Active Tickets (Count: IDs)':<32} "
                f"{'Resolved/Closed Tickets (Count: IDs)'}"
            )

            print("-" * 130)

            for staff in summary["staff"]:
                availability = staff["status"]

                active_ids = ", ".join(
                    staff["active_ticket_ids"]
                )

                resolved_closed_ids = ", ".join(
                    staff["resolved_closed_ticket_ids"]
                )

                active_display = (
                    f"{staff['active']} ({active_ids})"
                    if active_ids
                    else "0"
                )

                resolved_closed_display = (
                    f"{staff['resolved_closed']} "
                    f"({resolved_closed_ids})"
                    if resolved_closed_ids
                    else "0"
                )

                print(
                    f"{staff['name']:<25} "
                    f"{staff['speciality']:<12} "
                    f"{availability:<15} "
                    f"{active_display:<32} "
                    f"{resolved_closed_display}"
                )

            print("-" * 130)

            print(
                f"Unassigned active tickets: "
                f"{summary['unassigned']}"
            )

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
    