"""
Table Extraction Engine
Detects and extracts structured data from OCR bounding boxes.
"""

from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass
from collections import defaultdict
import re

try:
    from .ocr_engine import OCRBox, OCRPage, FrenchReferenceParser
    from .datatypes import CanonicalLabRow, ValueType, Flag, ReferenceRange, SourceTrace, DatetimePrecision
    from .analyte_normalizer import AnalyteNormalizer
    from .logging_config import get_logger
except ImportError:
    from ocr_engine import OCRBox, OCRPage, FrenchReferenceParser
    from datatypes import CanonicalLabRow, ValueType, Flag, ReferenceRange, SourceTrace, DatetimePrecision
    from analyte_normalizer import AnalyteNormalizer
    from logging_config import get_logger


@dataclass
class TableCell:
    """Single cell in detected table"""
    text: str
    bbox: Tuple[int, int, int, int]  # x, y, width, height
    confidence: float
    row_idx: int
    col_idx: int


@dataclass
class TableRow:
    """Single row in detected table"""
    cells: List[TableCell]
    y_position: int


class TableExtractor:
    """
    Extracts structured tables from OCR bounding boxes.
    Uses geometric analysis to detect rows and columns.
    """

    # Thresholds
    ROW_TOLERANCE = 15  # Pixels - boxes within this vertical distance = same row
    COL_TOLERANCE = 20  # Pixels - column boundary tolerance
    MIN_BOXES_PER_ROW = 2  # Minimum boxes to consider a row

    def __init__(self):
        self.logger = get_logger()

    def extract_tables(self, page: OCRPage) -> List[List[TableRow]]:
        """
        Extract all tables from page.

        Args:
            page: OCRPage with bounding boxes

        Returns:
            List of tables (each table is list of rows)
        """
        if not page.boxes:
            return []

        # Group boxes into rows by Y position
        rows = self._group_into_rows(page.boxes)

        if not rows:
            return []

        # Detect column boundaries
        col_boundaries = self._detect_columns(rows)

        # Assign cells to columns
        table_rows = self._assign_columns(rows, col_boundaries)

        # Split into separate tables (detect gaps)
        tables = self._split_tables(table_rows)

        self.logger.debug(f"Extracted {len(tables)} tables with {sum(len(t) for t in tables)} total rows")

        return tables

    def _group_into_rows(self, boxes: List[OCRBox]) -> List[TableRow]:
        """Group boxes into rows by Y position"""
        # Sort by Y position
        sorted_boxes = sorted(boxes, key=lambda b: b.y)

        rows = []
        current_row_boxes = []
        current_y = None

        for box in sorted_boxes:
            if current_y is None:
                current_y = box.y
                current_row_boxes = [box]
            elif abs(box.y - current_y) <= self.ROW_TOLERANCE:
                # Same row
                current_row_boxes.append(box)
            else:
                # New row
                if len(current_row_boxes) >= self.MIN_BOXES_PER_ROW:
                    rows.append(TableRow(
                        cells=[],  # Will assign later
                        y_position=current_y
                    ))
                    # Store boxes temporarily
                    rows[-1]._boxes = sorted(current_row_boxes, key=lambda b: b.x)

                current_y = box.y
                current_row_boxes = [box]

        # Last row
        if len(current_row_boxes) >= self.MIN_BOXES_PER_ROW:
            rows.append(TableRow(cells=[], y_position=current_y))
            rows[-1]._boxes = sorted(current_row_boxes, key=lambda b: b.x)

        return rows

    def _detect_columns(self, rows: List[TableRow]) -> List[int]:
        """
        Detect column boundaries from row structure.

        Returns:
            List of X positions (column boundaries)
        """
        # Collect all X positions
        x_positions = []
        for row in rows:
            for box in row._boxes:
                x_positions.append(box.x)

        if not x_positions:
            return []

        # Sort and find clusters
        x_positions.sort()

        boundaries = []
        current_cluster = [x_positions[0]]

        for x in x_positions[1:]:
            if x - current_cluster[-1] <= self.COL_TOLERANCE:
                current_cluster.append(x)
            else:
                # New cluster - add median as boundary
                boundaries.append(int(sum(current_cluster) / len(current_cluster)))
                current_cluster = [x]

        # Last cluster
        if current_cluster:
            boundaries.append(int(sum(current_cluster) / len(current_cluster)))

        return sorted(boundaries)

    def _assign_columns(self, rows: List[TableRow], col_boundaries: List[int]) -> List[TableRow]:
        """Assign each box to nearest column"""
        for row in rows:
            cells = []
            for box in row._boxes:
                # Find nearest column
                col_idx = self._find_column(box.x, col_boundaries)

                cell = TableCell(
                    text=box.text,
                    bbox=(box.x, box.y, box.width, box.height),
                    confidence=box.confidence,
                    row_idx=0,  # Will update later
                    col_idx=col_idx
                )
                cells.append(cell)

            row.cells = cells

        # Update row indices
        for idx, row in enumerate(rows):
            for cell in row.cells:
                cell.row_idx = idx

        return rows

    def _find_column(self, x: int, boundaries: List[int]) -> int:
        """Find which column an X position belongs to"""
        if not boundaries:
            return 0

        # Find nearest boundary
        distances = [abs(x - b) for b in boundaries]
        return distances.index(min(distances))

    def _split_tables(self, rows: List[TableRow]) -> List[List[TableRow]]:
        """Split rows into separate tables based on vertical gaps"""
        if not rows:
            return []

        tables = []
        current_table = [rows[0]]

        for i in range(1, len(rows)):
            prev_row = rows[i-1]
            curr_row = rows[i]

            # Check gap
            gap = curr_row.y_position - prev_row.y_position

            if gap > 50:  # Large gap = new table
                tables.append(current_table)
                current_table = [curr_row]
            else:
                current_table.append(curr_row)

        # Last table
        if current_table:
            tables.append(current_table)

        return tables


