# -*- coding: utf-8 -*-
import csv
import os

CSV_DIR = "CSV"
MAPS_CSV = os.path.join(CSV_DIR, "maps.csv")
FISH_CSV = os.path.join(CSV_DIR, "fish.csv")
ITEMS_CSV = os.path.join(CSV_DIR, "items.csv")

# 1. Hardcoded Default Fallbacks
DEFAULT_MAPS = {
    "MAP_01": {
        "id": "MAP_01", "name": "잔잔한 은빛 호수", "boat_req": "BOAT_01",
        "min_time": 3.0, "max_time": 10.0,
        "rates": {"common": (0.80, 0.60), "rare": (0.18, 0.10), "epic": (0.02, 0.00)},
        "visual_desc": "초보자용 구역. 평화로운 숲과 노을빛 호수 배경.",
        "bg_color": (30, 45, 60), "water_color": (50, 90, 120),
    },
    "MAP_02": {
        "id": "MAP_02", "name": "파도치는 갈매기 해변", "boat_req": "BOAT_02",
        "min_time": 4.0, "max_time": 12.0,
        "rates": {"common": (0.60, 0.40), "rare": (0.33, 0.20), "epic": (0.07, 0.02)},
        "visual_desc": "모래사장과 부서지는 파도. 갈매기 소리. 서서히 상승하는 난이도.",
        "bg_color": (40, 60, 80), "water_color": (40, 120, 160),
    },
    "MAP_03": {
        "id": "MAP_03", "name": "안개 낀 망각의 늪", "boat_req": "BOAT_03",
        "min_time": 5.0, "max_time": 15.0,
        "rates": {"common": (0.45, 0.25), "rare": (0.40, 0.25), "epic": (0.15, 0.05)},
        "visual_desc": "몽환적이고 어두운 늪지대. 안개 효과로 리듬 타겟 박스 식별이 까다로움.",
        "bg_color": (25, 35, 25), "water_color": (35, 70, 50),
    },
    "MAP_04": {
        "id": "MAP_04", "name": "심해의 불타는 산호초", "boat_req": "BOAT_04",
        "min_time": 6.0, "max_time": 18.0,
        "rates": {"common": (0.25, 0.10), "rare": (0.50, 0.30), "epic": (0.25, 0.10)},
        "visual_desc": "네온 빛을 내는 심해 생태계. 전설 물고기 비중이 높고 파이팅 저항이 매우 강함.",
        "bg_color": (15, 10, 30), "water_color": (60, 20, 120),
    }
}

