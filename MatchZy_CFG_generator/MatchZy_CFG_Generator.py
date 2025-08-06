import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import json
import os
import re

# Constants
MAP_POOL = ["de_inferno", "de_mirage", "de_nuke", "de_overpass", "de_ancient", "de_dust2", "de_train"]
SIDE_OPTIONS = ["team1_ct", "team1_t", "team2_ct", "team2_t", "knife"]
DEFAULT_CVARS = {
    "mp_spec_swapplayersides": "1",
    "hostname": "",
    "mp_friendlyfire": "1"
}

TEAM_FOLDER = "teams"
SPECTATOR_FILE = "spectators.json"
os.makedirs(TEAM_FOLDER, exist_ok=True)

def is_valid_steamid(steamid):
    return bool(re.fullmatch(r"\d{17}", steamid))

def sanitize_filename(name):
    return re.sub(r"[^\w\-]", "_", name.strip())

class TeamManager:
    def __init__(self, frame, team_num):
        self.frame = frame
        self.team_num = team_num
        self.players = {}

        self.name_var = tk.StringVar()

        ttk.Label(frame, text=f"Team {team_num} Name").pack()
        ttk.Entry(frame, textvariable=self.name_var).pack()

        self.player_frame = ttk.LabelFrame(frame, text="Players")
        self.player_frame.pack(fill="x")

        self.nickname_var = tk.StringVar()
        self.steamid_var = tk.StringVar()

        entry_row = ttk.Frame(self.player_frame)
        entry_row.pack(fill="x")
        ttk.Entry(entry_row, textvariable=self.nickname_var, width=20).pack(side="left")
        ttk.Entry(entry_row, textvariable=self.steamid_var, width=30).pack(side="left")
        ttk.Button(entry_row, text="Add", command=self.add_player).pack(side="left")

        self.player_list = tk.Listbox(self.player_frame)
        self.player_list.pack(fill="both", expand=True)

        ttk.Button(self.player_frame, text="Remove Selected", command=self.remove_selected).pack()
        ttk.Button(frame, text="Save Team", command=self.save_team).pack()
        ttk.Button(frame, text="Load Team", command=self.load_team).pack()

    def add_player(self):
        nick = self.nickname_var.get().strip()
        sid = self.steamid_var.get().strip()
        if not (nick and sid):
            return
        if not is_valid_steamid(sid):
            messagebox.showerror("Invalid SteamID", "SteamID must be a 17-digit numeric string.")
            return
        if sid in self.players:
            messagebox.showwarning("Duplicate", f"SteamID {sid} already exists in the team.")
            return
        self.players[sid] = nick
        self.refresh_player_list()
        self.nickname_var.set("")
        self.steamid_var.set("")

    def remove_selected(self):
        selection = self.player_list.curselection()
        if selection:
            sid = list(self.players.keys())[selection[0]]
            del self.players[sid]
            self.refresh_player_list()

    def refresh_player_list(self):
        self.player_list.delete(0, tk.END)
        for sid, nick in self.players.items():
            self.player_list.insert(tk.END, f"{nick} ({sid})")

    def save_team(self):
        name = self.name_var.get().strip()
        if name:
            team_data = {"name": name, "players": self.players}
            with open(os.path.join(TEAM_FOLDER, f"{name}.json"), "w") as f:
                json.dump(team_data, f, indent=2)
            messagebox.showinfo("Saved", f"Team '{name}' saved.")

    def load_team(self):
        filepath = filedialog.askopenfilename(initialdir=TEAM_FOLDER, filetypes=[["JSON Files", "*.json"]])
        if filepath:
            with open(filepath, "r") as f:
                data = json.load(f)
                self.name_var.set(data["name"])
                self.players = data["players"]
                self.refresh_player_list()

    def get_team_data(self):
        return {
            "name": self.name_var.get(),
            "players": self.players
        }

    def get_team_name(self):
        return self.name_var.get()

