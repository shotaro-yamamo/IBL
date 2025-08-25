# IBL/utils/stepcheck_ext.py
from IPython.display import display

from .stepcheck import StepCheck

_ui = None  # 拡張のライフサイクルで保持

def load_ipython_extension(ipython):
    """%load_ext IBL.utils.stepcheck_ext で呼ばれる。UIを即表示。"""
    global _ui
    if _ui is None:
        _ui = StepCheck()
    _ui.display()
    # 使いやすいようにユーザーNSへも注入（ui.mark(...), ui.set_progress(...))
    ipython.push({"ui": _ui})

def unload_ipython_extension(ipython):
    """%unload_ext IBL.utils.stepcheck_ext"""
    global _ui
    _ui = None