DEFAULT_FISH = {
    "FISH_01": {
        "id": "FISH_01", "name": "피라미", "map_id": "MAP_01", "rarity": "common",
        "min_size": 5, "max_size": 15, "hp": 100, "min_dist": 10, "max_dist": 20,
        "ring_speed": 1.8, "target_radius": 50, "hold_time": 1.5, "gold": 10
    },
    "FISH_02": {
        "id": "FISH_02", "name": "붕어", "map_id": "MAP_01", "rarity": "common",
        "min_size": 15, "max_size": 35, "hp": 150, "min_dist": 15, "max_dist": 25,
        "ring_speed": 1.5, "target_radius": 45, "hold_time": 2.0, "gold": 25
    },
    "FISH_03": {
        "id": "FISH_03", "name": "황금 잉어", "map_id": "MAP_01", "rarity": "epic",
        "min_size": 50, "max_size": 90, "hp": 400, "min_dist": 35, "max_dist": 55,
        "ring_speed": 1.0, "target_radius": 30, "hold_time": 3.5, "gold": 300
    },
    "FISH_04": {
        "id": "FISH_04", "name": "보리멸", "map_id": "MAP_02", "rarity": "common",
        "min_size": 10, "max_size": 25, "hp": 130, "min_dist": 12, "max_dist": 22,
        "ring_speed": 1.6, "target_radius": 48, "hold_time": 1.8, "gold": 20
    },
    "FISH_05": {
        "id": "FISH_05", "name": "농어", "map_id": "MAP_02", "rarity": "rare",
        "min_size": 40, "max_size": 80, "hp": 300, "min_dist": 25, "max_dist": 45,
        "ring_speed": 1.2, "target_radius": 38, "hold_time": 2.8, "gold": 120
    },
    "FISH_06": {
        "id": "FISH_06", "name": "청상아리", "map_id": "MAP_02", "rarity": "epic",
        "min_size": 180, "max_size": 350, "hp": 800, "min_dist": 60, "max_dist": 100,
        "ring_speed": 0.8, "target_radius": 25, "hold_time": 4.5, "gold": 750
    },
    "FISH_07": {
        "id": "FISH_07", "name": "진흙 메기", "map_id": "MAP_03", "rarity": "common",
        "min_size": 30, "max_size": 60, "hp": 220, "min_dist": 20, "max_dist": 30,
        "ring_speed": 1.4, "target_radius": 40, "hold_time": 2.2, "gold": 50
    },
    "FISH_08": {
        "id": "FISH_08", "name": "독가시치", "map_id": "MAP_03", "rarity": "rare",
        "min_size": 20, "max_size": 40, "hp": 350, "min_dist": 22, "max_dist": 38,
        "ring_speed": 1.1, "target_radius": 35, "hold_time": 3.0, "gold": 180
    },
    "FISH_09": {
        "id": "FISH_09", "name": "늪지 크라켄", "map_id": "MAP_03", "rarity": "epic",
        "min_size": 200, "max_size": 500, "hp": 1000, "min_dist": 80, "max_dist": 120,
        "ring_speed": 0.7, "target_radius": 22, "hold_time": 5.0, "gold": 1200
    },
    "FISH_10": {
        "id": "FISH_10", "name": "클라운피시", "map_id": "MAP_04", "rarity": "common",
        "min_size": 8, "max_size": 15, "hp": 180, "min_dist": 10, "max_dist": 20,
        "ring_speed": 1.5, "target_radius": 45, "hold_time": 1.5, "gold": 60
    },
    "FISH_11": {
        "id": "FISH_11", "name": "대왕 다랑어", "map_id": "MAP_04", "rarity": "rare",
        "min_size": 100, "max_size": 220, "hp": 600, "min_dist": 45, "max_dist": 75,
        "ring_speed": 1.0, "target_radius": 32, "hold_time": 3.5, "gold": 450
    },
    "FISH_12": {
        "id": "FISH_12", "name": "화염룡 돗돔", "map_id": "MAP_04", "rarity": "epic",
        "min_size": 120, "max_size": 250, "hp": 1200, "min_dist": 100, "max_dist": 150,
        "ring_speed": 0.6, "target_radius": 20, "hold_time": 5.5, "gold": 2000
    }
}

