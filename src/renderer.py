"""
ChronosLab Clinician Cockpit HTML Renderer
Renders collapsible panel interface with complete data guarantee.

Harmonization fixes applied:
- S1: atomic write (was output_path.write_text -> partial HTML on crash)
- C4: em-dash for missing values (was mojibaked '')
- C7: UTF-8 literals (title dash, chevron) were mojibaked
- C9: patient name in <title> only (Datenschutz), fallback case_id
- R4: flag classification compares on the Flag enum, not strings
- v1.6.0: index banner navigation
Theme: forest-navy dark (per constitution.json clinician_cockpit.colors),
NOT the v1.6.0-spec teal/light theme -- switching to that requires editing
the locked constitution.json (would break its stored hash). Kept as-is.
"""

from pathlib import Path
from collections import defaultdict
from html import escape
from typing import Dict, List, Set

try:
    from .datatypes import CaseBundle, CanonicalLabRow, Flag
    from .config import Constitution
    from .qualitative import QualitativeAnalyzer
    from .fileio import atomic_write
except ImportError:
    from datatypes import CaseBundle, CanonicalLabRow, Flag
    from config import Constitution
    from qualitative import QualitativeAnalyzer
    from fileio import atomic_write


# Proper Unicode literals (were mojibaked in the original file)
EM_DASH = "\u2014"   # —
EN_DASH = "\u2013"   # –
CHEV = "\u25B6"      # ▶


