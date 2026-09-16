import pygame
import random
import math

pygame.font.init()

WIDTH, HEIGHT = 900, 680

# Colors
COLOR_BG        = (242, 247, 245)
COLOR_CARD      = (255, 255, 255)
COLOR_BEAM      = (74, 85, 104)
COLOR_BEAD_5    = (255, 107, 107)
COLOR_BEAD_1    = (78, 205, 196)
COLOR_GOLD      = (255, 230, 109)
COLOR_TEXT      = (45, 55, 72)
COLOR_PURPLE    = (157, 78, 221)

DISCO_COLORS = [
    (255, 107, 107), (78, 205, 196), (255, 230, 109), 
    (157, 78, 221),  (255, 159, 243), (84, 160, 255)
]

FONT_TITLE  = pygame.font.SysFont("monospace", 28, bold=True)
FONT_BODY   = pygame.font.SysFont("monospace", 18, bold=True)
FONT_HUGE   = pygame.font.SysFont("monospace", 42, bold=True)
FONT_IMPACT = pygame.font.SysFont("monospace", 36, bold=True)


class Juicer:
    """Handles screenshake and impact popups."""
    def __init__(self):
        self.shake_intensity = 0
        self.shake_decay = 0.85
        self.impact_texts = [] # [{text, x, y, size, alpha, color, timer}]

    def trigger_shake(self, intensity):
        self.shake_intensity = max(self.shake_intensity, intensity)

    def add_impact(self, text, x, y, is_big=False):
        color = COLOR_BEAD_5 if is_big else COLOR_BEAD_1
        self.impact_texts.append({
            'text': text,
            'x': x,
            'y': y,
            'scale': 1.8 if is_big else 1.2,
            'color': color,
            'timer': pygame.time.get_ticks()
        })

    def get_offset(self):
        if self.shake_intensity > 0.5:
            ox = random.uniform(-self.shake_intensity, self.shake_intensity)
            oy = random.uniform(-self.shake_intensity, self.shake_intensity)
            self.shake_intensity *= self.shake_decay
            return int(ox), int(oy)
        self.shake_intensity = 0
        return 0, 0


class DiscoParty:
    def __init__(self):
        self.active = False
        self.timer = 0
        self.particles = []

    def start(self):
        self.active = True
        self.timer = pygame.time.get_ticks()
        self.particles = []
        for _ in range(60):
            self.particles.append({
                'x': random.randint(50, WIDTH - 50),
                'y': random.randint(-100, 0),
                'color': random.choice(DISCO_COLORS),
                'speed': random.uniform(3, 7),
                'size': random.randint(6, 14),
                'angle': random.uniform(0, 360)
            })

    def update_and_draw(self, surface, offset=(0,0)):
        ox, oy = offset
        if not self.active:
            return
        
        now = pygame.time.get_ticks()
        if now - self.timer > 2200:
            self.active = False
            return

        for p in self.particles:
            p['y'] += p['speed']
            p['angle'] += 5
            rect = pygame.Rect(p['x'] + ox, p['y'] + oy, p['size'], p['size'])
            pygame.draw.rect(surface, p['color'], rect)


def render_menu(screen):
    screen.fill(COLOR_BG)
    card_rect = pygame.Rect(150, 100, 600, 480)
    pygame.draw.rect(screen, COLOR_CARD, card_rect, border_radius=20)
    pygame.draw.rect(screen, COLOR_BEAM, card_rect, width=4, border_radius=20)

    t_surf = FONT_TITLE.render("🪩 DISCO SOROBAN STUDIO 🪩", True, COLOR_PURPLE)
    s_surf = FONT_BODY.render("SELECT YOUR GAME MODE:", True, COLOR_TEXT)
    
    m1_surf = FONT_BODY.render("[ 1 ]  1-DIGIT ONLY (5 Numbers)", True, COLOR_BEAD_1)
    m2_surf = FONT_BODY.render("[ 2 ]  1-2 DIGITS   (5 Numbers)", True, COLOR_BEAD_5)
    m3_surf = FONT_BODY.render("[ 3 ]  NORMAL MODE  (Full Range)", True, COLOR_TEXT)
    
    hint_surf = FONT_BODY.render("PRESS 1, 2, OR 3 ON KEYBOARD TO PLAY", True, COLOR_BEAM)

    screen.blit(t_surf, (220, 150))
    screen.blit(s_surf, (280, 210))
    screen.blit(m1_surf, (230, 290))
    screen.blit(m2_surf, (230, 350))
    screen.blit(m3_surf, (230, 410))
    screen.blit(hint_surf, (200, 500))


