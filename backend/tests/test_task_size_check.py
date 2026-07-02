from backend.app.checks.task_size_check import is_valid_fargate_size


def test_valid_fargate_combinations() -> None:
    assert is_valid_fargate_size(256, 512)
    assert is_valid_fargate_size(512, 4096)
    assert is_valid_fargate_size(1024, 8192)
    assert is_valid_fargate_size(2048, 16384)
    assert is_valid_fargate_size(4096, 30720)


def test_invalid_fargate_combinations() -> None:
    assert not is_valid_fargate_size(256, 4096)
    assert not is_valid_fargate_size(512, 512)
    assert not is_valid_fargate_size(1024, 1024)
    assert not is_valid_fargate_size(8192, 16384)
