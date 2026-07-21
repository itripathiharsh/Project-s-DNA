from contextvars import ContextVar

current_branch: ContextVar[str] = ContextVar("current_branch", default="")
