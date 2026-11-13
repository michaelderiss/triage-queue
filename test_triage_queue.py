import unittest

from triage_queue import EmptyQueueError, Patient, TriageQueue


class TriageQueueTests(unittest.TestCase):
    def setUp(self):
        self.queue = TriageQueue()

    def test_priority_and_fifo_order(self):
        standard = Patient("Standard", 3)
        urgent_first = Patient("Urgent first", 2)
        urgent_second = Patient("Urgent second", 2)
        critical = Patient("Critical", 1)

        for patient in (standard, urgent_first, urgent_second, critical):
            self.queue.enqueue(patient)

        self.assertEqual(
            self.queue.list_queue(),
            [critical, urgent_first, urgent_second, standard],
        )

    def test_peek_does_not_remove_patient_and_stats_include_empty_levels(self):
        patient = Patient("Urgent", 2)
        self.queue.enqueue(patient)

        self.assertIs(self.queue.peek(), patient)
        self.assertEqual(self.queue.stats(), {1: 0, 2: 1, 3: 0})
        self.assertIs(self.queue.dequeue(), patient)

    def test_empty_dequeue_and_peek_raise_meaningful_error(self):
        with self.assertRaisesRegex(EmptyQueueError, "No patients are waiting"):
            self.queue.dequeue()
        with self.assertRaisesRegex(EmptyQueueError, "No patients are waiting"):
            self.queue.peek()

    def test_patient_rejects_invalid_triage_level_and_blank_name(self):
        with self.assertRaises(ValueError):
            Patient("Patient", 4)
        with self.assertRaises(ValueError):
            Patient("  ", 1)


if __name__ == "__main__":
    unittest.main()