DEFAULT_ITEMS = {
    "ROD": {
        "ROD_01": {
            "id": "ROD_01", "name": "대나무 낚싯대", "price": 0, "upgrade_cost": 100,
            "stats": [1.00, 1.05, 1.10, 1.15, 1.20]
        },
        "ROD_02": {
            "id": "ROD_02", "name": "카본 카스틸", "price": 800, "upgrade_cost": 300,
            "stats": [1.20, 1.30, 1.40, 1.50, 1.65]
        },
        "ROD_03": {
            "id": "ROD_03", "name": "발키리 티타늄", "price": 4500, "upgrade_cost": 1200,
            "stats": [1.70, 1.85, 2.00, 2.15, 2.35]
        },
        "ROD_04": {
            "id": "ROD_04", "name": "포세이돈의 삼지창", "price": 15000, "upgrade_cost": 4000,
            "stats": [2.50, 2.75, 3.00, 3.30, 3.70]
        }
    },
    "REEL": {
        "REEL_01": {
            "id": "REEL_01", "name": "플라스틱 스핀 릴", "price": 0, "upgrade_cost": 100,
            "stats": [3.0, 3.3, 3.6, 3.9, 4.2]
        },
        "REEL_02": {
            "id": "REEL_02", "name": "알루미늄 다이캐스팅", "price": 700, "upgrade_cost": 250,
            "stats": [4.5, 4.9, 5.3, 5.7, 6.2]
        },
        "REEL_03": {
            "id": "REEL_03", "name": "골드 드래그 베이트", "price": 4000, "upgrade_cost": 1000,
            "stats": [6.5, 7.1, 7.7, 8.3, 9.0]
        },
        "REEL_04": {
            "id": "REEL_04", "name": "레비아탄 다이얼", "price": 12000, "upgrade_cost": 3500,
            "stats": [10.0, 11.0, 12.0, 13.0, 14.5]
        }
    },
    "BOBBER": {
        "BOB_01": {
            "id": "BOB_01", "name": "코르크 원형 찌", "price": 0, "upgrade_cost": 50,
            "stats": [0, 1, 2, 3, 5]
        },
        "BOB_02": {
            "id": "BOB_02", "name": "시인성 오렌지 캐미", "price": 500, "upgrade_cost": 150,
            "stats": [3, 4, 5, 6, 8]
        },
        "BOB_03": {
            "id": "BOB_03", "name": "레이저 발광 LED찌", "price": 3000, "upgrade_cost": 800,
            "stats": [6, 8, 10, 12, 15]
        },
        "BOB_04": {
            "id": "BOB_04", "name": "스마트 수온감지찌", "price": 10000, "upgrade_cost": 2500,
            "stats": [12, 15, 18, 22, 28]
        }
    },
    "KEEP": {
        "KEEP_01": {
            "id": "KEEP_01", "name": "가죽 살림주머니", "price": 0, "upgrade_cost": 150,
            "stats": [5, 8, 11, 15, 20]
        },
        "KEEP_02": {
            "id": "KEEP_02", "name": "대형 와이어 살림망", "price": 2000, "upgrade_cost": 800,
            "stats": [20, 25, 30, 38, 50]
        }
    },
    "BOAT": {
        "BOAT_01": {
            "id": "BOAT_01", "name": "기본 맨발 (도보)", "price": 0,
            "desc": "MAP_01 진입 가능"
        },
        "BOAT_02": {
            "id": "BOAT_02", "name": "1인용 고무 보트", "price": 1500,
            "desc": "MAP_02 진입 가능"
        },
        "BOAT_03": {
            "id": "BOAT_03", "name": "구형 목재 어선", "price": 6000,
            "desc": "MAP_03 진입 가능"
        },
        "BOAT_04": {
            "id": "BOAT_04", "name": "쾌속 크루저", "price": 25000,
            "desc": "MAP_04 진입 가능"
        }
    },
    "BAIT": {
        "BAIT_01": {
            "id": "BAIT_01", "name": "기본 떡밥", "price": 0, "pack_size": 1,
            "time_reduction": 0.0, "rare_mod": 0.0, "epic_mod": 0.0
        },
        "BAIT_02": {
            "id": "BAIT_02", "name": "붉은 지렁이", "price": 50, "pack_size": 10,
            "time_reduction": 2.0, "rare_mod": 0.05, "epic_mod": 0.00
        },
        "BAIT_03": {
            "id": "BAIT_03", "name": "냉동 크릴새우", "price": 200, "pack_size": 10,
            "time_reduction": 4.0, "rare_mod": 0.10, "epic_mod": 0.03
        },
        "BAIT_04": {
            "id": "BAIT_04", "name": "야광 갯지렁이", "price": 600, "pack_size": 10,
            "time_reduction": 6.0, "rare_mod": 0.15, "epic_mod": 0.07
        },
        "BAIT_05": {
            "id": "BAIT_05", "name": "마스터 골드 루어", "price": 2000, "pack_size": 10,
            "time_reduction": 8.0, "rare_mod": 0.20, "epic_mod": 0.15
        }
    }
}

# 2. Setup CSV folder if missing
if not os.path.exists(CSV_DIR):
    os.makedirs(CSV_DIR)

