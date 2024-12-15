import pygame
import pygame.gfxdraw

class Player:
    def __init__(self, x, y):
        # Block inventory: {'block_type': count}
        self.block_inventory = {}  # Stores block types and their counts
        self.max_block_slots = 7  # Maximum block types in the inventory
        self.load_textures()
        self.image = pygame.transform.scale(self.textures['player'], (32, 32))
        self.rect = self.image.get_rect(topleft=(x, y))

        # Movement attributes
        self.velocity = pygame.math.Vector2(0, 0)
        self.gravity = 0.5
        self.jump_strength = -10
        self.base_speed = 3
        self.sprint_speed = 10
        self.speed = self.base_speed

        # Stamina attributes
        self.max_stamina = 100
        self.stamina = self.max_stamina
        self.stamina_regeneration_rate = 0.5  # Stamina regenerates per frame
        self.stamina_consumption_rate = 1  # Stamina is consumed per frame while sprinting

        # Tools and inventory
        self.inventory = ['axe', 'pickaxe', 'shovel']
        self.item_held = 0  # Index of the currently held item
        self.is_tool_selected = True  # True if a tool is selected, False if a block is selected

        # Falling attributes
        self.is_falling = False  # Whether the player is currently falling
        self.fall_distance = 0  # Distance fallen before landing
        self.fall_damage_threshold = 7  # Falling more than 5 blocks causes damage
        self.lives = 5  # Starting lives

    def load_textures(self):
        self.textures = {
            'player': pygame.transform.scale(pygame.image.load('assets/player.png'), (33, 48)),
            'axe': pygame.image.load('assets/tools/axe.png'),
            'pickaxe': pygame.image.load('assets/tools/pickaxe.png'),
            'shovel': pygame.image.load('assets/tools/shovel.png'),
            'dirt': pygame.image.load('assets/blocks/dirt.png'),
            'stone': pygame.image.load('assets/blocks/stone.png'),
            'grass': pygame.image.load('assets/blocks/grass.png'),
            'wood': pygame.image.load('assets/blocks/wood.png'),
            'cobblestone': pygame.image.load('assets/blocks/cobblestone.png'),
            'bomb':pygame.image.load('assets/blocks/shrooms.png'),
            'flower1':pygame.image.load('assets/blocks/flower1.png'),
            'flower2':pygame.image.load('assets/blocks/flower2.png'),
            'gem':pygame.image.load('assets/blocks/diamond.png'),
            'granite': pygame.image.load('assets/blocks/granite.png'),
            'andesite': pygame.image.load('assets/blocks/andesite.png'),
        }

    def get_pos(self):
        return (self.rect.centerx // 32, self.rect.centery // 32)

    def update(self, camera, world):
        keys = pygame.key.get_pressed()

        # Handle horizontal movement
        if keys[pygame.K_a]:  # Move left
            self.velocity.x = -self.speed
        elif keys[pygame.K_d]:  # Move right
            self.velocity.x = self.speed
        else:
            self.velocity.x = 0

        # Handle sprinting with the SHIFT key
        if keys[pygame.K_LSHIFT] and (keys[pygame.K_a] or keys[pygame.K_d]):
            if self.stamina > self.max_stamina * 0.3:  # Sprinting only if stamina > 30%
                self.speed = self.sprint_speed
                self.stamina -= self.stamina_consumption_rate
        else:  # Not sprinting or stamina too low
            self.speed = self.base_speed
            if self.stamina < self.max_stamina:  # Regenerate stamina
                self.stamina += self.stamina_regeneration_rate

        # Make sure stamina doesn't exceed max or go below zero
        self.stamina = max(0, min(self.stamina, self.max_stamina))

        # Handle jumping
        if keys[pygame.K_SPACE] and self.is_on_ground(world):
            self.velocity.y = self.jump_strength

        # Apply gravity
        self.velocity.y = min(self.velocity.y + self.gravity, 10)  # Cap falling speed

        # Update player position

        self.rect.x += self.velocity.x
        self.handle_collisions(camera, world, axis='x')  # Handle horizontal collisions
        self.rect.y += self.velocity.y
        self.handle_collisions(camera, world, axis='y')  # Handle vertical collisions

        # Switch tools (1-9)
        combined_inventory = self.inventory + list(self.block_inventory.keys())  # Merge tools and blocks
        for i in range(0, 10):  # Keys 1–9
            if keys[getattr(pygame, f'K_{i}')] and i <= len(combined_inventory):
                self.switch_item(i, combined_inventory)

        # Track falling state
        if not self.is_on_ground(world):
            if not self.is_falling:
                self.is_falling = True
                self.fall_distance = 0  # Reset fall distance when starting to fall
            else:
                self.fall_distance += abs(self.velocity.y) / 32  # Accumulate fall distance
        else:
            self.is_falling = False
            self.fall_distance = 0  # Reset fall distance upon landing
        


    def is_on_ground(self, world):
        self.rect.y += 1  # Temporarily move down to check for ground
        on_ground = pygame.sprite.spritecollideany(self, world.tiles, collided=pygame.sprite.collide_rect)
        self.rect.y -= 1  # Reset the player's position
        return on_ground

    # Adjusting the fall damage logic to account for uneven terrain without altering most of the existing structure.
    # Updating the handle_collisions method to improve fall damage handling.

    def handle_collisions(self, camera, world, axis):
        collided_tiles = pygame.sprite.spritecollide(self, world.tiles, False, collided=pygame.sprite.collide_rect)
        # collided_blocks = [tile for tile in collided_tiles if tile.tile_type != 'flower1' and tile.tile_type != 'flower2' and tile.tile_type != 'bomb']

        for tile in collided_tiles:
            if tile.tile_type not in ['flower1', 'flower2', 'bomb']:
                # Ensure the player does not take fall damage when initially spawned (not falling from the initial spawn height)
                if self.rect.top == 0:  # Check if the player is at the starting position
                    self.is_falling = False  # Prevent fall damage trigger at initialization
                    self.fall_distance = 0
                    continue  # Skip this iteration if the player is just spawned

                # if tile not in {'air', 'flower', 'bomb'}:  # Process solid tiles
                if axis == 'x':  # Horizontal collision
                    if self.velocity.x > 0:  # Moving right
                        self.rect.right = tile.rect.left
                    elif self.velocity.x < 0:  # Moving left
                        self.rect.left = tile.rect.right
                    self.velocity.x = 0
                elif axis == 'y':  # Vertical collision
                    if self.velocity.y > 0:  # Falling
                        # Check if the player was falling
                        if self.is_falling:
                            # Calculate effective fall distance based on terrain height difference
                            terrain_height_diff = abs(self.rect.bottom - tile.rect.top)
                            effective_fall_distance = max(self.fall_distance, terrain_height_diff / 32)

                            if effective_fall_distance > self.fall_damage_threshold:
                                self.take_damage()

                            self.fall_distance = 0  # Reset fall distance after taking damage
                        self.rect.bottom = tile.rect.top
                        self.velocity.y = 0
                        self.is_falling = False  # Player has landed
                    elif self.velocity.y < 0:  # Jumping
                        self.rect.top = tile.rect.bottom
                        self.velocity.y = 0

            if tile.tile_type == 'bomb':  # Check if the player collided with a bomb tile
                self.take_damage()
                world.break_block(camera, self, tile.rect.centerx + 1, tile.rect.centery + 1, self.inventory[self.item_held])

    def render(self, screen, camera):
        # Render the player
        screen_x = self.rect.x - camera.offset.x
        screen_y = self.rect.y - camera.offset.y
        screen.blit(self.image, (screen_x, screen_y))

        # Render the stamina bar
        self.render_stamina(screen)

        self.render_health(screen)

        # Render the inventory bar
        self.render_inventory(screen)

        # Render the tool or block in the player's hand
        if self.is_tool_selected:
            current_tool = self.inventory[self.item_held]  # Tool is selected
            if current_tool:
                tool_offset_x = 8
                tool_offset_y = -12
                tool_x = screen_x + self.rect.width // 2 + tool_offset_x
                tool_y = screen_y + self.rect.height // 2 + tool_offset_y
                tool_image = pygame.transform.scale(self.textures[current_tool], (20, 20))
                screen.blit(tool_image, (tool_x, tool_y))
        else:
            try:
                current_block = list(self.block_inventory.keys())[self.item_held]  # Block is selected
                if current_block:
                    block_offset_x = 8  # Adjust this value for horizontal offset
                    block_offset_y = -15  # Adjust this value for vertical offset
                    block_x = screen_x + self.rect.width // 2 + block_offset_x
                    block_y = screen_y + self.rect.height // 2 + block_offset_y

                    block_image = pygame.transform.scale(self.textures[current_block], (23, 23))  # Adjust size as needed
                    screen.blit(block_image, (block_x, block_y))
            except:
                pass

    def render_stamina(self, screen):
        stamina_bar_width = 200
        stamina_bar_height = 10
        stamina_percentage = self.stamina / self.max_stamina
        current_stamina_bar_width = stamina_bar_width * stamina_percentage

        # Position of the stamina bar
        bar_x, bar_y = 10, 35

        # Draw the stamina bar background
        pygame.draw.rect(screen, (60, 60, 60), (bar_x, bar_y, stamina_bar_width, stamina_bar_height))
        # Draw the current stamina
        pygame.draw.rect(screen, (255, 255, 255), (bar_x, bar_y, current_stamina_bar_width, stamina_bar_height))
        # Draw the border
        pygame.draw.rect(screen, (0, 0, 0), (bar_x, bar_y, stamina_bar_width, stamina_bar_height), 2)


    def take_damage(self):
        """Handle player damage when falling."""
        
        # Check if the player still has lives
        self.lives -= 1
        if self.lives > 0:
            # Render the message "One Life Lost"
            font = pygame.font.Font("assets/gui/menu_font.ttf", 20)  # Bigger font size for emphasis
            text = font.render("One Life Lost", True, (255, 0, 0))  # Red color for the message
            screen = pygame.display.get_surface()  # Get the current screen surface
            
            # Positioning the message below the health, not using the health positions
            # Place the text a bit lower, below the health bar
            text_rect = text.get_rect(center=(400, 450))  # Position the message below the screen center

            # Add a subtle shadow effect for better visibilit
            shadow_offset = 3  # Slight offset for shadow
            shadow_text = font.render("One Life Lost", True, (0, 0, 0))  # Black shadow
            shadow_rect = shadow_text.get_rect(center=(400 + shadow_offset, 450 + shadow_offset))
            screen.blit(shadow_text, shadow_rect)  # Draw the shadow first
            
            # Draw the original text (on top of the shadow)
            screen.blit(text, text_rect)
            pygame.display.flip()  # Update the display

            # Wait for a brief moment before continuing
            pygame.time.wait(1000)  # Display the message for 1 second

    def render_health(self, screen):
        health_image = pygame.image.load('assets/lifeline.png')
        health_image = pygame.transform.scale(health_image, (15, 15))
        # health_rect=health_image.get_rect()
        health_x1, health_y1 = 75, 10

        # Render the lives remaining
        if self.lives > 0:
            for i in range(self.lives):
                screen.blit(health_image, (health_x1 - (i * 16), health_y1))

    def add_block_to_inventory(self, block_type, count=1):
        """Add blocks to inventory, create new type or increase count."""
        if block_type in self.block_inventory:
            self.block_inventory[block_type] += count
        elif len(self.block_inventory) < self.max_block_slots:
            self.block_inventory[block_type] = count

    def remove_block_from_inventory(self, block_type, count=1):
        """Remove blocks from inventory, decrease count or remove type if count is zero."""
        if block_type in self.block_inventory:
            if self.block_inventory[block_type] > count:
                self.block_inventory[block_type] -= count
            else:
                del self.block_inventory[block_type]
                if len(self.block_inventory) == 0:
                    self.item_held = 0
                    self.is_tool_selected = True
        else:
            print(f"No {block_type} found in inventory.")

    def render_inventory(self, screen):
        inventory_bar_width = 450
        inventory_bar_height = 60
        slot_width = inventory_bar_width // (self.max_block_slots + len(self.inventory))  # Adjust for both tools and blocks
        screen_width, screen_height = screen.get_size()

        # Position the inventory bar
        inventory_x = (screen_width - inventory_bar_width) // 2
        inventory_y = screen_height - inventory_bar_height - 20

        # Draw semi-transparent background
        background_rect = pygame.Rect(inventory_x, inventory_y, inventory_bar_width, inventory_bar_height)
        pygame.gfxdraw.box(screen, background_rect, (0, 0, 0, 150))  # Black with transparency

        combined_inventory = self.inventory + list(self.block_inventory.keys())  # Combine tools and blocks

        # Render each item (tools + blocks)
        for i, item in enumerate(combined_inventory):
            slot_x = inventory_x + i * slot_width

            # Highlight the box if the item is selected
            box_color = (0, 0, 0)  # Default border color
            if self.is_tool_selected and i < len(self.inventory) and i == self.item_held:  # Highlight selected tool
                box_color = (200, 200, 200)  # Dark border for selected tool
            elif not self.is_tool_selected and i >= len(self.inventory) and (i - len(self.inventory)) == self.item_held:
                # Highlight selected block
                box_color = (200, 200, 200)

            # Draw the border
            pygame.draw.rect(screen, box_color, (slot_x, inventory_y, slot_width, inventory_bar_height), 2)

            # Render the tool or block
            item_texture = self.textures.get(item)
            if item_texture:
                screen.blit(item_texture,
                            (slot_x + (slot_width - 20) // 2, inventory_y + (inventory_bar_height - 20) // 2))

            # If it's a block, show the count
            if item in self.block_inventory:
                self.render_block_count(screen, slot_x, inventory_y, self.block_inventory[item])

    def render_block_count(self, screen, x, y, count):
        font = pygame.font.Font(None, 24)
        count_text = font.render(str(count), True, (255, 255, 255))
        screen.blit(count_text, (x + 2, y + 2))  # Slight offset for visibility

    def switch_item(self, item_index, combined_inventory):
        """Switch the held item (tool or block) based on its position in the combined inventory."""
        # Adjust to 0-based index
        item_index -= 1

        if item_index < len(self.inventory):  # If the selected item is a tool
            self.item_held = item_index
            self.is_tool_selected = True
            print(f"Switched to tool: {self.inventory[self.item_held]}")
        else:  # If the selected item is a block
            block_index = item_index - len(self.inventory)
            if block_index < len(list(self.block_inventory.keys())):  # Check if the block index is within range
                self.item_held = block_index
                self.is_tool_selected = False
                selected_block = list(self.block_inventory.keys())[block_index]
                print(f"Switched to block: {selected_block}")
            else:  # If the inventory is empty, select the axe (first tool)
                self.item_held = 0
                self.is_tool_selected = True
                print("Inventory is empty. Switched to axe (first tool).")

    def get_selected_block(self):
        """Return the type of the selected block in hand."""
        if not self.is_tool_selected:  # If the selected item is a block
            selected_block_index = self.item_held
            block_types = list(self.block_inventory.keys())
            if selected_block_index < len(block_types):
                return block_types[selected_block_index]
        return None

    def has_block_in_inventory(self, block_type):
        """Check if a specific block type is in the inventory."""
        return block_type in self.block_inventory