import pygame
import random
from .hole import Hole

# Game Engine

DARK_BROWN = (60, 40, 20)
MOLE_BROWN = (140, 95, 55)
BLACK = (0, 0, 0)

class GameEngine:
    def __init__(self, width, height, rows=3, cols=3):
        self.width = width
        self.height = height

        self.holes = []
        spacing_x = width // (cols + 1)
        spacing_y = (height - 80) // (rows + 1)
        for r in range(rows):
            for c in range(cols):
                cx = spacing_x * (c + 1)
                cy = 80 + spacing_y * (r + 1)
                self.holes.append(Hole(cx, cy))

        self.spawn_chance = 0.02   # per-hole, per-frame chance to pop up
        self.mole_up_frames = 45   # how long a mole stays up if not whacked

        self.round_seconds = 30
        self.time_left_frames = self.round_seconds * 60

        self.score = 0
        self.misses = 0
        self.font = pygame.font.SysFont("Arial", 28)
        self.game_over = False
        self.exit_requested = False

    def handle_event(self, event):
        if self.game_over:
            if event.type == pygame.KEYDOWN:
                self.exit_requested = True
            return

        if event.type == pygame.MOUSEBUTTONDOWN:
            self._handle_click(event.pos)

    def _handle_click(self, pos):
        hit_something = False

        # NOTE: this loop does not stop after the first hole it finds
        # under the click - it checks every hole. Each hole's hit-box
        # (Hole.hit_size) is deliberately a bit larger than the
        # spacing between holes, so neighboring hit-boxes overlap
        # slightly near the grid lines. If two adjacent moles happen
        # to both be up and the player clicks in that overlap zone,
        # both holes register a hit from the same click, awarding two
        # points for a single whack. See Task 1 in the README.

        for hole in self.holes:
            if hole.rect().collidepoint(pos):
                if hole.whack():
                    self.score += 1
                    hit_something = True
                    break

        if not hit_something:
            self.misses += 1

    def handle_input(self):
        # Reserved for continuously-held-key input; this game is
        # entirely mouse-driven, so there's nothing to poll here.
        pass

    def update(self):
        if self.game_over:
            return

        self.time_left_frames -= 1
        if self.time_left_frames <= 0:
            self.game_over = True
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
        screen.blit(timer_text, (self.width - 140, 10))

        if self.game_over:
            overlay = pygame.Surface((self.width, self.height))
            overlay.set_alpha(220)
            overlay.fill((255, 255, 255))
            screen.blit(overlay, (0, 0))

            game_over_text = self.font.render(
                "GAME OVER",
                True,
                BLACK
            )
            game_over_rect = game_over_text.get_rect(
                center=(self.width // 2, self.height // 2 - 40)
            )
            screen.blit(game_over_text, game_over_rect)

            final_score_text = self.font.render(
                f"Final Score: {self.score}",
                True,
                BLACK
            )
            final_score_rect = final_score_text.get_rect(
                center=(self.width // 2, self.height // 2 + 10)
            )
            screen.blit(final_score_text, final_score_rect)

            instruction_text = self.font.render(
                "Press any key to exit",
                True,
                BLACK
            )
            instruction_rect = instruction_text.get_rect(
                center=(self.width // 2, self.height // 2 + 60)
            )
            screen.blit(instruction_text, instruction_rect)