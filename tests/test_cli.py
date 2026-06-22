import subprocess
import tempfile


def test_exec_command_blocks_filesystem():
    """Verify that decoy exec blocks filesystem access attempts."""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.sql', delete=False) as f:
        f.write("SELECT * FROM read_csv_auto('/etc/passwd')")
        f.flush()
        filepath = f.name

    result = subprocess.run(
        ['python', '-m', 'decoy.cli', 'exec', filepath],
        capture_output=True, text=True,
    )

    assert result.returncode != 0
    assert "Permission Error" in result.stderr or "disabled" in result.stderr.lower()