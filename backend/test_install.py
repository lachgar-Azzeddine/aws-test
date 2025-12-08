"""Unit tests for the install.py module."""

import unittest
import install
from repository import initialize_database


class AppTest(unittest.TestCase):
    """Unit tests for the install.py module."""

    def my_status_handler(self, data, runner_config):
        print("\nStatus handler : -------------------------------------------\n")
        print(data)
        print(runner_config)

    def my_event_handler(self, data):
        print("\nEvent handler : -------------------------------------------\n")
        print(data)

    def test_call_playbook(self):
        """Test the call_playbook function."""
        DATABASE_URL = "./tests/harmonisation_runner.db"
        _, Session = initialize_database(DATABASE_URL)

        install.call_role("testrole", Session)
