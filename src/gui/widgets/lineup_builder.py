"""Lineup builder widget with 9 batting order slots."""

import tkinter as tk
from tkinter import ttk
from typing import List, Optional, Dict, Any
from src.models.player import Player


class LineupBuilder(ttk.Frame):
    """Widget for building and managing 9-player lineup."""

    def __init__(self, parent, **kwargs):
        """
        Initialize lineup builder.

        Args:
            parent: Parent widget
            **kwargs: Additional frame arguments
        """
        super().__init__(parent, **kwargs)

        self.lineup: List[Optional[Player]] = [None] * 9
        self.constraints: List[Dict[str, Any]] = []
        self.locked_positions: set = set()  # Positions with constraints

        # Create listbox for lineup
        self.listbox = tk.Listbox(self, height=9, font=('TkDefaultFont', 10))
        self.listbox.grid(row=0, column=0, sticky='nsew', padx=(0, 5))

        # Create scrollbar
        scrollbar = ttk.Scrollbar(self, orient='vertical', command=self.listbox.yview)
        self.listbox.configure(yscrollcommand=scrollbar.set)
        scrollbar.grid(row=0, column=1, sticky='ns')

        # Create control buttons
        btn_frame = ttk.Frame(self)
        btn_frame.grid(row=0, column=2, sticky='ns', padx=(5, 0))

        self.up_btn = ttk.Button(btn_frame, text="▲ Move Up", command=self.move_up, width=12)
        self.up_btn.pack(pady=2)

        self.down_btn = ttk.Button(btn_frame, text="▼ Move Down", command=self.move_down, width=12)
        self.down_btn.pack(pady=2)

        self.remove_btn = ttk.Button(btn_frame, text="✖ Remove", command=self.remove_player, width=12)
        self.remove_btn.pack(pady=2)

        ttk.Separator(btn_frame, orient='horizontal').pack(fill='x', pady=10)

        self.clear_btn = ttk.Button(btn_frame, text="Clear All", command=self.clear_lineup, width=12)
        self.clear_btn.pack(pady=2)

        # Configure grid weights
        self.rowconfigure(0, weight=1)
        self.columnconfigure(0, weight=1)

        # Initial refresh
        self.refresh()

    def refresh(self):
        """Refresh the listbox display."""
        self.listbox.delete(0, tk.END)

        for i, player in enumerate(self.lineup):
            if player is None:
                text = f"{i+1}. (empty)"
                self.listbox.insert(tk.END, text)
                self.listbox.itemconfig(i, foreground='gray')
            else:
                lock_icon = "🔒 " if i in self.locked_positions else ""
                pos_display = f"[{player.position}] " if player.position else ""
                text = f"{i+1}. {lock_icon}{pos_display}{player.name} ({player.ba:.3f}/{player.obp:.3f}/{player.slg:.3f})"
                self.listbox.insert(tk.END, text)

                # Highlight locked positions
                if i in self.locked_positions:
                    self.listbox.itemconfig(i, background='#ffffcc')

    def add_player(self, player: Player, position: Optional[int] = None) -> bool:
        """
        Add a player to the lineup.

        Args:
            player: Player object to add
            position: Specific position (0-8), or None to add to first empty slot

        Returns:
            True if player was added, False otherwise
        """
        # Check if player already in lineup
        if player in self.lineup:
            return False

        if position is not None:
            # Add to specific position
            if 0 <= position < 9:
                self.lineup[position] = player
                self.refresh()
                return True
            return False
        else:
            # Find first empty slot
            try:
                idx = self.lineup.index(None)
                self.lineup[idx] = player
                self.refresh()
                return True
            except ValueError:
                # Lineup is full
                return False

    def remove_player(self):
        """Remove the selected player from lineup."""
        selection = self.listbox.curselection()
        if not selection:
            return

        idx = selection[0]

        # Don't allow removing locked positions
        if idx in self.locked_positions:
            return

        self.lineup[idx] = None
        self.refresh()

    def move_up(self):
        """Move selected player up in batting order."""
        selection = self.listbox.curselection()
        if not selection or selection[0] == 0:
            return

        idx = selection[0]

        # Don't allow moving locked positions
        if idx in self.locked_positions or (idx-1) in self.locked_positions:
            return

        # Swap with previous
        self.lineup[idx], self.lineup[idx-1] = self.lineup[idx-1], self.lineup[idx]
        self.refresh()
        self.listbox.selection_clear(0, tk.END)
        self.listbox.selection_set(idx-1)

    def move_down(self):
        """Move selected player down in batting order."""
        selection = self.listbox.curselection()
        if not selection or selection[0] == 8:
            return

        idx = selection[0]

        # Don't allow moving locked positions
        if idx in self.locked_positions or (idx+1) in self.locked_positions:
            return

        # Swap with next
        self.lineup[idx], self.lineup[idx+1] = self.lineup[idx+1], self.lineup[idx]
        self.refresh()
        self.listbox.selection_clear(0, tk.END)
        self.listbox.selection_set(idx+1)

    def clear_lineup(self):
        """Clear the entire lineup (except locked positions)."""
        for i in range(9):
            if i not in self.locked_positions:
                self.lineup[i] = None
        self.refresh()

    def get_lineup(self) -> List[Optional[Player]]:
        """Get current lineup."""
        return self.lineup.copy()

    def set_lineup(self, lineup: List[Optional[Player]]):
        """
        Set the lineup.

        Args:
            lineup: List of 9 Player objects (or None for empty slots)
        """
        if len(lineup) != 9:
            raise ValueError("Lineup must have exactly 9 slots")

        self.lineup = lineup.copy()
        self.refresh()

    def apply_constraints(self, constraints: List[Dict[str, Any]]):
        """
        Apply constraints to the lineup.

        Args:
            constraints: List of constraint dicts
        """
        self.constraints = constraints
        self.locked_positions.clear()

        # Mark positions that have fixed_position constraints
        for constraint in constraints:
            if constraint.get('type') == 'fixed_position':
                position = constraint.get('position')
                if position and 1 <= position <= 9:
                    self.locked_positions.add(position - 1)

        self.refresh()

    def is_full(self) -> bool:
        """Check if lineup has all 9 players."""
        return all(player is not None for player in self.lineup)

    def is_valid(self) -> bool:
        """Check if lineup is valid (all 9 slots filled)."""
        return self.is_full()
