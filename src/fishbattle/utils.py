# -*- coding: utf-8 -*-
import pygame
import random
import math

# Palettes
NEON_BLUE = (0, 191, 255)
NEON_GREEN = (57, 255, 20)
NEON_RED = (255, 7, 58)
NEON_PURPLE = (188, 19, 254)
NEON_YELLOW = (255, 239, 0)
NEON_ORANGE = (255, 110, 0)
WHITE = (255, 255, 255)
GRAY = (128, 128, 128)
DARK_GRAY = (40, 40, 40)
BLACK = (0, 0, 0)

# Difficulty colors
RARITY_COLORS = {
    "common": (200, 200, 200),
    "rare": NEON_BLUE,
    "epic": NEON_YELLOW
}

def get_font(size, bold=False):
    return pygame.font.SysFont(["malgungothic", "gulim", "dotum", "applegothic", "nanumgothic", "arial"], size, bold=bold)

def lerp(a, b, t):
    return a + (b - a) * t

def lerp_color(c1, c2, t):
    t = max(0.0, min(1.0, t))
    return (
        int(lerp(c1[0], c2[0], t)),
        int(lerp(c1[1], c2[1], t)),
        int(lerp(c1[2], c2[2], t))
    )

def draw_text_with_shadow(surface, text, font, color, pos, shadow_color=(0, 0, 0), offset=(2, 2), align="center"):
    text_surf = font.render(text, True, color)
    shadow_surf = font.render(text, True, shadow_color)
    
    rect = text_surf.get_rect()
    if align == "center":
        rect.center = pos
    elif align == "left":
        rect.topleft = pos
    elif align == "right":
        rect.topright = pos
        
    shadow_pos = (rect.x + offset[0], rect.y + offset[1])
    surface.blit(shadow_surf, shadow_pos)
    surface.blit(text_surf, rect)
    return rect

def draw_neon_glow_circle(surface, color, center, radius, width=2, glow_factor=3):
    """Draws a circles with surrounding glow."""
    for i in range(glow_factor, 0, -1):
        alpha = int(100 / (i + 1))
        glow_radius = radius + i * 2
        glow_color = (*color, alpha)
        
        temp_surface = pygame.Surface((glow_radius * 2, glow_radius * 2), pygame.SRCALPHA)
        pygame.draw.circle(temp_surface, glow_color, (glow_radius, glow_radius), glow_radius, width + i)
        surface.blit(temp_surface, (center[0] - glow_radius, center[1] - glow_radius))
        
    pygame.draw.circle(surface, color, center, radius, width)

def draw_rounded_rect(surface, color, rect, radius=8, width=0):
    """Draws a rounded rectangle using pygame.draw.rect"""
    pygame.draw.rect(surface, color, rect, width=width, border_radius=radius)

class FloatingText:
    def __init__(self, text, x, y, color=WHITE, font_size=24, speed_y=-50, duration=1.0):
        self.text = text
        self.x = x
        self.y = y
        self.color = color
        self.font_size = font_size
        self.speed_y = speed_y
        self.duration = duration
        self.elapsed = 0.0
        self.font = get_font(font_size, bold=True)
        
    def update(self, dt):
        self.y += self.speed_y * dt
        self.elapsed += dt
        
    def draw(self, surface):
        if self.elapsed >= self.duration:
            return
        alpha = int(255 * (1.0 - (self.elapsed / self.duration)))
        text_surf = self.font.render(self.text, True, self.color)
        text_surf.set_alpha(alpha)
        
        rect = text_surf.get_rect(center=(int(self.x), int(self.y)))
        shadow_surf = self.font.render(self.text, True, (0, 0, 0))
        shadow_surf.set_alpha(int(alpha * 0.7))
        surface.blit(shadow_surf, (rect.x + 2, rect.y + 2))
        surface.blit(text_surf, rect)

    def is_dead(self):
        return self.elapsed >= self.duration
