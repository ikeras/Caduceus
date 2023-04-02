from dataclasses import dataclass

@dataclass
class EdgeScan:
    direction: int = 0
    remaining_scans: int = 0
    current_end: int = 0
    source_x: float = 0.0
    source_y: float = 0.0
    source_step_x: float = 0.0
    source_step_y: float = 0.0
    dest_x: int = 0
    dest_x_int_step: int = 0
    dest_x_direction: int = 0
    dest_x_error_term: int = 0
    dest_x_adj_up: int = 0
    dest_x_adj_down: int = 0