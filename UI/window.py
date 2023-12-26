import pygame
from world_map import WorldMap


class Window:
    def __init__(self, world_map, fullscreen=False, padding=10):
        self.world_map = world_map
        self.fullscreen = fullscreen
        self.padding = padding
        pygame.init()

        if self.fullscreen:
            self.screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
        else:
            self.screen = pygame.display.set_mode(
                (world_map.grid_width + 2 * padding, world_map.grid_height + 2 * padding))

        pygame.display.set_caption("Nation Simulation")

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
        return True

    def display(self):
        self.screen.fill((255, 255, 255))
        x_0 = self.padding
        y_0 = self.padding
        self.world_map.display(self.screen, x_0, y_0)
        pygame.display.flip()

    def run(self):
        running = True
        while running:
            running = self.handle_events()
            self.display()
        pygame.quit()