# 3. Dynamic loaders
def load_maps():
    maps = {}
    try:
        if not os.path.exists(MAPS_CSV):
            write_default_maps_csv()
            
        with open(MAPS_CSV, mode="r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                map_id = row["id"]
                bg_col = tuple(map(int, row["bg_color"].split("|")))
                water_col = tuple(map(int, row["water_color"].split("|")))
                
                maps[map_id] = {
                    "id": map_id,
                    "name": row["name"],
                    "boat_req": row["boat_req"],
                    "min_time": float(row["min_time"]),
                    "max_time": float(row["max_time"]),
                    "rates": {
                        "common": (float(row["rates_common_base"]), float(row["rates_common_floor"])),
                        "rare": (float(row["rates_rare_base"]), float(row["rates_rare_floor"])),
                        "epic": (float(row["rates_epic_base"]), float(row["rates_epic_floor"]))
                    },
                    "visual_desc": row["visual_desc"],
                    "bg_color": bg_col,
                    "water_color": water_col
                }
    except Exception as e:
        print(f"Error loading maps CSV: {e}. Falling back to defaults.")
        maps = DEFAULT_MAPS
    return maps

def load_fish():
    fish = {}
    try:
        if not os.path.exists(FISH_CSV):
            write_default_fish_csv()
            
        with open(FISH_CSV, mode="r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                fish_id = row["id"]
                fish[fish_id] = {
                    "id": fish_id,
                    "name": row["name"],
                    "map_id": row["map_id"],
                    "rarity": row["rarity"],
                    "min_size": float(row["min_size"]),
                    "max_size": float(row["max_size"]),
                    "hp": float(row["hp"]),
                    "min_dist": int(float(row["min_dist"])),
                    "max_dist": int(float(row["max_dist"])),
                    "ring_speed": float(row["ring_speed"]),
                    "target_radius": int(float(row["target_radius"])),
                    "hold_time": float(row["hold_time"]),
                    "gold": int(row["gold"])
                }
    except Exception as e:
        print(f"Error loading fish CSV: {e}. Falling back to defaults.")
        fish = DEFAULT_FISH
    return fish

def load_items():
    items = {
        "ROD": {}, "REEL": {}, "BOBBER": {}, "KEEP": {}, "BOAT": {}, "BAIT": {}
    }
    try:
        if not os.path.exists(ITEMS_CSV):
            write_default_items_csv()
            
        with open(ITEMS_CSV, mode="r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                cat = row["category"]
                item_id = row["id"]
                
                item_dict = {
                    "id": item_id,
                    "name": row["name"],
                    "price": int(row["price"]) if row["price"] else 0
                }
                
                # Check optional fields
                if row.get("upgrade_cost"):
                    item_dict["upgrade_cost"] = int(row["upgrade_cost"])
                    
                if row.get("stats"):
                    raw_stats = row["stats"].split("|")
                    if cat in ("BOBBER", "KEEP"):
                        item_dict["stats"] = [int(x) for x in raw_stats if x]
                    else:
                        item_dict["stats"] = [float(x) for x in raw_stats if x]
                        
                if row.get("desc"):
                    item_dict["desc"] = row["desc"]
                    
                if row.get("pack_size"):
                    item_dict["pack_size"] = int(row["pack_size"])
                    
                if row.get("time_reduction"):
                    item_dict["time_reduction"] = float(row["time_reduction"])
                    
                if row.get("rare_mod"):
                    item_dict["rare_mod"] = float(row["rare_mod"])
                    
                if row.get("epic_mod"):
                    item_dict["epic_mod"] = float(row["epic_mod"])
                    
                items[cat][item_id] = item_dict
    except Exception as e:
        print(f"Error loading items CSV: {e}. Falling back to defaults.")
        items = DEFAULT_ITEMS
    return items

# 4. Default CSV Generators (if CSVs are deleted or missing)
def write_default_maps_csv():
    headers = [
        "id", "name", "boat_req", "min_time", "max_time",
        "rates_common_base", "rates_common_floor",
        "rates_rare_base", "rates_rare_floor",
        "rates_epic_base", "rates_epic_floor",
        "visual_desc", "bg_color", "water_color"
    ]
    with open(MAPS_CSV, mode="w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(headers)
        for m_id, m in DEFAULT_MAPS.items():
            bg_col_str = f"{m['bg_color'][0]}|{m['bg_color'][1]}|{m['bg_color'][2]}"
            water_col_str = f"{m['water_color'][0]}|{m['water_color'][1]}|{m['water_color'][2]}"
            writer.writerow([
                m_id, m["name"], m["boat_req"], m["min_time"], m["max_time"],
                m["rates"]["common"][0], m["rates"]["common"][1],
                m["rates"]["rare"][0], m["rates"]["rare"][1],
                m["rates"]["epic"][0], m["rates"]["epic"][1],
                m["visual_desc"], bg_col_str, water_col_str
            ])

def write_default_fish_csv():
    headers = ["id", "name", "map_id", "rarity", "min_size", "max_size", "hp", "min_dist", "max_dist", "ring_speed", "target_radius", "hold_time", "gold"]
    with open(FISH_CSV, mode="w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(headers)
        for f_id, fi in DEFAULT_FISH.items():
            writer.writerow([
                f_id, fi["name"], fi["map_id"], fi["rarity"],
                fi["min_size"], fi["max_size"], fi["hp"],
                fi["min_dist"], fi["max_dist"], fi["ring_speed"],
                fi["target_radius"], fi["hold_time"], fi["gold"]
            ])

def write_default_items_csv():
    headers = ["category", "id", "name", "price", "upgrade_cost", "stats", "desc", "pack_size", "time_reduction", "rare_mod", "epic_mod"]
    with open(ITEMS_CSV, mode="w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(headers)
        for cat, items_group in DEFAULT_ITEMS.items():
            for item_id, item in items_group.items():
                stats_str = "|".join(map(str, item.get("stats", [])))
                writer.writerow([
                    cat, item_id, item["name"], item.get("price", ""),
                    item.get("upgrade_cost", ""), stats_str, item.get("desc", ""),
                    item.get("pack_size", ""), item.get("time_reduction", ""),
                    item.get("rare_mod", ""), item.get("epic_mod", "")
                ])

# 5. Initialize active database
MAPS = load_maps()
FISH = load_fish()
ITEMS = load_items()
