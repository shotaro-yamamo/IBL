from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Union

try:
    import ipywidgets as widgets
except Exception as e:
    raise RuntimeError("ipywidgets>=8 が必要です。") from e

from IPython import get_ipython
from IPython.display import display

# ==== ハードコーディングしたステップ一覧 ====
STEPS = [
    "1. GPU確認",
    "2. ライブラリ導入",
    "3. 外部ストレージ準備",
    "4. モデルロード(7B)",
    "5. スモークテスト",
    "6. API起動",
]
TITLE = "実行チェックリスト"
STEP_COMMENT_PREFIX = "# STEP:"


@dataclass
class StepState:
    ok: bool = False
    msg: str = ""
    ts: Optional[str] = None


class StepTracker:
    def __init__(self, steps: List[str]):
        self.steps = steps
        self.state: Dict[str, StepState] = {s: StepState() for s in steps}
        self._checks = {s: widgets.Checkbox(description=s, value=False, disabled=True) for s in steps}
        self._notes = {s: widgets.HTML("") for s in steps}
        self._rows = widgets.VBox([widgets.HBox([self._checks[s], self._notes[s]]) for s in steps])
        self._bar = widgets.IntProgress(value=0, min=0, max=len(steps), description="Progress")
        self.panel = widgets.VBox([widgets.HTML(f"<h3>{TITLE}</h3>"), self._rows, self._bar])

    def show(self): display(self.panel); self._refresh()
    def done(self, step: str, msg: str = ""):
        from datetime import datetime
        ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.state[step] = StepState(True, msg, ts)
        self._checks[step].value = True
        self._notes[step].value = f"<span style='color:gray'>OK @ {ts} {msg}</span>"
        self._refresh()
    def fail(self, step: str, err: Union[Exception,str]):
        from datetime import datetime
        ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.state[step] = StepState(False, str(err), ts)
        self._checks[step].value = False
        self._notes[step].value = f"<span style='color:#d33'>NG @ {ts} — {err}</span>"
        self._refresh()
    def all_done(self) -> bool: return all(st.ok for st in self.state.values())
    def summary(self) -> Dict[str, Dict[str, Any]]:
        return {k: {"ok": v.ok, "msg": v.msg, "ts": v.ts} for k,v in self.state.items()}
    def _refresh(self):
        okc = sum(1 for st in self.state.values() if st.ok)
        self._bar.value = okc
        self._bar.bar_style = "success" if okc == len(self.steps) else ("info" if okc>0 else "")


# === モジュールスコープ ===
_tracker: Optional[StepTracker] = None
_registered = False

def get_tracker() -> StepTracker:
    if _tracker is None:
        raise RuntimeError("stepcheck: not initialized")
    return _tracker

def all_done(): return get_tracker().all_done()
def summary(): return get_tracker().summary()
def done(step, msg=""): get_tracker().done(step, msg)
def fail(step, err): get_tracker().fail(step, err)

# === IPython拡張 ===
def load_ipython_extension(ip):
    global _tracker, _registered
    if _tracker is None:
        _tracker = StepTracker(STEPS)
        _tracker.show()

    # %%step <name>
    from IPython.core.magic import register_cell_magic
    @register_cell_magic
    def step(line, cell):
        name = (line or "").strip()
        res = ip.run_cell(cell)
        if getattr(res, "success", False): _tracker.done(name)
        else: _tracker.fail(name, getattr(res, "error_in_exec", None) or "Execution failed")

    if not _registered:
        def _after(result):
            try:
                ih = ip.user_ns.get("_ih", [""])
                src = ih[-1] if ih else ""
                first = src.splitlines()[0].strip() if src else ""
                if first.startswith(STEP_COMMENT_PREFIX):
                    name = first.split(":",1)[1].strip()
                    if getattr(result, "success", False): _tracker.done(name)
                    else: _tracker.fail(name, getattr(result, "error_in_exec", None) or "Execution failed")
            except: pass
        ip.events.register("post_run_cell", _after)
        _registered = True

def unload_ipython_extension(ip): pass
