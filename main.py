import arcade
import random
import math
import timeit


colors = {"white": arcade.color.WHITE, "black": arcade.color.BLACK, "red": arcade.color.RED, "sky": arcade.color.SKY_BLUE, "db": arcade.color.DARK_BLUE_GRAY}
groups = ["Command", "Research", "Engineering", "Medical", "Security"]
slots = [575, 475, 375, 275, 175]
menu_slots = [{"x": 300, "y": 550}, {"x": 450, "y": 550}, {"x": 600, "y": 550},
              {"x": 300, "y": 400}, {"x": 450, "y": 400}, {"x": 600, "y": 400},
              {"x": 300, "y": 250}, {"x": 450, "y": 250}, {"x": 600, "y": 250}]


# Class for physical objects on map
class Object:
    def __init__(self, x, y, vel_x, vel_y, size_x, size_y, type):
        self.x = x  # x coordinate position
        self.y = y  # y coordinate position
        self.size_x = size_x  # x coordinate size
        self.size_y = size_y  # y coordinate size
        self.vel_x = vel_x  # x coordinate momentum
        self.vel_y = vel_y  # y coordinate momentum
        self.type = type  # Object color on map, as well as type of object for now
        self.location = None
        self.angle = 0

    # Draws object, game passes in the Arcade windows, x is x coordinate position, y is y coordinate position
    def draw(self, game, x, y):
        game.draw_list.append(arcade.create_rectangle_filled(x, y, self.size_x, self.size_y, colors["red"], self.angle))

    def hit_check(self, x, y, amt_x, amt_y):
        if (abs(self.x - x) < amt_x) and (abs(self.y - y) < amt_y):
            return True
        else:
            return False

    # Moves object on map, game passes in the Arcade window
    def move(self, game):
        if self.vel_x != 0:  # Checks if there is x coordinate momentum
            # Smooth movement in the x coordinate, instead of teleporting vel_x units of distance
            for x in range(0, abs(int(math.ceil(self.vel_x)))):
                if self.vel_x > 0:  # Moves to the right if x momentum is positive
                    self.x += 1
                elif self.vel_x < 0:  # Moves to the left is x momentum is negative
                    self.x -= 1
            if self.x < 0:  # Checks if at edge of the map
                self.x = 0
                if self == game.player:  # Stops momentum of player object
                    self.vel_x = 0
                else:  # Reverses momentum of regular objects
                    self.vel_x = -self.vel_x
            elif self.x > game.mapX:  # Checks if at edge of the map
                self.x = game.mapX
                if self == game.player:  # Stops momentum of player object
                    self.vel_x = 0
                else:  # Reverses momentum of regular objects
                    self.vel_x = -self.vel_x
        if self.vel_y != 0:  # Checks if there is y coordinate momentum
            # Smooth movement in the y coordinate, instead of teleporting vel_y units of distance
            for y in range(0, abs(int(math.ceil(self.vel_y)))):
                if self.vel_y > 0:  # Moves up if y momentum is positive
                    self.y += 1
                elif self.vel_y < 0:  # Moves down if y momentum is negative
                    self.y -= 1
            if self.y < 0:  # Checks if at edge of the map
                self.y = 0
                if self == game.player:  # Stops momentum of player object
                    self.vel_y = 0
                else:  # Reverses momentum of regular objects
                    self.vel_y = -self.vel_y
            elif self.y > game.mapY:  # Checks if at edge of the map
                self.y = game.mapY
                if self == game.player:  # Stops momentum of player object
                    self.vel_y = 0
                else:  # Reverses momentum of regular objects
                    self.vel_y = -self.vel_y


# Class for player object, inherits physicality from Object and adds stats, items, crew, missions, etc
class Player(Object):
    def __init__(self, x, y, vel_x, vel_y, size_x, size_y):
        super().__init__(x, y, vel_x, vel_y, size_x, size_y, 0)
        self.image = arcade.load_texture("spaceship.png")
        self.thrust = {"w": False, "a": False, "s": False, "d": False}
        self.stats = {"credits": 1000, "missiles": 50, "energy": 100, "cargo_mass": 0}
        self.laser = False
        self.rocket = False
        self.waypoint = False
        self.search = False
        self.location = None
        self.target = {"x": 1000, "y": 1000}
        self.ship = {"engine": 10, "hull": 1000, "current_hull": 1000, "laser": 1, "missile": 1, "cargo_capacity": 100}
        self.crew = []  # List holding Crew objects
        self.cargo = []  # List holding Cargo objects

    def draw(self, game, x, y):
        arcade.draw_texture_rectangle(x, y, self.size_x, self.size_y, self.image, self.angle)


