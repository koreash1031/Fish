# -*- coding: utf-8 -*-
import pygame
import math
import random
from state_manager import State
from ui import Button
from utils import (
    draw_text_with_shadow, draw_rounded_rect, get_font,
    NEON_BLUE, NEON_GREEN, NEON_RED, NEON_YELLOW, NEON_PURPLE, NEON_ORANGE,
    WHITE, GRAY, DARK_GRAY, BLACK, RARITY_COLORS
)
from data import MAPS, ITEMS

class MenuState(State):
    def __init__(self, manager):
        super().__init__(manager)
        self.font_title = get_font(44, bold=True)
        self.font_button = get_font(20, bold=True)
        self.font_desc = get_font(14)
        
        self.show_map_select = False
        self.wave_offset = 0.0
        self.particles = []
        
        # Initialize menu buttons
        self.menu_buttons = [
            Button((80, 260, 200, 45), "낚시 시작 (Start)", self.font_button, action=lambda: self.manager.change_to("FISHING")),
            Button((80, 320, 200, 45), "상 점 (Shop)", self.font_button, action=lambda: self.manager.change_to("SHOP")),
            Button((80, 380, 200, 45), "도 감 (Encyclopedia)", self.font_button, action=lambda: self.manager.change_to("ENCYCLOPEDIA")),
            Button((80, 440, 200, 45), "게임 종료 (Exit)", self.font_button, action=lambda: pygame.event.post(pygame.event.Event(pygame.QUIT)))
        ]
        
        # Map select buttons
        self.map_buttons = []
        self.back_button = Button((80, 560, 200, 40), "뒤로 가기 (Back)", self.font_button, action=self.close_map_select)

    def enter(self, **kwargs):
        self.show_map_select = False
        self.wave_offset = 0.0
        self.profile.sell_all_fish() # Automatically sell fish when returning to menu

    def open_map_select(self):
        self.show_map_select = True
        self.setup_map_buttons()

    def close_map_select(self):
        self.show_map_select = False

    def setup_map_buttons(self):
        self.map_buttons = []
        y_start = 140
        for i, (map_id, map_data) in enumerate(MAPS.items()):
            boat_req = map_data["boat_req"]
            unlocked = boat_req in self.profile.unlocked_boats
            
            # Action when map is clicked
            # Need to capture map_id in lambda correctly
            def make_action(mid=map_id):
                return lambda: self.select_map(mid)
                
            btn_text = map_data["name"]
            if not unlocked:
                boat_name = ITEMS["BOAT"][boat_req]["name"]
                btn_text = f"🔒 {map_data['name']}"
                action = lambda b=boat_name: self.notifications.show(f"{b}가 필요합니다!", NEON_RED)
            else:
                action = make_action()
                
            btn = Button(
                (40, y_start + i * 95, 280, 50), btn_text, self.font_button,
                base_color=DARK_GRAY if unlocked else (30, 30, 30),
                border_color=NEON_BLUE if unlocked else GRAY,
                action=action
            )
            self.map_buttons.append((btn, map_data, unlocked))

    def select_map(self, map_id):
        self.profile.current_map = map_id
        self.profile.save()
        self.manager.change_to("FISHING")

    def handle_event(self, event):
        # Update hover states
        mouse_pos = self.manager.mouse_pos
        
        if self.show_map_select:
            self.back_button.check_hover(mouse_pos)
            self.back_button.handle_event(event)
            for btn, _, _ in self.map_buttons:
                btn.check_hover(mouse_pos)
                btn.handle_event(event)
        else:
            for btn in self.menu_buttons:
                btn.check_hover(mouse_pos)
                btn.handle_event(event)

    def update(self, dt):
        self.wave_offset += 2.0 * dt
        
        # Update particles in menu background for visual punch
        if len(self.particles) < 15 and random.random() < 0.05:
            self.particles.append({
                "x": random.randint(0, 360),
                "y": 640 + 10,
                "speed": random.uniform(30, 70),
                "size": random.randint(2, 5),
                "color": random.choice([NEON_BLUE, NEON_PURPLE, NEON_GREEN]),
                "alpha": random.randint(50, 150)
            })
            
        for p in self.particles:
            p["y"] -= p["speed"] * dt
            
        self.particles = [p for p in self.particles if p["y"] > -10]
        
        # Update buttons
        if self.show_map_select:
            self.back_button.update(dt)
            for btn, _, _ in self.map_buttons:
                btn.update(dt)
        else:
            for btn in self.menu_buttons:
                btn.update(dt)

    def draw(self, surface):
        # Draw background gradient
        for y in range(640):
            # Slow interpolation from very dark blue to cyan-blue
            ratio = y / 640.0
            r = int(10 * (1.0 - ratio) + 5 * ratio)
            g = int(15 * (1.0 - ratio) + 40 * ratio)
            b = int(35 * (1.0 - ratio) + 80 * ratio)
            pygame.draw.line(surface, (r, g, b), (0, y), (360, y))
            
        # Draw floating particles
        for p in self.particles:
            temp_surf = pygame.Surface((p["size"] * 2, p["size"] * 2), pygame.SRCALPHA)
            pygame.draw.circle(temp_surf, (*p["color"], p["alpha"]), (p["size"], p["size"]), p["size"])
            surface.blit(temp_surf, (int(p["x"] - p["size"]), int(p["y"] - p["size"])))

        # Draw water waves at the bottom
        for wave_idx in range(3):
            wave_y = 520 + wave_idx * 40
            points = []
            for x in range(0, 365, 10):
                # Calculate wave height using sine waves
                sine_val = math.sin((x / 50.0) + self.wave_offset + wave_idx * 1.5)
                y = wave_y + sine_val * 15
                points.append((x, y))
            points.append((360, 640))
            points.append((0, 640))
            
            # Translucent wave color
            wave_color = (0, 120 + wave_idx * 30, 200 + wave_idx * 20, 80 - wave_idx * 15)
            wave_surf = pygame.Surface((360, 640), pygame.SRCALPHA)
            pygame.draw.polygon(wave_surf, wave_color, points)
            surface.blit(wave_surf, (0, 0))

        # Top Bar (Gold & Stats)
        draw_rounded_rect(surface, (0, 0, 0, 120), (10, 10, 340, 40), 6)
        draw_text_with_shadow(surface, f"Gold: {self.profile.gold} G", self.font_button, NEON_YELLOW, (20, 20), align="left")
        boat_name = ITEMS["BOAT"][self.profile.equipped_boat]["name"]
        draw_text_with_shadow(surface, f"{boat_name}", self.font_button, WHITE, (340, 20), align="right")

        if not self.show_map_select:
            # Main Menu screen
            # Glowing Game Title
            draw_text_with_shadow(surface, "FISHBATTLE", self.font_title, NEON_BLUE, (180, 130), shadow_color=NEON_PURPLE, offset=(3, 3))
            draw_text_with_shadow(surface, "피시 배틀", self.font_button, NEON_GREEN, (180, 185))
            
            # Draw buttons
            for btn in self.menu_buttons:
                btn.draw(surface)
        else:
            # Map Selection screen
            draw_text_with_shadow(surface, "지역 선택 (Map Select)", self.font_title, WHITE, (180, 80), offset=(2, 2))
            
            # Draw map selection list
            for btn, map_data, unlocked in self.map_buttons:
                btn.draw(surface)
                
                # Draw description below map button
                rect = btn.rect
                desc_color = GRAY if not unlocked else NEON_GREEN
                
                # Display rates for rare/epic fish
                rates = map_data["rates"]
                epic_prob = int(rates["epic"][0] * 100)
                rare_prob = int(rates["rare"][0] * 100)
                info_text = f"희귀 {rare_prob}% | 전설 {epic_prob}% - {map_data['visual_desc']}"
                
                # Draw short info text below button
                draw_text_with_shadow(
                    surface, info_text, self.font_desc, desc_color,
                    (rect.x + 10, rect.bottom + 4), align="left"
                )
                
            self.back_button.draw(surface)
