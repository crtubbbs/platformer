import arcade
from arcade.tilemap import load_tilemap

# Constants
SCREEN_WIDTH = 1000
SCREEN_HEIGHT = 650
SCREEN_TITLE = "Platformer"

# Constants used to scale our sprites from their original size
CHARACTER_SCALING = 0.5
TILE_SCALING = 1.5
COIN_SCALING = 1
SPRITE_PIXEL_SIZE = 128
GRID_PIXEL_SIZE = SPRITE_PIXEL_SIZE * TILE_SCALING

# Movement speed of player, in pixels per frame
PLAYER_MOVEMENT_SPEED = 8
GRAVITY = 1
PLAYER_JUMP_SPEED = 15

# Player starting position
PLAYER_START_X = 10
PLAYER_START_Y = 225

# Layer Names from our TileMap
LAYER_NAME_PLATFORMS = "Platforms"
LAYER_NAME_COINS = "Coins"
LAYER_NAME_FOREGROUND = "Foreground"
LAYER_NAME_BACKGROUND = "Background"
LAYER_NAME_DONT_TOUCH = "Don't Touch"
LAYER_NAME_END = "End"

# List of map files
MAP_LIST = ["actual.json","parkour.json","realuppies.json"]

class MyGame(arcade.Window):
    """
    Main application class.
    """

    def __init__(self):
        super().__init__(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)
        self.tile_map = None
        self.scene = None
        self.player_sprite = None
        self.physics_engine = None
        self.camera = None
        self.gui_camera = None
        self.score = 0
        # self.end_of_map = 0
        self.level = 0  # Start at the first level
        self.collect_coin_sound = arcade.load_sound(":resources:sounds/coin1.wav")
        self.jump_sound = arcade.load_sound(":resources:sounds/jump1.wav")
        self.game_over = arcade.load_sound(":resources:sounds/gameover1.wav")

    def setup(self):
        # Setup the Cameras
        self.camera = arcade.Camera(self.width, self.height)
        self.gui_camera = arcade.Camera(self.width, self.height)

        # Map name
        map_name = MAP_LIST[self.level]

        # Load in TileMap
        self.tile_map = load_tilemap(map_name, TILE_SCALING)

        # Initiate New Scene with our TileMap, this will automatically add all layers
        # from the map as SpriteLists in the scene in the proper order.
        self.scene = arcade.Scene.from_tilemap(self.tile_map)

        # Keep track of the score
        self.score = 0

        # Add Player Spritelist before "Foreground" layer. This will make the foreground
        # be drawn after the player, making it appear to be in front of the Player.
        self.scene.add_sprite_list_after("Player", LAYER_NAME_FOREGROUND)

        # Set up the player, specifically placing it at these coordinates.
        image_source = ":resources:images/animated_characters/male_person/malePerson_idle.png"
        self.player_sprite = arcade.Sprite(image_source, CHARACTER_SCALING)
        self.player_sprite.center_x = PLAYER_START_X
        self.player_sprite.center_y = PLAYER_START_Y
        self.scene.add_sprite("Player", self.player_sprite)

        # Calculate the right edge of the map in pixels
        # self.end_of_map = self.tile_map.width * GRID_PIXEL_SIZE

        # Set the background color if specified in the JSON map
        if self.tile_map.background_color:
            arcade.set_background_color(self.tile_map.background_color)

        # Create the 'physics engine'
        self.physics_engine = arcade.PhysicsEnginePlatformer(
            self.player_sprite,
            gravity_constant=GRAVITY,
            walls=self.scene[LAYER_NAME_PLATFORMS],
        )

    def on_draw(self):
        """Render the screen."""
        arcade.start_render()
        self.camera.use()
        self.scene.draw()
        self.gui_camera.use()
        score_text = f"Score: {self.score}"
        arcade.draw_text(
            score_text,
            10,
            10,
            arcade.csscolor.BLACK,
            18,
        )

    def on_key_press(self, key, modifiers):
        """Called whenever a key is pressed."""
        if key == arcade.key.UP or key == arcade.key.W:
            if self.physics_engine.can_jump():
                self.player_sprite.change_y = PLAYER_JUMP_SPEED
                arcade.play_sound(self.jump_sound)
        elif key == arcade.key.LEFT or key == arcade.key.A:
            self.player_sprite.change_x = -PLAYER_MOVEMENT_SPEED
        elif key == arcade.key.RIGHT or key == arcade.key.D:
            self.player_sprite.change_x = PLAYER_MOVEMENT_SPEED

    def on_key_release(self, key, modifiers):
        """Called when the user releases a key."""
        if key == arcade.key.LEFT or key == arcade.key.A:
            self.player_sprite.change_x = 0
        elif key == arcade.key.RIGHT or key == arcade.key.D:
            self.player_sprite.change_x = 0

    def center_camera_to_player(self):
        screen_center_x = self.player_sprite.center_x - (self.camera.viewport_width / 2)
        screen_center_y = self.player_sprite.center_y - (
            self.camera.viewport_height / 2
        )
        if screen_center_x < 0:
            screen_center_x = 0
        if screen_center_y < 0:
            screen_center_y = 0
        player_centered = screen_center_x, screen_center_y
        self.camera.move_to(player_centered)

    def update(self, delta_time):
        """Movement and game logic"""
        self.physics_engine.update()

        # Check for collisions with coins
        coin_hit_list = arcade.check_for_collision_with_list(
            self.player_sprite, self.scene[LAYER_NAME_COINS]
        )
        for coin in coin_hit_list:
            coin.remove_from_sprite_lists()
            arcade.play_sound(self.collect_coin_sound)
            self.score += 1

        # Check for falling off the map
        if self.player_sprite.center_y < -100:
            self.player_sprite.center_x = PLAYER_START_X
            self.player_sprite.center_y = PLAYER_START_Y
            arcade.play_sound(self.game_over)

        # Check for touching something the player shouldn't
        if arcade.check_for_collision_with_list(
            self.player_sprite, self.scene[LAYER_NAME_DONT_TOUCH]
        ):
            self.player_sprite.change_x = 0
            self.player_sprite.change_y = 0
            self.player_sprite.center_x = PLAYER_START_X
            self.player_sprite.center_y = PLAYER_START_Y
            arcade.play_sound(self.game_over)

        # Check if player reached end of the level
        if arcade.check_for_collision_with_list(
            self.player_sprite, self.scene[LAYER_NAME_END]
        ):
            self.level += 1
            if self.level < len(MAP_LIST):
                self.setup()  # Load next level
            else:
                arcade.close_window()  # End the game if no more levels

        # Position the camera
        self.center_camera_to_player()

def main():
    window = MyGame()
    window.setup()
    arcade.run()

if __name__ == "__main__":
    main()