class Ship(Object):
    def __init__(self, x, y, level):
        super().__init__(x, y, random.randrange(-5, 5), random.randrange(-5, 5), 5 + (level * 5), 5 + (level * 5), 0)
        self.level = level
        self.hull = level * 100
        self.att = level * 5
        self.cargo = []
        self.station = random.randrange(0, 99)

    def draw(self, game, x, y):
        game.draw_list.append(arcade.create_ellipse_outline(x, y, self.size_x, self.size_y, colors["db"], 4))
        game.draw_list.append(arcade.create_ellipse_filled(x, y, self.size_x / 3, self.size_y / 3, colors["sky"]))

    def attack(self, game):
        game.player.ship["current_hull"] -= self.att

    def damage(self, game, amount):
        self.hull -= amount


class Location(Object):
    def __init__(self, x, y, name):
        super().__init__(x, y, 0, 0, 80, 80, 2)
        self.name = name
        self.cargo = []
        self.credits = 1000
        self.favor = 0
        self.position = None
        temp = []
        for i in range(0, 8):
            pr = random.randrange(1, 10)
            temp.append({"buy": pr, "sell": pr - 1})
        self.prices = temp

    def draw(self, game, x, y):
        game.draw_list.append(arcade.create_ellipse_outline(x, y, self.size_x, self.size_y, colors["sky"], 10, 0))
        game.draw_list.append(arcade.create_rectangle_filled(x, y, self.size_x / 2, self.size_y / 2, colors["sky"], 45))
        game.draw_list.append(arcade.create_ellipse_outline(x - 20, y + 20, 10, 10, colors["db"], 5, 0))
        game.draw_list.append(arcade.create_ellipse_outline(x - 20, y - 20, 10, 10, colors["db"], 5, 0))
        game.draw_list.append(arcade.create_ellipse_outline(x + 20, y + 20, 10, 10, colors["db"], 5, 0))
        game.draw_list.append(arcade.create_ellipse_outline(x + 20, y - 20, 10, 10, colors["db"], 5, 0))
        game.draw_list.append(arcade.create_rectangle_outline(x, y + 30, 10, 10, colors["db"], 4, 45))
        game.draw_list.append(arcade.create_rectangle_outline(x, y - 30, 10, 10, colors["db"], 4, 45))
        game.draw_list.append(arcade.create_rectangle_outline(x + 30, y, 10, 10, colors["db"], 4, 45))
        game.draw_list.append(arcade.create_rectangle_outline(x - 30, y, 10, 10, colors["db"], 4, 45))
        game.draw_list.append(arcade.create_line(x - 80, y, x + 80, y, colors["db"], 2))
        game.draw_list.append(arcade.create_line(x, y - 80, x, y + 80, colors["db"], 2))
        game.draw_list.append(arcade.create_line(x - 60, y + 60, x + 60, y - 60, colors["db"], 1))
        game.draw_list.append(arcade.create_line(x - 60, y - 60, x + 60, y + 60, colors["db"], 1))
        game.draw_list.append(arcade.create_ellipse_filled(x - 60, y + 60, 14, 14, colors["db"]))
        game.draw_list.append(arcade.create_ellipse_filled(x + 60, y + 60, 14, 14, colors["db"]))
        game.draw_list.append(arcade.create_ellipse_filled(x - 60, y - 60, 14, 14, colors["db"]))
        game.draw_list.append(arcade.create_ellipse_filled(x + 60, y - 60, 14, 14, colors["db"]))
        game.draw_list.append(arcade.create_ellipse_filled(x - 80, y, 14, 14, colors["db"]))
        game.draw_list.append(arcade.create_ellipse_filled(x + 80, y, 14, 14, colors["db"]))
        game.draw_list.append(arcade.create_ellipse_filled(x, y + 80, 14, 14, colors["db"]))
        game.draw_list.append(arcade.create_ellipse_filled(x, y - 80, 14, 14, colors["db"]))
        game.draw_list.append(arcade.create_ellipse_filled(x - 60, y + 60, 6, 6, colors["white"]))
        game.draw_list.append(arcade.create_ellipse_filled(x + 60, y + 60, 6, 6, colors["white"]))
        game.draw_list.append(arcade.create_ellipse_filled(x - 60, y - 60, 6, 6, colors["white"]))
        game.draw_list.append(arcade.create_ellipse_filled(x + 60, y - 60, 6, 6, colors["white"]))
        game.draw_list.append(arcade.create_ellipse_filled(x - 80, y, 6, 6, colors["white"]))
        game.draw_list.append(arcade.create_ellipse_filled(x + 80, y, 6, 6, colors["white"]))
        game.draw_list.append(arcade.create_ellipse_filled(x, y + 80, 6, 6, colors["white"]))
        game.draw_list.append(arcade.create_ellipse_filled(x, y - 80, 6, 6, colors["white"]))
        game.draw_list.append(arcade.create_ellipse_filled(x, y, 10, 10, colors["white"]))


