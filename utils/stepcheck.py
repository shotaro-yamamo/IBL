# IBL/utils/stepcheck.py
from __future__ import annotations

from typing import List, Optional

from IPython.display import display
from ipywidgets import HTML, Checkbox, IntProgress, Layout, VBox


class StepCheck:
    """
    チェックボックス＋進行度だけを表示し、更新はコード側から行うシンプルUI。
    手順リストはハードコーディング。
    """
    # ハードコーディングされた手順
    DEFAULT_STEPS = ["GPU確認", "データ読み込み", "前処理", "学習", "評価"]

    def __init__(self, title: str = "処理フロー", progress_max: int = 100) -> None:
        self.title: str = title
        self.step_labels: List[str] = list(self.DEFAULT_STEPS)

        self._steps = [Checkbox(description=s, indent=False) for s in self.step_labels]
        self._progress = IntProgress(min=0, max=int(progress_max), value=0, layout=Layout(width="100%"))
        self._progress_label = HTML(f"進行度: 0/{int(progress_max)} (0%)")

        self._ui = VBox(
            [
                HTML(f"<h3 style='margin:6px 0;'>{self.title}</h3>"),
                VBox(self._steps),
                self._progress,
                self._progress_label,
            ],
            layout=Layout(gap="8px"),
        )

    # --- 表示 ---
    def display(self) -> None:
        display(self._ui)

    # --- 更新API ---
    def mark(self, label: str, checked: bool = True) -> bool:
        cb = next((cb for cb in self._steps if cb.description == label), None)
        if cb is None:
            return False
        cb.value = bool(checked)
        return True

    def set_progress(self, value: int) -> None:
        v = max(self._progress.min, min(self._progress.max, int(value)))
        self._progress.value = v
        percent = int(round(100 * v / max(1, self._progress.max)))
        self._progress_label.value = f"進行度: {v}/{self._progress.max} ({percent}%)"

    def reset(self) -> None:
        for cb in self._steps:
            cb.value = False
        self.set_progress(0)
