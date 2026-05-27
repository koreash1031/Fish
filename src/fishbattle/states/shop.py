# -*- coding: utf-8 -*-
import pygame
from state_manager import State
from ui import Button
from utils import (
    draw_text_with_shadow, draw_rounded_rect, get_font,
    NEON_BLUE, NEON_GREEN, NEON_RED, NEON_YELLOW, NEON_ORANGE,
    WHITE, GRAY, DARK_GRAY, BLACK
)
from data import ITEMS

class ShopState(State):
    def __init__(self, manager):
        super().__init__(manager)
        self.font_title = get_font(28, bold=True)
        self.font_header = get_font(20, bold=True)
        self.font_button = get_font(14, bold=True)
        self.font_text = get_font(13)
        
        self.active_tab = "GEAR" # GEAR, BOAT, BAIT
        
        # Tab buttons
        self.tab_buttons = {
            "GEAR": Button((15, 60, 100, 35), "장비 강화", self.font_button, action=lambda: self.set_tab("GEAR")),
            "BOAT": Button((130, 60, 100, 35), "보트 구매", self.font_button, action=lambda: self.set_tab("BOAT")),
            "BAIT": Button((245, 60, 100, 35), "미끼 상점", self.font_button, action=lambda: self.set_tab("BAIT"))
        }
        
        self.back_button = Button((80, 580, 200, 40), "메인 메뉴로 (Back)", self.font_header, action=lambda: self.manager.change_to("MENU"))
        
        # Dynamic scroll offset or list of buttons for each tab
        self.action_buttons = []

    def enter(self, **kwargs):
        self.set_tab(self.active_tab)
        # Sell all fish automatically when entering town/shop
        earned = self.profile.sell_all_fish()
        if earned > 0:
            self.notifications.show(f"보관함의 물고기를 모두 판매하여 +{earned} G를 획득했습니다!", NEON_GREEN, 3.5)

    def set_tab(self, tab_name):
        self.active_tab = tab_name
        self.refresh_buttons()

    def refresh_buttons(self):
        self.action_buttons = []
        
        # Tab highlight color updating
        for name, btn in self.tab_buttons.items():
            if name == self.active_tab:
                btn.base_color = NEON_BLUE
                btn.border_color = WHITE
            else:
                btn.base_color = DARK_GRAY
                btn.border_color = GRAY

        if self.active_tab == "GEAR":
            self.setup_gear_tab()
        elif self.active_tab == "BOAT":
            self.setup_boat_tab()
        elif self.active_tab == "BAIT":
            self.setup_bait_tab()

    def setup_gear_tab(self):
        # 4 types of gear: ROD, REEL, BOBBER, KEEP
        gear_types = ["ROD", "REEL", "BOBBER", "KEEP"]
        y_pos = 115
        
        for gear_type in gear_types:
            curr_id = self.profile.equipped[gear_type]
            curr_lv = self.profile.levels[gear_type] # 0-4
            
            gear_data = ITEMS[gear_type][curr_id]
            name = gear_data["name"]
            
            # 1. Upgrade button
            if curr_lv < 4: # Max level index 4 (Lv.5)
                cost = gear_data["upgrade_cost"]
                
                # Check current and next stats
                curr_stat = gear_data["stats"][curr_lv]
                next_stat = gear_data["stats"][curr_lv + 1]
                
                def do_upgrade(gt=gear_type, c=cost):
                    self.upgrade_gear(gt, c)
                    
                up_btn = Button(
                    (195, y_pos + 30, 70, 30), f"강화 {cost}G", self.font_button,
                    base_color=(50, 80, 50), border_color=NEON_GREEN,
                    action=do_upgrade
                )
            else:
                up_btn = Button(
                    (195, y_pos + 30, 70, 30), "MAX", self.font_button,
                    base_color=(30, 30, 30), border_color=GRAY,
                    action=None
                )
                
            self.action_buttons.append(up_btn)
            
            # 2. Buy Next Tier button
            # Find next item in database
            sorted_keys = sorted(ITEMS[gear_type].keys()) # ROD_01, ROD_02, etc.
            curr_idx = sorted_keys.index(curr_id)
            
            if curr_idx < len(sorted_keys) - 1:
                next_id = sorted_keys[curr_idx + 1]
                next_data = ITEMS[gear_type][next_id]
                next_price = next_data["price"]
                
                def do_buy_tier(gt=gear_type, nid=next_id, price=next_price):
                    self.buy_gear_tier(gt, nid, price)
                    
                buy_btn = Button(
                    (275, y_pos + 30, 70, 30), f"구매 {next_price}G", self.font_button,
                    base_color=(80, 50, 50), border_color=NEON_YELLOW,
                    action=do_buy_tier
                )
            else:
                buy_btn = Button(
                    (275, y_pos + 30, 70, 30), "최고 등급", self.font_button,
                    base_color=(30, 30, 30), border_color=GRAY,
                    action=None
                )
                
            self.action_buttons.append(buy_btn)
            y_pos += 115

    def setup_boat_tab(self):
        boats = sorted(ITEMS["BOAT"].items()) # BOAT_01, BOAT_02, etc.
        y_pos = 120
        
        for i, (boat_id, boat_data) in enumerate(boats):
            is_unlocked = boat_id in self.profile.unlocked_boats
            is_equipped = self.profile.equipped_boat == boat_id
            
            # Button logic
            if is_equipped:
                btn = Button((250, y_pos + 25, 95, 30), "사용 중", self.font_button, base_color=(30, 60, 30), border_color=NEON_GREEN)
            elif is_unlocked:
                def equip_boat(bid=boat_id):
                    self.profile.equipped_boat = bid
                    self.profile.save()
                    self.refresh_buttons()
                    self.notifications.show(f"{ITEMS['BOAT'][bid]['name']}를 장착했습니다.", NEON_BLUE)
                    
                btn = Button((250, y_pos + 25, 95, 30), "장착하기", self.font_button, base_color=DARK_GRAY, border_color=WHITE, action=equip_boat)
            else:
                price = boat_data["price"]
                def buy_boat(bid=boat_id, pr=price):
                    self.purchase_boat(bid, pr)
                    
                btn = Button((250, y_pos + 25, 95, 30), f"{price} G 구매", self.font_button, base_color=(80, 50, 50), border_color=NEON_YELLOW, action=buy_boat)
                
            self.action_buttons.append(btn)
            y_pos += 110

    def setup_bait_tab(self):
        baits = sorted(ITEMS["BAIT"].items()) # BAIT_01, BAIT_02, etc.
        y_pos = 115
        
        for i, (bait_id, bait_data) in enumerate(baits):
            is_free = bait_data["price"] == 0
            
            if is_free:
                btn = Button((250, y_pos + 17, 95, 30), "무제한", self.font_button, base_color=DARK_GRAY, border_color=GRAY)
            else:
                price = bait_data["price"]
                pack = bait_data["pack_size"]
                def buy_bait(bid=bait_id, pr=price, pk=pack):
                    self.purchase_bait(bid, pr, pk)
                    
                btn = Button((250, y_pos + 17, 95, 30), f"{price}G (10개)", self.font_button, base_color=(50, 80, 50), border_color=NEON_GREEN, action=buy_bait)
                
            self.action_buttons.append(btn)
            y_pos += 90

    # Operations
    def upgrade_gear(self, gear_type, cost):
        if self.profile.gold >= cost:
            self.profile.gold -= cost
            self.profile.levels[gear_type] += 1
            self.profile.save()
            self.refresh_buttons()
            self.notifications.show("장비 강화 성공!", NEON_GREEN)
        else:
            self.notifications.show("골드가 부족합니다!", NEON_RED)

    def buy_gear_tier(self, gear_type, next_id, price):
        if self.profile.gold >= price:
            self.profile.gold -= price
            self.profile.equipped[gear_type] = next_id
            self.profile.levels[gear_type] = 0 # Starts at Lv 1 (index 0)
            self.profile.save()
            self.refresh_buttons()
            self.notifications.show(f"{ITEMS[gear_type][next_id]['name']} 장착 성공!", NEON_YELLOW)
        else:
            self.notifications.show("골드가 부족합니다!", NEON_RED)

    def purchase_boat(self, boat_id, price):
        if self.profile.gold >= price:
            self.profile.gold -= price
            self.profile.unlocked_boats.append(boat_id)
            self.profile.equipped_boat = boat_id # Auto equip
            self.profile.save()
            self.refresh_buttons()
            self.notifications.show(f"{ITEMS['BOAT'][boat_id]['name']} 구매 및 장착 성공!", NEON_GREEN)
        else:
            self.notifications.show("골드가 부족합니다!", NEON_RED)

    def purchase_bait(self, bait_id, price, pack_size):
        if self.profile.gold >= price:
            self.profile.gold -= price
            self.profile.baits[bait_id] = self.profile.baits.get(bait_id, 0) + pack_size
            self.profile.save()
            self.refresh_buttons()
            self.notifications.show(f"{ITEMS['BAIT'][bait_id]['name']} {pack_size}개 구매 완료!", NEON_GREEN)
        else:
            self.notifications.show("골드가 부족합니다!", NEON_RED)

    def handle_event(self, event):
        mouse_pos = self.manager.mouse_pos
        
        self.back_button.check_hover(mouse_pos)
        self.back_button.handle_event(event)
        
        for tab_name, btn in self.tab_buttons.items():
            btn.check_hover(mouse_pos)
            btn.handle_event(event)
            
        for btn in self.action_buttons:
            btn.check_hover(mouse_pos)
            btn.handle_event(event)

    def update(self, dt):
        self.back_button.update(dt)
        for tab_name, btn in self.tab_buttons.items():
            btn.update(dt)
        for btn in self.action_buttons:
            btn.update(dt)

    def draw(self, surface):
        # Background
        for y in range(640):
            ratio = y / 640.0
            r = int(25 * (1.0 - ratio) + 15 * ratio)
            g = int(20 * (1.0 - ratio) + 15 * ratio)
            b = int(25 * (1.0 - ratio) + 30 * ratio)
            pygame.draw.line(surface, (r, g, b), (0, y), (360, y))

        # Title
        draw_text_with_shadow(surface, "마을 상점 (Town Shop)", self.font_title, NEON_BLUE, (180, 25), offset=(2, 2))
        
        # Gold
        draw_rounded_rect(surface, (0, 0, 0, 100), (210, 15, 135, 30), 4)
        draw_text_with_shadow(surface, f"보유 Gold: {self.profile.gold} G", self.font_button, NEON_YELLOW, (277, 30))

        # Draw tabs
        for tab_name, btn in self.tab_buttons.items():
            btn.draw(surface)

        # Tab Content Box
        draw_rounded_rect(surface, (0, 0, 0, 80), (10, 105, 340, 460), 8)
        pygame.draw.rect(surface, GRAY, (10, 105, 340, 460), 1, border_radius=8)

        # Draw content
        if self.active_tab == "GEAR":
            self.draw_gear_tab(surface)
        elif self.active_tab == "BOAT":
            self.draw_boat_tab(surface)
        elif self.active_tab == "BAIT":
            self.draw_bait_tab(surface)

        self.back_button.draw(surface)

    def draw_gear_tab(self, surface):
        gear_types = ["ROD", "REEL", "BOBBER", "KEEP"]
        y_pos = 115
        labels = {
            "ROD": ("낚싯대", "리듬 데미지 배율", "x"),
            "REEL": ("릴", "릴링 파워 (m/s)", "m/s"),
            "BOBBER": ("찌", "타겟 반경 보정", "+ px"),
            "KEEP": ("살림망", "최대 보관 마리", "마리")
        }
        
        btn_idx = 0
        for gear_type in gear_types:
            curr_id = self.profile.equipped[gear_type]
            curr_lv = self.profile.levels[gear_type]
            
            gear_data = ITEMS[gear_type][curr_id]
            curr_val = gear_data["stats"][curr_lv]
            
            # Render labels
            title_lbl, stat_lbl, unit = labels[gear_type]
            
            # Border box for each row
            draw_rounded_rect(surface, (40, 40, 40, 100), (15, y_pos - 5, 330, 105), 6)
            pygame.draw.rect(surface, DARK_GRAY, (15, y_pos - 5, 330, 105), 1, border_radius=6)
            
            draw_text_with_shadow(surface, f"{title_lbl}: {gear_data['name']}", self.font_header, WHITE, (25, y_pos + 15), align="left")
            draw_text_with_shadow(surface, f"현재 레벨: Lv.{curr_lv + 1} ({curr_val}{unit})", self.font_text, GRAY, (25, y_pos + 42), align="left")
            
            # Next level stats
            if curr_lv < 4:
                next_val = gear_data["stats"][curr_lv + 1]
                draw_text_with_shadow(surface, f"강화 시 ➔ {next_val}{unit}", self.font_text, NEON_GREEN, (25, y_pos + 62), align="left")
            else:
                draw_text_with_shadow(surface, "최대 강화 레벨 도달", self.font_text, NEON_BLUE, (25, y_pos + 62), align="left")
                
            # Draw buttons in this row
            if btn_idx < len(self.action_buttons):
                self.action_buttons[btn_idx].draw(surface)
                self.action_buttons[btn_idx+1].draw(surface)
                
            btn_idx += 2
            y_pos += 115

    def draw_boat_tab(self, surface):
        boats = sorted(ITEMS["BOAT"].items())
        y_pos = 120
        
        for i, (boat_id, boat_data) in enumerate(boats):
            is_unlocked = boat_id in self.profile.unlocked_boats
            
            draw_rounded_rect(surface, (40, 40, 40, 100), (15, y_pos - 5, 330, 95), 6)
            pygame.draw.rect(surface, DARK_GRAY, (15, y_pos - 5, 330, 95), 1, border_radius=6)
            
            color = NEON_GREEN if is_unlocked else GRAY
            draw_text_with_shadow(surface, boat_data["name"], self.font_header, color, (25, y_pos + 15), align="left")
            draw_text_with_shadow(surface, boat_data["desc"], self.font_text, WHITE, (25, y_pos + 45), align="left")
            
            # Draw button
            if i < len(self.action_buttons):
                self.action_buttons[i].draw(surface)
                
            y_pos += 110

    def draw_bait_tab(self, surface):
        baits = sorted(ITEMS["BAIT"].items())
        y_pos = 115
        
        for i, (bait_id, bait_data) in enumerate(baits):
            draw_rounded_rect(surface, (40, 40, 40, 100), (15, y_pos - 5, 330, 75), 6)
            pygame.draw.rect(surface, DARK_GRAY, (15, y_pos - 5, 330, 75), 1, border_radius=6)
            
            draw_text_with_shadow(surface, bait_data["name"], self.font_header, WHITE, (25, y_pos + 12), align="left")
            
            owned = self.profile.baits.get(bait_id, 0)
            owned_str = "무제한" if bait_id == "BAIT_01" else f"보유: {owned}개"
            draw_text_with_shadow(surface, owned_str, self.font_text, NEON_YELLOW, (25, y_pos + 42), align="left")
            
            # Buff info
            buff_str = f"대기-{int(bait_data['time_reduction'])}초 | 희귀+{int(bait_data['rare_mod']*100)}% 전설+{int(bait_data['epic_mod']*100)}%"
            draw_text_with_shadow(surface, buff_str, self.font_text, GRAY, (130, y_pos + 42), align="left")
            
            # Draw button
            if i < len(self.action_buttons):
                self.action_buttons[i].draw(surface)
                
            y_pos += 90