class Item:
    def __init__(self, name, mass, position):
        self.name = name
        self.mass = mass
        self.position = position

    def buy(self, game, amount, price):
        location = game.locations[game.player.location]
        if game.player.stats["credits"] >= amount * price and game.player.ship["cargo_capacity"] >= (self.mass * amount) + game.player.stats["cargo_mass"] and location.cargo[self.position] >= amount:
            game.player.stats["credits"] -= amount * price
            game.player.cargo[self.position] += amount
            game.player.stats["cargo_mass"] += self.mass * amount
            location.cargo[self.position] -= amount
            location.credits += amount * price

    def sell(self, game, amount, price):
        location = game.locations[game.player.location]
        if location.credits >= amount * price and game.player.cargo[self.position] >= amount:
            game.player.cargo[self.position] -= amount
            location.credits -= amount * price
            location.cargo[self.position] += amount
            game.player.stats["credits"] += amount * price
            game.player.stats["cargo_mass"] -= self.mass * amount


# Class for ship crew
class Crew:
    def __init__(self, name, group, rank):
        self.name = name  # Displayed name of crewman
        self.group = group  # Division of crewman
        self.rank = rank  # Rank of crewman
        self.experience = 0  # Experience towards next rank

    def gain_exp(self, amount):  # Adds an amount of experience, increases rank and resets exp if above threshold
        self.experience += amount
        if self.experience > 100 * self.rank:
            self.experience -= 100 * self.rank
            self.rank += 1


