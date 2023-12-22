from random import randint

import pygame as pg


# game classes
class Bird(pg.sprite.Sprite):
    def __init__(self):
        super().__init__()
        image_1 = pg.image.load("assets/bird1.png").convert_alpha()
        image_2 = pg.image.load("assets/bird2.png").convert_alpha()
        image_3 = pg.image.load("assets/bird3.png").convert_alpha()

        self.images = [image_1, image_2, image_3]
        self.current_image = 0

        self.image = self.images[self.current_image]
        self.rect = self.image.get_rect(center=(100, (screen_height / 2) - 20))

        self.score = 0
        self.gravity = 0
        self.pass_pipe = False

    def bird_animation(self):
        """
        the overall flipping wings animation of the bird
        """
        self.current_image += 0.5
        if self.current_image >= int(len(self.images)):
            self.current_image = 0
        self.image = self.images[int(self.current_image)]

    def contain_bird_on_screen(self):
        """
        prevents the bird from flying above the screen
        and falling below the screen
        """
        global game_active
        if self.rect.top <= 0:
            self.rect.top = 0
            game_active = False
        if self.rect.bottom >= screen_height - 110:
            self.rect.bottom = screen_height - 110
            game_active = False

    def gravity_exertion(self):
        """
        the exertion of gravity on the bird
        :return:
        """
        # exerting gravity on the bird
        self.gravity += 0.5
        self.rect.bottom += self.gravity

    def flight(self):
        # bird flight
        self.gravity = -7

    def pipe_collision(self):
        """
        collision with pipe
        """
        global game_active, start_game
        if pg.sprite.spritecollide(self, pipe_group, False):
            game_active = False
            # start_game = False

    def show_score(self):
        """
        showing player score
        """
        font = pg.font.SysFont("Arial", 50)
        font_text = font.render(str(self.score), True, "white")
        font_text_rect = font_text.get_rect(center=(screen_width // 2, 50))
        screen.blit(font_text, font_text_rect)

    def increase_score(self):
        """
        increasing the score when the bird passes
         through the middle of the pipes
        """
        if len(pipe_group) > 0:
            if (
                    self.rect.left > pipe_group.sprites()[0].rect.left
                    and self.rect.right < pipe_group.sprites()[0].rect.right
                    and not self.pass_pipe
            ):
                self.pass_pipe = True
            # if bird has passed a pipe
            if self.pass_pipe:
                if self.rect.left > pipe_group.sprites()[0].rect.right:
                    self.score += 1
                    self.pass_pipe = False

    def update(self):
        """
        updates the bird object in every game loop
        """
        self.show_score()
        if start_game:
            self.gravity_exertion()
            self.contain_bird_on_screen()
            self.increase_score()
        if game_active:
            self.pipe_collision()
            self.bird_animation()
            self.image = pg.transform.rotate(self.images[int(self.current_image)], self.gravity * -2)
        else:
            self.image = pg.transform.rotate(self.images[int(self.current_image)], -90)


class Pipe(pg.sprite.Sprite):
    def __init__(self, x_pos: int, y_pos: int, pipe_type: str):
        super().__init__()
        self.image = pg.image.load("assets/pipe.png").convert_alpha()
        self.pipe_gap = 150

        if pipe_type == "top":
            self.image = pg.transform.flip(self.image, False, True)
            self.rect = self.image.get_rect(bottomleft=(x_pos, y_pos - self.pipe_gap // 2))
        else:
            self.rect = self.image.get_rect(topleft=(x_pos, y_pos - self.pipe_gap // 2))

    def pipe_movement(self):
        """
        moving the pipe across the screen
        """
        if game_active and start_game:
            movement_speed = 6
            self.rect.left -= movement_speed

    def pipe_deletion(self):
        if self.rect.left <= -80:
            self.kill()

    def update(self):
        """
        updating the mechanics of the pipe
        """
        self.pipe_movement()
        self.pipe_deletion()


class Button:
    def __init__(self):
        self.image = pg.image.load("assets/restart.png").convert_alpha()
        self.rect = self.image.get_rect(center=(screen_width // 2, screen_height / 2))

    def draw_button(self):
        if not game_active:
            screen.blit(self.image, self.rect)


def draw_background():
    """
    showing the background of the game
    """
    bg = pg.image.load("assets/bg.png")
    screen.blit(bg, (0, -160))


def scroll_ground():
    """
    making the ground scroll
    :return: the current scroll of the ground
    """
    global ground_scroll
    scroll_speed = 4
    if game_active:
        ground_scroll -= scroll_speed

    if abs(ground_scroll) > 35:
        ground_scroll = 0
    return ground_scroll


def restart_game():
    """
    restarts the entire game
    """
    pipe_group.empty()
    bird.gravity = 0
    bird.rect.left = 100
    bird.rect.y = (screen_height / 2) - 20
    bird.score = 0


# game set up
pg.init()
screen_width = 864
screen_height = 600
screen = pg.display.set_mode((screen_width, screen_height))
pg.display.set_caption("Flappy Bird")
fps = pg.time.Clock()
ground_scroll = 0

# game modes
run = True
start_game = False
game_active = True

# ground
ground = pg.image.load("assets/ground.png")

# spite groups
bird_group = pg.sprite.GroupSingle()
pipe_group = pg.sprite.Group()

bird = Bird()
bird_group.add(bird)

# restart button
restart_button = Button()

# timer for pipe appearance
pipe_timer = pg.USEREVENT + 1
pg.time.set_timer(pipe_timer, 1800)

while run:
    for event in pg.event.get():
        if event.type == pg.QUIT:
            run = False

        if event.type == pg.KEYDOWN and event.key == pg.K_SPACE:
            if not start_game:
                start_game = True
            if start_game and game_active:
                bird.flight()

            if not game_active:
                game_active = True
                start_game = False
                restart_game()

        if event.type == pipe_timer:
            pipe_height = randint(-100, 100)
            top_pipe = Pipe(screen_width, screen_height // 2 + pipe_height, "top")
            bottom_pipe = Pipe(screen_width, screen_height - (screen_height - 250) // 2 + pipe_height, "bottom")
            # adding pipes to group
            pipe_group.add(top_pipe)
            pipe_group.add(bottom_pipe)

    # drawing game background and ground
    draw_background()

    # drawing pipes
    pipe_group.draw(screen)
    pipe_group.update()

    # drawing the bird
    bird_group.draw(screen)
    # updating the bird object
    bird_group.update()

    # showing ground
    screen.blit(ground, (ground_scroll, screen_height - 110))
    if start_game:
        ground_scroll = scroll_ground()

    restart_button.draw_button()

    pg.display.update()
    fps.tick(60)
