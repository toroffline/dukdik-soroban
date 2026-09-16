import os
import sys
import asyncio
import pygame

# Suppress warnings & setup Pygame display
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "hide"

from engine import SorobanEngine, generate_valid_sequence
import ui

async def main():
    pygame.init()
    pygame.display.init()

    screen = pygame.display.set_mode((ui.WIDTH, ui.HEIGHT))
    pygame.display.set_caption("🪩 WIGGLE SLASH: REAL SOROBAN 🪩")
    clock = pygame.time.Clock()

    engine = SorobanEngine()
    disco = ui.DiscoParty()
    juicer = ui.Juicer()

    state = "MENU"
    mode = 1
    score = 0
    combo = 1
    streak = 0

    sequence, target = [], 0
    buffer_key = None
    buffer_time = 0

    status_msg = ""
    status_timer = 0

    def get_col_x(col_idx):
        col_width = 620 // 5
        return 140 + col_idx * col_width + col_width // 2

    def start_game(selected_mode):
        nonlocal mode, state, score, combo, streak, sequence, target
        mode = selected_mode
        state = "PLAYING"
        score = 0
        combo = 1
        streak = 0
        sequence, target = generate_valid_sequence(mode=mode, length=5)
        engine.reset_beads()

    running = True
    # --- WEB-READY ASYNC GAME LOOP ---
    while running:
        now = pygame.time.get_ticks()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            elif event.type == pygame.KEYDOWN:
                key_name = pygame.key.name(event.key).lower()

                if state == "MENU":
                    if key_name in ['1', '2', '3']:
                        start_game(int(key_name))

                elif state == "PLAYING":
                    if event.key == pygame.K_ESCAPE:
                        state = "MENU"
                        buffer_key = None
                        continue

                    prefix_map = {'q': 1, 'w': 2, 'e': 3, 'r': 4, 't': 5}
                    if key_name in prefix_map:
                        engine.prefix = prefix_map[key_name]
                        continue

                    pos_map = {'1': 4, '2': 3, '3': 2, '4': 1, '5': 0}
                    if key_name in pos_map:
                        engine.active_col = pos_map[key_name]
                        continue

                    if event.key == pygame.K_BACKSPACE:
                        engine.reset_beads()
                        buffer_key = None
                        continue

                    if event.key == pygame.K_SPACE:
                        if engine.get_current_value() == target:
                            streak += 1
                            score += 100 * combo
                            combo += 1
                            status_msg = f"🪩 DISCO FEVER! +{100 * (combo-1)} PTS 🪩"
                            disco.start()
                            juicer.trigger_shake(12)
                            sequence, target = generate_valid_sequence(mode=mode, length=5)
                            engine.reset_beads()
                        else:
                            streak = 0
                            combo = 1
                            status_msg = f"❌ OOPS! Target was {target}"
                        status_timer = now
                        buffer_key = None
                        continue

                    # --- SLIDING GESTURES ---
                    if buffer_key and (now - buffer_time < 500):
                        gesture = buffer_key + key_name
                        cx = get_col_x(engine.active_col)

                        if gesture == 'nm':
                            val = engine.prefix
                            engine.apply_smart_delta(+val)
                            if val >= 5:
                                juicer.trigger_shake(10)
                                juicer.add_impact(f"+{val} BOOM!", cx, 300, is_big=True)
                            else:
                                juicer.trigger_shake(3)
                                juicer.add_impact(f"+{val}", cx, 380, is_big=False)
                            engine.prefix = 1

                        elif gesture == '7u':
                            val = engine.prefix
                            engine.apply_smart_delta(-val)
                            if val >= 5:
                                juicer.trigger_shake(10)
                                juicer.add_impact(f"-{val} CRASH!", cx, 300, is_big=True)
                            else:
                                juicer.trigger_shake(3)
                                juicer.add_impact(f"-{val}", cx, 380, is_big=False)
                            engine.prefix = 1

                        elif gesture == '78':
                            engine.apply_smart_delta(+5)
                            juicer.trigger_shake(14)
                            juicer.add_impact("💥 +5 FLIP!", cx, 270, is_big=True)

                        elif gesture == '87':
                            engine.apply_smart_delta(-5)
                            juicer.trigger_shake(14)
                            juicer.add_impact("💥 -5 FLIP!", cx, 270, is_big=True)

                        buffer_key = None
                    else:
                        buffer_key = key_name
                        buffer_time = now

        # Render Frame
        if state == "MENU":
            ui.render_menu(screen)
        else:
            game_data = {
                'mode': mode,
                'score': score,
                'combo': combo,
                'streak': streak,
                'sequence': sequence,
                'current_val': engine.get_current_value(),
                'beads': engine.beads,
                'active_col': engine.active_col,
                'prefix': engine.prefix,
                'status_msg': status_msg,
                'status_timer': status_timer
            }
            ui.render_gameplay(screen, game_data, disco, juicer)

        pygame.display.flip()
        clock.tick(60)

        # CRITICAL FOR BROWSER / PYGBAG: Yield execution back to WebAssembly
        await asyncio.sleep(0)

    pygame.quit()
    sys.exit()

# Web entry point execution
if __name__ == "__main__":
    asyncio.run(main())

