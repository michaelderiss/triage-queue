"""Priority-based patient intake queue and terminal interface."""

from collections import deque
from dataclasses import dataclass, field
from datetime import datetime
from threading import Lock
from typing import Deque, Dict, List, Optional


TRIAGE_LEVELS = (1, 2, 3)


@dataclass(frozen=True)
class Patient:
    """A patient waiting for care."""

    name: str
    triage_level: int
    arrived_at: datetime = field(default_factory=datetime.now)

    def __post_init__(self) -> None:
        if not self.name.strip():
            raise ValueError("Patient name cannot be empty.")
        if self.triage_level not in TRIAGE_LEVELS:
            raise ValueError("Triage level must be 1 (critical), 2 (urgent), or 3 (standard).")
        if not isinstance(self.arrived_at, datetime):
            raise TypeError("arrived_at must be a datetime.")


class EmptyQueueError(IndexError):
    """Raised when an operation requires a patient but the queue is empty."""


class TriageQueue:
    """Thread-safe priority queue with FIFO ordering within each triage level."""

    def __init__(self) -> None:
        self._queues: Dict[int, Deque[Patient]] = {
            level: deque() for level in TRIAGE_LEVELS
        }
        self._lock = Lock()

    def enqueue(self, patient: Patient) -> None:
        """Add a patient to the end of their triage-level queue."""
        if not isinstance(patient, Patient):
            raise TypeError("patient must be a Patient instance.")
        with self._lock:
            self._queues[patient.triage_level].append(patient)

    def dequeue(self) -> Patient:
        """Remove and return the highest-priority patient."""
        with self._lock:
            for level in TRIAGE_LEVELS:
                if self._queues[level]:
                    return self._queues[level].popleft()
        raise EmptyQueueError("No patients are waiting.")

    def peek(self) -> Patient:
        """Return the highest-priority patient without removing them."""
        with self._lock:
            for level in TRIAGE_LEVELS:
                if self._queues[level]:
                    return self._queues[level][0]
        raise EmptyQueueError("No patients are waiting.")

    def list_queue(self) -> List[Patient]:
        """Return waiting patients in the order they will be attended."""
        with self._lock:
            return [
                patient
                for level in TRIAGE_LEVELS
                for patient in self._queues[level]
            ]

    def stats(self) -> Dict[int, int]:
        """Return the number of waiting patients at each triage level."""
        with self._lock:
            return {
                level: len(self._queues[level])
                for level in TRIAGE_LEVELS
            }


def _prompt(text: str) -> Optional[str]:
    try:
        return input(text)
    except EOFError:
        return None


def main() -> None:
    queue = TriageQueue()
    actions = {
        "1": "Add a patient",
        "2": "Call the next patient",
        "3": "View the queue",
        "4": "View queue stats",
        "5": "Peek at the next patient",
        "6": "Exit",
    }

    while True:
        print("\nTriage Queue")
        for number, action in actions.items():
            print("{}. {}".format(number, action))

        choice = _prompt("Choose an option: ")
        if choice is None or choice.strip() == "6":
            print("Goodbye.")
            return

        choice = choice.strip()
        if choice == "1":
            name = _prompt("Patient name: ")
            level_text = _prompt("Triage level (1-3): ")
            if name is None or level_text is None:
                print("\nGoodbye.")
                return
            try:
                patient = Patient(name.strip(), int(level_text.strip()))
                queue.enqueue(patient)
                print("Added {} (level {}).".format(patient.name, patient.triage_level))
            except ValueError as error:
                print("Invalid patient: {}".format(error))
        elif choice == "2":
            try:
                patient = queue.dequeue()
                print("Calling {} (level {}).".format(patient.name, patient.triage_level))
            except EmptyQueueError as error:
                print(error)
        elif choice == "3":
            patients = queue.list_queue()
            if not patients:
                print("No patients are waiting.")
            else:
                for position, patient in enumerate(patients, start=1):
                    print(
                        "{}. {} - level {} - arrived {}".format(
                            position,
                            patient.name,
                            patient.triage_level,
                            patient.arrived_at.isoformat(sep=" ", timespec="seconds"),
                        )
                    )
        elif choice == "4":
            counts = queue.stats()
            print(
                "Critical (1): {}; Urgent (2): {}; Standard (3): {}".format(
                    counts[1], counts[2], counts[3]
                )
            )
        elif choice == "5":
            try:
                patient = queue.peek()
                print("Next: {} (level {}).".format(patient.name, patient.triage_level))
            except EmptyQueueError as error:
                print(error)
        else:
            print("Invalid option. Choose a number from 1 to 6.")


if __name__ == "__main__":
    main()
