import pygame
import random
import math
from array import array
from .hole import Hole

# Game Engine

DARK_BROWN = (60, 40, 20)
MOLE_BROWN = (140, 95, 55)
BLACK = (0, 0, 0)


class GameEngine:
    def __init__(self, width, height, rows=3, cols=3):
        self.width = width
        self.height = height

        self.rows = rows
        self.cols = cols

        self.holes = []
        spacing_x = width // (cols + 1)
        spacing_y = (height - 80) // (rows + 1)
        for r in range(rows):
            for c in range(cols):
                cx = spacing_x * (c + 1)
                cy = 80 + spacing_y * (r + 1)
                self.holes.append(Hole(cx, cy))

        self.spawn_chance = 0.02
        self.mole_up_frames = 45

        self.round_seconds = 30
        self.time_left_frames = self.round_seconds * 60

        self.score = 0
        self.misses = 0
        self.font = pygame.font.SysFont("Arial", 28)
        self.game_over = False
        self.exit_requested = False

        self._setup_sounds()

    def _setup_sounds(self):
        self.hit_sound = None
        self.miss_sound = None
        self.game_over_sound = None

        try:
            if not pygame.mixer.get_init():
                pygame.mixer.init()

            self.hit_sound = self._create_sound(800, 0.10)
            self.miss_sound = self._create_sound(250, 0.12)
            self.game_over_sound = self._create_sound(120, 0.30)

        except pygame.error:
            self.hit_sound = None
            self.miss_sound = None
            self.game_over_sound = None

    def _create_sound(self, frequency, duration):
        sample_rate = 44100
        samples = int(sample_rate * duration)

        buffer = array("h")

        for i in range(samples):
            value = int(
                12000
                * math.sin(
                    2 * math.pi * frequency * i / sample_rate
                )
            )
            buffer.append(value)

        return pygame.mixer.Sound(buffer=buffer.tobytes())

    def handle_event(self, event):
        if self.game_over:
            if event.type == pygame.KEYDOWN:

                if event.key == pygame.K_1:
                    self._start_new_round("Easy")

                elif event.key == pygame.K_2:
                    self._start_new_round("Medium")

                elif event.key == pygame.K_3:
                    self._start_new_round("Hard")

                elif event.key == pygame.K_4:
                    self.exit_requested = True

            return

        if event.type == pygame.MOUSEBUTTONDOWN:
            self._handle_click(event.pos)

    def _handle_click(self, pos):
        hit_something = False

        # Task 1: stop after the first successful hit
        # so one click cannot score multiple points.

        for hole in self.holes:
            if hole.rect().collidepoint(pos):
                if hole.whack():
                    self.score += 1
                    hit_something = True

                    if self.hit_sound:
                        self.hit_sound.play()

                    break

        if not hit_something:
            self.misses += 1

            if self.miss_sound:
                self.miss_sound.play()

    def _start_new_round(self, difficulty):
        if difficulty == "Easy":
            self.spawn_chance = 0.015
            self.mole_up_frames = 60

        elif difficulty == "Medium":
            self.spawn_chance = 0.02
            self.mole_up_frames = 45

        elif difficulty == "Hard":
            self.spawn_chance = 0.035
            self.mole_up_frames = 30

        self.score = 0
        self.misses = 0
        self.time_left_frames = self.round_seconds * 60
        self.game_over = False
        self.exit_requested = False

        self.holes = []
        spacing_x = self.width // (self.cols + 1)
        spacing_y = (self.height - 80) // (self.rows + 1)

        for r in range(self.rows):
            for c in range(self.cols):
                cx = spacing_x * (c + 1)
                cy = 80 + spacing_y * (r + 1)
                self.holes.append(Hole(cx, cy))

    def handle_input(self):
        # Reserved for continuously-held-key input.
        pass

    def update(self):
        if self.game_over:
            return

        self.time_left_frames -= 1

        if self.time_left_frames <= 0:
            self.time_left_frames = 0
            self.game_over = True

            if self.game_over_sound:
                self.game_over_sound.play()

            return

        for hole in self.holes:
            hole.update()

            if not hole.active and random.random() < self.spawn_chance:
                hole.pop_up(self.mole_up_frames)

    def render(self, screen):
        for hole in self.holes:
            pygame.draw.circle(
                screen,
                DARK_BROWN,
                (hole.center_x, hole.center_y),
                40
            )

            if hole.active:
                pygame.draw.circle(
                    screen,
                    MOLE_BROWN,
                    (hole.center_x, hole.center_y),
                    32
                )

        score_text = self.font.render(
            f"Score: {self.score}",
            True,
            BLACK
        )
        screen.blit(score_text, (10, 10))

        seconds_left = max(0, self.time_left_frames // 60)

        timer_text = self.font.render(
            f"Time: {seconds_left}s",
            True,
            BLACK
        )
        screen.blit(
            timer_text,
            (self.width - 140, 10)
        )

        if self.game_over:
            overlay = pygame.Surface(
                (self.width, self.height)
            )
            overlay.set_alpha(220)
            overlay.fill((255, 255, 255))
            screen.blit(overlay, (0, 0))

            game_over_text = self.font.render(
                "GAME OVER",
                True,
                BLACK
            )
            game_over_rect = game_over_text.get_rect(
                center=(
                    self.width // 2,
                    self.height // 2 - 100
                )
            )
            screen.blit(
                game_over_text,
                game_over_rect
            )

            final_score_text = self.font.render(
                f"Final Score: {self.score}",
                True,
                BLACK
            )
            final_score_rect = final_score_text.get_rect(
                center=(
                    self.width // 2,
                    self.height // 2 - 55
                )
            )
            screen.blit(
                final_score_text,
                final_score_rect
            )

            instruction_text = self.font.render(
                "Choose Difficulty",
                True,
                BLACK
            )
            instruction_rect = instruction_text.get_rect(
                center=(
                    self.width // 2,
                    self.height // 2 - 10
                )
            )
            screen.blit(
                instruction_text,
                instruction_rect
            )

            easy_text = self.font.render(
                "1 - Easy",
                True,
                BLACK
            )
            easy_rect = easy_text.get_rect(
                center=(
                    self.width // 2,
                    self.height // 2 + 35
                )
            )
            screen.blit(easy_text, easy_rect)

            medium_text = self.font.render(
                "2 - Medium",
                True,
                BLACK
            )
            medium_rect = medium_text.get_rect(
                center=(
                    self.width // 2,
                    self.height // 2 + 75
                )
            )
            screen.blit(medium_text, medium_rect)

            hard_text = self.font.render(
                "3 - Hard",
                True,
                BLACK
            )
            hard_rect = hard_text.get_rect(
                center=(
                    self.width // 2,
                    self.height // 2 + 115
                )
            )
            screen.blit(hard_text, hard_rect)

            exit_text = self.font.render(
                "4 - Exit",
                True,
                BLACK
            )
            exit_rect = exit_text.get_rect(
                center=(
                    self.width // 2,
                    self.height // 2 + 155
                )
            )
            screen.blit(exit_text, exit_rect)