class LabDataParser:
    """
    Parses lab data from extracted tables.
    Converts table rows to CanonicalLabRow objects.
    """

    # Column type detection patterns (FIXED: removed UTF-8/Latin-1 mojibake)
    ANALYTE_PATTERNS = [
        r'^[A-ZÀ-Ö][a-zà-ö]+',  # Capitalized word
        r'[A-Z]{2,}',  # Abbreviation (HB, CRP, etc.)
    ]

    NUMERIC_PATTERN = r'^[<>]?\s*\d+[.,]?\d*$'

    # FIXED: clean unit patterns (were mojibaked: Âµmol/L, /mmÂ³, g/[dL]L, ...)
    UNIT_PATTERNS = [
        r'g/dL',
        r'g/L',
        r'mmol/L',
        r'mg/dL',
        r'mg/L',
        r'µmol/L',
        r'umol/L',
        r'/mm³',
        r'/mm3',
        r'%',
        r'UI/L',
        r'U/L',
    ]

    def __init__(self, default_date: str = "2024-01-01"):
        """
        Initialize parser.

        Args:
            default_date: Default date if not found in document
        """
        self.default_date = default_date
        self.normalizer = AnalyteNormalizer()
        self.logger = get_logger()

    def parse_table(
        self,
        table: List[TableRow],
        doc_id: str,
        page_num: int
    ) -> List[CanonicalLabRow]:
        """
        Parse table into canonical lab rows.

        Args:
            table: Table rows
            doc_id: Source document ID
            page_num: Page number

        Returns:
            List of CanonicalLabRow objects
        """
        if not table:
            return []

        # Detect column types
        col_types = self._detect_column_types(table)

        # Find analyte, value, unit, reference columns
        analyte_col = self._find_column_type(col_types, 'analyte')
        value_col = self._find_column_type(col_types, 'value')
        unit_col = self._find_column_type(col_types, 'unit')
        ref_col = self._find_column_type(col_types, 'reference')

        if analyte_col is None or value_col is None:
            self.logger.warning("Could not identify analyte and value columns")
            return []

        # Parse each row
        rows = []
        for table_row in table[1:]:  # Skip header
            row = self._parse_row(
                table_row,
                analyte_col,
                value_col,
                unit_col,
                ref_col,
                doc_id,
                page_num
            )
            if row:
                rows.append(row)

        return rows

    def _detect_column_types(self, table: List[TableRow]) -> Dict[int, str]:
        """
        Detect what type each column is.

        Returns:
            Dict mapping column index to type
        """
        if not table:
            return {}

        # Get max columns
        max_cols = max(len(row.cells) for row in table)

        # Analyze each column
        col_types = {}

        for col_idx in range(max_cols):
            # Collect all text from this column
            col_texts = []
            for row in table:
                for cell in row.cells:
                    if cell.col_idx == col_idx:
                        col_texts.append(cell.text)

            if not col_texts:
                continue

            # Determine type
            col_type = self._classify_column(col_texts)
            col_types[col_idx] = col_type

        return col_types

    def _classify_column(self, texts: List[str]) -> str:
        """Classify column type from sample texts"""
        # Count patterns
        numeric_count = sum(1 for t in texts if re.match(self.NUMERIC_PATTERN, t))
        unit_count = sum(1 for t in texts if any(re.search(p, t, re.IGNORECASE) for p in self.UNIT_PATTERNS))

        # Reference patterns
        ref_count = sum(1 for t in texts if '-' in t and any(c.isdigit() for c in t))

        total = len(texts)

        # Classify
        if numeric_count / total > 0.7:
            return 'value'
        elif unit_count / total > 0.5:
            return 'unit'
        elif ref_count / total > 0.5:
            return 'reference'
        else:
            return 'analyte'

    def _find_column_type(self, col_types: Dict[int, str], target_type: str) -> Optional[int]:
        """Find first column of given type"""
        for col_idx, col_type in col_types.items():
            if col_type == target_type:
                return col_idx
        return None

    def _parse_row(
        self,
        table_row: TableRow,
        analyte_col: int,
        value_col: int,
        unit_col: Optional[int],
        ref_col: Optional[int],
        doc_id: str,
        page_num: int
    ) -> Optional[CanonicalLabRow]:
        """Parse single table row into CanonicalLabRow"""
        # Get cell values
        analyte = self._get_cell_text(table_row, analyte_col)
        value_raw = self._get_cell_text(table_row, value_col)
        unit = self._get_cell_text(table_row, unit_col) if unit_col is not None else None
        ref_raw = self._get_cell_text(table_row, ref_col) if ref_col is not None else None

        if not analyte or not value_raw:
            return None

        # Normalize analyte name -> Returns (canonical, confidence)
        analyte_canonical, norm_confidence = self.normalizer.normalize(analyte)

        # Parse value
        value_numeric, value_type, flag = self._parse_value(value_raw)

        # Parse reference
        ref_low, ref_high, ref_conf = None, None, "LOW"
        if ref_raw:
            ref_low, ref_high, ref_conf = FrenchReferenceParser.parse(ref_raw)

        # Determine flag from value vs reference
        # FIXED: Flag.NONE does not exist -> use Flag.NORMAL
        if flag == Flag.NORMAL and value_numeric is not None:
            flag = self._determine_flag(value_numeric, ref_low, ref_high)

        # Build source trace
        analyte_cell = next((c for c in table_row.cells if c.col_idx == analyte_col), None)
        source_trace = None
        if analyte_cell:
            # FIXED: SourceTrace.bbox is typed Optional[tuple]; pass a tuple, not a comma-string.
            bx = analyte_cell.bbox
            source_trace = SourceTrace(
                doc_id=doc_id,
                page=page_num,
                bbox=(bx[0], bx[1], bx[2], bx[3]),
                confidence=analyte_cell.confidence,
                extraction_method="ocr",
            )

        return CanonicalLabRow(
            case_id="",  # Will be set by processor (_assign_panels)
            doc_id=doc_id,
            page=page_num,
            datetime=self.default_date + "T00:00:00",
            datetime_precision=DatetimePrecision.DAY,  # FIXED: required field was missing -> TypeError
            analyte_canonical=analyte_canonical,  # Normalized
            analyte_raw=analyte.strip(),  # Original OCR text
            value_numeric=value_numeric,
            value_raw=value_raw,
            value_type=value_type,
            unit_canonical=unit,
            unit_raw=unit,
            reference=ReferenceRange(
                text_raw=ref_raw,
                low=ref_low,
                high=ref_high,
                parse_confidence=ref_conf,
                source_trace=source_trace
            ),
            flag=flag,
            panel_key="",  # Will be assigned by processor (_assign_panels)
            analyte_order=0,
            source_trace=source_trace,
            confidence_parse=analyte_cell.confidence if analyte_cell else 0.0
        )

    def _get_cell_text(self, row: TableRow, col_idx: Optional[int]) -> Optional[str]:
        """Get text from cell at column index"""
        if col_idx is None:
            return None

        for cell in row.cells:
            if cell.col_idx == col_idx:
                return cell.text

        return None

    def _parse_value(self, value_raw: str) -> Tuple[Optional[float], ValueType, Flag]:
        """
        Parse value string.

        Returns:
            (numeric_value, value_type, flag)
        """
        value_raw = value_raw.strip()

        # Check for qualitative (NEG, POS, etc.)  FIXED: mojibake 'NÃGATIF' -> 'NÉGATIF'
        if value_raw.upper() in ['NEG', 'NEGATIF', 'NÉGATIF', 'NEGATIVE']:
            return (None, ValueType.QUALITATIVE, Flag.NORMAL)
        if value_raw.upper() in ['POS', 'POSITIF', 'POSITIVE']:
            return (None, ValueType.QUALITATIVE, Flag.NORMAL)

        # Check for inequality
        if value_raw.startswith('<'):
            # "< 5" -> value_numeric = 5, flag = LOW
            try:
                num = float(value_raw[1:].strip().replace(',', '.'))
                return (num, ValueType.NUMERIC, Flag.LOW)  # FIXED: Flag.L -> Flag.LOW
            except ValueError:  # FIXED: bare except -> except ValueError
                return (None, ValueType.UNKNOWN, Flag.NORMAL)  # FIXED: TEXT -> UNKNOWN
        if value_raw.startswith('>'):
            # "> 100" -> value_numeric = 100, flag = HIGH
            try:
                num = float(value_raw[1:].strip().replace(',', '.'))
                return (num, ValueType.NUMERIC, Flag.HIGH)  # FIXED: Flag.H -> Flag.HIGH
            except ValueError:
                return (None, ValueType.UNKNOWN, Flag.NORMAL)

        # Try numeric
        try:
            num = float(value_raw.replace(',', '.'))
            return (num, ValueType.NUMERIC, Flag.NORMAL)
        except ValueError:
            return (None, ValueType.UNKNOWN, Flag.NORMAL)

    def _determine_flag(
        self,
        value: float,
        ref_low: Optional[float],
        ref_high: Optional[float]
    ) -> Flag:
        """Determine flag from value and reference range"""
        if ref_low is not None and value < ref_low:
            return Flag.LOW
        if ref_high is not None and value > ref_high:
            return Flag.HIGH
        return Flag.NORMAL
