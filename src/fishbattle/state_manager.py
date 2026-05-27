# -*- coding: utf-8 -*-
import pygame

class State:
    def __init__(self, manager):
        self.manager = manager
        self.profile = manager.profile
        self.notifications = manager.notifications

    def enter(self, **kwargs):
        pass

    def exit(self):
        pass

    def handle_event(self, event):
        pass

    def update(self, dt):
        pass

    def draw(self, surface):
        pass


class StateManager:
    def __init__(self, profile, notifications):
        self.profile = profile
        self.notifications = notifications
        self.states = {}
        self.current_state = None
        self.current_state_name = ""

    def register(self, name, state_instance):
        self.states[name] = state_instance

    def change_to(self, name, **kwargs):
        if self.current_state:
            self.current_state.exit()
            
        prev_state = self.current_state_name
        self.current_state = self.states[name]
        self.current_state_name = name
        
        kwargs["prev_state"] = prev_state
        self.current_state.enter(**kwargs)

    def handle_event(self, event):
        if self.current_state:
            self.current_state.handle_event(event)

    def update(self, dt):
        if self.current_state:
            self.current_state.update(dt)

    def draw(self, surface):
        if self.current_state:
            self.current_state.draw(surface)
