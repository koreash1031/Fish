# -*- coding: utf-8 -*-
import json
import os
from data import ITEMS, MAPS, FISH

# Save file path. On Android, it must be written in the user home directory (which is writeable).
import sys
if sys.platform == "android" or "ANDROID_ARGUMENT" in os.environ:
    SAVE_FILE = os.path.join(os.path.expanduser("~"), "save_data.json")
else:
    SAVE_FILE = "save_data.json"

class PlayerProfile:
    def __init__(self):
        self.gold = 200
        self.equipped = {
            "ROD": "ROD_01",
            "REEL": "REEL_01",
            "BOBBER": "BOB_01",
            "KEEP": "KEEP_01"
        }
        self.levels = {
            "ROD": 0,
            "REEL": 0,
            "BOBBER": 0,
            "KEEP": 0
        }
        self.unlocked_boats = ["BOAT_01"]
        self.equipped_boat = "BOAT_01"
        
        self.baits = {
            "BAIT_01": 9999,
            "BAIT_02": 0,
            "BAIT_03": 0,
            "BAIT_04": 0,
            "BAIT_05": 0
        }
        self.equipped_bait = "BAIT_01"
        
        self.encyclopedia = {}
        self.fish_keep = []
        self.current_map = "MAP_01"

    def load(self):
        if os.path.exists(SAVE_FILE):
            try:
                with open(SAVE_FILE, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    self.gold = data.get("gold", 200)
                    self.equipped = data.get("equipped", self.equipped)
                    self.levels = data.get("levels", self.levels)
                    self.unlocked_boats = data.get("unlocked_boats", ["BOAT_01"])
                    self.equipped_boat = data.get("equipped_boat", "BOAT_01")
                    self.baits = data.get("baits", self.baits)
                    self.baits["BAIT_01"] = 9999
                    self.equipped_bait = data.get("equipped_bait", "BAIT_01")
                    self.encyclopedia = data.get("encyclopedia", {})
                    self.current_map = data.get("current_map", "MAP_01")
            except Exception as e:
                print(f"Error loading save data: {e}")

    def save(self):
        data = {
            "gold": self.gold,
            "equipped": self.equipped,
            "levels": self.levels,
            "unlocked_boats": self.unlocked_boats,
            "equipped_boat": self.equipped_boat,
            "baits": self.baits,
            "equipped_bait": self.equipped_bait,
            "encyclopedia": self.encyclopedia,
            "current_map": self.current_map
        }
        try:
            with open(SAVE_FILE, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=4)
        except Exception as e:
            print(f"Error saving save data: {e}")

    def get_rod_dmg_mult(self):
        rod_id = self.equipped["ROD"]
        lv_idx = self.levels["ROD"]
        return ITEMS["ROD"][rod_id]["stats"][lv_idx]

    def get_reel_power(self):
        reel_id = self.equipped["REEL"]
        lv_idx = self.levels["REEL"]
        return ITEMS["REEL"][reel_id]["stats"][lv_idx]

    def get_bobber_radius_bonus(self):
        bob_id = self.equipped["BOBBER"]
        lv_idx = self.levels["BOBBER"]
        return ITEMS["BOBBER"][bob_id]["stats"][lv_idx]

    def get_keep_capacity(self):
        keep_id = self.equipped["KEEP"]
        lv_idx = self.levels["KEEP"]
        return ITEMS["KEEP"][keep_id]["stats"][lv_idx]

    def is_keep_full(self):
        return len(self.fish_keep) >= self.get_keep_capacity()

    def add_fish_to_keep(self, fish_id, size, is_new_record=False):
        if self.is_keep_full():
            return False
        
        self.fish_keep.append({
            "id": fish_id,
            "size": size
        })
        
        if fish_id not in self.encyclopedia:
            self.encyclopedia[fish_id] = {"count": 0, "max_size": 0.0}
        
        self.encyclopedia[fish_id]["count"] += 1
        if size > self.encyclopedia[fish_id]["max_size"]:
            self.encyclopedia[fish_id]["max_size"] = size
            is_new_record = True
            
        self.save()
        return is_new_record

    def sell_all_fish(self):
        total_gold_earned = 0
        for f_item in self.fish_keep:
            fish_id = f_item["id"]
            base_gold = FISH[fish_id]["gold"]
            size = f_item["size"]
            min_size = FISH[fish_id]["min_size"]
            max_size = FISH[fish_id]["max_size"]
            
            size_ratio = (size - min_size) / max(1, max_size - min_size)
            gold_mult = 1.0 + (size_ratio * 0.5)
            earned = int(base_gold * gold_mult)
            total_gold_earned += earned
            
        self.gold += total_gold_earned
        self.fish_keep = []
        if total_gold_earned > 0:
            self.save()
        return total_gold_earned
