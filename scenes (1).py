import pygame
import json
import buttons
import inputbox
import main
from pygame.locals import *

white = (255, 255, 255)
blue = (0, 0, 255)
black = (0, 0, 0)


class TextBox:
    def __init__(self, pos, image_path, font_paths, text_rects, font_sizes=(18, 18), text_color=blue):
        self.image = pygame.image.load(image_path).convert_alpha()
        self.rect = self.image.get_rect()
        self.rect.topleft = pos

        self.text = ''
        self.text_scrolling = False

        self.text_font = pygame.font.Font(font_paths[0], font_sizes[0])
        self.character_name_font = pygame.font.Font(font_paths[1], font_sizes[1])

        self.text_color = text_color
        self.character_text_color = text_color

        self.text_surface = self.text_font.render("", True, self.text_color)
        self.character_name_surface = self.character_name_font.render("", True, self.character_text_color)

        self.text_space = text_rects[0]
        self.character_name_rect = text_rects[1]

        self.time_passed = 0
        self.text_index = 1

    def update(self, dt):
        if self.text_scrolling:
            self.time_passed += dt
            self.text_index = int(self.time_passed / 30)
            try:
                if self.text[self.text_index] == '\n':
                    self.text_index += 1
            except IndexError:
                self.text_scrolling = False
                self.text_index = len(self.text)
                self.time_passed = 0
            self.text_surface = self.text_font.render(self.text[:self.text_index], True, self.text_color)

    def get_surface(self):
        return_surface = self.image.copy()
        return_surface.blit(self.character_name_surface, self.character_name_rect)
        return_surface.blit(self.text_surface, self.text_space)
        return return_surface, self.rect

    def set_text(self, text):
        words = text.split()
        max_width = self.text_space.w
        rt_text = ''

        for word in words:
            test_add = rt_text + ' ' + word
            if self.text_font.size(test_add)[0] > max_width:
                rt_text = rt_text + '\n'
            else:
                rt_text = test_add

        self.text = rt_text[1:]
        self.text_surface = self.text_font.render(rt_text[0], True, self.text_color)
        self.text_scrolling = True

    def set_character(self, name, color):
        self.character_name_surface = self.character_name_font.render(name, True, color)

    def skip_scroll(self):
        self.text_scrolling = False
        self.time_passed = 0
        self.text_surface = self.text_font.render(self.text, True, self.text_color)


class Character:
    def __init__(self, name, sprite_path_dict, text_color):
        self.name = name

        self.sprites = {}
        for name, path in sprite_path_dict.items():
            self.sprites[name] = pygame.image.load(path).convert_alpha()

        self.sprite = pygame.Surface((0, 0))

        self.text_color = text_color

        self.rect = self.sprite.get_rect()
        self.rect.bottomleft = (1280, 720)
        self.x, self.y = self.rect.topleft

        self.target_rect = self.rect
        self.speed = 0

        self.exiting = False

    def get_surface(self):
        return self.sprite, self.rect

    def update(self, dt):
        if self.target_rect != self.rect:
            x_dist = abs(self.rect.x - self.target_rect.x) + 7
            y_dist = abs(self.rect.y - self.target_rect.y) + 7

            x_change = min((x_dist / 2.5) * (dt / 500) * self.speed, 200 * (dt / 1000) * self.speed)
            y_change = min((y_dist / 2.5) * (dt / 500) * self.speed, 200 * (dt / 1000) * self.speed)

            x, y = self.x, self.y
            target_x, target_y = self.target_rect.topleft
            if target_x - x < 0:
                x_change = -x_change
            if target_y - y < 0:
                y_change = -y_change

            if abs(target_x - x) < (x_change + 2):
                x = target_x
            else:
                x += x_change
            if abs(target_y - y) < (y_change + 2):
                y = target_y
            else:
                y += y_change
            self.x, self.y = x, y
        else:
            self.speed = 0
        self.rect.topleft = (self.x, self.y)

    def set_sprite(self, sprite_key):
        self.sprite = self.sprites[sprite_key]
        self.rect = self.sprites[sprite_key].get_rect()
        self.rect.topleft = (self.x, self.y)

    def exit(self):
        target = self.rect.copy()
        target.right = -100
        self.move(target)
        self.exiting = True

    def move(self, target, speed=5):
        self.target_rect = target
        self.speed = speed