def render_gameplay(screen, game_data, disco, juicer):
    now = pygame.time.get_ticks()
    ox, oy = juicer.get_offset()  # Camera Shake Offset

    bg_color = random.choice([(255, 240, 245), (240, 255, 250), (255, 255, 240)]) if disco.active else COLOR_BG
    screen.fill(bg_color)

    # Header Panel
    header_rect = pygame.Rect(40 + ox, 25 + oy, 820, 85)
    pygame.draw.rect(screen, COLOR_CARD, header_rect, border_radius=16)
    pygame.draw.rect(screen, COLOR_BEAM, header_rect, width=3, border_radius=16)

    mode_name = ["1-DIGIT", "1-2 DIGIT", "NORMAL"][game_data['mode'] - 1]
    title_surf = FONT_TITLE.render(f"🪩 MODE: {mode_name}", True, COLOR_PURPLE if disco.active else COLOR_TEXT)
    score_surf = FONT_BODY.render(f"SCORE: {game_data['score']} | COMBO: {game_data['combo']}x | STREAK: 🔥 {game_data['streak']}", True, COLOR_TEXT)
    screen.blit(title_surf, (60 + ox, 40 + oy))
    screen.blit(score_surf, (420 + ox, 52 + oy))

    # Target Sequence Panel
    seq_str = " ".join([f"+{n}" if n > 0 else str(n) for n in game_data['sequence']])
    seq_surf = FONT_BODY.render(f"PUZZLE SEQUENCE: {seq_str}", True, COLOR_TEXT)
    val_surf = FONT_HUGE.render(f"VALUE: {game_data['current_val']}", True, COLOR_TEXT)
    screen.blit(seq_surf, (60 + ox, 130 + oy))
    screen.blit(val_surf, (60 + ox, 165 + oy))

    # Abacus Board Frame
    board_rect = pygame.Rect(140 + ox, 230 + oy, 620, 340)
    pygame.draw.rect(screen, COLOR_CARD, board_rect, border_radius=20)
    pygame.draw.rect(screen, COLOR_BEAM, board_rect, width=4, border_radius=20)
    
    beam_rect = pygame.Rect(140 + ox, 320 + oy, 620, 14)
    pygame.draw.rect(screen, COLOR_BEAM, beam_rect)

    col_width = 620 // 5
    active_cx = 0
    for col in range(5):
        cx = 140 + ox + col * col_width + col_width // 2
        
        # Highlight Active Column
        if col == game_data['active_col']:
            active_cx = cx
            active_rect = pygame.Rect(140 + ox + col * col_width + 8, 240 + oy, col_width - 16, 320)
            pygame.draw.rect(screen, COLOR_GOLD, active_rect, border_radius=14)
            pulse_y = 220 + oy + math.sin(now * 0.01) * 4
            pygame.draw.circle(screen, COLOR_PURPLE, (cx, int(pulse_y)), 6)

        pygame.draw.line(screen, COLOR_BEAM, (cx, 240 + oy), (cx, 560 + oy), 4)

        val = game_data['beads'][col]
        has_five = val >= 5
        ones_count = val % 5

        # Upper 5-Bead
        b5_y = 290 if has_five else 250
        bead_5_rect = pygame.Rect(cx - 26, b5_y + oy, 52, 24)
        pygame.draw.rect(screen, COLOR_BEAD_5, bead_5_rect, border_radius=12)
        pygame.draw.rect(screen, COLOR_BEAM, bead_5_rect, width=2, border_radius=12)

        # Lower 1-Beads
        for i in range(4):
            b1_y = 350 + (i * 30) if i < ones_count else 410 + (i * 30)
            bead_1_rect = pygame.Rect(cx - 26, b1_y + oy, 52, 24)
            pygame.draw.rect(screen, COLOR_BEAD_1, bead_1_rect, border_radius=12)
            pygame.draw.rect(screen, COLOR_BEAM, bead_1_rect, width=2, border_radius=12)

    # Render Floating Impact Text Pops
    alive_impacts = []
    for imp in juicer.impact_texts:
        elapsed = now - imp['timer']
        if elapsed < 600:
            alive_impacts.append(imp)
            progress = elapsed / 600.0
            float_y = imp['y'] - (progress * 40) + oy
            surf = FONT_IMPACT.render(imp['text'], True, imp['color'])
            screen.blit(surf, (imp['x'] + ox - surf.get_width()//2, float_y))
    juicer.impact_texts = alive_impacts

    # Status & Footer Hints
    if game_data['status_msg'] and (now - game_data['status_timer'] < 2200):
        msg_color = COLOR_PURPLE if "FEVER" in game_data['status_msg'] else COLOR_BEAD_5
        msg_surf = FONT_BODY.render(game_data['status_msg'], True, msg_color)
        screen.blit(msg_surf, (280 + ox, 590 + oy))

    hint_surf = FONT_BODY.render(f"PREFIX: [+{game_data['prefix']}] | GESTURES: [nm]=+ [7u]=- | [ESC]=Menu", True, COLOR_BEAM)
    screen.blit(hint_surf, (80 + ox, 635 + oy))

    disco.update_and_draw(screen, offset=(ox, oy))

