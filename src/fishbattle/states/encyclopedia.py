# -*- coding: utf-8 -*-
import pygame
from state_manager import State
from ui import Button
from utils import (
    draw_text_with_shadow, draw_rounded_rect, get_font,
    NEON_BLUE, NEON_GREEN, NEON_RED, NEON_YELLOW, WHITE, GRAY, DARK_GRAY, BLACK, RARITY_COLORS
)
from data import FISH

class EncyclopediaState(State):
    def __init__(self, manager):
        super().__init__(manager)
        self.font_title = get_font(28, bold=True)
        self.font_header = get_font(16, bold=True)
        self.font_text = get_font(11)
        self.font_bold = get_font(11, bold=True)
        
        self.back_button = Button((80, 580, 200, 40), "메인 메뉴로 (Back)", self.font_header, action=lambda: self.manager.change_to("MENU"))
        
        # Paginate or scroll if needed, but 12 fish fit in 2 columns x 6 rows
        # FISH are ordered FISH_01 to FISH_12

    def handle_event(self, event):
        mouse_pos = self.manager.mouse_pos
        self.back_button.check_hover(mouse_pos)
        self.back_button.handle_event(event)

    def update(self, dt):
        self.back_button.update(dt)

    def draw(self, surface):
        # Background
        for y in range(640):
            ratio = y / 640.0
            r = int(15 * (1.0 - ratio) + 20 * ratio)
            g = int(15 * (1.0 - ratio) + 30 * ratio)
            b = int(25 * (1.0 - ratio) + 40 * ratio)
            pygame.draw.line(surface, (r, g, b), (0, y), (360, y))

        # Title
        draw_text_with_shadow(surface, "물고기 도감 (Fish Book)", self.font_title, NEON_BLUE, (180, 25), offset=(2, 2))
        
        # Stats summary
        total_types = len(FISH)
        caught_types = sum(1 for f_id in FISH if f_id in self.profile.encyclopedia)
        draw_text_with_shadow(surface, f"발견율: {caught_types} / {total_types} ({int(caught_types/total_types*100)}%)", self.font_header, WHITE, (180, 60))

        # Content Box
        draw_rounded_rect(surface, (0, 0, 0, 80), (10, 85, 340, 480), 8)
        pygame.draw.rect(surface, GRAY, (10, 85, 340, 480), 1, border_radius=8)

        # 2 columns x 6 rows grid
        fish_ids = sorted(FISH.keys())
        box_w = 158
        box_h = 68
        x_gap = 10
        y_gap = 8
        
        start_x = 17
        start_y = 95
        
        for idx, f_id in enumerate(fish_ids):
            row = idx // 2
            col = idx % 2
            
            x = start_x + col * (box_w + x_gap)
            y = start_y + row * (box_h + y_gap)
            
            fish_data = FISH[f_id]
            is_caught = f_id in self.profile.encyclopedia
            
            # Draw item box background
            box_rect = pygame.Rect(x, y, box_w, box_h)
            
            # Rarity border
            border_color = GRAY
            if is_caught:
                border_color = RARITY_COLORS[fish_data["rarity"]]
                
            draw_rounded_rect(surface, (30, 30, 30, 150), box_rect, 6)
            pygame.draw.rect(surface, border_color, box_rect, 1, border_radius=6)
            
            if is_caught:
                # Caught fish details
                record = self.profile.encyclopedia[f_id]
                rarity_text = "일반" if fish_data["rarity"] == "common" else "희귀" if fish_data["rarity"] == "rare" else "전설"
                
                # Name & Rarity
                draw_text_with_shadow(surface, fish_data["name"], self.font_header, border_color, (x + 8, y + 10), align="left")
                draw_text_with_shadow(surface, rarity_text, self.font_bold, border_color, (x + box_w - 8, y + 10), align="right")
                
                # Stats
                draw_text_with_shadow(surface, f"최대 크기: {record['max_size']:.1f} cm", self.font_text, WHITE, (x + 8, y + 32), align="left")
                draw_text_with_shadow(surface, f"낚은 횟수: {record['count']}회", self.font_text, WHITE, (x + 8, y + 48), align="left")
                draw_text_with_shadow(surface, f"가치: {fish_data['gold']}G", self.font_text, NEON_YELLOW, (x + box_w - 8, y + 48), align="right")
            else:
                # Uncaught silhouette
                draw_text_with_shadow(surface, "???", self.font_header, GRAY, (x + box_w // 2, y + box_h // 2 - 10), align="center")
                draw_text_with_shadow(surface, "미발견", self.font_text, DARK_GRAY, (x + box_w // 2, y + box_h // 2 + 10), align="center")
                
        self.back_button.draw(surface)
