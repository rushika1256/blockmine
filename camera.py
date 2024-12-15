import pygame

class Camera:
    def __init__(self, width, height):
        """
        Initialize the camera.
        
        :param width: Width of the camera viewport (screen width).
        :param height: Height of the camera viewport (screen height).
        :param world_width: Total width of the game world.
        :param world_height: Total height of the game world.
        """
        self.width = width
        self.height = height
        self.offset = pygame.math.Vector2()

    def update(self, player):
        """
        Update the camera's position to follow the player.
        
        :param player: The player object.
        """
        self.offset.x = player.rect.centerx - self.width // 2
        self.offset.y = player.rect.centery - self.height // 2
