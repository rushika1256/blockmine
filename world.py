import pygame
import pygame.gfxdraw
import random
import time
import math

class World:
    def __init__(self):
        self.tile_size = 32  # Size of each tile in pixels
        self.tiles = pygame.sprite.Group()
        self.tile_map = {}
        self.world_width = 200
        self.world_height = 200
        self.render_distance = 25
        self.load_textures()
        self.clouds = self.generate_clouds()
        self.generate_world()

        # Day-Night Cycle
        self.start_time = time.time()  # Track the start time of the game
        self.day_night_duration = 60  

    def load_textures(self):
        self.textures = {
            'dirt': pygame.image.load('assets/blocks/dirt.png'),
            'grass': pygame.image.load('assets/blocks/grass.png'),
            'cobblestone': pygame.image.load('assets/blocks/cobblestone.png'),
            'wood': pygame.image.load('assets/blocks/wood.png'),
            'flower1': pygame.image.load('assets/blocks/flower1.png'),
            'flower2': pygame.image.load('assets/blocks/flower2.png'),
            'bomb': pygame.image.load('assets/blocks/shrooms.png'),
            'cloud': pygame.image.load('assets/gui/cloud2.png'),
            'gem': pygame.image.load('assets/blocks/diamond_ore.png'),
            'leaves': pygame.image.load('assets/blocks/leaves.png'),
            'granite': pygame.image.load('assets/blocks/granite.png'),
            'andesite': pygame.image.load('assets/blocks/andesite.png'),
        }

    def generate_world(self):
        """Generate a 2D world layout with cliffs and uneven terrain."""
        world_data = []
        cliff_height = self.world_height // 2  # Starting height for the grass layer

        # Initialize rows (vertical filling)
        for y in range(self.world_height):
            world_data.append([])

        # Generate terrain
        for x in range(0, self.world_width):  # Columns (horizontal terrain generation)
            # Adjust cliff height with some randomness
            if x > 0:  # Skip the first column to avoid index issues
                change = random.choice([-1, 0, 1])  # Step up, down, or stay flat
                cliff_height += change  # Limit height range
            for y in range(0, self.world_width):  # Rows (vertical filling)
                if y > 0 and world_data[y - 1][x] == 'wood' and y < cliff_height:
                    block = 'wood'
                elif y == cliff_height - 3:
                    block = 'wood' if random.random() < 0.15 else 'air'
                elif y < cliff_height:
                    block = 'air'
                elif y == cliff_height:
                    block = 'grass'
                    if world_data[y - 1][x] != 'wood':
                        if random.random() < 0.08:  # 8% chance for a flower
                            # if len(world_data) > y - 1 and len(world_data[y - 1]) > x:
                                world_data[y - 1][x] = 'flower1' if random.random() < 0.5 else 'flower2'
                        elif random.random() < 0.15:  # 15% chance for a bomb
                            # if len(world_data) > y - 1 and len(world_data[y - 1]) > x:
                                world_data[y - 1][x] = 'bomb'
                else:       # everything below grass
                    if y in [cliff_height + 1, cliff_height + 2, cliff_height + 3]:
                        block = 'dirt'
                    elif y > cliff_height + 3 and y < cliff_height + 8:
                        if random.random() < 0.8:
                            block = 'cobblestone'
                        else:
                            block = 'dirt'
                    else:
                        ran = random.random()
                        if ran <= 0.05:
                            block = 'gem'
                        elif ran > 0.05 and ran <= 0.4:
                            block = 'cobblestone'
                        elif ran > 0.4 and ran <= 0.7:
                            block = 'granite'
                        else:
                            block = 'andesite'
                # Append block to the correct row
                world_data[y].append(block)

        # Add leaves around the topmost wood block
        # Add leaves around the topmost wood block

        for x in range(self.world_width):  # Iterate over columns
            for y in range(self.world_height):  # Iterate over rows from top to bottom
                if world_data[y][x] == 'wood':  # Check if the block is wood
                    # Add leaves above the wood block
                    if y - 2 >= 0 and world_data[y - 2][x] == 'air':  # Check bounds and air block
                        world_data[y - 2][x] = 'leaves'

                    # Add surrounding leaves
                    for dx, dy in [(0, -1), (-1, -1), (1, -1), (-1, 0), (1, 0)]:
                        nx, ny = x + dx, y + dy
                        if 0 <= nx < self.world_width and 0 <= ny < self.world_height:  # Ensure within bounds
                            if world_data[ny][nx] == 'air':  # Only replace air blocks with leaves
                                world_data[ny][nx] = 'leaves'
                    break  # Stop after processing the first wood block in this column
        
        for y in range(0, self.world_height):
            for x in range(0, self.world_width):
                if world_data[y][x] != 'air':
                    tile = Tile(x - (self.world_width // 2), y - (self.world_height // 2), world_data[y][x], self.textures[world_data[y][x]], self.tile_size)
                    self.tiles.add(tile)
                    self.tile_map[(x - (self.world_width // 2), y - (self.world_height // 2))] = tile

    def generate_clouds(self):
        """Generate random cloud positions in the sky."""
        clouds = []
        for _ in range(5):  # Create 5 clouds (adjust as needed)
            x = random.randint(0, 800)  # Random x position within screen width
            y = random.randint(0, 100)  # Set cloud y position higher (closer to the top)
            cloud_width = random.randint(100, 200)  # Random cloud width
            cloud_height = random.randint(40, 70)  # Random cloud height
            clouds.append((x, y, cloud_width, cloud_height))
        return clouds

    def update_day_night_cycle(self):
        """Update the sky's color based on the time of day (1 minute loop from very light blue to dark blue)."""
        elapsed_time = time.time() - self.start_time  # Elapsed time since game start
        cycle_progress = (elapsed_time % self.day_night_duration) / self.day_night_duration  # Progress from 0 to 1

        # Use sine wave to smoothly transition between 0 and 1 over the course of 60 seconds
        transition_progress = (math.sin(2 * math.pi * cycle_progress - math.pi / 2) + 1) / 2

        # Define the RGB values for light blue and dark blue
        light_blue = (135, 206, 235)  # Very light blue (sky blue)
        dark_blue = (25, 25, 112)  # Very dark blue (midnight blue)

        # Interpolate between light blue and dark blue
        r = int(light_blue[0] * (1 - transition_progress) + dark_blue[0] * transition_progress)
        g = int(light_blue[1] * (1 - transition_progress) + dark_blue[1] * transition_progress)
        b = int(light_blue[2] * (1 - transition_progress) + dark_blue[2] * transition_progress)

        # Set the sky color based on the interpolation
        self.sky_color = (r, g, b)

    def render(self, screen, camera, player):
        """Render the world, including the background and tiles."""
        # Update the day-night cycle and get the sky color
        self.update_day_night_cycle()

        # Draw the sky background with fading effect
        pygame.draw.rect(screen, self.sky_color, (0, 0, 800, 600))  # Apply the interpolated sky color

        for cloud in self.clouds:
            screen.blit(self.textures['cloud'], (cloud[0], cloud[1]))

        # Get player's tile position
        player_tile_x, player_tile_y = player.get_pos()

        # Calculate the range of tiles to render
        start_x = player_tile_x - self.render_distance
        end_x = player_tile_x + self.render_distance
        start_y = player_tile_y - self.render_distance
        end_y = player_tile_y + self.render_distance

        # Render visible tiles
        for y in range(start_y, end_y + 1):
            for x in range(start_x, end_x + 1):
                if (x, y) in self.tile_map:
                    tile = self.tile_map[(x, y)]
                    screen_x = tile.rect.x - camera.offset.x
                    screen_y = tile.rect.y - camera.offset.y
                    screen.blit(tile.image, (screen_x, screen_y))
    #
    # def render_inventory(self, screen):
    #     inventory_bar_width = 300
    #     inventory_bar_height = 60
    #     slot_width = inventory_bar_width // (self.max_block_slots + len(self.inventory))  # Adjust for both tools and blocks
    #     screen_width, screen_height = screen.get_size()
    #
    #     # Position the inventory bar
    #     inventory_x = (screen_width - inventory_bar_width) // 2
    #     inventory_y = screen_height - inventory_bar_height - 20
    #
    #     # Draw semi-transparent background
    #     background_rect = pygame.Rect(inventory_x, inventory_y, inventory_bar_width, inventory_bar_height)
    #     pygame.gfxdraw.box(screen, background_rect, (0, 0, 0, 150))  # Black with transparency
    #
    #     # Render tools in the inventory
    #     for i, tool in enumerate(self.inventory):
    #         slot_x = inventory_x + i * slot_width
    #
    #         # Darken the box if the tool is equipped
    #         box_color = (200, 200, 200)  # Default white border
    #         if i == self.item_held:  # If this tool is the selected one
    #             box_color = (0, 0, 0)  # Darken the box color to indicate it's equipped
    #
    #         # Draw the border around the tool slot
    #         pygame.draw.rect(screen, box_color, (slot_x, inventory_y, slot_width, inventory_bar_height), 2)
    #
    #         # Render the tool image inside the slot
    #         tool_texture = self.textures.get(tool)
    #         if tool_texture:
    #             screen.blit(tool_texture, (slot_x + (slot_width - 20) // 2, inventory_y + (inventory_bar_height - 20) // 2))
    #
    #     # Render blocks in the inventory
    #     block_x = inventory_x + len(self.inventory) * slot_width
    #     for block_type, count in self.block_inventory.items():
    #         block_texture = self.textures.get(block_type)
    #         if block_texture:
    #             pygame.draw.rect(screen, (255, 255, 255), (block_x, inventory_y, slot_width, inventory_bar_height), 1)
    #             screen.blit(block_texture, (block_x + (slot_width - 20) // 2, inventory_y + (inventory_bar_height - 20) // 2))
    #             self.render_block_count(screen, block_x, inventory_y, count)
    #             block_x += slot_width

    # def render_block_count(self, screen, x, y, count):
    #     font = pygame.font.Font(None, 24)
    #     count_text = font.render(str(count), True, (255, 255, 255))
    #     screen.blit(count_text, (x + 2, y + 2))  # Slight offset for visibility

    def place_block(self, camera, player, x, y, block_type):
        """Place a block of the specified type at position (x, y) if the player has the block in their inventory."""
        block_x = x + camera.offset.x
        block_y = y + camera.offset.y
        tile_x = block_x // self.tile_size
        tile_y = block_y // self.tile_size
        tile_pos = (tile_x, tile_y)

        if abs(player.get_pos()[0] - tile_x) <= 2 and abs(player.get_pos()[1] - tile_y) <= 3:
            if tile_pos not in self.tile_map:
                if player.has_block_in_inventory(block_type):
                    # Remove the block from the player's inventory
                    player.remove_block_from_inventory(block_type)
                    tile = Tile(tile_x, tile_y, block_type, self.textures[block_type], self.tile_size)
                    self.tiles.add(tile)
                    self.tile_map[tile_pos] = tile

    def break_block(self, camera, player, x, y, tool):
        """Break a block at position (x, y) if the correct tool is used and add it to the player's inventory."""
        block_x = x + camera.offset.x
        block_y = y + camera.offset.y
        tile_x = block_x // self.tile_size
        tile_y = block_y // self.tile_size
        tile_pos = (tile_x, tile_y)

        block_broken = False
        if abs(player.get_pos()[0] - tile_x) <= 2 and abs(player.get_pos()[1] - tile_y) <= 3:
            # Check if the tile exists in self.tile_map
            if tile_pos in self.tile_map:
                tile_sprite = self.tile_map[tile_pos]
                block_type = tile_sprite.tile_type  # Access the block type

                # Check if the correct tool is used
                if (tool == 'pickaxe'):
                    if block_type in ['cobblestone', 'andesite', 'granite', 'gem', 'flower1', 'flower2'] and block_type != 'leaves':
                        block_broken = True
                elif (tool == 'axe'):
                    if block_type in ['wood', 'leaves', 'flower1', 'flower2'] and block_type != 'leaves':
                        block_broken = True
                elif (tool == 'shovel'):
                    if block_type in ['grass', 'dirt', 'flower1', 'flower2'] and block_type != 'leaves':
                        block_broken = True
                if block_broken:
                    player.add_block_to_inventory(block_type)
                    tile_sprite.kill()  # Remove sprite from rendering and groups
                    del self.tile_map[tile_pos]  # Remove tile from the dictionary
                elif block_type in ['leaves', 'bomb']:
                    tile_sprite.kill()  # Remove sprite from rendering and groups
                    del self.tile_map[tile_pos]  # Remove tile from the dictionary

    def handle_click(self, player, camera, pos, tool, button):
        """Handle player clicks, breaking blocks and placing blocks."""
        x, y = pos

        # Check if the player is breaking a block
        self.break_block(camera, player, x, y, tool)

        # Check if the player is placing a block (only for the right mouse button click)
        if button == 3:  # Right mouse button click
            block_type = player.get_selected_block()  # Assuming the player has a method to get the selected block type
            if block_type:
                self.place_block(camera, player, x, y, block_type)

class Tile(pygame.sprite.Sprite):
    def __init__(self, x, y, tile_type, texture, tile_size):
        super().__init__()
        self.image = texture
        self.rect = self.image.get_rect(topleft=(x * tile_size, y * tile_size))
        self.tile_type = tile_type