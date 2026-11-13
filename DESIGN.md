# Triage queue design

The queue uses three `collections.deque` instances, one per triage level. The
queue checks levels from 1 to 3 when selecting the next patient, so critical
patients always precede urgent and standard patients. Appending and removing
from each deque is O(1), and FIFO order within each level is preserved without
re-sorting all waiting patients on every arrival. A single deque would not
prioritize late-arriving critical patients; a sorted list would require
repositioning entries; a heap is possible but adds ordering/tie-breaker
complexity for only three fixed priorities.

The queue's lock protects each state operation. In particular, dequeue checks
the highest-priority non-empty deque and removes its first patient while
holding the same lock. Enqueue uses that lock too, so workers cannot select or
remove the same patient twice, and an enqueue concurrent with dequeue is
serialized before or after that atomic removal.
