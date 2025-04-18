import pygame
from menu import MainMenu
from game import Connect6

def main():
    pygame.init()
    screen = pygame.display.set_mode((800, 600))
    pygame.display.set_caption("Connect6")
    clock = pygame.time.Clock()

    menu = MainMenu()
    running = True

    while running:
        if menu.needs_redraw:
            menu.draw(screen)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            action = menu.handle_event(event, screen)
            if action == "play_ai":
                print(f"Starting AI game with sound_enabled={menu.sound_enabled}, music_busy={pygame.mixer.music.get_busy()}")
                game = Connect6(size=19, ai_enabled=True, sound_enabled=menu.sound_enabled)
                result = game.run()
                if result == "menu":
                    menu.needs_redraw = True
                    pygame.display.set_mode((800, 600))
                    if menu.sound_enabled:
                        try:
                            pygame.mixer.music.load("intro.mp3")
                            pygame.mixer.music.set_volume(0.5)
                            pygame.mixer.music.play(-1)
                            print("Music restarted in menu")
                        except Exception as e:
                            print(f"Error restarting music: {e}")
                elif result == "quit":
                    running = False
            elif action == "play_human":
                print(f"Starting Human game with sound_enabled={menu.sound_enabled}, music_busy={pygame.mixer.music.get_busy()}")
                game = Connect6(size=19, ai_enabled=False, sound_enabled=menu.sound_enabled)
                result = game.run()
                if result == "menu":
                    menu.needs_redraw = True
                    pygame.display.set_mode((800, 600))
                    if menu.sound_enabled:
                        try:
                            pygame.mixer.music.load("intro.mp3")
                            pygame.mixer.music.set_volume(0.5)
                            pygame.mixer.music.play(-1)
                            print("Music restarted in menu")
                        except Exception as e:
                            print(f"Error restarting music: {e}")
                elif result == "quit":
                    running = False
            elif action == "quit":
                running = False

        clock.tick(60)

    pygame.quit()

if __name__ == "__main__":
    main()