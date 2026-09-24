"""
HTML Generation Planner
Calculates how many generation passes needed to avoid truncation.
"""

from typing import List, Dict, Tuple
from pathlib import Path

try:
    from .datatypes import CaseBundle
    from .config import Constitution
except ImportError:
    from datatypes import CaseBundle
    from config import Constitution


class GenerationPlanner:
    """
    Calculates optimal HTML generation strategy.
    Prevents token limit truncation.
    """
    
    # Token costs (approximate)
    TOKEN_COST_PER_ROW = 50  # HTML table row with data
    TOKEN_COST_PER_DATE = 20  # Column header
    TOKEN_COST_CSS = 800  # CSS block (once)
    TOKEN_COST_HEADER = 200  # HTML header (once)
    TOKEN_COST_PANEL_HEADER = 50  # Panel wrapper
    TOKEN_SAFETY_MARGIN = 1.2  # 20% safety buffer
    
    # Target limits
    MAX_TOKENS_PER_GENERATION = 3000  # Conservative limit for output
    
    def __init__(self, constitution: Constitution):
        self.constitution = constitution
    
    def plan_generation(self, case: CaseBundle) -> Dict:
        """
        Calculate generation strategy.
        
        Returns:
            {
                'total_rows': int,
                'total_dates': int,
                'estimated_tokens': int,
                'parts_needed': int,
                'parts_recommended': int,  # +1 for safety
                'rows_per_part': int,
                'strategy': 'single' | 'multi'
            }
        """
        rows = case.canonical_rows_long
        
        # Count unique dates
        dates = set(row.datetime[:10] for row in rows)
        
        # Estimate token cost
        base_cost = self.TOKEN_COST_CSS + self.TOKEN_COST_HEADER
        data_cost = (
            len(rows) * self.TOKEN_COST_PER_ROW +
            len(dates) * self.TOKEN_COST_PER_DATE
        )
        
        # Add panel overhead
        panels = set(row.panel_key for row in rows)
        panel_cost = len(panels) * self.TOKEN_COST_PANEL_HEADER
        
        total_estimated = base_cost + data_cost + panel_cost
        total_with_margin = int(total_estimated * self.TOKEN_SAFETY_MARGIN)
        
        # Calculate parts needed
        if total_with_margin <= self.MAX_TOKENS_PER_GENERATION:
            parts_needed = 1
            strategy = 'single'
        else:
            # Calculate how many parts we need
            data_tokens_per_part = self.MAX_TOKENS_PER_GENERATION - (base_cost / 4)
            parts_needed = int((data_cost + panel_cost) / data_tokens_per_part) + 1
            strategy = 'multi'
        
        # Add +1 for safety as requested
        parts_recommended = parts_needed + 1
        
        # Calculate rows per part
        rows_per_part = len(rows) // parts_recommended if strategy == 'multi' else len(rows)
        
        return {
            'total_rows': len(rows),
            'total_dates': len(dates),
            'total_panels': len(panels),
            'estimated_tokens': total_estimated,
            'estimated_with_margin': total_with_margin,
            'parts_needed': parts_needed,
            'parts_recommended': parts_recommended,
            'rows_per_part': rows_per_part,
            'strategy': strategy
        }
    
    def split_by_panels(self, case: CaseBundle, n_parts: int) -> List[List[str]]:
        """
        Split panels across N parts for generation.
        
        Returns:
            List of panel lists, one per generation part
        """
        rows = case.canonical_rows_long
        
        # Group by panel and count rows
        panel_row_counts = {}
        for row in rows:
            panel = row.panel_key
            panel_row_counts[panel] = panel_row_counts.get(panel, 0) + 1
        
        # Sort panels by constitutional order
        ordered_panels = [
            p for p in self.constitution.panel_order
            if p in panel_row_counts
        ]
        
        # Distribute panels across parts to balance row counts
        parts = [[] for _ in range(n_parts)]
        part_row_counts = [0] * n_parts
        
        for panel in ordered_panels:
            # Find part with fewest rows
            min_part_idx = part_row_counts.index(min(part_row_counts))
            parts[min_part_idx].append(panel)
            part_row_counts[min_part_idx] += panel_row_counts[panel]
        
        return parts
    
    def print_plan(self, plan: Dict) -> None:
        """Print generation plan for user."""
        print(f"\n{'='*60}")
        print("HTML GENERATION PLAN")
        print(f"{'='*60}")
        print(f"Total rows: {plan['total_rows']}")
        print(f"Total dates: {plan['total_dates']}")
        print(f"Total panels: {plan['total_panels']}")
        print(f"Estimated tokens: {plan['estimated_tokens']}")
        print(f"With margin: {plan['estimated_with_margin']}")
        print(f"\nStrategy: {plan['strategy'].upper()}")
        print(f"Parts needed (calculated): {plan['parts_needed']}")
        print(f"Parts recommended (+1 safety): {plan['parts_recommended']}")
        
        if plan['strategy'] == 'multi':
            print(f"Rows per part: ~{plan['rows_per_part']}")
            print(f"\n⚠️  Multi-part generation required to avoid truncation")
        else:
            print(f"\n✓ Single-part generation sufficient")
        
        print(f"{'='*60}\n")
