from __future__ import annotations

from typing import List, Optional

from IPython.display import display
from ipywidgets import HTML, Checkbox, IntProgress, Layout, VBox


class StepCheck:
    """
    チェックボックス + 進行度バーのみを表示するJupyter用最小UI。
    - 手順リストは**ハードコーディング**（変更UIなし）
    - 手動操作UI（ボタン等）は提供しない
    - 更新はコード側から mark()/set_progress() を呼ぶ
    """

    # ハードコーディングされた手順（変更不要）
    DEFAULT_STEPS: List[str] = ["GPU確認", "データ読み込み", "前処理", "学習", "評価"]

    def __init__(self, title: str = "処理フロー", progress_max: int = 100) -> None:
        self.title = title
        self.progress_max = int(progress_max)

        # ウィジェット
        self._steps = [Checkbox(description=s, indent=False) for s in self.DEFAULT_STEPS]
        self._progress = IntProgress(min=0, max=self.progress_max, value=0, layout=Layout(width="100%"))
        self._label = HTML(self._label_text(0))

        # レイアウト（チェックボックス + 進行度のみ）
        self._ui = VBox(
            [
                HTML(f"<h3 style='margin:6px 0;'>{self.title}</h3>"),
                VBox(self._steps),
                self._progress,
                self._label,
            ],
            layout=Layout(gap="8px"),
        )

    # ===== Public APIs =====
    def display(self) -> None:
        """ノートブックにUIを表示"""
        display(self._ui)

    def mark(self, label: str, checked: bool = True) -> bool:
        """
        指定ラベルのチェックON/OFF。
        返り値: 更新できたら True（見つからなければ False）
        """
        cb = next((c for c in self._steps if c.description == label), None)
        if cb is None:
            return False
        cb.value = bool(checked)
        return True

    def set_progress(self, value: int) -> None:
        """進行度を更新（0..progress_max）"""
        v = max(self._progress.min, min(self._progress.max, int(value)))
        self._progress.value = v
        self._label.value = self._label_text(v)

    def reset(self) -> None:
        """全チェックOFF & 進行度0"""
        for c in self._steps:
            c.value = False
        self.set_progress(0)

    def is_done(self, label: str) -> Optional[bool]:
        """指定ラベルのチェック状態（見つからなければ None）"""
        cb = next((c for c in self._steps if c.description == label), None)
        return None if cb is None else bool(cb.value)

    # ===== Internal =====
    def _label_text(self, v: int) -> str:
        pct = int(round(100 * v / max(1, self._progress.max)))
        return f"進行度: {v}/{self._progress.max} ({pct}%)"
