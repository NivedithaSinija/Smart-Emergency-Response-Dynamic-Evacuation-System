MENU = """
=== Campus Emergency System ===
1. Report incident
2. Update incident severity
3. Update incident status
4. Block / reopen corridor
5. Set corridor congestion
6. Set exit availability
7. Get evacuation route
8. List all incidents
9. List incidents in ID range (B+ Tree range query)
10. List incidents by severity range
0. Quit
> """


def show_route(result, why):
    if result:
        print("Route :", " -> ".join(result["route"]))
        print(f"Cost  : {result['cost']:.1f}   Exit: {result['exit']}")
    print("Note  :", why)


def show_incidents(incidents):
    if not incidents:
        print("(no incidents)")
    for i in incidents:
        print(f"#{i.id} {i.kind} @ {i.location} sev={i.severity} [{i.status}] {i.created}")


def run(manager):
    g = manager.map.graph
    print("Locations:", ", ".join(g.kinds))
    while True:
        choice = input(MENU).strip()
        try:
            if choice == "1":
                inc = manager.report_incident(input("Type: "), input("Location: "), int(input("Severity 1-5: ")))
                print("Recorded incident #", inc.id)
            elif choice == "2":
                manager.update_severity(int(input("Incident ID: ")), int(input("New severity: ")))
            elif choice == "3":
                manager.update_status(int(input("Incident ID: ")), input("Status (reported/responding/contained/resolved): "))
            elif choice == "4":
                manager.set_corridor_blocked(input("From: "), input("To: "), input("Block? (y/n): ").lower() == "y")
            elif choice == "5":
                manager.set_congestion(input("From: "), input("To: "), float(input("Factor (>=1): ")))
            elif choice == "6":
                manager.set_shelter_available(input("Exit: "), input("Available? (y/n): ").lower() == "y")
            elif choice == "7":
                show_route(*manager.get_route(input("Person: "), input("Current location: ")))
            elif choice == "8":
                show_incidents(manager.store.all())
            elif choice == "9":
                show_incidents(manager.incidents_in_range(int(input("From ID: ")), int(input("To ID: "))))
            elif choice == "10":
                show_incidents(manager.incidents_by_severity(int(input("Min severity: ")), int(input("Max severity: "))))
            elif choice == "0":
                break
        except (ValueError, KeyError) as e:
            print("Error:", e)
