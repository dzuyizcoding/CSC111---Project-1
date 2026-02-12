"""CSC111 Assignment 1: Text Adventure Game - Simulator

Instructions (READ THIS FIRST!)
===============================

This Python module contains code for Assignment 1 that allows a user to simulate the
playthrough of the game. Please consult the handout for instructions and details.

Do NOT modify any function/method headers, type contracts, etc. in this class (similar
to CSC110 assignments).

Copyright and Usage Information
===============================

This file is provided solely for the personal and private use of students
taking CSC111 at the University of Toronto St. George campus. All forms of
distribution of this code, whether as given or with any changes, are
expressly prohibited. For more information on copyright for CSC111 materials,
please consult our Course Syllabus.

This file is Copyright (c) 2026 CSC111 Teaching Team
"""
from __future__ import annotations
from event_logger import Event, EventList
from adventure import AdventureGame


# Note: We have completed the Location class for you. Do NOT modify it here for A1.

class AdventureGameSimulation:
    """A simulation of an adventure game playthrough.
    """
    _game: AdventureGame
    _events: EventList

    def __init__(self, game_data_file: str, initial_location_id: int, commands: list[str]) -> None:
        """
        Initialize a new game simulation based on the given game data, that runs through the given commands.

        Preconditions:
        - len(commands) > 0
        - all commands in the given list are valid commands when starting from the location at initial_location_id
        """
        self._events = EventList()
        self._game = AdventureGame(game_data_file, initial_location_id, simulate=True)

        # Add initial location event
        start_loc = self._game.get_location()
        first_event = Event(start_loc.id_num, start_loc.long_description)
        self._events.add_event(first_event, None)

        self.generate_events(commands)

    def generate_events(self, commands: list[str]) -> None:
        """Generate events in this simulation, based on current_location and commands."""

        for command in commands:
            parts = command.split()

            # NEVER allow arena to run during simulation (ignore arena commands entirely)
            if parts and parts[0] in {"rock", "paper", "scissors", "shadow"}:
                continue
            if command == "quit":
                continue

            # Snapshot BEFORE
            prev_loc_id = self._game.current_location_id
            prev_loc = self._game.get_location()

            prev_inv = tuple(getattr(self._game, "inventory",
                                     getattr(self._game, "_inventory", [])))

            prev_loc_items = tuple(getattr(prev_loc, "items", []))

            # Apply command
            self._game.process_choice(command)

            # Snapshot AFTER
            new_loc_id = self._game.current_location_id
            new_loc = self._game.get_location()

            new_inv = tuple(getattr(self._game, "inventory",
                                    getattr(self._game, "_inventory", [])))

            new_loc_items = tuple(getattr(new_loc, "items", []))

            # Log ONLY if something actually changed
            if (
                    new_loc_id != prev_loc_id
                    or new_inv != prev_inv
                    or new_loc_items != prev_loc_items
            ):
                new_event = Event(
                    new_loc_id,
                    self._game.describe_current_location(force_long=False)
                )
                self._events.add_event(new_event, command)

            if not self._game.ongoing:
                break

    def get_id_log(self) -> list[int]:
        """
        Get back a list of all location IDs in the order that they are visited within a game simulation
        that follows the given commands.
        """
        # Note: We have completed this method for you. Do NOT modify it for A1.
        return self._events.get_id_log()

    def run(self) -> None:
        """
        Run the game simulation and log location descriptions.
        """
        # Note: We have completed this method for you. Do NOT modify it for A1.
        current_event = self._events.first

        while current_event:
            print(current_event.description)
            if current_event is not self._events.last:
                print("You choose:", current_event.next_command)
            current_event = current_event.next


if __name__ == "__main__":
    import python_ta
    python_ta.check_all(config={
        'max-line-length': 120,
        'disable': ['R1705', 'E9998', 'E9999', 'static_type_checker']
    })

    # WIN DEMO
    win_walkthrough = [
        "go east",  # 1 -> 2
        "take laptop charger",  # stay 2
        "go south",  # 2 -> 3
        "go west",  # 3 -> 4
        "take USB drive",  # stay 4
        "go west",  # 4 -> 5
        "take lucky mug",  # stay 5
        "go east",  # 5 -> 4
        "go north",  # 4 -> 1
        # arena happens here when you take laptop in normal gameplay
        "take laptop",  # stay 1 (after winning arena gate)
        "go west",  # 1 -> 6
        "drop laptop",
        "drop USB drive",
        "drop lucky mug",
        "drop laptop charger",
    ]

    expected_log = [1, 2, 2, 3, 4, 4, 5, 5, 4, 1, 1, 6, 6, 6, 6, 6]

    sim = AdventureGameSimulation('game_data.json', 1, win_walkthrough)
    print("EXPECTED:", expected_log)
    print("ACTUAL  :", sim.get_id_log())
    assert expected_log == sim.get_id_log()

    # LOSE DEMO
    lose_demo = ["go east", "go west"] * 15
    expected_log = [1] + [2, 1] * 15
    sim = AdventureGameSimulation('game_data.json', 1, lose_demo)
    print("---- CHECKING ----")
    print("EXPECTED:", expected_log)
    print("ACTUAL  :", sim.get_id_log())

    assert expected_log == sim.get_id_log()

    # INVENTORY DEMO
    inventory_demo = [
        "inventory",
        "go south",
        "take lucky mug",
        "inventory",
        "go north",
        "drop lucky mug",
        "inventory"
    ]

    expected_log = [6, 5, 5, 6, 6]

    sim = AdventureGameSimulation('game_data.json', 6, inventory_demo)
    print("---- CHECKING ----")
    print("EXPECTED:", expected_log)
    print("ACTUAL  :", sim.get_id_log())

    assert expected_log == sim.get_id_log()

    # SCORE DEMO
    scores_demo = [
        "go south",
        "take lucky mug",
        "score",
        "go north",
        "drop lucky mug",
        "score"
    ]

    expected_log = [6, 5, 5, 6, 6]
    sim = AdventureGameSimulation('game_data.json', 6, scores_demo)
    print("---- CHECKING ----")
    print("EXPECTED:", expected_log)
    print("ACTUAL  :", sim.get_id_log())

    assert expected_log == sim.get_id_log()

    # ENHANCEMENT 1
    enhancement1_demo = [
        "go east",
        "go south",
        "go west",
        "go north",
        "take laptop",
        "quit",
        "inventory"
    ]

    expected_log = [1, 2, 3, 4, 1, 1]

    sim = AdventureGameSimulation('game_data.json', 1, enhancement1_demo)
    print("---- CHECKING ----")
    print("EXPECTED:", expected_log)
    print("ACTUAL  :", sim.get_id_log())

    assert expected_log == sim.get_id_log()

    # ENAHNCEMENT 2
    enhancement2_demo = [
        "go east",
        "go south",
        "take laptop charger",
        "undo",
        "undo"
    ]

    expected_log = [1, 2, 3, 2, 1]

    sim = AdventureGameSimulation('game_data.json', 1, enhancement2_demo)
    print("---- CHECKING ----")
    print("EXPECTED:", expected_log)
    print("ACTUAL  :", sim.get_id_log())

    assert expected_log == sim.get_id_log()

    # ENHANCEMENT 3
    enhancement3_demo = [
        "go east",
        "take laptop charger",
        "restart",
        "go west"
    ]

    expected_log = [1, 2, 2, 1, 6]

    sim = AdventureGameSimulation('game_data.json', 1, enhancement3_demo)
    print("---- CHECKING ----")
    print("EXPECTED:", expected_log)
    print("ACTUAL  :", sim.get_id_log())

    assert expected_log == sim.get_id_log()
