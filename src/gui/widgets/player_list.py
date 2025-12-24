"""Player list widget with sortable columns."""

import tkinter as tk
from tkinter import ttk, simpledialog
from typing import List, Optional
from src.models.player import Player


class PlayerList(ttk.Frame):
    """Treeview displaying players with sortable columns."""

    def __init__(self, parent, **kwargs):
        """
        Initialize player list.

        Args:
            parent: Parent widget
            **kwargs: Additional frame arguments
        """
        super().__init__(parent, **kwargs)

        self.players: List[Player] = []
        self.sort_column = 'pa'
        self.sort_reverse = True

        # Create treeview with extended selection mode (allows Ctrl/Shift multi-select)
        columns = ('name', 'position', 'pa', 'ba', 'obp', 'slg', 'iso')
        self.tree = ttk.Treeview(self, columns=columns, show='headings', height=15, selectmode='extended')

        # Define headings
        self.tree.heading('name', text='Name', command=lambda: self.sort_by('name'))
        self.tree.heading('position', text='Pos', command=lambda: self.sort_by('position'))
        self.tree.heading('pa', text='PA', command=lambda: self.sort_by('pa'))
        self.tree.heading('ba', text='BA', command=lambda: self.sort_by('ba'))
        self.tree.heading('obp', text='OBP', command=lambda: self.sort_by('obp'))
        self.tree.heading('slg', text='SLG', command=lambda: self.sort_by('slg'))
        self.tree.heading('iso', text='ISO', command=lambda: self.sort_by('iso'))

        # Define column widths
        self.tree.column('name', width=150)
        self.tree.column('position', width=50, anchor='center')
        self.tree.column('pa', width=60, anchor='center')
        self.tree.column('ba', width=60, anchor='center')
        self.tree.column('obp', width=60, anchor='center')
        self.tree.column('slg', width=60, anchor='center')
        self.tree.column('iso', width=60, anchor='center')

        # Create scrollbar
        scrollbar = ttk.Scrollbar(self, orient='vertical', command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)

        # Grid layout
        self.tree.grid(row=0, column=0, sticky='nsew')
        scrollbar.grid(row=0, column=1, sticky='ns')

        self.rowconfigure(0, weight=1)
        self.columnconfigure(0, weight=1)

        # Add right-click context menu
        self.context_menu = tk.Menu(self, tearoff=0)
        self.context_menu.add_command(label="Set Position...", command=self._set_position)
        self.tree.bind("<Button-3>", self._show_context_menu)  # Right-click

    def load_players(self, players: List[Player]):
        """
        Load players into the list.

        Args:
            players: List of Player objects
        """
        self.players = players
        self.refresh()

    def refresh(self):
        """Refresh the treeview with current players."""
        # Clear existing items
        for item in self.tree.get_children():
            self.tree.delete(item)

        # Sort players
        if self.sort_column == 'name':
            sorted_players = sorted(self.players, key=lambda p: p.name, reverse=self.sort_reverse)
        elif self.sort_column == 'position':
            sorted_players = sorted(self.players, key=lambda p: p.position or 'ZZZ', reverse=self.sort_reverse)
        elif self.sort_column == 'pa':
            sorted_players = sorted(self.players, key=lambda p: p.pa, reverse=self.sort_reverse)
        elif self.sort_column == 'ba':
            sorted_players = sorted(self.players, key=lambda p: p.ba, reverse=self.sort_reverse)
        elif self.sort_column == 'obp':
            sorted_players = sorted(self.players, key=lambda p: p.obp, reverse=self.sort_reverse)
        elif self.sort_column == 'slg':
            sorted_players = sorted(self.players, key=lambda p: p.slg, reverse=self.sort_reverse)
        elif self.sort_column == 'iso':
            sorted_players = sorted(self.players, key=lambda p: p.iso, reverse=self.sort_reverse)
        else:
            sorted_players = self.players

        # Insert players
        for player in sorted_players:
            self.tree.insert('', 'end', values=(
                player.name,
                player.position or '-',
                player.pa,
                f"{player.ba:.3f}",
                f"{player.obp:.3f}",
                f"{player.slg:.3f}",
                f"{player.iso:.3f}"
            ))

    def sort_by(self, column: str):
        """
        Sort by a specific column.

        Args:
            column: Column name to sort by
        """
        if self.sort_column == column:
            # Toggle sort direction
            self.sort_reverse = not self.sort_reverse
        else:
            # New column - default to descending (except name and position)
            self.sort_column = column
            self.sort_reverse = (column not in ['name', 'position'])

        self.refresh()

    def get_selected(self) -> Optional[Player]:
        """
        Get the first selected player (for backward compatibility).

        Returns:
            Selected Player object, or None if no selection
        """
        selection = self.tree.selection()
        if not selection:
            return None

        item = self.tree.item(selection[0])
        name = item['values'][0]

        # Find player by name
        for player in self.players:
            if player.name == name:
                return player

        return None

    def get_selected_multiple(self) -> List[Player]:
        """
        Get all currently selected players.

        Returns:
            List of selected Player objects (empty if no selection)
        """
        selection = self.tree.selection()
        if not selection:
            return []

        selected_players = []
        for item_id in selection:
            item = self.tree.item(item_id)
            name = item['values'][0]

            # Find player by name
            for player in self.players:
                if player.name == name:
                    selected_players.append(player)
                    break

        return selected_players

    def get_selected_index(self) -> Optional[int]:
        """
        Get the index of the selected player in the original players list.

        Returns:
            Index of selected player, or None if no selection
        """
        player = self.get_selected()
        if player is None:
            return None

        try:
            return self.players.index(player)
        except ValueError:
            return None

    def _show_context_menu(self, event):
        """Show context menu on right-click."""
        # Select the item under the cursor
        item = self.tree.identify_row(event.y)
        if item:
            self.tree.selection_set(item)
            self.context_menu.post(event.x_root, event.y_root)

    def _set_position(self):
        """Set/edit position for selected player."""
        player = self.get_selected()
        if not player:
            return

        # Common positions
        positions = ['C', '1B', '2B', '3B', 'SS', 'LF', 'CF', 'RF', 'OF', 'DH', 'UT']

        # Create dialog
        dialog = tk.Toplevel(self)
        dialog.title(f"Set Position for {player.name}")
        dialog.transient(self)
        dialog.grab_set()
        dialog.geometry("300x250")

        ttk.Label(dialog, text=f"Select position for {player.name}:").pack(padx=10, pady=10)

        # Current position
        if player.position:
            ttk.Label(dialog, text=f"Current: {player.position}", foreground='gray').pack(padx=10, pady=5)

        # Position buttons
        btn_frame = ttk.Frame(dialog)
        btn_frame.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

        result = [None]

        def set_pos(pos):
            result[0] = pos
            dialog.destroy()

        # Create buttons in a grid
        for i, pos in enumerate(positions):
            row = i // 3
            col = i % 3
            btn = ttk.Button(btn_frame, text=pos, command=lambda p=pos: set_pos(p), width=8)
            btn.grid(row=row, column=col, padx=5, pady=5)

        # Custom entry
        custom_frame = ttk.Frame(dialog)
        custom_frame.pack(padx=10, pady=10)
        ttk.Label(custom_frame, text="Or enter custom:").pack(side=tk.LEFT, padx=5)
        custom_entry = ttk.Entry(custom_frame, width=10)
        custom_entry.pack(side=tk.LEFT, padx=5)
        ttk.Button(custom_frame, text="OK", command=lambda: set_pos(custom_entry.get())).pack(side=tk.LEFT, padx=5)

        # Clear button
        ttk.Button(dialog, text="Clear Position", command=lambda: set_pos('')).pack(pady=5)

        self.wait_window(dialog)

        if result[0] is not None:
            player.position = result[0] if result[0] else None
            self.refresh()
