# -*- coding: utf-8 -*-
import pygame
import random
import math
from utils import (
    draw_rounded_rect, draw_text_with_shadow, lerp, lerp_color, get_font,
    NEON_BLUE, NEON_GREEN, NEON_RED, NEON_PURPLE, NEON_YELLOW, WHITE, GRAY, DARK_GRAY, BLACK
)

class Button:
    def __init__(self, rect, text, font, base_color=DARK_GRAY, text_color=WHITE,
                 hover_color=NEON_BLUE, border_color=GRAY, border_width=2, radius=8, action=None):
        self.rect = pygame.Rect(rect)
        self.text = text
        self.font = font
        self.base_color = base_color
        self.text_color = text_color
        self.hover_color = hover_color
        self.border_color = border_color
        self.border_width = border_width
        self.radius = radius
        self.action = action
        
        self.is_hovered = False
        self.scale_factor = 1.0
        self.target_scale = 1.0

    def check_hover(self, mouse_pos):
        self.is_hovered = self.rect.collidepoint(mouse_pos)
        self.target_scale = 1.05 if self.is_hovered else 1.0

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.is_hovered and self.action:
                self.action()
                return True
        return False

    def update(self, dt):
        self.scale_factor = lerp(self.scale_factor, self.target_scale, 15 * dt)

    def draw(self, surface):
        w = int(self.rect.width * self.scale_factor)
        h = int(self.rect.height * self.scale_factor)
        cx, cy = self.rect.center
        draw_rect = pygame.Rect(cx - w // 2, cy - h // 2, w, h)
        
        color = self.hover_color if self.is_hovered else self.base_color
        border_color = WHITE if self.is_hovered else self.border_color
        
        draw_rounded_rect(surface, color, draw_rect, self.radius)
        if self.border_width > 0:
            draw_rounded_rect(surface, border_color, draw_rect, self.radius, self.border_width)
            
        draw_text_with_shadow(
            surface, self.text, self.font, self.text_color,
            draw_rect.center, shadow_color=BLACK, offset=(1, 1), align="center"
        )


class ProgressBar:
    def __init__(self, rect, max_val, current_val=0, bg_color=DARK_GRAY,
                 fill_color=NEON_GREEN, border_color=WHITE, radius=4):
        self.rect = pygame.Rect(rect)
        self.max_val = max(1.0, float(max_val))
        self.current_val = float(current_val)
        self.target_val = float(current_val)
        
        self.bg_color = bg_color
        self.fill_color = fill_color
        self.border_color = border_color
        self.radius = radius

    def set_value(self, val):
        self.target_val = max(0.0, min(self.max_val, float(val)))

    def set_instant_value(self, val):
        self.target_val = max(0.0, min(self.max_val, float(val)))
        self.current_val = self.target_val

    def update(self, dt):
        self.current_val = lerp(self.current_val, self.target_val, 10 * dt)

    def draw(self, surface):
        draw_rounded_rect(surface, self.bg_color, self.rect, self.radius)
        
        ratio = self.current_val / self.max_val
        fill_width = int(self.rect.width * ratio)
        
        if fill_width > 4:
            fill_rect = pygame.Rect(self.rect.x, self.rect.y, fill_width, self.rect.height)
            draw_rounded_rect(surface, self.fill_color, fill_rect, self.radius)
            
        if self.border_color:
            draw_rounded_rect(surface, self.border_color, self.rect, self.radius, 1)


class Particle:
    def __init__(self, x, y, vx, vy, color, size, duration, gravity=0):
        self.x = x
        self.y = y
        self.vx = vx
        self.vy = vy
        self.color = color
        self.size = size
        self.max_size = size
        self.duration = duration
        self.elapsed = 0.0
        self.gravity = gravity

    def update(self, dt):
        self.vy += self.gravity * dt
        self.x += self.vx * dt
        self.y += self.vy * dt
        self.elapsed += dt

    def draw(self, surface):
        if self.elapsed >= self.duration:
            return
        progress = self.elapsed / self.duration
        current_size = max(1.0, lerp(self.max_size, 1.0, progress))
        alpha = int(255 * (1.0 - progress))
        
        p_surf = pygame.Surface((int(current_size * 2), int(current_size * 2)), pygame.SRCALPHA)
        p_color = (*self.color, alpha) if len(self.color) == 3 else self.color
        pygame.draw.circle(p_surf, p_color, (int(current_size), int(current_size)), int(current_size))
        surface.blit(p_surf, (int(self.x - current_size), int(self.y - current_size)))

    def is_dead(self):
        return self.elapsed >= self.duration


class ParticleSystem:
    def __init__(self):
        self.particles = []

    def emit(self, x, y, vx_range, vy_range, color_list, size_range, duration_range, count=1, gravity=0):
        for _ in range(count):
            vx = random.uniform(*vx_range)
            vy = random.uniform(*vy_range)
            color = random.choice(color_list)
            size = random.uniform(*size_range)
            duration = random.uniform(*duration_range)
            self.particles.append(Particle(x, y, vx, vy, color, size, duration, gravity))

    def update(self, dt):
        for p in self.particles:
            p.update(dt)
        self.particles = [p for p in self.particles if not p.is_dead()]

    def draw(self, surface):
        for p in self.particles:
            p.draw(surface)


class Notification:
    def __init__(self, text, color=NEON_YELLOW, duration=2.5):
        self.text = text
        self.color = color
        self.duration = duration
        self.elapsed = 0.0
        self.y_offset = -50
        self.font = get_font(20, bold=True)

    def update(self, dt):
        self.elapsed += dt
        if self.elapsed < 0.3:
            self.y_offset = lerp(self.y_offset, 20, 10 * dt)
        elif self.elapsed > self.duration - 0.3:
            self.y_offset = lerp(self.y_offset, -50, 10 * dt)
        else:
            self.y_offset = 20

    def draw(self, surface, screen_width):
        rect = pygame.Rect(20, int(self.y_offset), screen_width - 40, 36)
        bg_surf = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
        bg_surf.fill((0, 0, 0, 200))
        surface.blit(bg_surf, rect.topleft)
        
        pygame.draw.rect(surface, self.color, rect, 1, border_radius=6)
        
        draw_text_with_shadow(
            surface, self.text, self.font, self.color,
            rect.center, shadow_color=BLACK, offset=(1, 1), align="center"
        )

    def is_dead(self):
        return self.elapsed >= self.duration


class NotificationManager:
    def __init__(self):
        self.active_notif = None
        self.queue = []

    def show(self, text, color=NEON_YELLOW, duration=2.5):
        self.queue.append(Notification(text, color, duration))

    def update(self, dt):
        if self.active_notif:
            self.active_notif.update(dt)
            if self.active_notif.is_dead():
                self.active_notif = None
        
        if not self.active_notif and self.queue:
            self.active_notif = self.queue.pop(0)

    def draw(self, surface, screen_width):
        if self.active_notif:
            self.active_notif.draw(surface, screen_width)