class ClinicianCockpitRenderer:
    """
    Renders the clinician cockpit HTML interface.

    GUARANTEES:
    - All extracted rows are rendered (no truncation)
    - Panels follow constitutional order
    - Color emphasis only when references exist
    - No JavaScript dependencies
    - Atomic file write (no partial output on crash)
    """

    def __init__(self, constitution: Constitution):
        self.constitution = constitution
        self.colors = constitution.colors

    def render(self, case: CaseBundle, output_path: Path) -> Dict[str, int]:
        """
        Render clinician cockpit HTML.

        Args:
            case: CaseBundle with canonical rows
            output_path: Where to save HTML file

        Returns:
            Stats dict with row counts for verification
        """
        rows = case.canonical_rows_long

        # Organize by panel
        by_panel = defaultdict(list)
        dates: Set[str] = set()

        for row in rows:
            panel = row.panel_key or "MISC"
            by_panel[panel].append(row)
            dates.add(row.datetime[:10])  # Extract date only

        dates_sorted = sorted(dates)

        # Drop empty dates if configured
        if self.constitution.clinician_cockpit.get("drop_empty_dates", True):
            dates_sorted = self._filter_non_empty_dates(by_panel, dates_sorted)

        # Render panels in constitutional order
        panels_html = []
        stats = {"total_rows": len(rows), "panels_rendered": 0, "analytes_rendered": 0}

        rendered_panel_keys = []
        for panel_key in self.constitution.panel_order:
            if panel_key not in by_panel:
                continue

            panel_html = self._render_panel(panel_key, by_panel[panel_key], dates_sorted)
            if panel_html:
                panels_html.append(panel_html)
                stats["panels_rendered"] += 1
                rendered_panel_keys.append(panel_key)

        # Count unique analytes rendered
        unique_analytes = set(row.analyte_canonical for row in rows)
        stats["analytes_rendered"] = len(unique_analytes)

        # Detect qualitative state changes
        state_changes = QualitativeAnalyzer.detect_state_changes(rows)
        if state_changes:
            state_changes_html = QualitativeAnalyzer.render_state_changes_html(state_changes)
            panels_html.append(state_changes_html)

        # C9: patient name in <title> only (Datenschutz); fallback to case_id
        title_name = case.patient_name or case.case_id

        # Build complete HTML (pass rendered panel keys for the index banner)
        html = self._build_html_document(panels_html, title_name, stats, rendered_panel_keys)

        # S1: atomic write -- no partial HTML if the process is killed mid-write
        output_path.parent.mkdir(parents=True, exist_ok=True)
        atomic_write(output_path, html, encoding='utf-8')

        return stats

    def _render_panel(self, panel_key: str, rows: List[CanonicalLabRow], dates: List[str]) -> str:
        """
        Render a single panel with all its analytes.

        Args:
            panel_key: Panel identifier
            rows: All rows for this panel
            dates: Sorted list of dates

        Returns:
            HTML string for panel
        """
        if not rows:
            return ""

        # Organize by analyte
        by_analyte = defaultdict(dict)
        meta = {}

        for row in rows:
            analyte = row.analyte_canonical
            date = row.datetime[:10]
            by_analyte[analyte][date] = row

            # Store metadata (unit, reference) - take first occurrence
            if analyte not in meta:
                meta[analyte] = {
                    "unit": row.unit_canonical or row.unit_raw or "",
                    "ref_text": row.reference.text_raw,
                    "ref_low": row.reference.low,
                    "ref_high": row.reference.high,
                    "order": row.analyte_order
                }

        # Sort analytes by order
        analytes_sorted = sorted(
            by_analyte.keys(),
            key=lambda a: meta[a]["order"]
        )

        # Build table rows
        table_rows = []
        for analyte in analytes_sorted:
            m = meta[analyte]

            # Format reference
            ref_display, has_ref = self._format_reference(m)

            # Build cells for each date
            cells = []
            for date in dates:
                if date in by_analyte[analyte]:
                    row = by_analyte[analyte][date]
                    cell_html = self._render_cell(row, has_ref)
                    cells.append(cell_html)
                else:
                    # C4: em-dash for missing (proper Unicode, was mojibaked)
                    cells.append(f'<td class="empty">{EM_DASH}</td>')

            # Build variable column (sticky left)
            var_html = (
                f'<th class="var-col">'
                f'<div class="var">'
                f'<div><b>{escape(analyte)}</b> '
                f'<span class="unit">({escape(m["unit"])})</span></div>'
                f'<span class="refline">ref: <b>{ref_display}</b></span>'
                f'</div>'
                f'</th>'
            )

            table_rows.append(f"<tr>{var_html}{''.join(cells)}</tr>")

        # Build panel header
        panel_label = self.constitution.panel_labels.get(panel_key, panel_key)
        anchor = self._panel_anchor(panel_key)

        # Build table
        date_headers = ''.join(f'<th class="date-col">{d}</th>' for d in dates)

        panel_html = f"""
        <details class="panel" id="{anchor}" open>
            <summary>
                <span class="chev">{CHEV}</span> {escape(panel_label)}
            </summary>
            <div class="panelBody">
                <table>
                    <thead>
                        <tr>
                            <th class="var-col">Variable</th>
                            {date_headers}
                        </tr>
                    </thead>
                    <tbody>
                        {''.join(table_rows)}
                    </tbody>
                </table>
            </div>
        </details>
        """

        return panel_html

    def _render_cell(self, row: CanonicalLabRow, has_ref: bool) -> str:
        """
        Render a single data cell.

        Args:
            row: Lab result row
            has_ref: Whether reference exists for this analyte

        Returns:
            HTML <td> element
        """
        # R4: classify on the Flag enum directly (was passing flag.value string)
        css_class = self._classify_value(row.flag, has_ref)

        # Format value
        if row.value_numeric is not None:
            display_value = self._format_number(row.value_numeric)
        else:
            display_value = escape(row.value_raw)

        # Evidence attributes (hidden, inspectable)
        data_attrs = f'data-page="{row.page}" data-doc="{escape(row.doc_id)}"'
        if row.source_trace:
            if row.source_trace.bbox:
                data_attrs += f' data-bbox="{row.source_trace.bbox}"'
            data_attrs += f' data-confidence="{row.confidence_parse:.2f}"'

        return f'<td {data_attrs}><span class="val {css_class}">{display_value}</span></td>'

    def _classify_value(self, flag: Flag, has_ref: bool) -> str:
        """
        Determine CSS class for value.
        RULE: Color only if reference exists.
        R4: compares on the Flag enum, not the string value.
        """
        if not has_ref:
            return "normal"

        if flag in (Flag.LOW, Flag.CRITICAL_LOW):
            return "low"
        elif flag in (Flag.HIGH, Flag.CRITICAL_HIGH):
            return "high"
        else:
            return "normal"

    def _format_reference(self, meta: Dict) -> tuple:
        """
        Format reference range for display.

        Returns:
            (display_string, has_reference)
        """
        low = meta.get("ref_low")
        high = meta.get("ref_high")
        text = meta.get("ref_text")

        if low is not None and high is not None:
            # en-dash for ranges (was mojibaked)
            return f"{self._format_number(low)}{EN_DASH}{self._format_number(high)}", True
        elif text:
            return escape(text), True
        else:
            return EM_DASH, False

    @staticmethod
    def _format_number(value: float) -> str:
        """Format numeric value for display"""
        # Remove unnecessary trailing zeros
        if value == int(value):
            return str(int(value))
        else:
            return f"{value:.2f}".rstrip('0').rstrip('.')

    def _filter_non_empty_dates(self, by_panel: Dict, dates: List[str]) -> List[str]:
        """
        Filter out dates with no data across all panels.
        """
        dates_with_data = set()

        for panel_rows in by_panel.values():
            for row in panel_rows:
                dates_with_data.add(row.datetime[:10])

        return [d for d in dates if d in dates_with_data]

    @staticmethod
    def _panel_anchor(panel_key: str) -> str:
        """Stable HTML id from a panel key (lowercase, ascii-ish)."""
        import re
        return re.sub(r'[^a-z0-9]+', '-', panel_key.lower()).strip('-') or 'panel'

    def _build_html_document(
        self,
        panels_html: List[str],
        title_name: str,
        stats: Dict,
        rendered_panel_keys: List[str],
    ) -> str:
        """
        Build complete HTML document with CSS.
        """
        forest_navy = self.colors.get("forest_navy", "#0a1f2e")
        forest_navy_2 = self.colors.get("forest_navy_2", "#06202b")
        low_color = self.colors.get("low", "#c1121f")
        high_color = self.colors.get("high", "#0033cc")

        # v1.6.0 index banner: one link per RENDERED panel, in constitutional order
        banner_items = []
        for pk in rendered_panel_keys:
            label = self.constitution.panel_labels.get(pk, pk)
            banner_items.append(
                f'<a href="#{self._panel_anchor(pk)}">{escape(label)}</a>'
            )
        banner = (
            '<nav class="index-banner">' + ''.join(banner_items) + '</nav>'
            if banner_items else ''
        )

        html = f"""<!doctype html>
<html lang="fr">
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>ChronosLab {EM_DASH} {escape(title_name)}</title>
    <style>
        :root {{
            --forest-navy: {forest_navy};
            --forest-navy-2: {forest_navy_2};
            --low-color: {low_color};
            --high-color: {high_color};
        }}

        * {{ box-sizing: border-box; }}

        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', system-ui, sans-serif;
            background: #0b0d10;
            color: #e7edf5;
            margin: 0;
            padding: 20px;
            line-height: 1.5;
        }}

        h1 {{
            font-size: 1.4rem;
            font-weight: 700;
            margin: 0 0 1rem 0;
            color: #e7edf5;
        }}

        /* Index banner (v1.6.0) */
        .index-banner {{
            background: #0f1318;
            border: 1px solid #1b2330;
            border-radius: 6px;
            padding: 10px 12px;
            margin-bottom: 20px;
            display: flex;
            flex-wrap: wrap;
            gap: 8px;
        }}
        .index-banner a {{
            background: #1a2230;
            border: 1px solid #2a3340;
            padding: 4px 10px;
            border-radius: 4px;
            text-decoration: none;
            color: #a9b4c2;
            font-size: 0.85rem;
        }}
        .index-banner a:hover {{ background: #243040; color: #e7edf5; }}

        table {{
            border-collapse: collapse;
            width: 100%;
            background: #0f1318;
            margin-top: 10px;
        }}

        th, td {{
            border: 1px solid #1b2330;
            padding: 8px 12px;
            text-align: left;
        }}

        thead th {{
            background: #0f1318;
            font-weight: 700;
            position: sticky;
            top: 0;
            z-index: 10;
        }}

        .var-col {{
            min-width: 200px;
            position: sticky;
            left: 0;
            background: #0f1318;
            z-index: 5;
        }}

        thead .var-col {{
            z-index: 15;
        }}

        .date-col {{
            min-width: 100px;
            font-size: 13px;
        }}

        .empty {{
            color: #555;
            text-align: center;
        }}

        .var {{
            display: flex;
            flex-direction: column;
            gap: 4px;
        }}

        .unit {{
            color: #8a95a3;
            font-weight: normal;
            font-size: 13px;
        }}

        .refline {{
            font-size: 11px;
            color: #a9b4c2;
        }}

        .val {{
            font-variant-numeric: tabular-nums;
        }}

        .val.low {{
            color: var(--low-color);
            font-weight: 800;
        }}

        .val.high {{
            color: var(--high-color);
            font-weight: 800;
        }}

        .val.normal {{
            color: #e7edf5;
        }}

        details.panel {{
            margin-bottom: 20px;
            border-radius: 4px;
            overflow: hidden;
        }}

        details.panel summary {{
            list-style: none;
            cursor: pointer;
            padding: 12px 16px;
            background: linear-gradient(90deg, var(--forest-navy), var(--forest-navy-2));
            color: #e7edf5;
            font-weight: 800;
            font-size: 15px;
            display: flex;
            gap: 10px;
            align-items: center;
            user-select: none;
        }}

        details.panel summary::-webkit-details-marker {{
            display: none;
        }}

        .chev {{
            transition: transform 0.15s ease;
            display: inline-block;
            font-size: 12px;
        }}

        details.panel[open] .chev {{
            transform: rotate(90deg);
        }}

        .panelBody {{
            padding: 0;
            overflow-x: auto;
        }}

        @media print {{
            .index-banner {{ display: none; }}
            details.panel {{ page-break-inside: avoid; }}
            details.panel > .panelBody {{ display: block !important; }}
        }}
    </style>
</head>
<body>
    <h1>ChronosLab {EM_DASH} {escape(title_name)}</h1>
    {banner}
    {''.join(panels_html)}
</body>
</html>
"""
        return html

    @staticmethod
    def _get_timestamp() -> str:
        """Get current timestamp in ISO format"""
        from datetime import datetime, timezone
        return datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')
