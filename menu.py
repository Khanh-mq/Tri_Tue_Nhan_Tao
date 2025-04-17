import pygame
import numpy as np
import sys

# Constants
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FONT_SIZE = 36
TITLE_FONT_SIZE = 72
BUTTON_WIDTH = 200
BUTTON_HEIGHT = 40
BUTTON_SPACING = 20

# Colors
COLOR_TEXT = (33, 33, 33)
COLOR_BUTTON_NORMAL = (76, 175, 80)
COLOR_BUTTON_HOVER = (56, 142, 60)
COLOR_BUTTON_PRESSED = (27, 94, 32)
COLOR_POPUP = (255, 255, 255)
TITLE_COLOR = (25, 118, 210)

class MainMenu:
    def __init__(self):
        pygame.init()
        self.background = pygame.image.load("image.jpg")
        self.background = pygame.transform.scale(self.background, (SCREEN_WIDTH, SCREEN_HEIGHT))

        self.font = pygame.font.SysFont("Segoe UI", FONT_SIZE, bold=True)
        self.title_font = pygame.font.SysFont("Segoe UI", TITLE_FONT_SIZE, bold=True)
        self.instruction_font = pygame.font.SysFont("Segoe UI", 20)
        self.buttons = []
        self.sound_enabled = True
        self.setup_menu()
        self.needs_redraw = True
        self.click_sound = self.create_click_sound()
        self.load_background_music()

    def load_background_music(self):
        """Load and play background music if sound is enabled"""
        try:
            pygame.mixer.music.load("intro.mp3")  # Thay bằng đường dẫn thực tế
            pygame.mixer.music.set_volume(0.5)
            if self.sound_enabled:
                pygame.mixer.music.play(-1)
        except Exception as e:
            print(f"Error loading music: {e}")

    def stop_background_music(self):
        """Stop background music"""
        if pygame.mixer.music.get_busy():
            pygame.mixer.music.stop()

    def toggle_sound(self):
        """Toggle sound state and update music"""
        self.sound_enabled = not self.sound_enabled
        self.needs_redraw = True
        if self.sound_enabled:
            try:
                pygame.mixer.music.play(-1)  # Phát lại nhạc ngay lập tức
            except Exception as e:
                print(f"Error playing music: {e}")
        else:
            self.stop_background_music()

    def setup_menu(self):
        button_texts = [
            "AI",
            "Human",
            "Instructions",
            "Sound",
            "Quit"
        ]
        center_x = SCREEN_WIDTH // 2 - BUTTON_WIDTH // 2
        start_y = 250

        self.buttons.clear()
        for i, text in enumerate(button_texts):
            rect = pygame.Rect(center_x, start_y + i * (BUTTON_HEIGHT + BUTTON_SPACING), BUTTON_WIDTH, BUTTON_HEIGHT)
            self.buttons.append({"text": text, "rect": rect})

    def create_click_sound(self):
        try:
            freq = 440
            duration = 0.1
            sample_rate = 44100
            t = np.linspace(0, duration, int(sample_rate * duration), endpoint=False)
            wave = (np.sin(2 * np.pi * freq * t) * 32767).astype(np.int16)
            stereo_wave = np.column_stack((wave, wave)).flatten().tobytes()
            return pygame.mixer.Sound(buffer=stereo_wave)
        except:
            return None

    def play_click_sound(self):
        if self.sound_enabled and self.click_sound:
            self.click_sound.play()

    def show_instructions(self, screen):
        instructions = [
            "Instructions:",
            "- Game có kích thước 19*19.",
            "- Người chơi chọn các điểm trên bàn cờ.",
            "- Lần đi đầu tiên chỉ được 1 quân với quân đen",
            " các lần đi tiếp theo được đi 2 quân",
            "- người chơi đánh được 6 quân trước sẽ win",
            "",
            "Click anywhere to return to the menu."
        ]
        self.stop_background_music()
        screen.fill(COLOR_POPUP)
        y = 50
        for line in instructions:
            text_surface = self.font.render(line, True, COLOR_TEXT)
            text_rect = text_surface.get_rect(center=(SCREEN_WIDTH // 2, y))
            screen.blit(text_surface, text_rect)
            y += 50
        pygame.display.flip()

        waiting = True
        while waiting:
            for event in pygame.event.get():
                if event.type in [pygame.QUIT, pygame.MOUSEBUTTONDOWN, pygame.KEYDOWN]:
                    waiting = False

        self.needs_redraw = True
        if self.sound_enabled:
            try:
                pygame.mixer.music.play(-1)
            except Exception as e:
                print(f"Error playing music: {e}")

    def draw(self, screen):
        if not self.needs_redraw:
            return

        screen.blit(self.background, (0, 0))

        # Title
        title_surface = self.title_font.render("CONNECT6", True, TITLE_COLOR)
        title_rect = title_surface.get_rect(center=(SCREEN_WIDTH // 2, 150))
        screen.blit(title_surface, title_rect)

        mouse_pos = pygame.mouse.get_pos()
        for button in self.buttons:
            rect = button["rect"]
            text = button["text"]
            if text == "Sound":
                text = f"Sound: {'On' if self.sound_enabled else 'Off'}"
            text_surface = self.font.render(text, True, (255, 255, 255))
            text_rect = text_surface.get_rect(center=rect.center)

            is_hovered = rect.collidepoint(mouse_pos)
            if is_hovered:
                if pygame.mouse.get_pressed()[0]:
                    color = COLOR_BUTTON_PRESSED
                else:
                    color = COLOR_BUTTON_HOVER
            else:
                color = COLOR_BUTTON_NORMAL

            # Shadow
            shadow_rect = rect.copy()
            shadow_rect.move_ip(4, 4)
            pygame.draw.rect(screen, (0, 0, 0, 50), shadow_rect, border_radius=12)

            # Button
            pygame.draw.rect(screen, color, rect, border_radius=12)
            screen.blit(text_surface, text_rect)

        pygame.display.flip()
        self.needs_redraw = False

    def handle_event(self, event, screen):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            for button in self.buttons:
                if button["rect"].collidepoint(event.pos):
                    self.play_click_sound()
                    text = button["text"]
                    if text == "AI":
                        self.stop_background_music()
                        return "play_ai"
                    elif text == "Human":
                        self.stop_background_music()
                        return "play_human"
                    elif text == "Instructions":
                        self.show_instructions(screen)
                    elif text == "Sound":
                        self.toggle_sound()
                    elif text == "Quit":
                        pygame.quit()
                        sys.exit()
        return None