class MatchConfigApp:
    def __init__(self, root):
        self.root = root
        root.title("MatchZy Config Generator")

        self.main_frame = ttk.Frame(root, padding=10)
        self.main_frame.pack(fill="both", expand=True)

        self.team1 = TeamManager(ttk.LabelFrame(self.main_frame, text="Team 1"), 1)
        self.team1.frame.grid(row=0, column=0, padx=10, pady=10, sticky="n")

        self.team2 = TeamManager(ttk.LabelFrame(self.main_frame, text="Team 2"), 2)
        self.team2.frame.grid(row=0, column=1, padx=10, pady=10, sticky="n")

        self.settings_frame = ttk.LabelFrame(self.main_frame, text="Match Settings")
        self.settings_frame.grid(row=0, column=2, padx=10, pady=10, sticky="n")

        self.match_id = tk.IntVar()
        self.tournament_name = tk.StringVar()
        self.stage_name = tk.StringVar()
        self.hostname = tk.StringVar()
        self.match_type = tk.StringVar(value="bo1")

        ttk.Label(self.settings_frame, text="Match ID").pack()
        ttk.Entry(self.settings_frame, textvariable=self.match_id).pack()
        ttk.Label(self.settings_frame, text="Tournament Name").pack()
        ttk.Entry(self.settings_frame, textvariable=self.tournament_name).pack()
        ttk.Label(self.settings_frame, text="Stage (optional)").pack()
        ttk.Entry(self.settings_frame, textvariable=self.stage_name).pack()
        ttk.Label(self.settings_frame, text="Hostname").pack()
        ttk.Entry(self.settings_frame, textvariable=self.hostname).pack()

        ttk.Label(self.settings_frame, text="Match Type").pack()
        ttk.Combobox(self.settings_frame, textvariable=self.match_type, values=["bo1", "bo3"]).pack()

        self.map_frame = ttk.LabelFrame(self.main_frame, text="Maps and Sides")
        self.map_frame.grid(row=1, column=0, columnspan=3, sticky="ew", padx=10, pady=10)

        self.map_vars = []
        for i in range(3):
            row = ttk.Frame(self.map_frame)
            row.pack(fill="x")
            map_var = tk.StringVar(value=MAP_POOL[i])
            side_var = tk.StringVar(value="knife")
            ttk.Label(row, text=f"Map {i+1}").pack(side="left")
            ttk.Combobox(row, textvariable=map_var, values=MAP_POOL).pack(side="left")
            ttk.Combobox(row, textvariable=side_var, values=SIDE_OPTIONS).pack(side="left")
            self.map_vars.append((map_var, side_var))

        self.spec_frame = ttk.LabelFrame(self.main_frame, text="Spectators")
        self.spec_frame.grid(row=2, column=0, columnspan=3, sticky="ew", padx=10, pady=10)
        self.spectators = {}
        self.spec_nick = tk.StringVar()
        self.spec_id = tk.StringVar()
        spec_row = ttk.Frame(self.spec_frame)
        spec_row.pack()
        ttk.Entry(spec_row, textvariable=self.spec_nick, width=20).pack(side="left")
        ttk.Entry(spec_row, textvariable=self.spec_id, width=30).pack(side="left")
        ttk.Button(spec_row, text="Add", command=self.add_spectator).pack(side="left")
        self.spec_list = tk.Listbox(self.spec_frame)
        self.spec_list.pack(fill="x")
        ttk.Button(self.spec_frame, text="Remove Selected", command=self.remove_spectator).pack()
        ttk.Button(self.spec_frame, text="Save Spectators", command=self.save_spectators).pack()
        ttk.Button(self.spec_frame, text="Load Spectators", command=self.load_spectators).pack()

        self.cvar_frame = ttk.LabelFrame(self.main_frame, text="Server CVARs")
        self.cvar_frame.grid(row=3, column=0, columnspan=3, sticky="ew", padx=10, pady=10)
        self.cvar_vars = {key: tk.StringVar(value=value) for key, value in DEFAULT_CVARS.items()}
        for key, var in self.cvar_vars.items():
            row = ttk.Frame(self.cvar_frame)
            row.pack(fill="x")
            ttk.Label(row, text=key, width=25).pack(side="left")
            ttk.Entry(row, textvariable=var).pack(side="left", fill="x", expand=True)

        ttk.Button(self.main_frame, text="Generate Config", command=self.generate_config).grid(row=4, column=0, columnspan=3, pady=20)

    def add_spectator(self):
        sid = self.spec_id.get().strip()
        nick = self.spec_nick.get().strip()
        if not (sid and nick):
            return
        if not is_valid_steamid(sid):
            messagebox.showerror("Invalid SteamID", "Spectator SteamID must be a 17-digit numeric string.")
            return
        if sid in self.spectators:
            messagebox.showwarning("Duplicate", f"Spectator SteamID {sid} already added.")
            return
        self.spectators[sid] = nick
        self.update_spec_list()
        self.spec_nick.set("")
        self.spec_id.set("")

    def remove_spectator(self):
        sel = self.spec_list.curselection()
        if sel:
            sid = list(self.spectators.keys())[sel[0]]
            del self.spectators[sid]
            self.update_spec_list()

    def update_spec_list(self):
        self.spec_list.delete(0, tk.END)
        for sid, nick in self.spectators.items():
            self.spec_list.insert(tk.END, f"{nick} ({sid})")

    def save_spectators(self):
        with open(SPECTATOR_FILE, "w") as f:
            json.dump(self.spectators, f, indent=2)
        messagebox.showinfo("Saved", f"Spectators saved to {SPECTATOR_FILE}")

    def load_spectators(self):
        if os.path.exists(SPECTATOR_FILE):
            with open(SPECTATOR_FILE, "r") as f:
                self.spectators = json.load(f)
                self.update_spec_list()
            messagebox.showinfo("Loaded", f"Spectators loaded from {SPECTATOR_FILE}")
        else:
            messagebox.showwarning("Not Found", f"{SPECTATOR_FILE} not found")

    def generate_config(self):
        config = {
            "matchid": self.match_id.get(),
            "team1": self.team1.get_team_data(),
            "team2": self.team2.get_team_data(),
            "num_maps": 1 if self.match_type.get() == "bo1" else 3,
            "maplist": [m.get() for m, _ in self.map_vars if m.get()],
            "map_sides": [s.get() for _, s in self.map_vars if s.get()],
            "spectators": {"players": self.spectators},
            "clinch_series": True,
            "players_per_team": len(self.team1.players),
            "cvars": {k: v.get() for k, v in self.cvar_vars.items()}
        }

        if not config["cvars"]["hostname"]:
            config["cvars"]["hostname"] = f"{self.tournament_name.get()} | {self.match_id.get()} | {self.team1.get_team_name()} vs {self.team2.get_team_name()}"

        sanitized_tournament = sanitize_filename(self.tournament_name.get())
        sanitized_team1 = sanitize_filename(self.team1.get_team_name())
        sanitized_team2 = sanitize_filename(self.team2.get_team_name())

        default_filename = f"UA1_Match_{self.match_id.get()}-{sanitized_team1}_VS_{sanitized_team2}.json"
        save_path = filedialog.asksaveasfilename(defaultextension=".json", initialfile=default_filename, filetypes=[["JSON Files", "*.json"]])
        if save_path:
            with open(save_path, "w") as f:
                json.dump(config, f, indent=2)
            messagebox.showinfo("Success", f"Match config saved to {save_path}")

if __name__ == "__main__":
    root = tk.Tk()
    app = MatchConfigApp(root)
    root.mainloop()