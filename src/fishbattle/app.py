# -*- coding: utf-8 -*-
import pygame
import sys
import os

# Set working directory to the directory of this file to resolve resources correctly
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BASE_DIR)
os.chdir(BASE_DIR)

from profile import PlayerProfile
from ui import NotificationManager
from state_manager import StateManager
from utils import BLACK

# Virtual resolution
V_WIDTH = 360
V_HEIGHT = 640

def main():
    pygame.init()
    pygame.font.init()
    
    # We set initial window size (can scale up)
    win_width = 396
    win_height = 704
    window = pygame.display.set_mode((win_width, win_height), pygame.RESIZABLE)
    pygame.display.set_caption("FishBattle")
    
    virtual_screen = pygame.Surface((V_WIDTH, V_HEIGHT))
    
    clock = pygame.time.Clock()
    
    # Load profile
    profile = PlayerProfile()
    profile.load()
    
    # Notification manager
    notifications = NotificationManager()
    
    # State Manager
    state_manager = StateManager(profile, notifications)
    
    # Import states
    from states.menu import MenuState
    from states.fishing import FishingState
    from states.shop import ShopState
    from states.encyclopedia import EncyclopediaState
    
    # Register states
    state_manager.register("MENU", MenuState(state_manager))
    state_manager.register("FISHING", FishingState(state_manager))
    state_manager.register("SHOP", ShopState(state_manager))
    state_manager.register("ENCYCLOPEDIA", EncyclopediaState(state_manager))
    
    # Start at fishing immediately
    state_manager.change_to("FISHING")
    
    running = True
    while running:
        # Calculate delta time (seconds)
        dt = clock.tick(60) / 1000.0
        dt = min(dt, 0.1)
        
        # Get mouse pos relative to virtual screen
        real_mouse_pos = pygame.mouse.get_pos()
        current_win_w, current_win_h = window.get_size()
        
        scale = min(current_win_w / V_WIDTH, current_win_h / V_HEIGHT)
        scaled_w = int(V_WIDTH * scale)
        scaled_h = int(V_HEIGHT * scale)
        offset_x = (current_win_w - scaled_w) // 2
        offset_y = (current_win_h - scaled_h) // 2
        
        mx = (real_mouse_pos[0] - offset_x) / scale
        my = (real_mouse_pos[1] - offset_y) / scale
        virtual_mouse_pos = (int(mx), int(my))
        
        # Inject virtual mouse pos into state manager
        state_manager.mouse_pos = virtual_mouse_pos
        
        # Handle events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                profile.save()
                running = False
                
            elif event.type == pygame.VIDEORESIZE:
                pass
                
            state_manager.handle_event(event)
            
        state_manager.update(dt)
        notifications.update(dt)
        
        # Draw
        virtual_screen.fill(BLACK)
        state_manager.draw(virtual_screen)
        notifications.draw(virtual_screen, V_WIDTH)
        
        window.fill(BLACK)
        
        scaled_surf = pygame.transform.smoothscale(virtual_screen, (scaled_w, scaled_h))
        window.blit(scaled_surf, (offset_x, offset_y))
        
        pygame.display.flip()
        
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
