import pygame

colour1 = (255, 255, 255)
colour2 = (200, 200, 200)
colour3 = (180, 180, 180)
colour4 = (0, 0, 0)

pygame.init()


class Text:
    def __init__(self, x_pos, y_pos, text, colour=colour4, font="roboto", font_size=20, code=""):
        self.x = x_pos
        self.y = y_pos

        self.code = code
        self.text = text
        self.font = pygame.font.SysFont(font, font_size, True)
        self.colour = colour

    def draw(self, win):

        text = self.font.render(self.text, True, self.colour)

        win.blit(text, (self.x - text.get_width() / 2, self.y - text.get_height() / 2))


class Button:
    def __init__(self, x_pos, y_pos, width, height, code, start_colour=colour1,
                 hover_colour=colour2, select_colour=colour3, text_colour=colour4,
                 text="", font="roboto", font_size=20):
        self.x = x_pos
        self.y = y_pos
        self.w = width
        self.h = height

        self.code = code
        self.text = text
        self.font = pygame.font.SysFont(font, font_size, True)
        self.start_colour = start_colour
        self.hover_colour = hover_colour
        self.text_colour = text_colour
        self.select_colour = select_colour

    def draw(self, win, mouse_pos, is_clicking):

        draw_colour = self.start_colour
        if self.x < mouse_pos[0] < self.x + self.w:
            if self.y < mouse_pos[1] < self.y + self.h:
                draw_colour = self.hover_colour

                if is_clicking:
                    draw_colour = self.select_colour

        text = self.font.render(self.text, True, self.text_colour)

        pygame.draw.rect(win, draw_colour, (self.x, self.y, self.w, self.h))
        win.blit(text, ((self.x + self.w / 2) - text.get_width() / 2, (self.y + self.h / 2) - text.get_height() / 2))


class TextBox:

    def __init__(self, x_pos, y_pos, width, height, colour=colour1, text_colour=colour4,
                 font="roboto", font_size=60, code=""):
        self.x = x_pos
        self.y = y_pos
        self.w = width
        self.h = height

        self.code = code
        self.text = ""
        self.font = pygame.font.SysFont(font, font_size, True)
        self.colour = colour
        self.text_colour = text_colour

    def draw(self, win):
        pygame.draw.rect(win, self.colour, (self.x, self.y, self.w, self.h))

        text = self.font.render(self.text, True, self.text_colour)
        win.blit(text, (self.x + 5, (self.y + self.h / 2) - text.get_height() / 2))
