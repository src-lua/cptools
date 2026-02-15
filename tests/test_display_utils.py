"""
Unit tests for lib/display_utils.py
"""
from cptools.lib.display_utils import get_status_emoji


class TestGetStatusEmoji:
    """Tests for get_status_emoji function."""

    def test_pending_statuses(self):
        """Test pending/not attempted statuses."""
        assert get_status_emoji('~') == '⬜'
        assert get_status_emoji('pending') == '⬜'
        assert get_status_emoji('not attempted') == '⬜'
        assert get_status_emoji('') == '⬜'

    def test_accepted_statuses(self):
        """Test accepted/solved statuses."""
        assert get_status_emoji('AC') == '✅'
        assert get_status_emoji('ac') == '✅'
        assert get_status_emoji('Accepted') == '✅'
        assert get_status_emoji('Solved') == '✅'
        assert get_status_emoji('ACCEPTED') == '✅'

    def test_in_progress_statuses(self):
        """Test in progress statuses."""
        assert get_status_emoji('WIP') == '🔄'
        assert get_status_emoji('wip') == '🔄'
        assert get_status_emoji('Attempting') == '🔄'
        assert get_status_emoji('in progress') == '🔄'

    def test_wrong_answer(self):
        """Test wrong answer status."""
        assert get_status_emoji('WA') == '⚠️'
        assert get_status_emoji('wa') == '⚠️'
        assert get_status_emoji('Wrong Answer') == '⚠️'

    def test_time_limit_exceeded(self):
        """Test time limit exceeded status."""
        assert get_status_emoji('TLE') == '⏱️'
        assert get_status_emoji('tle') == '⏱️'
        assert get_status_emoji('Time Limit') == '⏱️'
        assert get_status_emoji('Time Limit Exceeded') == '⏱️'

    def test_memory_limit_exceeded(self):
        """Test memory limit exceeded status."""
        assert get_status_emoji('MLE') == '💾'
        assert get_status_emoji('mle') == '💾'
        assert get_status_emoji('Memory Limit') == '💾'
        assert get_status_emoji('Memory Limit Exceeded') == '💾'

    def test_runtime_error(self):
        """Test runtime error status."""
        assert get_status_emoji('RE') == '💥'
        assert get_status_emoji('re') == '💥'
        assert get_status_emoji('Runtime Error') == '💥'

    def test_unknown_status(self):
        """Test unknown/unsolved status."""
        assert get_status_emoji('UNKNOWN') == '❌'
        assert get_status_emoji('Not Solved') == '❌'
        assert get_status_emoji('XYZ') == '❌'

    def test_case_insensitive(self):
        """Test that status matching is case insensitive."""
        assert get_status_emoji('Ac') == '✅'
        assert get_status_emoji('Wa') == '⚠️'
        assert get_status_emoji('Tle') == '⏱️'
        assert get_status_emoji('Mle') == '💾'
        assert get_status_emoji('Re') == '💥'
        assert get_status_emoji('Wip') == '🔄'

    def test_whitespace_handling(self):
        """Test that extra whitespace is handled."""
        assert get_status_emoji('  AC  ') == '✅'
        assert get_status_emoji(' WA ') == '⚠️'
        assert get_status_emoji('  ~  ') == '⬜'
