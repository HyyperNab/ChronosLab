"""
Qualitative State-Change Detection
Detects transitions in non-numeric lab results (NEG→POS, etc.)
"""

from typing import List, Dict, Optional
from datetime import datetime

try:
    from .datatypes import CanonicalLabRow, ValueType
except ImportError:
    from datatypes import CanonicalLabRow, ValueType


# ---- Canonical qualitative-state normalization (FR/EN/DE) ----
# Maps language-specific variants to a single canonical token so that
# cross-language synonyms (e.g. NÉGATIF vs NEGATIV) do NOT register as
# false-positive state changes. The original lab text is still displayed
# in the cells — this only affects the comparison logic.
_ACCENTS = {
    "É": "E", "È": "E", "Ê": "E", "Ë": "E",
    "À": "A", "Â": "A", "Ä": "A",
    "Ô": "O", "Ö": "O",
    "Û": "U", "Ü": "U",
    "Ç": "C", "Î": "I", "Ï": "I",
}
_NEGATIVE_TOKENS = {
    "NEG", "NEGATIF", "NEGATIVE", "NEGATIV", "NEG.",
    "NON-REACTIVE", "NON REACTIVE", "NONREACTIVE",
}
_POSITIVE_TOKENS = {
    "POS", "POSITIF", "POSITIVE", "POSITIV", "POS.",
    "REACTIVE", "REACTIF",
}


def _canonical_qualitative_state(value: str) -> str:
    """
    Normalize a qualitative value to a canonical token for comparison.

    Returns 'NEGATIVE' or 'POSITIVE' for known variants across FR/EN/DE;
    otherwise returns the uppercased, accent-stripped original (so genuinely
    different results like TRACE still trigger a change).
    """
    if not value:
        return ""
    v = " ".join(value.strip().upper().split())
    for acc, plain in _ACCENTS.items():
        v = v.replace(acc, plain)
    if v in _NEGATIVE_TOKENS:
        return "NEGATIVE"
    if v in _POSITIVE_TOKENS:
        return "POSITIVE"
    return v


class StateChange:
    """Represents a qualitative state change"""
    def __init__(
        self,
        analyte: str,
        from_state: str,
        to_state: str,
        change_date: str,
        from_date: str
    ):
        self.analyte = analyte
        self.from_state = from_state
        self.to_state = to_state
        self.change_date = change_date
        self.from_date = from_date

    def __str__(self) -> str:
        return f"{self.analyte}: {self.from_state} → {self.to_state} on {self.change_date}"


class QualitativeAnalyzer:
    """
    Analyzes qualitative lab results for state changes.
    Non-interpretive, fact-based only.
    """

    @staticmethod
    def detect_state_changes(rows: List[CanonicalLabRow]) -> List[StateChange]:
        """
        Detect state changes in qualitative results.

        Compares on a canonical (language-normalized) token so that the same
        result in different languages (NÉGATIF vs NEGATIV) does NOT produce a
        false-positive change. The original text is still stored for display.
        """
        qualitative_by_analyte = {}

        for row in rows:
            if row.value_type != ValueType.QUALITATIVE:
                continue

            analyte = row.analyte_canonical
            if analyte not in qualitative_by_analyte:
                qualitative_by_analyte[analyte] = []

            raw_state = row.value_raw.strip().upper()
            qualitative_by_analyte[analyte].append({
                'date': row.datetime[:10],
                'state': raw_state,                                  # original for display
                'state_canonical': _canonical_qualitative_state(raw_state),  # for comparison
                'datetime': row.datetime
            })

        changes = []

        for analyte, results in qualitative_by_analyte.items():
            results_sorted = sorted(results, key=lambda x: x['datetime'])

            for i in range(1, len(results_sorted)):
                prev = results_sorted[i - 1]
                curr = results_sorted[i]

                # Compare on CANONICAL form — cross-language synonyms are NOT changes
                if prev['state_canonical'] != curr['state_canonical']:
                    change = StateChange(
                        analyte=analyte,
                        from_state=prev['state'],      # original text for display
                        to_state=curr['state'],        # original text for display
                        change_date=curr['date'],
                        from_date=prev['date']
                    )
                    changes.append(change)

        return changes

    @staticmethod
    def render_state_changes_html(changes: List[StateChange]) -> str:
        if not changes:
            return ""

        rows_html = []
        for change in changes:
            rows_html.append(f"""
                <tr>
                    <td><strong>{change.analyte}</strong></td>
                    <td>{change.from_state}</td>
                    <td>→</td>
                    <td>{change.to_state}</td>
                    <td>{change.change_date}</td>
                </tr>
            """)

        return f"""
        <details class="panel" id="state-changes" open>
            <summary><span class="chev">▶</span> State Changes (Qualitative)</summary>
            <div class="panelBody">
                <table>
                    <thead>
                        <tr>
                            <th>Parameter</th>
                            <th>From</th>
                            <th></th>
                            <th>To</th>
                            <th>Date</th>
                        </tr>
                    </thead>
                    <tbody>
                        {''.join(rows_html)}
                    </tbody>
                </table>
            </div>
        </details>
        """