class Game(arcade.Window):
    def __init__(self):
        super().__init__(800, 800, "Game1")
        self.player = None
        self.set_mouse_visible(False)
        self.set_update_rate(1 / 60)
        self.explosion = arcade.load_texture("explosion.png")
        self.object_list = []
        self.draw_list = None
        self.scene = 0
        self.enemy = None
        self.draw_time = 0
        self.processing_time = 0
        self.menu_options = ["Missions", "Ship", "Stats", "Cargo", "Crew"]
        self.items = [
            Item("Spice", 1, 0),
            Item("Weapons", 2, 1),
            Item("Medicine", 1, 2),
            Item("Metal", 3, 3),
            Item("Crystal", 2, 4),
            Item("Fuel", 1, 5),
        ]
        self.stars = []
        self.locations = []
        self.mapX = 100000
        self.mapY = 100000
        self.scroll_offset = 0
        self.list_pos = 0
        self.battle_cursor = 0
        self.station_cursor = 0
        self.cursor = 4
        arcade.set_background_color(colors["black"])

    def setup(self):
        self.player = Player(5000, 5000, 0, 0, 40, 40)
        self.player.crew.append(Crew("Captain X", 0, 10))
        self.player.crew.append(Crew("Officer Y", 0, 5))
        self.player.crew.append(Crew("Officer Z", 0, 5))
        self.player.crew.append(Crew("Researcher A", 1, 5))
        self.player.crew.append(Crew("Engineer B", 2, 5))
        self.player.crew.append(Crew("Doctor C", 3, 5))
        self.player.crew.append(Crew("Trooper D", 4, 1))
        self.player.cargo = [0 for _ in range(len(self.items))]
        self.object_list.append(self.player)
        self.draw_list = arcade.ShapeElementList()
        for s in range(0, 100):
            new_location = Location(random.randrange(1, self.mapX - 400), random.randrange(1, self.mapY - 400), str(s))
            self.object_list.append(new_location)
            self.locations.append(new_location)
            new_location.position = len(self.locations) - 1
            new_location.cargo = random.sample(range(100), len(self.items))
        for ship in range(0, 5000):
            new_ship = Ship(random.randrange(1, self.mapX - 400), random.randrange(1, self.mapY - 400), random.randrange(1, 5))
            self.object_list.append(new_ship)
            new_ship.cargo = random.sample(range(10), len(self.items))
        for j in range(0, 40000):
            rand_x, rand_y = random.randrange(1, self.mapX), random.randrange(1, self.mapY)
            self.stars.append({"x": rand_x, "y": rand_y})
        for i in range(0, 5000):
            size = random.randrange(15, 25)
            self.object_list.append(Object(random.randrange(1, self.mapX - 400), random.randrange(1, self.mapY - 400),
                                          random.randrange(-2, 2), random.randrange(-2, 2), size, size, 1))
        closest_location = self.closest_station()
        self.player.target["x"], self.player.target["y"] = closest_location.x, closest_location.y

    def stars_render(self):
        for j in range(0, len(self.stars)):
            star = self.stars[j]
            if abs(self.player.x - star["x"]) < 800 and abs(self.player.y - star["y"]) < 800:
                self.draw_list.append(arcade.create_rectangle_filled(400 - (self.player.x - star["x"]), 400 - (self.player.y - star["y"]), 1, 1, colors["white"], 0))

    def laser_animation(self):
        for i in range(0, 25):
            arcade.draw_line(400, 240, 400, 220 + ((i / 25) * 400), arcade.color.BLUE, 4)
            arcade.draw_text(str(10 * self.player.ship["laser"]), 385, 650, colors["white"],
                             font_size=18)
        arcade.draw_texture_rectangle(400, 600, 40, 40, self.explosion, 0)
        self.player.laser = False

    def rocket_animation(self):
        for i in range(0, 8):
            arcade.draw_rectangle_filled(400, 220 + (i * 50), 10, 10, arcade.color.LIGHT_RED_OCHRE)
            arcade.draw_text(str(20 * self.player.ship["missile"]), 385, 650, colors["white"],
                             font_size=18)
        arcade.draw_texture_rectangle(400, 600, 100, 100, self.explosion, 0)
        self.player.rocket = False

    def closest_station(self):
        closest_location, current_distance = None, self.mapX + self.mapY
        for i in self.locations:
            location_distance = abs(self.player.x - i.x) + abs(self.player.y - i.y)
            if location_distance < current_distance:
                current_distance = location_distance
                closest_location = i
        return closest_location

    def scene1_render(self):
        self.draw_list = arcade.ShapeElementList()
        if self.player.waypoint and self.player.target:
            # self.draw_list.append(arcade.create_ellipse_filled(400 + self.player.target["x"] - self.player.x, 400 + self.player.target["y"] - self.player.y, 10, 10, arcade.color.PINK))
            self.draw_list.append(arcade.create_line(400, 400, 400 + self.player.target["x"] - self.player.x, 400 + self.player.target["y"] - self.player.y, arcade.color.PINK, 1))
        self.player.move(self)
        # self.player.draw(self, 400, 400)
        if self.player.x < 400:
            self.draw_list.append(arcade.create_line(400 - self.player.x, 400 - self.player.y, 400 - self.player.x, 800, colors["white"], 4))
        if self.player.y < 400:
            self.draw_list.append(arcade.create_line(400 - self.player.x, 400 - self.player.y, 800, 400 - self.player.y, colors["white"], 4))
        if self.player.x > self.mapX - 800:
            self.draw_list.append(arcade.create_line(400 + (self.mapX - self.player.x), 0, 400 + (self.mapX - self.player.x),
                             400 + (self.mapY - self.player.y), colors["white"], 4))
        if self.player.y > self.mapY - 800:
            self.draw_list.append(arcade.create_line(0, 400 + (self.mapY - self.player.y), 400 + (self.mapX - self.player.x),
                             400 + (self.mapY - self.player.y), colors["white"], 4))
        self.stars_render()
        for i in range(1, len(self.object_list)):
            obj = self.object_list[i]
            if (abs(self.player.x - obj.x) < 800) and (abs(self.player.y - obj.y)) < 800:
                if obj.type == 0:
                    obj.move(self)
                obj.draw(self, 400 - (self.player.x - obj.x), 400 - (self.player.y - obj.y))

    def scene1_text(self):
        if self.player.waypoint and self.player.target:
            arcade.draw_text(str(abs(self.player.target["x"] - self.player.x) + abs(self.player.target["y"] - self.player.y)),
                             380, 380, colors["white"])
        arcade.draw_text(str(int(1 / self.draw_time)), 10, 772, colors["white"])
        arcade.draw_text(str(self.player.x) + "/" + str(self.player.y), 10, 760, colors["white"])
        offset = 0
        for k, v in self.player.stats.items():
            text = str(k).capitalize()
            if k == "cargo_mass":
                text = "Cargo Mass"
            arcade.draw_text(text + ": " + str(v), 10, 748 - (13 * offset), colors["white"])
            offset += 1
        arcade.draw_text("Hull: " + str(int(self.player.ship["current_hull"])) + "/" + str(self.player.ship["hull"]), 10, 694, colors["white"])
        # arcade.draw_text(str(self.player.vel_x) + "/" + str(self.player.vel_y), 10, 700, colors["white"])

    def scene1_key_press(self, key):
        if key == arcade.key.W or key == arcade.key.UP:
            self.player.thrust["w"] = True
        if key == arcade.key.A or key == arcade.key.LEFT:
            self.player.thrust["a"] = True
        if key == arcade.key.S or key == arcade.key.DOWN:
            self.player.thrust["s"] = True
        if key == arcade.key.D or key == arcade.key.RIGHT:
            self.player.thrust["d"] = True
        if key == arcade.key.H:
            if self.player.search:
                self.player.search, self.player.waypoint = False, False
            else:
                self.player.search, self.player.waypoint = True, True
        if key == arcade.key.E:
            if self.player.hit_check(self.player.target["x"], self.player.target["y"], 40, 40):
                new_target = self.locations[random.randrange(1, len(self.locations))]
                self.player.target["x"], self.player.target["y"] = new_target.x, new_target.y
                self.player.stats["credits"] += 100
            for i in range(1, len(self.object_list)):
                obj = self.object_list[i]
                if self.player.hit_check(obj.x, obj.y, self.player.size_x + obj.size_x, self.player.size_y + obj.size_y):
                    self.player.vel_x, self.player.vel_y = 0, 0
                    if obj.type == 0:
                        self.battle_cursor = 0
                        self.player.rocket, self.player.laser = False, False
                        self.enemy = obj
                    elif obj.type == 1:
                        self.player.ship["current_hull"] += self.player.ship["hull"] / 4
                        if self.player.ship["current_hull"] > self.player.ship["hull"]:
                            self.player.ship["current_hull"] = self.player.ship["hull"]
                        self.player.stats["credits"] += 25
                    elif obj.type == 2:
                        self.player.location = obj.position
                        self.scene = 4
                    if obj.type != 2:
                        self.object_list.pop(i)
                        self.object_list.append(Object(random.randrange(1, self.mapX), random.randrange(1, self.mapY),
                                                       random.randrange(-5, 5), random.randrange(-5, 5),
                                                       random.randrange(15, 20), random.randrange(15, 25), random.randrange(0, 2)))
                    break
        if key == arcade.key.SPACE:
            self.player.vel_x, self.player.vel_y = 0, 0
        if key == arcade.key.G:
            if self.player.waypoint:
                self.player.waypoint = False
            elif not self.player.waypoint:
                self.player.waypoint = True

    def scene2_render(self):
        self.draw_list = arcade.ShapeElementList()
        #  self.stars_render()
        #  self.draw_list.append(arcade.create_rectangle_filled(400, 400, 800, 800, arcade.color.DARK_BLUE, 0))
        self.draw_list.append(arcade.create_rectangle_filled(400, 400, 600, 600, colors["white"], 0))
        self.draw_list.append(arcade.create_line(300, 100, 300, 700, colors["black"], 4))
        for i in range(0, 5):
            self.draw_list.append(arcade.create_rectangle_filled(200, 600 - (100 * i), 50, 75, arcade.color.SILVER_LAKE_BLUE))
        self.draw_list.append(arcade.create_rectangle_outline(200, 200 + (self.cursor * 100), 50, 75, colors["black"], 3))

    def scene2_text(self):
        offset = 0
        arcade.draw_text(self.menu_options[self.cursor], 320, 650, colors["black"], font_size=20)
        if self.cursor == 2:
            arcade.draw_text("X: " + str(self.player.x) + " / " + "Y:" + str(self.player.y), 340, 600,
                             colors["black"])
            for k, v in self.player.stats.items():
                text = str(k).capitalize()
                if k == "cargo_mass":
                    text = "Cargo Mass"
                arcade.draw_text(text + ": " + str(v), 340, 550 - (offset * 50), colors["black"])
                offset += 1
        elif self.cursor == 3:
            for i in range(0, 5):
                if (self.scroll_offset + i) < len(self.items):
                    item = self.items[self.scroll_offset + i]
                    arcade.draw_rectangle_outline(500, slots[self.list_pos - self.scroll_offset], 350, 100,
                                                  colors["black"], 2)
                    arcade.draw_text(str(item.name), 340, 600 - (100 * i), colors["black"])
                    arcade.draw_text(str(self.player.cargo[item.position]), 340, 575 - (100 * i), colors["black"])
                else:
                    break
        elif self.cursor == 1:
            for k, v in self.player.ship.items():
                text = str(k).capitalize()
                if k == "cargo_capacity":
                    text = "Cargo Capacity"
                elif k == "current_hull":
                    text = "Current Hull"
                arcade.draw_text(text + ": " + str(v), 340, 600 - (offset * 50), colors["black"])
                offset += 1
        elif self.cursor == 4:
            arcade.draw_text("Roster: " + str(1 + self.list_pos) + "/" + str(len(self.player.crew)), 450, 655,
                             colors["black"])
            for i in range(0, 5):
                if (self.scroll_offset + i) < len(self.player.crew):
                    crewman = self.player.crew[self.scroll_offset + i]
                    arcade.draw_rectangle_outline(500, slots[self.list_pos - self.scroll_offset], 350, 100,
                                                  colors["black"], 2)
                    arcade.draw_text(str(crewman.name), 340, 600 - (100 * i), colors["black"])
                    arcade.draw_text(str(groups[crewman.group]), 340, 575 - (100 * i), colors["black"])
                    arcade.draw_text("Rank: " + str(crewman.rank) + " / " + str(crewman.experience), 340,
                                     550 - (100 * i), colors["black"])
                    arcade.draw_line(500, 550 - (100 * i), 650, 550 - (100 * i), arcade.color.GRAY, 4)
                    arcade.draw_line(500, 550 - (100 * i), 500 + (150 * (crewman.experience / (crewman.rank * 100))),
                                     550 - (100 * i), arcade.color.GREEN, 4)
                else:
                    break

    def scene2_key_press(self, key):
        crew_length, cargo_length = len(self.player.crew), len(self.player.cargo)
        if key == arcade.key.S and self.cursor > 0:
            self.cursor -= 1
            self.scroll_offset, self.list_pos = 0, 0
        if key == arcade.key.W and self.cursor < 4:
            self.cursor += 1
            self.scroll_offset, self.list_pos = 0, 0
        if key == arcade.key.D:
            if self.cursor == 4:
                if self.list_pos < crew_length - 1:
                    self.list_pos += 1
                    if self.list_pos >= 5:
                        self.scroll_offset += 1
            elif self.cursor == 3:
                if self.list_pos < cargo_length - 1:
                    self.list_pos += 1
                    if self.list_pos >= 5:
                        self.scroll_offset += 1
        if key == arcade.key.A:
            if self.cursor == 4 or self.cursor == 3:
                if self.list_pos > 4 and self.scroll_offset > 0:
                    self.scroll_offset -= 1
                if self.list_pos > 0:
                    self.list_pos -= 1
        if key == arcade.key.E:
            if self.cursor == 4:
                try:
                    self.player.crew.pop(self.list_pos)
                except IndexError:
                    return

    def scene3_render(self):
        self.draw_list = arcade.ShapeElementList()
        # self.stars_render()
        self.draw_list.append(arcade.create_rectangle_filled(400, 0, 800, 200, arcade.color.BLUE_GRAY, 0))
        # self.draw_list.append(arcade.create_rectangle_filled(400, 800, 800, 200, arcade.color.BLUE_GRAY, 0))
        self.draw_list.append(arcade.create_rectangle_filled(400, 113, 800, 25, arcade.color.LIGHT_GRAY, 0))
        self.draw_list.append(arcade.create_line(2, 0, 2, 124, arcade.color.DARK_BLUE, 4))
        self.draw_list.append(arcade.create_line(200, 0, 200, 101, arcade.color.DARK_BLUE, 4))
        self.draw_list.append(arcade.create_line(400, 0, 400, 101, arcade.color.DARK_BLUE, 4))
        self.draw_list.append(arcade.create_line(600, 0, 600, 101, arcade.color.DARK_BLUE, 4))
        self.draw_list.append(arcade.create_line(798, 0, 798, 124, arcade.color.DARK_BLUE, 4))
        self.draw_list.append(arcade.create_line(0, 100, 800, 100, arcade.color.DARK_BLUE, 4))
        self.draw_list.append(arcade.create_line(0, 124, 800, 124, arcade.color.DARK_BLUE, 4))
        self.draw_list.append(arcade.create_rectangle_outline(100 + (self.battle_cursor * 200), 50, 175, 75, colors["black"], 3))
        self.draw_list.append(
            arcade.create_ellipse_outline(400, 600, self.enemy.size_x, self.enemy.size_y, colors["db"], 4))
        self.draw_list.append(
            arcade.create_ellipse_filled(400, 600, self.enemy.size_x / 3, self.enemy.size_y / 3, colors["sky"]))

    def scene3_text(self):
        if self.enemy:
            arcade.draw_text("Health: " + str(int(self.player.ship["current_hull"])), 20, 106, arcade.color.DARK_SPRING_GREEN,
                             font_size=14)
            arcade.draw_text("Attack: " + str(int(self.player.ship["missile"])) + "/" + str(int(self.player.ship["laser"])), 150, 106, arcade.color.DARK_RED, font_size=14)
            arcade.draw_text(str(int(self.player.stats["energy"])) + " / " + str(int(self.player.stats["missiles"])), 280, 106, colors["black"], font_size=14)
            arcade.draw_text("Health: " + str(int(self.enemy.hull)), 420, 106, arcade.color.DARK_SPRING_GREEN,
                             font_size=14)
            arcade.draw_text("Attack: " + str(int(self.enemy.att)), 610, 105, arcade.color.DARK_RED, font_size=14)
            arcade.draw_text("Laser", 70, 42, colors["black"], font_size=20)
            arcade.draw_text("Missile", 270, 42, colors["black"], font_size=20)
            arcade.draw_text("Shield", 470, 42, colors["black"], font_size=20)
            arcade.draw_text("Retreat", 670, 42, colors["black"], font_size=20)

    def scene3_key_press(self, key):
        if self.enemy:
            if key == arcade.key.D and self.battle_cursor < 3:
                self.battle_cursor += 1
            elif key == arcade.key.A and self.battle_cursor > 0:
                self.battle_cursor -= 1
            if key == arcade.key.E and not self.player.laser or self.player.rocket:
                if self.battle_cursor == 0 and self.player.stats["energy"] > 0:
                    self.player.laser = True
                    self.player.stats["energy"] -= 1
                    self.enemy.damage(self, 10 * self.player.ship["laser"])
                elif self.battle_cursor == 1 and self.player.stats["missiles"] > 0:
                    self.player.rocket = True
                    self.player.stats["missiles"] -= 1
                    self.enemy.damage(self, 20 * self.player.ship["missile"])
                elif self.battle_cursor == 2:
                    self.player.ship["current_hull"] += 10
                elif self.battle_cursor == 3:
                    if random.randrange(0, 2) == 1:
                        self.scene = 1
                        self.enemy = None
                if self.enemy:
                    if self.enemy.hull <= 0:
                        self.player.crew[random.randrange(0, len(self.player.crew))].experience += self.enemy.level * 10
                        self.player.stats["credits"] += self.enemy.level * 25
                        self.closest_station().favor += 1
                        print(self.locations[self.enemy.station].favor)
                        self.scene = 1
                        self.enemy = None
                    elif self.enemy.hull > 0:
                        self.enemy.attack(self)
                        if self.player.ship["current_hull"] <= 0:
                            self.enemy = None
                            self.draw_list = arcade.ShapeElementList
                            self.object_list = []
                            self.stars = []
                            self.locations = []
                            self.player = None
                            self.scene = 0
                            self.setup()

    def scene4_render(self):
        self.draw_list = arcade.ShapeElementList()
        self.draw_list.append(arcade.create_rectangle_filled(400, 400, 600, 600, colors["db"], 0))
        self.draw_list.append(arcade.create_line(200, 100, 200, 700, arcade.color.DARK_BLUE, 4))
        self.draw_list.append(arcade.create_rectangle_outline(menu_slots[self.station_cursor]["x"], menu_slots[self.station_cursor]["y"], 140, 140, arcade.color.DARK_BLUE, 3))

    def scene4_text(self):
        arcade.draw_text("R to Repair\n" + str(int(self.player.ship["hull"] - self.player.ship["current_hull"])), 102, 600, colors["white"])
        arcade.draw_text("Z for Missiles\n" + str(int((self.player.ship["missile"] * 50) - self.player.stats["missiles"])), 102, 500,
                         colors["white"])
        arcade.draw_text("C for Laser\n" + str(int((self.player.ship["laser"] * 100) - self.player.stats["energy"])), 102, 400,
                         colors["white"])
        arcade.draw_text("Station " + self.locations[self.player.location].name, 350, 725, colors["white"], font_size=20)
        arcade.draw_text("Credits: " + str(self.player.stats["credits"]), 205, 660, colors["white"], font_size=16)
        arcade.draw_text("Cargo Hold: " + str(self.player.stats["cargo_mass"]) + "/" + str(self.player.ship["cargo_capacity"]),
                         450, 660, colors["white"], font_size=16)
        arcade.draw_text("Station Credits: " + str(self.locations[self.player.location].credits), 205, 635, colors["white"], font_size=16)
        arcade.draw_text("Station Favor: " + str(self.locations[self.player.location].favor), 450, 635, colors["white"], font_size=16)

        for i, v in enumerate(self.items):
            item, price = self.locations[self.player.location].cargo[i], self.locations[self.player.location].prices[i]
            arcade.draw_text(v.name + ": " + str(price["buy"]) + "/" + str(price["sell"]), menu_slots[i]["x"] - 60, menu_slots[i]["y"] - 4, colors["white"], font_size=12)
            arcade.draw_text(str(self.player.cargo[i]) + " : " + str(item), menu_slots[i]["x"] - 10, menu_slots[i]["y"] - 20,
                             colors["white"])

    def scene4_key_press(self, key):
        if key == arcade.key.W and self.station_cursor > 2:
            self.station_cursor -= 3
        elif key == arcade.key.S and self.station_cursor < 6:
            self.station_cursor += 3
        elif key == arcade.key.A and self.station_cursor != 0 and self.station_cursor != 3 and self.station_cursor != 6:
            self.station_cursor -= 1
        elif key == arcade.key.D and self.station_cursor != 2 and self.station_cursor != 5 and self.station_cursor != 8:
            self.station_cursor += 1
        if key == arcade.key.E:
            try:
                self.items[self.station_cursor].buy(self, 1, self.locations[self.player.location].prices[self.station_cursor]["buy"])
            except IndexError:
                return
        if key == arcade.key.Z:
            if self.player.stats["missiles"] < self.player.ship["missile"] * 50 and self.player.stats["credits"] >= (self.player.ship["missile"] * 50) - self.player.stats["missiles"]:
                self.player.stats["credits"] -= (self.player.ship["missile"] * 50) - self.player.stats["missiles"]
                self.player.stats["missiles"] = self.player.ship["missile"] * 50
        if key == arcade.key.C:
            if self.player.stats["energy"] < self.player.ship["laser"] * 100 and self.player.stats["credits"] >= (self.player.ship["laser"] * 100) - self.player.stats["energy"]:
                self.player.stats["credits"] -= (self.player.ship["laser"] * 100) - self.player.stats["energy"]
                self.player.stats["energy"] = self.player.ship["laser"] * 100
        elif key == arcade.key.Q:
            try:
                self.items[self.station_cursor].sell(self, 1, self.locations[self.player.location].prices[self.station_cursor]["sell"])
            except IndexError:
                return
        if key == arcade.key.R and self.player.ship["current_hull"] < self.player.ship["hull"] and self.player.stats["credits"] >= self.player.ship["hull"] - self.player.ship["current_hull"]:
            self.player.stats["credits"] -= (self.player.ship["hull"] - self.player.ship["current_hull"])
            self.locations[self.player.location].credits += (self.player.ship["hull"] - self.player.ship["current_hull"])
            self.player.ship["current_hull"] = self.player.ship["hull"]

    def text_draw(self):
        if self.scene == 0:
            for i in range(0, 16):
                if i % 2 == 0:
                    color = arcade.color.DARK_BLUE
                else:
                    color = colors["sky"]
                arcade.draw_circle_filled(400, 400, 360 - (20 * i), color)
            # arcade.draw_text("Star Gazer", 240, 440, arcade.color.AERO_BLUE, font_size=60)
            arcade.draw_text("Press F to start", 350, 400, colors["white"])
        elif self.scene == 1:
            self.scene1_text()
        elif self.scene == 2:
            self.scene2_text()
        elif self.scene == 3:
            self.scene3_text()
        elif self.scene == 4:
            self.scene4_text()

    def on_draw(self):
        draw_start_time = timeit.default_timer()
        if self.enemy:
            self.scene = 3
        if self.scene == 1:
            self.scene1_render()
        elif self.scene == 2:
            self.scene2_render()
        elif self.scene == 3:
            self.scene3_render()
        elif self.scene == 4:
            self.scene4_render()
        arcade.start_render()
        self.draw_list.draw()
        if self.scene == 1:
            self.player.draw(self, 400, 400)
        elif self.scene == 3:
            if self.player.laser:
                self.laser_animation()
                self.player.laser = False
            elif self.player.rocket:
                self.rocket_animation()
                self.player.rocket = False
            arcade.draw_texture_rectangle(400, 200, self.player.size_x, self.player.size_y, self.player.image, 90)
        self.text_draw()
        self.draw_time = timeit.default_timer() - draw_start_time

    def on_key_press(self, key, modifiers):
        if key == arcade.key.X:
            self.scene = 1
        if key == arcade.key.F:
            self.player.vel_x, self.player.vel_y = 0, 0
            if self.scene == 1:
                self.scene = 2
            elif self.scene == 2 or self.scene == 4 or self.scene == 0:
                self.scene = 1
                self.player.location = None
        if self.scene == 1:
            self.scene1_key_press(key)
        elif self.scene == 2:
            self.scene2_key_press(key)
        elif self.scene == 3:
            self.scene3_key_press(key)
        elif self.scene == 4:
            self.scene4_key_press(key)

    def on_key_release(self, key, modifiers):
        if self.scene == 1:
            if key == arcade.key.W or key == arcade.key.UP:
                self.player.thrust["w"] = False
            if key == arcade.key.A or key == arcade.key.LEFT:
                self.player.thrust["a"] = False
            if key == arcade.key.S or key == arcade.key.DOWN:
                self.player.thrust["s"] = False
            if key == arcade.key.D or key == arcade.key.RIGHT:
                self.player.thrust["d"] = False

    def update(self, delta_time):
        if self.player.thrust["w"] and self.player.vel_y < 5 * self.player.ship["engine"]:
            self.player.vel_y += 0.25
        if self.player.thrust["a"] and self.player.vel_x > -5 * self.player.ship["engine"]:
            self.player.vel_x -= 0.25
        if self.player.thrust["s"] and self.player.vel_y > -5 * self.player.ship["engine"]:
            self.player.vel_y -= 0.25
        if self.player.thrust["d"] and self.player.vel_x < 5 * self.player.ship["engine"]:
            self.player.vel_x += 0.25
        self.player.angle = math.degrees(math.atan2(self.player.vel_y, self.player.vel_x))
        if self.player.search:
            location = self.closest_station()
            self.player.target["x"], self.player.target["y"] = location.x, location.y


def main():
    window = Game()
    window.setup()
    arcade.run()


if __name__ == "__main__":
    main()
