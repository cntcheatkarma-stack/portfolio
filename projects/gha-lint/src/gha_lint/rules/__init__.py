from .unpinned_actions import UnpinnedActions
from .script_injection import ScriptInjection
from .permissions import BroadPermissions

ALL_RULES = [UnpinnedActions(), ScriptInjection(), BroadPermissions()]
