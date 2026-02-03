"""
Unit tests for lib/path_utils.py
"""
from lib.path_utils import detect_platform_from_path


class TestDetectPlatformFromPath:
    """Tests for detect_platform_from_path function."""

    def test_codeforces_contest(self):
        """Test detecting Codeforces contest."""
        platform, contest = detect_platform_from_path('/home/user/Codeforces/1234/A.cpp')
        assert platform == 'Codeforces'
        assert contest == '1234'

    def test_codeforces_gym(self):
        """Test detecting Codeforces Gym contest."""
        platform, contest = detect_platform_from_path('/home/user/Codeforces/Gym/12345/A.cpp')
        assert platform == 'Codeforces Gym'
        assert contest == '12345'

        # Test with directory (no file)
        platform, contest = detect_platform_from_path('/home/user/Codeforces/Gym/12345')
        assert platform == 'Codeforces Gym'
        assert contest == '12345'

    def test_atcoder_contest(self):
        """Test detecting AtCoder contest."""
        platform, contest = detect_platform_from_path('/home/user/AtCoder/abc123/a.cpp')
        assert platform == 'AtCoder'
        assert contest == 'abc123'

    def test_vjudge_contest(self):
        """Test detecting vJudge contest."""
        platform, contest = detect_platform_from_path('/home/user/vJudge/123456/A.cpp')
        assert platform == 'vJudge'
        assert contest == '123456'

    def test_yosupo(self):
        """Test detecting Yosupo."""
        platform, contest = detect_platform_from_path('/home/user/Yosupo/problem_name')
        assert platform == 'Yosupo'
        assert contest == 'problem_name'

    def test_trainings(self):
        """Test detecting Trainings."""
        platform, contest = detect_platform_from_path('/home/user/Trainings/week1/A.cpp')
        assert platform == 'Trainings'
        assert contest == 'week1'

    def test_other_with_subfolder(self):
        """Test detecting Other with custom subfolder name."""
        platform, contest = detect_platform_from_path('/home/user/Other/CustomContest/A.cpp')
        assert platform == 'CustomContest'
        assert contest == 'CustomContest'

    def test_unknown_platform(self):
        """Test fallback for unknown platform."""
        platform, contest = detect_platform_from_path('/home/user/SomeContest/A.cpp')
        assert platform == 'Contest'
        assert contest == 'A.cpp'

        # Test with directory
        platform, contest = detect_platform_from_path('/home/user/SomeContest')
        assert platform == 'Contest'
        assert contest == 'SomeContest'

    def test_relative_path(self):
        """Test with relative path."""
        platform, contest = detect_platform_from_path('Codeforces/1234/A.cpp')
        assert platform == 'Codeforces'
        assert contest == '1234'

    def test_codeforces_problemset(self):
        """Test detecting Codeforces Problemset."""
        platform, contest = detect_platform_from_path('/home/user/Codeforces/Problemset/1A.cpp')
        assert platform == 'Codeforces'
        assert contest == 'Problemset'
