from __future__ import annotations

from .stepcheck import StepCheck

_ui = None  # 拡張のライフサイクルで保持


def load_ipython_extension(ipython):
    """%load_ext IBL.utils.stepcheck_ext で呼ばれる。UIを即表示し、ui を注入。"""
    global _ui
    if _ui is None:
        _ui = StepCheck()
    _ui.display()
    # ユーザーの名前空間へ 'ui' を提供（ui.mark(), ui.set_progress() を即使える）
    ipython.push({"ui": _ui})


def unload_ipython_extension(ipython):
    """%unload_ext IBL.utils.stepcheck_ext"""
    global _ui
    _ui = None