class Scene:
    def __init__(self, source):
        self.res = (1280, 720)

        self.rect = pygame.Rect((0, 0), self.res)

        self.backgrounds = {}

        self.characters = {}
        self.on_screen_characters = []

        with open((source),"rb") as scene_file:
            scene = json.load(scene_file)
            self.prefix = scene["prefix"]

        with open(self.prefix + scene["characters"]) as character_file:
            characters = json.load(character_file)

        with open(self.prefix + scene["backgrounds"]) as background_file:
            backgrounds = json.load(background_file)

        with open(self.prefix + scene["soundtrack"]) as soundtrack_file:
            self.soundtrack = json.load(soundtrack_file)

        with open(self.prefix + scene["start"]) as start_script_file:
            self.script = json.load(start_script_file)

        for background, path in backgrounds.items():
            self.backgrounds[background] = pygame.image.load(path)

        self.background = self.backgrounds["Prologue"]

        for name, character in characters.items():
            self.characters[name] = Character(character[0], character[1], character[2])

        self.script_index = 0

        self.text_box = TextBox(
            (0, 650),
            "data/images/textbox.png",
            ("data/fonts/Amiko-Regular.ttf", "data/fonts/Amiko-Bold.ttf"),
            (pygame.Rect((2, 27), (1278, 198)), pygame.Rect((2, 2), (96, 21)))
        )

        self.choice_buttons = []
        self.choice_point = False
        self.affinity_points={}
        self.infamy_points=0
        self.money=0
        self.ability_points=0
        self.class_reputation=0
        self.kaiser_trust=0

    def update(self, dt):
        for character in self.on_screen_characters:
                character.update(dt)
                if character.exiting and not character.rect.colliderect(self.rect):
                    self.on_screen_characters.remove(character)
        self.text_box.update(dt)

    def get_surface(self):
        return_surface = pygame.Surface(self.res)

        return_surface.blit(self.background, (0, 0))

        for character in self.on_screen_characters:
                surface, rect = character.get_surface()
                return_surface.blit(surface, rect)

        textbox_surface, textbox_rect = self.text_box.get_surface()
        return_surface.blit(textbox_surface, textbox_rect)

        if self.choice_point:
            for button in self.choice_buttons:
                surface, rect = button.get_surface()
                return_surface.blit(surface, rect)

        return return_surface, self.rect

    def step(self):
        try:
            actions = self.script[self.script_index]
        except IndexError:
            print("Script ends without an ending action!")
            actions = []

        for action in actions:
            action_type = action[0]
            data = action[1]
            if action_type == "background":
                self.background = self.backgrounds[data]
            elif action_type == "music":
                pygame.mixer.music.load(self.soundtrack[data])
                pygame.mixer.music.play()
            elif action_type == "enter":
                self.characters[data[0]].set_sprite(data[1])
                self.on_screen_characters.append(self.characters[data[0]])
                align_characters(self.res, 800, 50, self.on_screen_characters)
            elif action_type == "exit":
                char_key = data
                self.characters[char_key].exit()
            elif action_type == "save":
                dict = {
                    "name": "Visual Novel",
                    "prefix": "data/01/",
                    "backgrounds": "backgrounds.json",
                    "characters": "characters.json",
                    "soundtrack": "soundtrack.json",
                    "start": data
                    }
                f = open("data/01/save.json","w")
                f.write(json.dumps(dict))
                f.close()
            elif action_type == "dialogue":
                self.text_box = TextBox(
                 (0, 650),
                 "data/images/textbox.png",
                 ("data/fonts/Amiko-Regular.ttf", "data/fonts/Amiko-Bold.ttf"),
                (pygame.Rect((2, 27), (1278, 198)), pygame.Rect((2, 2), (96, 21)))
                )
                character = data[0]
                dialogue = data[1]
                character = self.characters[character]
                self.text_box.set_character(character.name, character.text_color)
                self.text_box.set_text(dialogue)
            elif action_type == "thought":
                self.text_box = TextBox(
                (0, 650),
                "data/images/textbox.png",
                ("data/fonts/Arimo-Italic-Latin.ttf", "data/fonts/Amiko-Bold.ttf"),
                (pygame.Rect((2, 27), (1278, 198)), pygame.Rect((2, 2), (96, 21)))
                )
                character = data[0]
                thought = data[1]
                character = self.characters[character]
                self.text_box.set_character(character.name, character.text_color)
                self.text_box.set_text(thought)
            elif action_type == "action":
                self.text_box = TextBox(
                (0, 650),
                "data/images/textbox.png",
                ("data/fonts/Bam.TTF", "data/fonts/Amiko-Bold.ttf"),
                (pygame.Rect((2, 27), (1278, 198)), pygame.Rect((2, 2), (96, 21)))
                )
                character = data[0]
                action = data[1]
                character = self.characters[character]
                self.text_box.set_character(character.name, character.text_color)
                self.text_box.set_text(action)
            elif action_type == "look":
                character = data[0]
                new_sprite = data[1]
                self.characters[character].set_sprite(new_sprite)
            elif action_type == "affinity":
                self.text_box = TextBox(
                (0, 650),
                "data/images/textbox.png",
                ("data/fonts/Amiko-SemiBold.ttf", "data/fonts/Amiko-Bold.ttf"),
                (pygame.Rect((2, 27), (1278, 198)), pygame.Rect((2, 2), (96, 21))),(25, 25)
                )
                character="effect"
                char= data[0]
                points = data[1]
                ope=data[2]
                affinity= 'Affinity Points:'+ ope + points + "  "+char
                if char in self.affinity_points:
                    if ope == "+":
                        newpoint=int(self.affinity_points[char])+int(points)
                        self.affinity_points[char]=str(newpoint)
                    elif ope == "-":
                        newpoint=int(self.affinity_points[char])-int(points)
                        self.affinity_points[char]=str(newpoint)
                else:
                    if ope == "+":
                        self.affinity_points[char]=int(points)
                    elif ope == "-":
                        points=-int(points)
                        self.affinity_points[char]=points
                character = self.characters[character]
                self.text_box.set_character(character.name, character.text_color)
                self.text_box.set_text(affinity)
            elif action_type == "infamy":
                self.text_box = TextBox(
                (0, 650),
                "data/images/textbox.png",
                ("data/fonts/Amiko-SemiBold.ttf", "data/fonts/Amiko-Bold.ttf"),
                (pygame.Rect((2, 27), (1278, 198)), pygame.Rect((2, 2), (96, 21))), (25, 25)
                )
                character="effect"
                points =data[0]
                ope=data[1]
                infamy= 'Infamy Points:'+ ope + points
                if ope == "+":
                    self.infamy_points+=int(points)
                elif ope == "-":
                    self.infamy_points-=int(points)
                character = self.characters[character]
                self.text_box.set_character(character.name, character.text_color)
                self.text_box.set_text(infamy)
            elif action_type == "ability":
                self.text_box = TextBox(
                (0, 650),
                "data/images/textbox.png",
                ("data/fonts/Amiko-SemiBold.ttf", "data/fonts/Amiko-Bold.ttf"),
                (pygame.Rect((2, 27), (1278, 198)), pygame.Rect((2, 2), (96, 21))), (25, 25)
                )
                character="effect"
                points = data[0]
                ope=data[1]
                ability= 'Ability Points:'+ ope + points
                if ope == "+":
                    self.ability_points+=int(points)
                elif ope == "-":
                    self.ability_points-=int(points)
                character = self.characters[character]
                self.text_box.set_character(character.name, character.text_color)
                self.text_box.set_text(ability)
            elif action_type == "reputation":
                self.text_box = TextBox(
                (0, 650),
                "data/images/textbox.png",
                ("data/fonts/Amiko-SemiBold.ttf", "data/fonts/Amiko-Bold.ttf"),
                (pygame.Rect((2, 27), (1278, 198)), pygame.Rect((2, 2), (96, 21))), (25, 25)
                )
                character="effect"
                points = data[0]
                ope=data[1]
                reputation= 'Class Reputation:'+ ope + points
                if ope == "+":
                    self.class_reputation+=int(points)
                elif ope == "-":
                    self.class_reputation-=int(points)
                character = self.characters[character]
                self.text_box.set_character(character.name, character.text_color)
                self.text_box.set_text(reputation)
            elif action_type == "trust":
                self.text_box = TextBox(
                (0, 650),
                "data/images/textbox.png",
                ("data/fonts/Amiko-SemiBold.ttf", "data/fonts/Amiko-Bold.ttf"),
                (pygame.Rect((2, 27), (1278, 198)), pygame.Rect((2, 2), (96, 21))), (25, 25)
                )
                character="effect"
                points = data[0]
                ope=data[1]
                trust= "Kaiser's Trust:" + ope + points
                if ope == "+":
                    self.kaiser_trust+=int(points)
                elif ope == "-":
                    self.kaiser_trust-=int(points)
                character = self.characters[character]
                self.text_box.set_character(character.name, character.text_color)
                self.text_box.set_text(trust)
            elif action_type == "money":
                self.text_box = TextBox(
                (0, 650),
                "data/images/textbox.png",
                ("data/fonts/Amiko-SemiBold.ttf", "data/fonts/Amiko-Bold.ttf"),
                (pygame.Rect((2, 27), (1278, 198)), pygame.Rect((2, 2), (96, 21))), (25, 25)
                )
                character="effect"
                points = data
                self.money+=int(points)
                money= 'You earned '+ points + ' yen for finshing this scene' 
                character = self.characters[character]
                self.text_box.set_character(character.name, character.text_color)
                self.text_box.set_text(money)
            elif action_type == "update":
                self.text_box = TextBox(
                (0, 650),
                "data/images/textbox.png",
                ("data/fonts/Amiko-SemiBold.ttf", "data/fonts/Amiko-Bold.ttf"),
                (pygame.Rect((2, 27), (1278, 198)), pygame.Rect((2, 2), (96, 21))), (25, 25)
                )
                character="effect"
                if 'money' in data:
                    money = "Total Money:     " + str(self.money) + "  Yen"
                    character = self.characters[character]
                    self.text_box.set_character(character.name, character.text_color)
                    self.text_box.set_text(money)
                elif 'infamy' in data:
                    infamy = "Total Infamy:     " + str(self.infamy_points) 
                    character = self.characters[character]
                    self.text_box.set_character(character.name, character.text_color)
                    self.text_box.set_text(infamy)
                elif 'reputation' in data:
                    reputation = "Total Class Reputation:   " + str(self.class_reputation)
                    character = self.characters[character]
                    self.text_box.set_character(character.name, character.text_color)
                    self.text_box.set_text(reputation)
                elif 'ability' in data:
                    ability = "Total Ability Points:    " + str(self.ability_points)
                    character = self.characters[character]
                    self.text_box.set_character(character.name, character.text_color)
                    self.text_box.set_text(ability)
                elif 'trust'  in data:
                    trust = "Total Kaiser's Trust:   " + str(self.kaiser_trust)
                    character = self.characters[character]
                    self.text_box.set_character(character.name, character.text_color)
                    self.text_box.set_text(trust)
                elif 'affinity' in data:
                    y=data[1]
                    if y in self.affinity_points:
                        affinity = "Total Affinity for " + y + " is " + str(self.affinity_points[y])
                        self.text_box.set_text(affinity)
            elif action_type == "item":
                money=self.money
                items = data
                for item in items:
                    item_button = buttons.TextButton(
                        item[0],
                        "data/fonts/Amiko-Bold.ttf",
                        22,
                        white,
                        "data/images/bbutton.png"
                    )
                    if item[0] == "Exit Store" :
                        item_button.action = self.make_choice_action(item[2])
                        item_button.active = True
                        self.choice_buttons.append(item_button)               
                    if item[0] != "Exit Store":
                        if money>0:
                            item_button.action, money= self.make_purchase_action(item)
                            item_button.active = True
                            self.choice_buttons.append(item_button)
                        else:
                            item_button.active = False
                d=100
                for button in self.choice_buttons[::2]:
                    button.set_pos((100, d))
                    d+=100
                d=100
                for button in self.choice_buttons[1::2]:
                    button.set_pos((680, d))
                    d+=100
                self.choice_point = True
            elif action_type == "choice":
                choices = data
                for choice in choices:
                    print("Choice: {0}".format(choice[0]))
                    choice_button = buttons.TextButton(
                        choice[0],
                        "data/fonts/Amiko-Bold.ttf",
                        22,
                        white,
                        "data/images/button.png"
                    )
                    choice_button.action = self.make_choice_action(choice[1])
                    choice_button.active = True
                    self.choice_buttons.append(choice_button)
                align_buttons(self.res, 10, self.choice_buttons)
                self.choice_point = True
            elif action_type == "bchoice":
                choices = data
                for choice in choices:
                    print("Choice: {0}".format(choice[0]))
                    choice_button = buttons.TextButton(
                        choice[0],
                        "data/fonts/Amiko-Bold.ttf",
                        22,
                        white,
                        "data/images/bbutton.png"
                    )
                    choice_button.action = self.make_choice_action(choice[1])
                    choice_button.active = True
                    self.choice_buttons.append(choice_button)
                align_buttons(self.res, 10, self.choice_buttons)
                self.choice_point = True
            elif action_type == "end":
                next_scene = Scene(data) if data != "" else None
                return True, next_scene
        self.script_index += 1
        return False, None

    def click(self, pos):
        if self.choice_point:
            for button in self.choice_buttons:
                if button.hover(pos):
                    button.press()
            return False, None
        else:
            if self.text_box.text_scrolling:
                self.text_box.skip_scroll()
                return False, None
            else:
                return self.step()

    def make_choice_action(self, file):
        def choice_action():
            with open(self.prefix + file) as choice_script:
                self.choice_point = False
                self.script = json.load(choice_script)
                self.script_index = 0
                self.step()
            self.choice_buttons = []
        return choice_action

    def make_purchase_action(self, item=[]):
        character="effect"
        character = self.characters[character]
        self.text_box.set_character(character.name, character.text_color)
        price=int(item[1])
        effects= item[2]
        x=int(self.money)
        def choice_action():
            if x<0:
                self.text_box.set_text("You do not have enough money!")
            elif x >= 0:
                points=int(effects[1])
                z=str(points)
                if item[0]=="Bag of Books":
                    self.ability_points+=points
                    self.money-=price
                    self.text_box.set_text("You have earned " + z + " ability points")
                elif item[0]=="Bibimbap":
                    if effects[2] in self.affinity_points:
                        newpoint=int(self.affinity_points[effects[2] ])+int(points)
                        self.affinity_points[effects[2]]=str(newpoint)
                    else:
                        self.affinity_points[effects[2]]=int(points)
                    self.money-=price
                    self.text_box.set_text("You have earned " + z + effects[2] +" affinity points")
                elif item[0]=="Briefcase":
                    self.kaiser_trust+=points
                    self.money-=price
                    self.text_box.set_text("You have earned " + z + " Kaiser's trust")
                elif item[0]=="Chocolate Bar":
                    if effects[2] in self.affinity_points:
                        newpoint=int(self.affinity_points[effects[2] ])+int(points)
                        self.affinity_points[effects[2]]=str(newpoint)
                    else:
                        self.affinity_points[effects[2]]=int(points)
                    self.money-=price
                    self.text_box.set_text("You have earned " + z + effects[2] +" affinity points")
                elif item[0]=="Gelato":
                    if effects[2] in self.affinity_points:
                        newpoint=int(self.affinity_points[effects[2] ])+int(points)
                        self.affinity_points[effects[2]]=str(newpoint)
                    else:
                        self.affinity_points[effects[2]]=int(points)
                    self.money-=price
                    self.text_box.set_text("You have earned " + z + effects[2] +" affinity points")
                elif item[0]=="Surprise Gift":
                    self.class_reputation+=points
                    self.money-=price
                    self.text_box.set_text("You have earned " + z + " class reputation")
                elif item[0]=="Gingerbread Man":
                    if effects[2] in self.affinity_points:
                        newpoint=int(self.affinity_points[effects[2] ])+int(points)
                        self.affinity_points[effects[2]]=str(newpoint)
                    else:
                        self.affinity_points[effects[2]]=int(points)
                    self.money-=price
                    self.text_box.set_text("You have earned " + z + effects[2] +" affinity points")
                elif item[0]=="Ham":
                    if effects[2] in self.affinity_points:
                        newpoint=int(self.affinity_points[effects[2] ])+int(points)
                        self.affinity_points[effects[2]]=str(newpoint)
                    else:
                        self.affinity_points[effects[2]]=int(points)
                    self.money-=price
                    self.text_box.set_text("You have earned " + z + effects[2] +" affinity points")
                elif item[0]=="Shawarma":
                    if effects[2] in self.affinity_points:
                        newpoint=int(self.affinity_points[effects[2] ])+int(points)
                        self.affinity_points[effects[2]]=str(newpoint)
                    else:
                        self.affinity_points[effects[2]]=int(points)
                    self.money-=price
                    self.text_box.set_text("You have earned " + z + effects[2] +" affinity points")
                self.text_box.set_text("You have " + str(self.money) + " yen left")
        return choice_action, self.money

def align_characters(res, bottom, spacing, char_list):
    total_width = -spacing
    max_height = 0
    for character in char_list:
        rect = character.rect
        total_width += rect.w
        total_width += spacing
        max_height = max(max_height, rect.h)

    align_rect = pygame.Rect((0, 0), (total_width, max_height))
    align_rect.midbottom = ((res[0] / 2), bottom)

    offset = align_rect.left
    for character in char_list:
        rect = character.rect.copy()
        rect.bottomleft = (offset, bottom)
        offset = rect.right + spacing
        character.y = rect.y
        character.move(rect)


def align_buttons(res, spacing, button_list):
    max_width = 0
    total_height = -spacing
    for button in button_list:
        rect = button.rect
        total_height += rect.h + spacing
        max_width = max(max_width, rect.w)

    align_rect = pygame.Rect((0, 0), (max_width, total_height))
    align_rect.center = (res[0] / 2, res[1] / 2)

    offset = align_rect.top
    for button in button_list:
        button.set_pos((align_rect.x, offset))
        offset = button.rect.bottom + spacing