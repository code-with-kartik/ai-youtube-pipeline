from src.constants import STAGE_STATES
ALLOWED = {"PENDING":{"RUNNING","SKIPPED","BLOCKED"},"RUNNING":{"COMPLETED","FAILED","BLOCKED","REGENERATE"},"FAILED":{"RUNNING","BLOCKED"},"REGENERATE":{"RUNNING","BLOCKED"},"COMPLETED":set(),"BLOCKED":set(),"SKIPPED":set()}
class InvalidTransition(ValueError): pass
def validate_transition(current: str, target: str, *, force: bool = False) -> None:
    if current not in STAGE_STATES or target not in STAGE_STATES: raise InvalidTransition("unknown state")
    if current == target: return
    if force and target == "RUNNING": return
    if target not in ALLOWED[current]: raise InvalidTransition(f"transition {current} -> {target} is not allowed")

