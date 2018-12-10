import pygame

white = (255, 255, 255)
gray = (129, 129, 129)
black = (0, 0, 0)


class Menu:
    def __init__(self, rect, buttons, image_path):
        self.image = pygame.image.load(image_path).convert_alpha()
        self.rect = self.image.get_rect()
        self.rect.topleft = rect.topleft

        self.buttons = buttons

    def update(self, dt):
        for button in self.buttons:
            button.update(dt)

    def get_surface(self):
        return_surface = pygame.Surface(self.rect.size).convert_alpha()
        return_surface.fill((0, 0, 0, 0))
        return_surface.blit(self.image, (0, 0))
        for button in self.buttons:
            surface, rect = button.get_surface()
            return_surface.blit(surface, rect)
        return return_surface, self.rect

    def click(self, pos):
        for button in self.buttons:
            if button.hover(pos):
                button.press()


class Button:
    def __init__(self, rect):
        self.rect = rect
        self.action = None
        self.active = False

    def update(self, dt):
        pass

    def get_surface(self):
        raise NotImplementedError("Button derivatives must implement a get_surface method.")

    def press(self):
        if self.active:
            self.action()

    def hover(self, pos):
        if self.rect.collidepoint(pos):
            return True
        return False

    def set_pos(self, pos):
        self.rect.topleft = pos


class ImageButton(Button):
    def __init__(self, image_path, inactive_image_path):
        self.image = pygame.image.load(image_path).convert_alpha()
        self.inactive_image = pygame.image.load(inactive_image_path).convert_alpha()
        assert self.image.get_size() == self.inactive_image.get_size(), "inactive and active image size is different."

        super(ImageButton, self).__init__(self.image.get_rect)

        self.surface = pygame.Surface((20, 20))

        self.active = False

    def get_surface(self):
        if self.active:
            self.surface.blit(self.image, self.rect)
        else:
            self.surface.blit(self.inactive_image, self.rect)
        return self.surface, self.rect


class TextButton(Button):
    def __init__(self, text, font, size=22, text_color=white, background_path=None, inactive_color=gray):
        self.font = pygame.font.Font(font, size)
        self.text = self.font.render(text, True, text_color)
        self.inactive_text = self.font.render(text, True, inactive_color)
        if background_path:
            self.background = pygame.image.load(background_path).convert_alpha()
            super(TextButton, self).__init__(self.background.get_rect())
        else:
            self.background = None
            super(TextButton, self).__init__(self.text.get_rect())

        self.text_rect = self.text.get_rect()
        self.text_rect.center = self.rect.center

        self.inactive_text_rect = self.inactive_text.get_rect()
        self.inactive_text_rect.center = self.rect.center

        self.surface = pygame.Surface((self.rect.w, self.rect.h)).convert_alpha()

        self.active = False

        self.name = ""

    def get_surface(self):
        self.surface.fill((0, 0, 0, 0))
        if self.background:
            self.surface.blit(self.background, (0, 0))

        if self.active:
            self.surface.blit(self.text, self.text_rect)
        else:
            self.surface.blit(self.inactive_text, self.inactive_text_rect)

        return self.surface, self.rect
