import pygame
from menu import MainMenu
from game import Connect6

def main():
    pygame.init()
    screen = pygame.display.set_mode((800, 600))
    pygame.display.set_caption("Connect6")
    clock = pygame.time.Clock()  # Điều khiển tốc độ khung hình

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
                game = Connect6(size=19, ai_enabled=True)
                result = game.run()  # Nhận trạng thái từ game.run()
                if result == "menu":
                    menu.needs_redraw = True  # Vẽ lại menu
                    pygame.display.set_mode((800, 600))  # Khôi phục kích thước cửa sổ
                elif result == "quit":
                    running = False
            elif action == "play_human":
                game = Connect6(size=19, ai_enabled=False)
                result = game.run()
                if result == "menu":
                    menu.needs_redraw = True
                    pygame.display.set_mode((800, 600))
                elif result == "quit":
                    running = False
            elif action == "quit":
                running = False

        clock.tick(60)  # Giới hạn 60 FPS

    pygame.quit()

if __name__ == "__main__":
    main()