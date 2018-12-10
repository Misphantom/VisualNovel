#Cayas, Regina Maysa
#2018-02153

#Heeler, Esel Nanci
#2018-04217

import pygame
import buttons
import scenes

pygame.init()

GAME_MAINMENU = 0
GAME_RUNNING = 1
GAME_PAUSED = 2

black = (0, 0, 0)
blue = (0, 0, 255)
white = (255, 255, 255)


class GameObject:
    def __init__(self, width, height, caption):
        self.display_width = width
        self.display_height = height
        self.display = pygame.display.set_mode((self.display_width, self.display_height))
        pygame.display.set_caption(caption)

        pygame.mixer.music.set_volume(0.25)

        self.clock = pygame.time.Clock()

        self.state = ""

        self.scene = None

        self.button_list = []
        self.menu = None

    @staticmethod
    def exit():
        pygame.quit()
        quit()

    def main_menu(self, dt):
        """function for the main menu interface"""
        mouse_pos = pygame.mouse.get_pos()
        for event in pygame.event.get():  # Iterate over the list of events since the last loop.
            if event.type == pygame.QUIT:
                self.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:  # Watch for mouse button presses for button logic.
                if event.button == 1:  # Left click
                    for button in self.button_list:
                        if button.hover(mouse_pos):  # Test the mouse position on each button.
                            button.press()

        self.display.fill(blue)
        menuimage = pygame.image.load("data/images/backgrounds/bnhalogo.png").convert()
        self.display.blit(menuimage,(0, 0))
        for button in self.button_list:
            surface, rect = button.get_surface()
            game.display.blit(surface, rect)
        pygame.display.update()

    def game_update(self, dt):
        """key/click based interface to proceed form events"""
        mouse_pos = pygame.mouse.get_pos()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.game_pause()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    end, new_scene = self.scene.click(mouse_pos)
                    if end:
                        try:
                            self.scene = new_scene
                            self.scene.step()
                        except AttributeError:
                            self.game_mainmenu()
                            return

        self.scene.update(dt)

        self.display.fill((50, 50, 50))

        scene_surface, scene_rect = self.scene.get_surface()
        self.display.blit(scene_surface, scene_rect)

        pygame.display.update()

    def pause_menu(self, dt):
        mouse_pos = pygame.mouse.get_pos()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.set_state(GAME_RUNNING)
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    menu_rel_pos = []
                    for coords in zip(mouse_pos, self.menu.rect.topleft):
                        menu_rel_pos.append(coords[0] - coords[1])
                    self.menu.click(menu_rel_pos)

        self.menu.update(dt)

        menu_surface, menu_rect = self.menu.get_surface()
        self.display.blit(menu_surface, menu_rect)

        pygame.display.update()

    def set_state(self, state):
        self.state = state

    def loop(self):
        """Keeps the game running"""
        while True:
            dt = self.clock.tick()
            if self.state == GAME_MAINMENU:
                self.main_menu(dt)
            if self.state == GAME_RUNNING:
                self.game_update(dt)
                pygame.mixer.music.stop()
            if self.state == GAME_PAUSED:
                self.pause_menu(dt)

    def game_start(self,x):
        self.button_list = []
        self.menu = None
        self.scene = scenes.Scene(x)
        self.set_state(GAME_RUNNING)

    def game_pause(self):
        menu_rect = pygame.Rect((0, 50), (300, 600))
        menu_rect.centerx = game.display.get_rect().centerx
        self.menu = buttons.Menu(menu_rect, generate_menu_buttons("pause"), "data/images/pause_menu.png")
        self.menu.rect.center = self.display.get_rect().center
        self.set_state(GAME_PAUSED)

    def game_mainmenu(self):
        self.scene = None
        self.button_list = generate_menu_buttons("main")
        self.set_state(GAME_MAINMENU)


def generate_menu_buttons(menu):  # Returns a list of buttons for the menu "key" provided.
    """The main menu interface"""
    button_list = []
    if menu == "main":

        def start_action():
            """to start"""
            game.game_start("data/01/scene.json")
            game.scene.step()
        start_button = buttons.TextButton("Start Game", "data/fonts/Amiko-Bold.ttf")
        start_button.set_pos((200, 600))
        start_button.action = start_action
        start_button.active = True
        button_list.append(start_button)

        def load_action():
            """to load from a saved file"""
            game.game_start("data/01/save.json")
            game.scene.step()
        load_button = buttons.TextButton("Load Game", "data/fonts/Amiko-Bold.ttf")
        load_button.set_pos((550, 600))
        load_button.action = load_action
        load_button.active = True
        button_list.append(load_button)


        def exit_action():
            """terminate and exit"""
            game.exit()
        exit_button = buttons.TextButton("Exit Game", "data/fonts/Amiko-Bold.ttf")
        exit_button.set_pos((980, 600))
        exit_button.action = exit_action
        exit_button.active = True
        button_list.append(exit_button)

    elif menu == "pause":

        def continue_action():
            game.set_state(GAME_RUNNING)
        continue_button = buttons.TextButton("Continue", "data/fonts/Amiko-Bold.ttf", 22, white)
        continue_button.set_pos((10, 50))
        continue_button.action = continue_action
        continue_button.active = True
        button_list.append(continue_button)

        def main_menu_action():
            game.game_mainmenu()
        main_menu_button = buttons.TextButton("Main Menu", "data/fonts/Amiko-Bold.ttf", 22, white)
        main_menu_button.set_pos((10, 100))
        main_menu_button.action = main_menu_action
        main_menu_button.active = True
        button_list.append(main_menu_button)

        def exit_action():
            game.exit()
        exit_button = buttons.TextButton("Exit Game", "data/fonts/Amiko-Bold.ttf", 22, white)
        exit_button.set_pos((10, 150))
        exit_button.action = exit_action
        exit_button.active = True
        button_list.append(exit_button)

    return button_list


def main():
    global game
    game = GameObject(1280, 720, "Visual Novel")
    game.game_mainmenu()
    
    game.loop()


if __name__ == "__main__":
    main()
