from drift.core.global_workspace import GlobalWorkspace
import pytest
import os
import tempfile

class TestSQLiteIntegration:

    def setup_method(self):
        """Prepare an isolated database file for each test run."""
        self.temp_dir = tempfile.TemporaryDirectory()
        self.temp_db_path = os.path.join(self.temp_dir.name, "test_workspace.db")
        self.global_workspace = GlobalWorkspace(db_path=self.temp_db_path)

    def teardown_method(self):
        """Clean up the temporary database file."""
        self.temp_dir.cleanup()

    def test_database_initialization(self):
        """Ensure that the database initializes without errors."""
        assert os.path.exists(self.temp_db_path), "Database file should exist after initialization."

    def test_cycle_count_persistence(self):
        """Verify persistence of the cycle count in the SQLite database."""
        initial_count = self.global_workspace.state.cycle_count
        self.global_workspace.state.cycle_count += 1
        self.global_workspace._save_state()

        new_global_workspace = GlobalWorkspace(db_path=self.temp_db_path)
        assert new_global_workspace.state.cycle_count == initial_count + 1, "Cycle count should persist across instances."

    def test_competition_saves_to_db(self):
        """Ensure submission competition saves history to the database."""
        self.global_workspace.submit(
            source="test_module",
            content="test_content",
            salience=0.9
        )
        self.global_workspace.compete()  # Should save data to DB
        history = self.global_workspace.get_history(limit=1)

        assert len(history) == 1, "History should contain one record after a competition."
        assert history[0]["source"] == "test_module", "History source should match submission source."
        assert "test_content" in history[0]["content"], "Content should match the submitted content."

if __name__ == "__main__":
    pytest.main([__file__])