# -*- coding: utf-8 -*-
import pygame
import os
import random
import math
from state_manager import State
from ui import Button, ProgressBar, ParticleSystem
from utils import (
    draw_text_with_shadow, draw_rounded_rect, draw_neon_glow_circle, FloatingText, get_font,
    NEON_BLUE, NEON_GREEN, NEON_RED, NEON_YELLOW, NEON_PURPLE, NEON_ORANGE,
    WHITE, GRAY, DARK_GRAY, BLACK, RARITY_COLORS, lerp
)
from data import MAPS, FISH, ITEMS

class FishingState(State):
    def __init__(self, manager):
        super().__init__(manager)
        self.font_title = get_font(28, bold=True)
        self.font_large = get_font(22, bold=True)
        self.font_hud = get_font(16, bold=True)
        self.font_desc = get_font(13)
        
        # Sub-states: CASTING, WAITING, FIGHTING_A, FIGHTING_B, SHOW_CATCH, KEEPFULL
        self.phase = "CASTING"
        self.phase_timer = 0.0
        
        # General state variables
        self.active_fish = None
        self.fish_hp = 0.0
        self.fish_max_hp = 100.0
        self.distance = 0.0
        self.max_distance = 10.0
        
        self.tension = 0.0 # 0.0 to 100.0
        self.time_limit = 45.0 # Max duration for fighting
        
        self.rhythm_score = 0
        self.rhythm_targets_total = 0
        
        # Phase A variables (Rhythm - Multi Target)
        self.rhythm_targets = []
        self.rhythm_target_id_counter = 0
        self.targets_remaining_in_phase = 0
        self.rhythm_spawn_cooldown = 0.0
        
        # Phase B variables (Tension Reeling)
        # Gesture variables removed
        
        # UI controls
        self.back_to_menu_btn = Button((20, 580, 150, 40), "마을로 돌아가기", self.font_hud, action=lambda: self.manager.change_to("MENU"))
        self.change_map_btn = Button((190, 580, 150, 40), "지역 이동", self.font_hud, action=self.open_map_select_popup)
        self.bait_buttons = []
        
        # Map select popup controls
        self.show_map_select_popup = False
        self.map_select_buttons = []
        self.map_select_back_btn = None
        
        # Systems
        self.particles = ParticleSystem()
        self.floating_texts = []
        
        # Environment variables
        self.wave_offset = 0.0
        self.boat_bob_y = 0.0

        # Load character image if it exists
        self.char_img = None
        char_path = os.path.join("Resources", "Hero", "Player.png")
        if os.path.exists(char_path):
            try:
                self.char_img = pygame.image.load(char_path).convert_alpha()
                # Scale it down to a cute size (e.g. 50x50)
                self.char_img = pygame.transform.smoothscale(self.char_img, (50, 50))
            except Exception as e:
                print(f"Error loading player image: {e}")
                
        # Tension Reeling Battle variables
        self.strike_gauge = 0.0
        self.strike_ready = False
        self.stun_timer = 0.0
        self.is_reeling = False
        self.fish_pull = 0.0
        self.fish_pull_timer = 0.0
        self.slack_timer = 0.0
        self.reeling_timer_in_phase = 0.0
        
        # Fish Event Variables (TUG / RUSH)
        self.fish_event_timer = 0.0
        self.fish_event_type = "NORMAL"
        self.fish_event_announced = False
        
        # Snap Warning Timer
        self.snap_warning_timer = 0.0

    def enter(self, **kwargs):
        self.phase = "CASTING"
        self.phase_timer = 0.0
        self.tension = 0.0
        self.floating_texts = []
        self.active_fish = None
        self.strike_gauge = 0.0
        self.strike_ready = False
        self.stun_timer = 0.0
        self.is_reeling = False
        self.slack_timer = 0.0
        self.reeling_timer_in_phase = 0.0
        self.show_map_select_popup = False
        self.fish_event_timer = 0.0
        self.fish_event_type = "NORMAL"
        self.fish_event_announced = False
        self.snap_warning_timer = 0.0
        
        # Setup baits
        self.setup_bait_selection()
        
        # Automatically cast if keep is not full
        if self.profile.is_keep_full():
            self.phase = "KEEPFULL"
            self.notifications.show("살림망이 가득 찼습니다! 마을에서 판매하세요.", NEON_RED, 4.0)

    def setup_bait_selection(self):
        self.bait_buttons = []
        # Create buttons for baits
        baits = sorted(ITEMS["BAIT"].items())
        # Draw bait icons/buttons in bottom UI during Casting/Waiting
        btn_w = 60
        btn_h = 32
        x_start = 15
        for i, (bait_id, bait_data) in enumerate(baits):
            def equip_bait(bid=bait_id):
                self.equip_bait(bid)
                
            btn_text = bait_data["name"][:3] # Short name
            btn = Button(
                (x_start + i * 68, 520, btn_w, btn_h), btn_text, self.font_desc,
                base_color=DARK_GRAY, border_color=GRAY, action=equip_bait
            )
            self.bait_buttons.append((btn, bait_id))
        self.update_bait_buttons_colors()

    def update_bait_buttons_colors(self):
        for btn, bait_id in self.bait_buttons:
            if bait_id == self.profile.equipped_bait:
                btn.base_color = NEON_BLUE
                btn.border_color = WHITE
            else:
                btn.base_color = DARK_GRAY
                btn.border_color = GRAY

    def equip_bait(self, bait_id):
        owned = self.profile.baits.get(bait_id, 0)
        if bait_id == "BAIT_01" or owned > 0:
            self.profile.equipped_bait = bait_id
            self.profile.save()
            self.update_bait_buttons_colors()
            self.notifications.show(f"{ITEMS['BAIT'][bait_id]['name']}을 장착했습니다.", NEON_GREEN)
        else:
            self.notifications.show("미끼가 부족합니다! 상점에서 구매하세요.", NEON_RED)

    def handle_event(self, event):
        mouse_pos = self.manager.mouse_pos
        
        # 맵 선택 팝업 동작 중일 때
        if self.show_map_select_popup:
            if self.map_select_back_btn:
                self.map_select_back_btn.check_hover(mouse_pos)
                self.map_select_back_btn.handle_event(event)
            for btn, _, _ in self.map_select_buttons:
                btn.check_hover(mouse_pos)
                btn.handle_event(event)
            return
            
        # Catch Timer Event
        if event.type == pygame.USEREVENT + 1:
            pygame.time.set_timer(pygame.USEREVENT + 1, 0)
            if self.phase not in ("FIGHTING_A", "FIGHTING_B"):
                return
            if self.targets_remaining_in_phase <= 0:
                self.start_reeling_phase()
            else:
                self.start_new_rhythm_target()
            return
            
        if self.phase in ("CASTING", "WAITING", "KEEPFULL"):
            self.back_to_menu_btn.check_hover(mouse_pos)
            self.back_to_menu_btn.handle_event(event)
            self.change_map_btn.check_hover(mouse_pos)
            self.change_map_btn.handle_event(event)
            
            if self.phase != "KEEPFULL":
                for btn, _ in self.bait_buttons:
                    btn.check_hover(mouse_pos)
                    btn.handle_event(event)
                    
        elif self.phase == "FIGHTING_A":
            # Rhythm game click
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                self.handle_rhythm_click(mouse_pos)
                
        elif self.phase == "FIGHTING_B":
            # Reel button press
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                # Check click on Reel Button: center (180, 490), radius 45
                dist = math.hypot(mouse_pos[0] - 180, mouse_pos[1] - 490)
                if dist <= 45:
                    if self.strike_ready:
                        self.trigger_strike()
                    else:
                        self.is_reeling = True
            elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                self.is_reeling = False

        elif self.phase == "SHOW_CATCH":
            # Click anywhere to close catch popup and return to game loop
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if self.profile.is_keep_full():
                    self.phase = "KEEPFULL"
                else:
                    self.phase = "CASTING"
                    self.phase_timer = 0.0

    def update(self, dt):
        self.wave_offset += 1.5 * dt
        self.boat_bob_y = math.sin(pygame.time.get_ticks() / 600.0) * 4.0
        
        self.particles.update(dt)
        for t in self.floating_texts:
            t.update(dt)
        self.floating_texts = [t for t in self.floating_texts if not t.is_dead()]
        
        # 맵 선택 팝업 업데이트
        if self.show_map_select_popup:
            if self.map_select_back_btn:
                self.map_select_back_btn.update(dt)
            for btn, _, _ in self.map_select_buttons:
                btn.update(dt)
            return # 다른 낚시 진행 차단
            
        # Update back & change map buttons
        if self.phase in ("CASTING", "WAITING", "KEEPFULL"):
            self.back_to_menu_btn.update(dt)
            self.change_map_btn.update(dt)
            for btn, _ in self.bait_buttons:
                btn.update(dt)

        # Logic based on phase
        if self.phase == "CASTING":
            self.phase_timer += dt
            if self.phase_timer >= 1.5:
                self.start_waiting()
                
        elif self.phase == "WAITING":
            self.phase_timer -= dt
            if self.phase_timer <= 0.0:
                self.start_fighting()
                
        elif self.phase == "FIGHTING_A":
            if not self.active_fish:
                self.phase = "CASTING"
                self.phase_timer = 0.0
                return
            self.time_limit -= dt
            
            # Spawn new target dynamically
            self.rhythm_spawn_cooldown -= dt
            if self.rhythm_spawn_cooldown <= 0.0 and self.targets_remaining_in_phase > 0:
                self.spawn_rhythm_target()
                self.rhythm_spawn_cooldown = random.uniform(0.35, 0.55) # 스폰 주기 단축 (0.35~0.55초)
                
            # Update targets
            for target in self.rhythm_targets:
                if target["click_handled"]:
                    continue
                target["rhythm_timer"] += dt
                target["ring_scale"] = 1.8 - (target["rhythm_timer"] / target["ring_speed"]) * 1.8
                
                # Timeout check
                if target["ring_scale"] <= 0.0:
                    self.register_rhythm_hit_on_target(target, "MISS")
                    
            # Filter out dead targets
            self.rhythm_targets = [t for t in self.rhythm_targets if not t["click_handled"]]
            
            # Switch to Phase B if all targets are processed
            if self.targets_remaining_in_phase <= 0 and len(self.rhythm_targets) == 0:
                self.start_reeling_phase()
                return
                
            self.check_fight_end_conditions()
            
        elif self.phase == "FIGHTING_B":
            if not self.active_fish:
                self.phase = "CASTING"
                self.phase_timer = 0.0
                return
            self.time_limit -= dt
            self.reeling_timer_in_phase += dt
            
            # Stun logic
            self.stun_timer = max(0.0, self.stun_timer - dt)
            if self.stun_timer > 0.0:
                # Keep tension centered and pull rapidly
                self.tension = lerp(self.tension, 50.0, 10.0 * dt)
                self.distance = max(0.0, self.distance - 2.2 * (self.profile.get_reel_power() * 0.45) * dt)
                if random.random() < 0.25:
                    self.particles.emit(180, 160 + self.boat_bob_y, (-30, 30), (-30, 30), [NEON_YELLOW, WHITE], (2, 4), (0.3, 0.6), 2)
                self.fish_event_type = "NORMAL"
                self.fish_event_timer = 0.0
            else:
                # Fish Event System (TUG/RUSH/NORMAL) for extra excitement!
                self.fish_event_timer -= dt
                rarity = self.active_fish["rarity"]
                if self.fish_event_timer <= 0.0:
                    roll = random.random()
                    if rarity == "epic":
                        if roll < 0.40:
                            self.fish_event_type = "TUG"
                            self.fish_event_timer = random.uniform(0.7, 1.3)
                        elif roll < 0.65:
                            self.fish_event_type = "RUSH"
                            self.fish_event_timer = random.uniform(0.7, 1.3)
                        else:
                            self.fish_event_type = "NORMAL"
                            self.fish_event_timer = random.uniform(1.2, 2.2)
                    elif rarity == "rare":
                        if roll < 0.25:
                            self.fish_event_type = "TUG"
                            self.fish_event_timer = random.uniform(0.6, 1.1)
                        elif roll < 0.45:
                            self.fish_event_type = "RUSH"
                            self.fish_event_timer = random.uniform(0.6, 1.1)
                        else:
                            self.fish_event_type = "NORMAL"
                            self.fish_event_timer = random.uniform(1.5, 2.5)
                    else: # common
                        if roll < 0.15:
                            self.fish_event_type = "TUG"
                            self.fish_event_timer = random.uniform(0.5, 0.9)
                        elif roll < 0.30:
                            self.fish_event_type = "RUSH"
                            self.fish_event_timer = random.uniform(0.5, 0.9)
                        else:
                            self.fish_event_type = "NORMAL"
                            self.fish_event_timer = random.uniform(1.8, 2.8)
                    self.fish_event_announced = False
                
                # Fish Resistance AI & Vibration Wave (물고기의 불규칙 진동)
                self.fish_pull_timer -= dt
                if self.fish_pull_timer <= 0.0:
                    self.fish_pull_timer = random.uniform(0.8, 1.6) # 저항 주기 축소로 타이트함 증가
                    hp_ratio = self.fish_hp / self.fish_max_hp
                    base_pull = random.uniform(-15.0, 45.0) if hp_ratio > 0.5 else random.uniform(-5.0, 30.0)
                    
                    if rarity == "epic":
                        base_pull *= 1.45
                    self.fish_pull = base_pull
                    
                event_pull = 0.0
                if self.fish_event_type == "TUG":
                    # Strong sudden pull away (TUG 난이도를 피지컬 컨트롤이 가능하도록 하향 조정)
                    event_pull = 50.0 if rarity == "epic" else 30.0
                    if not self.fish_event_announced:
                        self.floating_texts.append(FloatingText("⚠️ TUG! 릴 놓기!", 180, 420, NEON_RED, 22, duration=0.8, speed_y=-50))
                        self.fish_event_announced = True
                        # Emit red shock particles from reel center
                        self.particles.emit(180, 480, (-50, 50), (-50, 50), [NEON_RED, WHITE], (2, 4), (0.2, 0.5), 10)
                elif self.fish_event_type == "RUSH":
                    # Sudden charge towards boat
                    event_pull = -60.0 if rarity == "epic" else -40.0
                    if not self.fish_event_announced:
                        self.floating_texts.append(FloatingText("⚡ SLACK! 감기!", 180, 420, NEON_BLUE, 22, duration=0.8, speed_y=-50))
                        self.fish_event_announced = True
                        # Emit blue shock particles from reel center
                        self.particles.emit(180, 480, (-50, 50), (-50, 50), [NEON_BLUE, WHITE], (2, 4), (0.2, 0.5), 10)
                
                # Real-time fish thrashing vibration wave (물고기 퍼덕임 부르르 진동 구현)
                hp_ratio = self.fish_hp / self.fish_max_hp
                vib_intensity = 16.0 if rarity == "epic" else 11.0
                if hp_ratio < 0.5:
                    vib_intensity *= 1.35
                vibration = math.sin(pygame.time.get_ticks() / 70.0) * vib_intensity
                
                # Update Tension (텐션 충전/방출 속도 조율로 합리적 탭 컨트롤 유도)
                if self.is_reeling:
                    self.tension += (80.0 + self.profile.get_reel_power() * 1.0) * dt
                else:
                    self.tension -= 165.0 * dt
                    
                self.tension += (self.fish_pull + event_pull + vibration) * dt
                self.tension = max(0.0, min(100.0, self.tension))
                
                # Slack check
                if self.tension <= 5.0:
                    self.slack_timer += dt
                    if self.slack_timer >= 1.8:
                        self.trigger_catch_fail("물고기가 느슨해진 줄에서 빠져 도망쳤습니다! (Line Slack)")
                        return
                else:
                    self.slack_timer = 0.0
                    
                # Sweet Spot check (40.0 to 70.0)
                if 40.0 <= self.tension <= 70.0:
                    reeling_speed_mult = 1.0
                    if self.fish_hp <= 0.0:
                        reeling_speed_mult = 2.0
                    self.distance = max(0.0, self.distance - (self.profile.get_reel_power() * 0.45) * reeling_speed_mult * dt)
                    
                    self.strike_gauge = min(100.0, self.strike_gauge + 25.0 * dt)
                    if self.strike_gauge >= 100.0:
                        self.strike_ready = True
                        
                    if random.random() < 0.15:
                        self.particles.emit(180, 160 + self.boat_bob_y, (-20, 20), (-20, 20), [NEON_GREEN, WHITE], (2, 3), (0.3, 0.6), 1)
                else:
                    self.strike_gauge = max(0.0, self.strike_gauge - 15.0 * dt)
                    if self.tension > 70.0:
                        self.distance = max(0.0, self.distance - 0.3 * (self.profile.get_reel_power() * 0.45) * dt)
                    elif self.tension < 40.0:
                        self.distance = min(self.max_distance, self.distance + 1.5 * dt)
                        
            # Snapped fail (단선 유예 장치를 추가하여 쪼는 맛과 극복하는 컨트롤 재미 부여)
            if self.tension >= 100.0:
                if self.is_reeling:
                    self.snap_warning_timer += dt
                    if self.snap_warning_timer >= 0.45: # 0.45초 동안 지속적으로 감을 경우에만 줄이 끊어짐
                        self.trigger_catch_fail("낚싯줄이 팽팽해져 끊어졌습니다! (Line Snapped)")
                        return
                else:
                    self.snap_warning_timer = max(0.0, self.snap_warning_timer - dt * 2.0)
            else:
                self.snap_warning_timer = 0.0
                
            # Phase transition back to A (Rhythm)
            trigger_rhythm = False
            transition_reason = "물고기가 몸부림칩니다! 버티세요!"
            
            if self.reeling_timer_in_phase >= self.reeling_target_time and self.stun_timer <= 0.0:
                trigger_rhythm = True
                transition_reason = "물고기가 거칠게 몸부림칩니다!"
                
            # Trigger 2: 텐션 위험 구역(85% 이상)에서 릴링을 할 때 무작위 몸부림 발동 (확률을 12%로 대폭 하향하여 컨트롤 위주로 극복 유도)
            elif self.tension >= 85.0 and self.is_reeling and self.stun_timer <= 0.0:
                if random.random() < 0.12 * dt: # 초당 약 12% 확률
                    trigger_rhythm = True
                    transition_reason = "텐션 위기! 물고기가 폭발적으로 저항합니다!"
                    
            # Trigger 3: 릴링으로 거리를 대폭 좁혔을 때 물고기의 기습 반격 몸부림 발동 (기준을 3m에서 6.5m로 완화하여 2페이즈 릴링 지속시간 연장)
            elif self.distance_at_phase_start - self.distance >= 6.5 and self.stun_timer <= 0.0:
                trigger_rhythm = True
                transition_reason = "물고기가 끌려오지 않으려 발악합니다!"
                # 물고기가 튀어나가며 약간 거리 후퇴 패널티
                self.distance = min(self.max_distance, self.distance + 1.5)
                
            if trigger_rhythm:
                self.notifications.show(transition_reason, NEON_RED, 2.0)
                self.floating_texts.append(FloatingText("THRASHING!!!", 180, 200, NEON_RED, 26, speed_y=-30, duration=1.5))
                self.is_reeling = False
                self.targets_remaining_in_phase = random.randint(2, 5) # 2~5개로 증가
                self.start_new_rhythm_target()
                
            self.check_fight_end_conditions()

    # Fishing Loop Triggers
    def start_waiting(self):
        self.phase = "WAITING"
        
        # Consume bait
        equipped_bait = self.profile.equipped_bait
        if equipped_bait != "BAIT_01":
            self.profile.baits[equipped_bait] -= 1
            if self.profile.baits[equipped_bait] <= 0:
                self.profile.equipped_bait = "BAIT_01" # Revert to infinite basic bait
                self.notifications.show("미끼를 다 소모하여 기본 떡밥으로 자동 변경됩니다.", NEON_ORANGE)
            self.profile.save()
            self.setup_bait_selection()
            
        # Calculate wait time
        map_data = MAPS[self.profile.current_map]
        bait_data = ITEMS["BAIT"][equipped_bait]
        
        min_time = map_data["min_time"]
        max_time = map_data["max_time"] - bait_data["time_reduction"]
        
        # Worst case limit protection
        max_time = max(min_time + 1.0, max_time)
        self.phase_timer = random.uniform(min_time, max_time)
        
        # Roll fish
        self.roll_fish(map_data, bait_data)

    def roll_fish(self, map_data, bait_data):
        # 1. Rarity Roll
        epic_rate, epic_floor = map_data["rates"]["epic"]
        rare_rate, rare_floor = map_data["rates"]["rare"]
        common_rate, common_floor = map_data["rates"]["common"]
        
        # Adjust with bait modifiers
        epic_final = max(epic_floor, epic_rate + bait_data["epic_mod"])
        rare_final = max(rare_floor, rare_rate + bait_data["rare_mod"])
        common_final = 1.0 - epic_final - rare_final
        
        roll = random.random()
        if roll < epic_final:
            rarity = "epic"
        elif roll < epic_final + rare_final:
            rarity = "rare"
        else:
            rarity = "common"
            
        # 2. Pick fish of rolled rarity in current map
        valid_fish = [f for f in FISH.values() if f["map_id"] == self.profile.current_map and f["rarity"] == rarity]
        
        # Rarity fallback
        if not valid_fish:
            valid_fish = [f for f in FISH.values() if f["map_id"] == self.profile.current_map]
            
        self.active_fish = random.choice(valid_fish)
        
        # Set up fight values
        self.fish_max_hp = float(self.active_fish["hp"])
        self.fish_hp = self.fish_max_hp
        self.distance = float(random.randint(self.active_fish["min_dist"], self.active_fish["max_dist"]))
        self.max_distance = self.distance
        
        self.rhythm_score = 0
        self.rhythm_targets_total = 0
        self.time_limit = 45.0
        self.tension = 0.0

    def start_fighting(self):
        self.phase = "FIGHTING_A"
        self.notifications.show("입질! FIGHTING!", NEON_RED, 1.5)
        self.floating_texts.append(FloatingText("HIT!!!", 180, 200, NEON_YELLOW, 36, speed_y=-30, duration=1.5))
        self.rhythm_targets = []
        self.rhythm_target_id_counter = 0
        self.targets_remaining_in_phase = random.randint(5, 8) # 스폰할 총 타겟 개수
        self.rhythm_spawn_cooldown = 0.0
        self.spawn_rhythm_target()

    def spawn_rhythm_target(self):
        if self.targets_remaining_in_phase <= 0:
            return
        
        tx = random.randint(50, 310)
        ty = random.randint(350, 510)
        
        # Target radius base + bobber bonus (원을 조금 더 작고 콤팩트하게 보정)
        base_radius = (float(self.active_fish["target_radius"]) + self.profile.get_bobber_radius_bonus()) * 0.62
        variance = random.uniform(0.85, 1.15)
        ring_speed = float(self.active_fish["ring_speed"]) * 0.65 * variance # 수축 속도 35% 향상
        
        target = {
            "id": self.rhythm_target_id_counter,
            "pos": (tx, ty),
            "radius": base_radius,
            "ring_scale": 1.8,
            "ring_speed": ring_speed,
            "rhythm_timer": 0.0,
            "click_handled": False
        }
        self.rhythm_target_id_counter += 1
        self.rhythm_targets.append(target)
        self.targets_remaining_in_phase -= 1

    def start_new_rhythm_target(self):
        self.phase = "FIGHTING_A"
        self.rhythm_targets = []
        self.targets_remaining_in_phase = random.randint(4, 7)
        self.rhythm_spawn_cooldown = 0.0
        self.spawn_rhythm_target()

    def handle_rhythm_click(self, mouse_pos):
        # Find the closest active target that was clicked
        clicked_target = None
        min_dist = 9999.0
        
        for target in self.rhythm_targets:
            if target["click_handled"]:
                continue
            dist = math.hypot(mouse_pos[0] - target["pos"][0], mouse_pos[1] - target["pos"][1])
            if dist <= target["radius"] * 1.5: # 판정 반경 1.5배 보정으로 쾌적한 터치
                if dist < min_dist:
                    min_dist = dist
                    clicked_target = target
                    
        if clicked_target:
            perfect_time = clicked_target["ring_speed"] * (2.0 / 3.0)
            diff = abs(clicked_target["rhythm_timer"] - perfect_time)
            
            if diff <= 0.07:
                self.register_rhythm_hit_on_target(clicked_target, "SPECIAL")
            elif diff <= 0.18:
                self.register_rhythm_hit_on_target(clicked_target, "VERY GOOD")
            elif diff <= 0.35:
                self.register_rhythm_hit_on_target(clicked_target, "GOOD")
            else:
                self.register_rhythm_hit_on_target(clicked_target, "MISS")

    def register_rhythm_hit_on_target(self, target, result):
        target["click_handled"] = True
        self.rhythm_targets_total += 1
        
        tx, ty = target["pos"]
        col = WHITE
        dmg_mult = 0.0
        score_add = 0
        
        if result == "SPECIAL":
            col = NEON_YELLOW
            dmg_mult = 1.0
            score_add = 5
            self.floating_texts.append(FloatingText("SPECIAL!!!", tx, ty - 15, col, 22))
            self.particles.emit(tx, ty, (-80, 80), (-80, 80), [NEON_YELLOW, WHITE], (3, 6), (0.4, 0.8), 20)
            self.tension = max(0.0, self.tension - 8.0)
        elif result == "VERY GOOD":
            col = NEON_GREEN
            dmg_mult = 0.75
            score_add = 2
            self.floating_texts.append(FloatingText("VERY GOOD!", tx, ty - 15, col, 20))
            self.particles.emit(tx, ty, (-60, 60), (-60, 60), [NEON_GREEN, WHITE], (2, 5), (0.4, 0.7), 12)
            self.tension = max(0.0, self.tension - 3.0)
        elif result == "GOOD":
            col = NEON_BLUE
            dmg_mult = 0.50
            score_add = 0
            self.floating_texts.append(FloatingText("GOOD", tx, ty - 15, col, 18))
            self.particles.emit(tx, ty, (-40, 40), (-40, 40), [NEON_BLUE, GRAY], (2, 4), (0.3, 0.6), 6)
        elif result == "MISS":
            col = NEON_RED
            dmg_mult = 0.0
            score_add = -3
            self.floating_texts.append(FloatingText("MISS", tx, ty - 15, col, 18))
            self.particles.emit(tx, ty, (-20, 20), (-20, 20), [NEON_RED, DARK_GRAY], (2, 4), (0.3, 0.5), 6)
            self.distance = min(self.max_distance, self.distance + 2.0)
            
        # Calculate Damage
        base_dmg = 45.0
        damage = base_dmg * dmg_mult * self.profile.get_rod_dmg_mult()
        self.fish_hp = max(0.0, self.fish_hp - damage)
        
        self.rhythm_score += score_add
        
        if self.fish_hp <= 0.0:
            self.notifications.show("물고기가 힘을 잃었습니다! 거리를 좁히세요!", NEON_YELLOW, 2.0)
            self.distance = max(1.0, self.distance - 4.5)
        
    # Fighting Phase B: Tension Reeling
    def start_reeling_phase(self):
        self.phase = "FIGHTING_B"
        self.reeling_timer_in_phase = 0.0
        self.is_reeling = False
        self.stun_timer = 0.0
        self.slack_timer = 0.0
        self.fish_pull_timer = 0.0
        self.fish_pull = 0.0
        rarity = self.active_fish["rarity"] if self.active_fish else "common"
        if rarity == "epic":
            self.reeling_target_time = random.uniform(14.0, 22.0)
        elif rarity == "rare":
            self.reeling_target_time = random.uniform(11.0, 18.0)
        else:
            self.reeling_target_time = random.uniform(9.0, 15.0)
        self.distance_at_phase_start = self.distance
        
        # Fish Event System (TUG/RUSH) for extra excitement!
        self.fish_event_timer = random.uniform(1.0, 1.8) # First event after 1-1.8s
        self.fish_event_type = "NORMAL"
        self.fish_event_announced = False
        self.snap_warning_timer = 0.0
        
        self.notifications.show("스위트 스팟을 유지하며 릴을 감으세요!", NEON_GREEN, 2.0)

    def trigger_strike(self):
        if not self.strike_ready:
            return
        self.strike_ready = False
        self.strike_gauge = 0.0
        self.stun_timer = 3.0
        
        # Pull distance significantly based on reel power
        strike_pull = 1.5 * self.profile.get_reel_power()
        self.distance = max(0.0, self.distance - strike_pull)
        
        # Feedback
        self.floating_texts.append(FloatingText("STRIKE!!!", 180, 200, NEON_YELLOW, 32, speed_y=-50, duration=2.0))
        self.particles.emit(180, 160 + self.boat_bob_y, (-150, 150), (-150, 150), [NEON_YELLOW, NEON_ORANGE, WHITE], (4, 8), (0.5, 1.0), 40)
        self.notifications.show("강력한 챔질! 물고기가 기절했습니다!", NEON_YELLOW, 2.0)

    def open_map_select_popup(self):
        self.show_map_select_popup = True
        self.map_select_buttons = []
        
        # Build map select buttons based on unlocked boats
        y_start = 160
        for i, (map_id, map_data) in enumerate(MAPS.items()):
            boat_req = map_data["boat_req"]
            unlocked = boat_req in self.profile.unlocked_boats
            
            def make_action(mid=map_id):
                return lambda: self.select_map_in_popup(mid)
                
            btn_text = map_data["name"]
            if not unlocked:
                boat_name = ITEMS["BOAT"][boat_req]["name"]
                btn_text = f"🔒 {map_data['name']}"
                action = lambda b=boat_name: self.notifications.show(f"{b}가 필요합니다!", NEON_RED)
            else:
                action = make_action()
                
            btn = Button(
                (50, y_start + i * 65, 260, 42), btn_text, self.font_hud,
                base_color=DARK_GRAY if unlocked else (30, 30, 30),
                border_color=NEON_BLUE if unlocked else GRAY,
                action=action
            )
            self.map_select_buttons.append((btn, map_data, unlocked))
            
        self.map_select_back_btn = Button((100, 440, 160, 35), "닫기", self.font_hud, action=self.close_map_select_popup)

    def close_map_select_popup(self):
        self.show_map_select_popup = False

    def select_map_in_popup(self, map_id):
        if self.profile.current_map != map_id:
            self.profile.current_map = map_id
            self.profile.save()
            self.notifications.show(f"{MAPS[map_id]['name']}(으)로 이동했습니다.", NEON_GREEN)
            
            # Restart casting loop on new map
            self.phase = "CASTING"
            self.phase_timer = 0.0
            self.active_fish = None
            self.floating_texts = []
            self.particles = ParticleSystem()
        self.show_map_select_popup = False

    # End Conditions
    def check_fight_end_conditions(self):
        # Success Catch
        if self.distance <= 0.0:
            self.trigger_catch_success()
            return
            
        # Fail Conditions
        fail_reason = ""
        if self.tension >= 100.0:
            fail_reason = "낚싯줄이 끊어졌습니다! (Line snapped)"
        elif self.time_limit <= 0.0:
            fail_reason = "제한 시간이 초과되었습니다! (Time out)"
            
        if fail_reason:
            self.trigger_catch_fail(fail_reason)

    def trigger_catch_success(self):
        self.phase = "SHOW_CATCH"
        pygame.time.set_timer(pygame.USEREVENT + 1, 0) # Clear timer
        
        # Calculate size based on rhythm accuracy
        min_size = float(self.active_fish["min_size"])
        max_size = float(self.active_fish["max_size"])
        
        # Maximum possible score (each target gives 5 max)
        # Prevent division by zero
        max_possible_score = max(5, self.rhythm_targets_total * 5)
        score_ratio = max(0.0, min(1.0, float(self.rhythm_score) / max_possible_score))
        
        final_size = min_size + (max_size - min_size) * score_ratio
        # Add slight randomness
        final_size += random.uniform(-0.5, 0.5)
        final_size = max(min_size, min(max_size, final_size))
        
        # Update profile
        is_new_record = self.profile.add_fish_to_keep(self.active_fish["id"], final_size)
        
        # Particles
        self.particles.emit(180, 160 + self.boat_bob_y, (-80, 80), (-80, 80), [NEON_GREEN, NEON_BLUE, WHITE], (3, 6), (0.4, 0.8), 20)
        self.notifications.show(f"{self.active_fish['name']} 포획 성공!", NEON_GREEN, 3.5)
        self.floating_texts.append(FloatingText("CATCH!", 180, 200, NEON_GREEN, 30, speed_y=-40, duration=2.5))
        
    def trigger_catch_fail(self, reason):
        self.phase = "CASTING"
        self.phase_timer = 0.0
        self.active_fish = None
        pygame.time.set_timer(pygame.USEREVENT + 1, 0)
        self.notifications.show(reason, NEON_RED, 3.5)
        self.floating_texts.append(FloatingText("놓쳤습니다!", 180, 200, NEON_RED, 26, duration=2.0))
        self.particles.emit(180, 160 + self.boat_bob_y, (-50, 50), (-50, 50), [GRAY, DARK_GRAY], (2, 5), (0.3, 0.6), 15)

    # Rendering Helpers
    def draw(self, target_surface):
        # Create temp surface for screen shake
        surface = pygame.Surface((360, 640))
        
        # Draw background based on map theme
        map_data = MAPS[self.profile.current_map]
        bg_col = map_data["bg_color"]
        water_col = map_data["water_color"]
        
        # 1. Sky & Environment Gradient
        for y in range(300):
            ratio = y / 300.0
            r = int(bg_col[0] * (1.0 - ratio) + (bg_col[0]+20) * ratio)
            g = int(bg_col[1] * (1.0 - ratio) + (bg_col[1]+20) * ratio)
            b = int(bg_col[2] * (1.0 - ratio) + (bg_col[2]+40) * ratio)
            pygame.draw.line(surface, (r, g, b), (0, y), (360, y))
            
        # Draw water from 150px down to 300px
        # We blend the water line with moving waves
        points = []
        for x in range(0, 365, 10):
            sine_val = math.sin((x / 30.0) + self.wave_offset)
            y = 150 + sine_val * 6
            points.append((x, y))
        points.append((360, 300))
        points.append((0, 300))
        
        # Fill water area
        pygame.draw.polygon(surface, water_col, points)
        
        # Draw some moving wave details on the water surface
        for i in range(4):
            wx = int((self.wave_offset * 40 + i * 110) % 400 - 40)
            wy = 175 + i * 25
            pygame.draw.line(surface, (255, 255, 255, 60), (wx, wy), (wx + 30, wy), 1)
 
        # 2. Draw Player & Boat
        boat_color = (139, 69, 19) # brown wood
        boat_req = map_data["boat_req"]
        if boat_req == "BOAT_02":
            boat_color = (255, 220, 0) # yellow rubber
        elif boat_req == "BOAT_03":
            boat_color = (100, 70, 40) # dark brown
        elif boat_req == "BOAT_04":
            boat_color = (240, 240, 250) # white yacht
            
        # Draw simple stylized boat at the bottom of the water area
        boat_rect = pygame.Rect(40, int(130 + self.boat_bob_y), 100, 30)
        draw_rounded_rect(surface, boat_color, boat_rect, radius=10)
        
        # Draw cute cat fisherman or custom player image
        bob_y = int(self.boat_bob_y)
        if self.char_img:
            # Draw custom player sprite centered above boat
            surface.blit(self.char_img, (105 - 25, int(112 + self.boat_bob_y) - 25))
        else:
            head_x, head_y = 105, 105 + bob_y
            
            # 1. Cat Body (cute yellow raincoat)
            body_rect = pygame.Rect(93, 114 + bob_y, 24, 20)
            draw_rounded_rect(surface, (255, 200, 50), body_rect, radius=6)
            
            # 2. Cat Head (orange-cream cat color)
            pygame.draw.circle(surface, (255, 180, 100), (head_x, head_y), 11)
            
            # 3. Cat Ears (two cute triangles)
            # Left ear
            pygame.draw.polygon(surface, (255, 180, 100), [(head_x - 10, head_y - 4), (head_x - 5, head_y - 12), (head_x - 2, head_y - 6)])
            pygame.draw.polygon(surface, (255, 140, 140), [(head_x - 8, head_y - 5), (head_x - 5, head_y - 10), (head_x - 4, head_y - 6)])
            # Right ear
            pygame.draw.polygon(surface, (255, 180, 100), [(head_x + 2, head_y - 6), (head_x + 5, head_y - 12), (head_x + 10, head_y - 4)])
            pygame.draw.polygon(surface, (255, 140, 140), [(head_x + 4, head_y - 6), (head_x + 5, head_y - 10), (head_x + 8, head_y - 5)])
            
            # 4. Cute Straw Hat
            # Brim
            pygame.draw.ellipse(surface, (220, 180, 100), (head_x - 14, head_y - 10, 28, 5))
            # Crown
            pygame.draw.circle(surface, (220, 180, 100), (head_x, head_y - 10), 6)
            
            # 5. Face details (cute closed eyes, pink nose, and whiskers)
            # Left eye
            pygame.draw.line(surface, BLACK, (head_x - 6, head_y + 1), (head_x - 3, head_y + 1), 1)
            # Right eye
            pygame.draw.line(surface, BLACK, (head_x + 3, head_y + 1), (head_x + 6, head_y + 1), 1)
            # Nose
            pygame.draw.circle(surface, (255, 120, 120), (head_x, head_y + 3), 2)
            # Whiskers
            pygame.draw.line(surface, (80, 80, 80), (head_x - 12, head_y + 3), (head_x - 6, head_y + 4), 1)
            pygame.draw.line(surface, (80, 80, 80), (head_x - 12, head_y + 6), (head_x - 6, head_y + 5), 1)
            pygame.draw.line(surface, (80, 80, 80), (head_x + 6, head_y + 4), (head_x + 12, head_y + 3), 1)
            pygame.draw.line(surface, (80, 80, 80), (head_x + 6, head_y + 5), (head_x + 12, head_y + 6), 1)
            
            # 6. Tiny Paw holding the rod
            pygame.draw.circle(surface, (255, 180, 100), (113, 118 + bob_y), 3)
        
        # 3. Draw Rod and Fishing line (if waiting or fighting)
        if self.phase in ("WAITING", "FIGHTING_A", "FIGHTING_B"):
            # Bending rod
            tip_x, tip_y = 170, int(80 + self.boat_bob_y)
            
            # Draw bending bezier or simple arcs
            if self.phase in ("FIGHTING_A", "FIGHTING_B"):
                # Bend more during fighting
                rod_mid_x, rod_mid_y = 140, int(85 + self.boat_bob_y)
                pygame.draw.line(surface, GRAY, (105, int(120 + self.boat_bob_y)), (rod_mid_x, rod_mid_y), 3)
                pygame.draw.line(surface, GRAY, (rod_mid_x, rod_mid_y), (tip_x, tip_y), 2)
            else:
                # Straighter
                pygame.draw.line(surface, GRAY, (105, int(120 + self.boat_bob_y)), (tip_x, tip_y), 3)
                
            # Fishing Line
            water_entry_x = 230
            # If fighting, line moves around
            if self.phase in ("FIGHTING_A", "FIGHTING_B"):
                water_entry_x = 200 + int(math.sin(pygame.time.get_ticks() / 150.0) * 35)
                
            pygame.draw.line(surface, (230, 230, 230, 180), (tip_x, tip_y), (water_entry_x, 150), 1)
            
            # Bobber or Splash
            if self.phase == "WAITING":
                # Floating Bobber
                bob_y = 150 + int(math.sin((water_entry_x / 30.0) + self.wave_offset) * 6)
                pygame.draw.circle(surface, NEON_RED, (water_entry_x, bob_y), 4)
                pygame.draw.circle(surface, WHITE, (water_entry_x, bob_y + 3), 3)
            else:
                # Water Splash during fight
                if random.random() < 0.3:
                    self.particles.emit(water_entry_x, 150, (-15, 15), (-35, -5), [NEON_BLUE, WHITE], (1, 3), (0.3, 0.6), 2, gravity=60)
                    
        # 4. Systems Render
        self.particles.draw(surface)
        for t in self.floating_texts:
            t.draw(surface)
 
        # 5. UI Panel Divider (at y=300)
        pygame.draw.line(surface, WHITE, (0, 300), (360, 300), 2)
        
        # HUD Area (Top overlay on upper area)
        draw_rounded_rect(surface, (0, 0, 0, 150), (10, 10, 340, 30), 4)
        draw_text_with_shadow(surface, f"{map_data['name']}", self.font_hud, WHITE, (20, 17), align="left")
        capacity = self.profile.get_keep_capacity()
        draw_text_with_shadow(surface, f"살림망: {len(self.profile.fish_keep)}/{capacity}", self.font_hud, NEON_GREEN, (340, 17), align="right")
 
        # Render lower UI based on Phase
        if self.phase == "CASTING":
            self.draw_casting_ui(surface)
        elif self.phase == "WAITING":
            self.draw_waiting_ui(surface)
        elif self.phase == "FIGHTING_A":
            self.draw_fighting_a_ui(surface)
        elif self.phase == "FIGHTING_B":
            self.draw_fighting_b_ui(surface)
        elif self.phase == "SHOW_CATCH":
            self.draw_catch_popup(surface)
        elif self.phase == "KEEPFULL":
            self.draw_keep_full_ui(surface)
            
        # Draw Map Select Popup overlay if active
        if self.show_map_select_popup:
            self.draw_map_select_popup(surface)
            
        # Screen Red Vignette Alert on high tension (쪼는 맛 극대화)
        if self.phase == "FIGHTING_B" and self.tension >= 80.0:
            alpha = int(70 + math.sin(pygame.time.get_ticks() / 50.0) * 50)
            vignette = pygame.Surface((360, 640), pygame.SRCALPHA)
            pygame.draw.rect(vignette, (255, 0, 0, alpha), (0, 0, 360, 640), 12)
            pygame.draw.rect(vignette, (255, 0, 0, alpha // 2), (0, 0, 360, 640), 24)
            surface.blit(vignette, (0, 0))
            
        # Camera Shake effect for High-Tension feedback
        shake_x = 0
        shake_y = 0
        if self.phase == "FIGHTING_B":
            if self.tension >= 80.0:
                shake_intensity = int(3 + (self.tension - 80) * 0.3)
                shake_x = random.randint(-shake_intensity, shake_intensity)
                shake_y = random.randint(-shake_intensity, shake_intensity)
            elif self.tension <= 15.0 and self.tension > 0.0:
                shake_x = random.randint(-1, 1)
                shake_y = random.randint(-1, 1)
            elif self.stun_timer > 0.0:
                shake_x = random.randint(-2, 2)
                shake_y = random.randint(-2, 2)
                
            # Extra shake during tug
            if self.fish_event_type == "TUG":
                shake_x += random.randint(-3, 3)
                shake_y += random.randint(-3, 3)
                
        target_surface.blit(surface, (shake_x, shake_y))

    # Sub-UI Drawing
    def draw_casting_ui(self, surface):
        # Draw bottom background
        surface.fill(DARK_GRAY, (0, 302, 360, 338))
        
        # Casting Progress
        progress = self.phase_timer / 1.5
        draw_text_with_shadow(surface, "자동 캐스팅 던지는 중...", self.font_large, WHITE, (180, 360))
        
        cast_bar = pygame.Rect(40, 400, 280, 20)
        draw_rounded_rect(surface, BLACK, cast_bar, 4)
        fill_bar = pygame.Rect(40, 400, int(280 * progress), 20)
        draw_rounded_rect(surface, NEON_GREEN, fill_bar, 4)
        pygame.draw.rect(surface, WHITE, cast_bar, 1, border_radius=4)
        
        # Bait selection label
        draw_text_with_shadow(surface, "낚시 미끼 선택", self.font_hud, NEON_YELLOW, (180, 480))
        for btn, _ in self.bait_buttons:
            btn.draw(surface)
            
        self.back_to_menu_btn.draw(surface)
        self.change_map_btn.draw(surface)

    def draw_waiting_ui(self, surface):
        surface.fill(DARK_GRAY, (0, 302, 360, 338))
        
        # Wait message
        draw_text_with_shadow(surface, "물고기 입질 대기 중...", self.font_large, NEON_BLUE, (180, 360))
        
        # Bait selection label
        draw_text_with_shadow(surface, "낚시 미끼 선택", self.font_hud, NEON_YELLOW, (180, 480))
        for btn, _ in self.bait_buttons:
            btn.draw(surface)
            
        self.back_to_menu_btn.draw(surface)
        self.change_map_btn.draw(surface)

    def draw_keep_full_ui(self, surface):
        surface.fill(DARK_GRAY, (0, 302, 360, 338))
        
        draw_text_with_shadow(surface, "살림망이 가득 찼습니다!", self.font_large, NEON_RED, (180, 360))
        draw_text_with_shadow(surface, "마을로 돌아가 물고기를 판매하여", self.font_hud, WHITE, (180, 400))
        draw_text_with_shadow(surface, "골드를 획득하고 살림망을 비우세요.", self.font_hud, WHITE, (180, 430))
        
        self.back_to_menu_btn.draw(surface)
        self.change_map_btn.draw(surface)

    def draw_fighting_a_ui(self, surface):
        # Fill background with dark battle zone color
        surface.fill((35, 30, 40), (0, 302, 360, 338))
        
        # HUD: Distance & HP
        self.draw_fighting_hud(surface)
        
        # Draw fighting area boundary
        pygame.draw.rect(surface, (60, 50, 70), (10, 310, 340, 240), 1, border_radius=8)
        
        # Render all active targets
        for target in self.rhythm_targets:
            if target["click_handled"]:
                continue
            tx, ty = target["pos"]
            r = int(target["radius"])
            draw_neon_glow_circle(surface, NEON_BLUE, (tx, ty), r, width=2, glow_factor=3)
            pygame.draw.circle(surface, WHITE, (tx, ty), 4)
            
            ring_r = int(r * target["ring_scale"])
            if ring_r > r:
                pygame.draw.circle(surface, NEON_YELLOW, (tx, ty), ring_r, 1)
                
            draw_text_with_shadow(surface, "◎ TOUCH!", get_font(8), GRAY, (tx, ty + r + 10))

    def draw_fighting_b_ui(self, surface):
        # 20년차 프로게이머 자문을 반영한 텐션 게이지 & 스위트 스팟 배틀 UI
        surface.fill((20, 25, 35), (0, 302, 360, 338))
        
        self.draw_fighting_hud(surface)
        
        pygame.draw.rect(surface, (50, 60, 70), (10, 310, 340, 240), 1, border_radius=8)
        
        # 1. State Status Indicator text
        status_text = "ADJUST TENSION!"
        status_color = WHITE
        if self.stun_timer > 0.0:
            status_text = "STUNNED! FAST REEL!"
            status_color = NEON_YELLOW
        elif self.snap_warning_timer > 0.0:
            status_text = "💥 LINE SNAPPING! RELEASE REEL! 💥"
            status_color = NEON_RED
        elif self.fish_event_type == "TUG":
            status_text = "⚠️ FISH TUG! RELEASE REEL! ⚠️"
            status_color = NEON_RED
        elif self.fish_event_type == "RUSH":
            status_text = "🌊 FISH CHARGING! REEL FAST! 🌊"
            status_color = NEON_BLUE
        elif self.tension >= 85.0:
            status_text = "DANGER! HIGH TENSION!"
            status_color = NEON_RED
        elif self.tension <= 10.0:
            status_text = "SLACK! TIGHTEN LINE!"
            status_color = NEON_BLUE
        elif 40.0 <= self.tension <= 70.0:
            status_text = "SWEET SPOT! REEL IN!"
            status_color = NEON_GREEN
            
        draw_text_with_shadow(surface, status_text, self.font_hud, status_color, (180, 395))
        
        # 2. Central REEL / STRIKE Button & Radial Tension Gauge
        # center = (180, 480), radius = 45
        # Calculate dynamic button shake/vibration for "쪼는 맛"
        btn_offset_x = 0
        btn_offset_y = 0
        if self.stun_timer <= 0.0:
            if self.fish_event_type == "TUG" or self.tension >= 80.0:
                shake_range = int(1 + (self.tension - 80.0) * 0.15) if self.tension >= 80.0 else 3
                btn_offset_x = random.randint(-shake_range, shake_range)
                btn_offset_y = random.randint(-shake_range, shake_range)
            elif self.fish_event_type == "RUSH" or self.tension <= 15.0:
                btn_offset_x = random.randint(-1, 1)
                btn_offset_y = random.randint(-1, 1)
                
        btn_center = (180 + btn_offset_x, 480 + btn_offset_y)
        btn_radius = 45
        
        # Determine current color based on tension
        curr_color = NEON_BLUE
        if self.tension > 70.0:
            curr_color = NEON_RED
        elif self.tension >= 40.0:
            curr_color = NEON_GREEN
            
        # 2-A. Radial Center Glow (중앙에서부터 차오르는 원)
        # 반지름을 최대 41로 제한하여 버튼 외각(45)을 침범하지 않게 함
        radial_r = int(41 * (self.tension / 100.0))
        if radial_r > 0:
            # Draw semi-transparent radial light filling from the center
            temp_glow = pygame.Surface((radial_r * 2, radial_r * 2), pygame.SRCALPHA)
            pygame.draw.circle(temp_glow, (*curr_color, 120), (radial_r, radial_r), radial_r)
            surface.blit(temp_glow, (btn_center[0] - radial_r, btn_center[1] - radial_r))
            
        # 2-B. Draw Central REEL / STRIKE Button
        if self.strike_ready:
            # Flash yellow neon for strike
            flash_intensity = (pygame.time.get_ticks() // 150) % 2
            btn_col = NEON_YELLOW if flash_intensity == 0 else NEON_ORANGE
            draw_neon_glow_circle(surface, btn_col, btn_center, btn_radius, width=0, glow_factor=3)
            draw_text_with_shadow(surface, "STRIKE!", self.font_large, BLACK, btn_center)
            
            # Particle emission for strike cue
            if random.random() < 0.2:
                self.particles.emit(btn_center[0], btn_center[1], (-40, 40), (-40, 40), [NEON_YELLOW, WHITE], (2, 4), (0.2, 0.4), 2)
        else:
            if self.is_reeling:
                # If high tension warning, flash reel button red/blue
                if self.tension >= 80.0:
                    flash_color = NEON_RED if (pygame.time.get_ticks() // 100) % 2 == 0 else (100, 20, 20)
                    pygame.draw.circle(surface, flash_color, btn_center, btn_radius)
                else:
                    pygame.draw.circle(surface, NEON_BLUE, btn_center, btn_radius)
                pygame.draw.circle(surface, WHITE, btn_center, btn_radius, 2)
                draw_text_with_shadow(surface, "REELING", self.font_large, WHITE, btn_center)
                
                # Reeling visual effects (rotating gear/line particles)
                if random.random() < 0.3:
                    self.particles.emit(btn_center[0] + random.randint(-20, 20), btn_center[1] + random.randint(-20, 20), (-10, 10), (-10, 10), [NEON_BLUE, WHITE], (1, 3), (0.1, 0.3), 1)
            else:
                # Idle button
                if self.tension >= 80.0:
                    flash_color = (130, 20, 20) if (pygame.time.get_ticks() // 100) % 2 == 0 else DARK_GRAY
                    pygame.draw.circle(surface, flash_color, btn_center, btn_radius)
                else:
                    pygame.draw.circle(surface, DARK_GRAY, btn_center, btn_radius)
                pygame.draw.circle(surface, GRAY, btn_center, btn_radius, 2)
                draw_text_with_shadow(surface, "REEL", self.font_large, WHITE, btn_center)
                
        # 2-C. Outer Radial Arc Tension Gauge (버튼 테두리 "안쪽" 밀착 원형 프로그레스바)
        # 반지름을 42.5로 주어 버튼(45) 밖으로 절대 나가지 않고 내부 경계를 따라 회전
        arc_rect = pygame.Rect(btn_center[0] - 42.5, btn_center[1] - 42.5, 85, 85)
        
        # Sweet Spot Outer Border Arc highlight (초록색 가이드 트랙)
        sw_start = -math.pi / 2.0 + 2.0 * math.pi * 0.40
        sw_end = -math.pi / 2.0 + 2.0 * math.pi * 0.70
        pygame.draw.arc(surface, NEON_GREEN, arc_rect, sw_start, sw_end, 2)
        
        # Current Tension Progress Arc (두께 3px)
        if self.tension > 0:
            arc_start = -math.pi / 2.0
            arc_end = -math.pi / 2.0 + 2.0 * math.pi * (self.tension / 100.0)
            if arc_start < arc_end:
                pygame.draw.arc(surface, curr_color, arc_rect, arc_start, arc_end, 3)
                
        # Sweet Spot needle markers
        marker_col = NEON_GREEN if 40.0 <= self.tension <= 70.0 else GRAY
        draw_text_with_shadow(surface, "SWEET SPOT", get_font(9, bold=True), marker_col, (btn_center[0], btn_center[1] + 70))
        
        # 3. Strike Gauge Bar (below button)
        # Position: x=60, y=538, w=240, h=6
        strike_bg = pygame.Rect(60, 538, 240, 6)
        draw_rounded_rect(surface, BLACK, strike_bg, 2)
        strike_w = int(240 * (self.strike_gauge / 100.0))
        if strike_w > 0:
            draw_rounded_rect(surface, NEON_YELLOW, pygame.Rect(60, 538, strike_w, 6), 2)
        pygame.draw.rect(surface, GRAY, strike_bg, 1, border_radius=2)
        draw_text_with_shadow(surface, f"STRIKE GAUGE: {int(self.strike_gauge)}%", get_font(10, bold=True), NEON_YELLOW, (180, 550))

    def draw_fighting_hud(self, surface):
        # 1. Tension bar (Left)
        tension_bar = pygame.Rect(18, 320, 16, 210)
        draw_rounded_rect(surface, BLACK, tension_bar, 4)
        
        ten_h = int(210 * (self.tension / 100.0))
        if ten_h > 0:
            # Alert color when high tension
            fill_col = NEON_GREEN if self.tension < 50 else NEON_ORANGE if self.tension < 80 else NEON_RED
            fill_rect = pygame.Rect(18, 320 + (210 - ten_h), 16, ten_h)
            draw_rounded_rect(surface, fill_col, fill_rect, 4)
            
        pygame.draw.rect(surface, WHITE, tension_bar, 1, border_radius=4)
        draw_text_with_shadow(surface, "텐", self.font_desc, WHITE, (26, 305))
        draw_text_with_shadow(surface, "션", self.font_desc, WHITE, (26, 540))

        # 2. HP Bar removed as per request (HP is internal size factor only)

        # 3. Distance Bar (Center top, shifted up to optimize space)
        dist_bar = pygame.Rect(60, 320, 280, 16)
        draw_rounded_rect(surface, BLACK, dist_bar, 4)
        
        # remaining distance fill
        dist_ratio = self.distance / self.max_distance
        dist_w = int(280 * (1.0 - dist_ratio))
        if dist_w > 0:
            draw_rounded_rect(surface, NEON_BLUE, pygame.Rect(60, 345, dist_w, 16), 4)
        pygame.draw.rect(surface, WHITE, dist_bar, 1, border_radius=4)
        
        draw_text_with_shadow(surface, f"물고기와의 거리: {self.distance:.1f} m", self.font_hud, WHITE, (200, 353))

        # 4. Time Limit
        time_color = NEON_YELLOW if self.time_limit > 15 else NEON_RED
        draw_text_with_shadow(surface, f"제한시간: {max(0.0, self.time_limit):.1f}초", self.font_hud, time_color, (200, 375))

    def draw_catch_popup(self, surface):
        # Draw regular game screen in background, then draw dim overlay
        overlay = pygame.Surface((360, 640), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        surface.blit(overlay, (0, 0))
        
        # Popup box
        popup_rect = pygame.Rect(30, 100, 300, 420)
        draw_rounded_rect(surface, (20, 20, 30), popup_rect, 12)
        
        # Glow border based on fish rarity
        rarity = self.active_fish["rarity"]
        border_col = RARITY_COLORS[rarity]
        pygame.draw.rect(surface, border_col, popup_rect, 3, border_radius=12)
        
        # Header
        rarity_str = "일반 물고기" if rarity == "common" else "희귀 물고기" if rarity == "rare" else "★ 전설의 물고기 ★"
        draw_text_with_shadow(surface, rarity_str, self.font_large, border_col, (180, 130))
        
        # Fish Name
        draw_text_with_shadow(surface, self.active_fish["name"], self.font_title, WHITE, (180, 175))
        
        # Simple fish graphic outline (retro vector fish)
        fish_center_y = 260
        fish_points = [
            (90, fish_center_y),
            (150, fish_center_y - 30),
            (210, fish_center_y - 20),
            (250, fish_center_y),
            (270, fish_center_y - 15),
            (270, fish_center_y + 15),
            (250, fish_center_y),
            (210, fish_center_y + 20),
            (150, fish_center_y + 30)
        ]
        pygame.draw.polygon(surface, border_col, fish_points, 2)
        pygame.draw.circle(surface, border_col, (120, fish_center_y - 5), 3) # Eye
        
        # Size stats
        last_fish = self.profile.fish_keep[-1] if self.profile.fish_keep else {"size": 0.0}
        size_val = last_fish["size"]
        draw_text_with_shadow(surface, f"길이: {size_val:.1f} cm", self.font_large, WHITE, (180, 335))
        
        # Check if record
        record_size = self.profile.encyclopedia.get(self.active_fish["id"], {}).get("max_size", 0.0)
        if abs(size_val - record_size) < 0.05:
            draw_text_with_shadow(surface, "NEW RECORD! 👑", self.font_hud, NEON_YELLOW, (180, 365))
            
        # Rarity score accuracy details
        max_possible_score = max(5, self.rhythm_targets_total * 5)
        score_pct = int(max(0.0, min(1.0, float(self.rhythm_score) / max_possible_score)) * 100)
        draw_text_with_shadow(surface, f"포획 정확도: {score_pct}%", self.font_desc, GRAY, (180, 390))
        
        # Gold Reward
        base_gold = self.active_fish["gold"]
        min_size = self.active_fish["min_size"]
        max_size = self.active_fish["max_size"]
        size_ratio = (size_val - min_size) / max(1, max_size - min_size)
        gold_mult = 1.0 + (size_ratio * 0.5)
        gold_earned = int(base_gold * gold_mult)
        
        draw_text_with_shadow(surface, f"예상 가치: +{gold_earned} G", self.font_large, NEON_YELLOW, (180, 420))
        draw_text_with_shadow(surface, "(마을 복귀 시 자동 판매 및 골드 합산)", self.font_desc, GRAY, (180, 445))
        
        # Instructions
        draw_text_with_shadow(surface, "- 아무 곳이나 눌러서 계속 -", self.font_hud, WHITE, (180, 490))

    def draw_map_select_popup(self, surface):
        # Dim background overlay
        overlay = pygame.Surface((360, 640), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        surface.blit(overlay, (0, 0))
        
        # Popup Box
        popup_rect = pygame.Rect(30, 100, 300, 390)
        draw_rounded_rect(surface, (20, 20, 30), popup_rect, 12)
        pygame.draw.rect(surface, NEON_BLUE, popup_rect, 2, border_radius=12)
        
        # Title
        draw_text_with_shadow(surface, "지역 이동", self.font_large, WHITE, (180, 130))
        
        # Draw buttons and unlock info
        for btn, map_data, unlocked in self.map_select_buttons:
            btn.draw(surface)
            
            # Display short rates info below each button
            rect = btn.rect
            desc_color = GRAY if not unlocked else NEON_GREEN
            rates = map_data["rates"]
            epic_prob = int(rates["epic"][0] * 100)
            rare_prob = int(rates["rare"][0] * 100)
            info_text = f"희귀 {rare_prob}% | 전설 {epic_prob}% - {map_data['visual_desc']}"
            
            draw_text_with_shadow(
                surface, info_text, get_font(10), desc_color,
                (rect.x + 8, rect.bottom + 3), align="left"
            )
            
        if self.map_select_back_btn:
            self.map_select_back_btn.draw(surface)
