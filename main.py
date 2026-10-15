"""Interactive command-line interface for Campusflow-OdIna."""

from campusflow.reports import format_report, format_ticket
from campusflow.storage import DEFAULT_STORAGE_PATH, load_tickets, save_tickets
from campusflow.tickets import create_ticket
from campusflow.staff import recommend_staff
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
    """Create a ticket and return to the field that needs correction."""

    # Step 1: Ask for the ticket title.
    while True:
        title = input("Ticket title: ").strip()

        if not title:
            print("Error: Ticket title cannot be empty. Please try again.")
            continue

        break

    # Step 2: Ask for a valid category.
    valid_categories = {
        "network": "Network",
        "hardware": "Hardware",
        "software": "Software",
        "other": "Other",
    }

    while True:
        category_input = input(
            "Category (Network/Hardware/Software/Other): "
        ).strip()

        category = valid_categories.get(category_input.casefold())

        if category is None:
            print(
                f"Error: '{category_input}' is not a valid category."
            )
            print("Please choose Network, Hardware, Software, or Other.")
            continue

        break

    # Step 3: Ask for a valid urgency.
    valid_urgencies = {
        "low": "low",
        "medium": "medium",
        "high": "high",
    }

    while True:
        urgency_input = input(
            "Urgency (low/medium/high): "
        ).strip()

        urgency = valid_urgencies.get(urgency_input.casefold())

        if urgency is None:
            print(
                f"Error: '{urgency_input}' is not a valid urgency."
            )
            print("Please choose low, medium, or high.")
            continue

        break

    # Step 4: Ask for the number of affected users.
    # ask_positive_integer or repeats the question
    # when the input is not an integer.
    affected_users = ask_positive_integer(
        "Number of affected users: "
    )

    # Step 5: Create the ticket.
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


def print_menu():
    print("\n=== OdReg-CampusFlowNext Ticket Manager ===")
    print("1. Create a ticket")
    print("2. List tickets")
    print("3. Assign a ticket")
    print("4. Update ticket status")
    print("5. Show report")
    print("6. Save tickets")
    print("7. Reload tickets from disk")
    print("8. Recommend staff for a ticket")
    print("9. Search tickets")
    print("0. Save and exit")


def main():
    try:
        tickets = load_tickets()
    except ValueError as exc:
        print(f"Could not load saved tickets: {exc}")
        print("Fix the data file before starting so saved data is not overwritten.")
        return

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
            ticket_id = input("Ticket ID: ")
            assignee = input("Assign to (name): ")

            try:
                ticket = assign_ticket(tickets, ticket_id, assignee)
                print(f"Assigned {ticket['id']} to {ticket['assigned_to']}.")
            except ValueError as exc:
                print(exc)

        elif choice == "4":
            ticket_id = input("Ticket ID: ")
            status = input(
                "New status (open/in_progress/resolved/closed): "
            )

            try:
                ticket = update_ticket_status(tickets, ticket_id, status)
                print(f"{ticket['id']} status is now {ticket['status']}.")
            except ValueError as exc:
                print(exc)

        elif choice == "5":
            print(format_report(tickets))

        elif choice == "6":
            try:
                save_tickets(tickets)
                print(f"Saved {len(tickets)} ticket(s) to {DEFAULT_STORAGE_PATH}.")
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
                recommendation = recommend_staff(ticket, tickets)
            except ValueError as exc:
                print(f"Could not recommend staff: {exc}")
                continue

            if recommendation is None:
                print(
                    f"No available specialist found for the "
                    f"{ticket['category']} category."
                )
            else:
                print("\nStaff Recommendation")
                print("--------------------")
                print(f"Name: {recommendation['name']}")
                print(f"Speciality: {recommendation['speciality']}")
                print("\nTo assign this person, select menu option 3.")

        elif choice == "9":
            valid_statuses = {"open", "in_progress", "resolved", "closed"}
            valid_priorities = {"critical", "high", "medium", "low"}
            valid_categories = {"network", "hardware", "software", "other"}

            title_keyword = input("Input ticket title: ").strip()
            if not title_keyword:
                print("No keyword detected. Please enter a keyword.")
                continue

            input_status = input("Input preferred status (press Enter to skip): ").strip()
            if  input_status:
                input_status = input_status.casefold()
                if input_status not in valid_statuses:
                    print("Invalid status. Choose open, in_progress, resolved, or closed.")
                    continue
            else:
                input_status = None
            input_priority = input("Input preferred priority (press Enter to skip): ").strip()
            if input_priority:
                input_priority = input_priority.casefold()
                if input_priority not in valid_priorities:
                    print("Invalid priority. Choose critical, high, medium, or low.")
                    continue
            else:
                input_priority = None

            input_category = input("Input preferred category (press Enter to skip): ").strip()
            if input_category:
                input_category = input_category.casefold()
                if input_category not in valid_categories:
                    print("Invalid category. Choose network, hardware, software, or other.")
                    continue
            else:
                input_category = None

            input_assignee = input("Input assignee (press Enter to skip): ").strip()
            if input_assignee:
                from campusflow.staff import STAFF_MEMBERS

                valid_assignees = {
                    member["name"].strip().casefold()
                    for member in STAFF_MEMBERS
                }

                if input_assignee.casefold() not in valid_assignees:
                    print("Invalid assignee. Choose a recognized staff member.")
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
                print(f"No tickets found matching '{title_keyword}'.")


            

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
