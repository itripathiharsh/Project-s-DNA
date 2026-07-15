class GitHistoryError(Exception):
    pass


class GitNotInstalledError(GitHistoryError):
    def __init__(self):
        super().__init__("Git is not installed or not found in PATH")


class GitCommandError(GitHistoryError):
    def __init__(self, command: str, exit_code: int, stderr: str):
        self.command = command
        self.exit_code = exit_code
        self.stderr = stderr
        super().__init__(f"Git command failed (exit {exit_code}): {command}\n{stderr}")
