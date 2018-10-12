import arcade
import random
import math
import timeit


colors = [arcade.color.WHITE, arcade.color.RED, arcade.color.BLUE, arcade.color.YELLOW]
staffs = ["Command", "Research", "Engineering", "Medical", "Military"]
slots = [575, 475, 375, 275, 175]
menu_slots = [{"x": 300, "y": 550}, {"x": 450, "y": 550}, {"x": 600, "y": 550},
              {"x": 300, "y": 400}, {"x": 450, "y": 400}, {"x": 600, "y": 400},
              {"x": 300, "y": 250}, {"x": 450, "y": 250}, {"x": 600, "y": 250}]


# Class for physical objects on map
class Object:
    def __init__(self, x, y, mom_x, mom_y, size_x, size_y, color):
        self.x = x  # x coordinate position
        self.y = y  # y coordinate position
        self.size_x = size_x  # x coordinate size
        self.size_y = size_y  # y coordinate size
        self.mom_x = mom_x  # x coordinate momentum
        self.mom_y = mom_y  # y coordinate momentum
        self.color = color  # Object color on map, as well as type of object for now
        self.location = None
        self.angle = 0

    # Draws object, game passes in the Arcade windows, x is x coordinate position, y is y coordinate position
    def draw(self, game, x, y):
        game.draw_list.append(arcade.create_rectangle_filled(x, y, self.size_x, self.size_y, colors[self.color], self.angle))

    # Moves object on map, game passes in the Arcade window
    def move(self, game):
        if self.mom_x != 0:  # Checks if there is x coordinate momentum
            # Smooth movement in the x coordinate, instead of teleporting mom_x units of distance
            for x in range(0, abs(self.mom_x)):
                if self.mom_x > 0:  # Moves to the right if x momentum is positive
                    self.x += 1
                elif self.mom_x < 0:  # Moves to the left is x momentum is negative
                    self.x -= 1
            if self.x < 0:  # Checks if at edge of the map
                self.x = 0
                if self == game.player:  # Stops momentum of player object
                    self.mom_x = 0
                else:  # Reverses momentum of regular objects
                    self.mom_x = -self.mom_x
            elif self.x > game.mapX:  # Checks if at edge of the map
                self.x = game.mapX
                if self == game.player:  # Stops momentum of player object
                    self.mom_x = 0
                else:  # Reverses momentum of regular objects
                    self.mom_x = -self.mom_x
        if self.mom_y != 0:  # Checks if there is y coordinate momentum
            # Smooth movement in the y coordinate, instead of teleporting mom_y units of distance
            for y in range(0, abs(self.mom_y)):
                if self.mom_y > 0:  # Moves up if y momentum is positive
                    self.y += 1
                elif self.mom_y < 0:  # Moves down if y momentum is negative
                    self.y -= 1
            if self.y < 0:  # Checks if at edge of the map
                self.y = 0
                if self == game.player:  # Stops momentum of player object
                    self.mom_y = 0
                else:  # Reverses momentum of regular objects
                    self.mom_y = -self.mom_y
            elif self.y > game.mapY:  # Checks if at edge of the map
                self.y = game.mapY
                if self == game.player:  # Stops momentum of player object
                    self.mom_y = 0
                else:  # Reverses momentum of regular objects
                    self.mom_y = -self.mom_y


# Class for player object, inherits physicality from Object and adds stats, items, crew, missions, etc
class Player(Object):
    def __init__(self, x, y, mom_x, mom_y, size_x, size_y):
        super().__init__(x, y, mom_x, mom_y, size_x, size_y, 0)
        self.waypoint = False
        self.turbo = False
        self.credits = 0
        self.health = 200
        self.attack = 20
        self.missiles = 100
        self.energy = 100
        self.location = None
        self.target = {"x": 1000, "y": 1000}
        self.ship = {"engine": 5, "hull": 1, "laser": 1, "missile": 2}
        self.crew = []  # List holding Crewman objects
        self.cargo = []  # List holding Cargo objects


class Location:
    def __init__(self, name, items):
        self.name = name
        self.items = items
        temp = []
        for i in range(0, 8):
            pr = random.randrange(1, 10)
            temp.append({"buy": pr, "sell": pr - 1})
        self.prices = temp


class Cargo:
    def __init__(self, name, weight):
        self.name = name
        self.weight = weight
        self.amount = 1


class Enemy:
    def __init__(self, hp, att, xp, cred, size_x, size_y):
        self.health = hp
        self.att = att
        self.xp = xp
        self.cred = cred
        self.size_x = size_x
        self.size_y = size_y

    def attack(self, game):
        game.player.health -= self.att

    def damage(self, game, amount):
        self.health -= amount


# Class for ship crewman
class Crewman:
    def __init__(self, name, staff, rank):
        self.name = name  # Displayed name of crewman
        self.staff = staff  # Division of crewman
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
        self.object_list = []
        self.draw_list = None
        self.scene = 0
        self.enemy = None
        self.draw_time = 0
        self.processing_time = 0
        self.menu_options = ["Missions", "Ship", "Stats", "Cargo", "Crew"]
        self.default_items = [Cargo("Spice", 1), Cargo("Guns", 1), Cargo("Medicine", 1), Cargo("Fuel", 1), Cargo("Gold", 1),
                         Cargo("Crystals", 1), Cargo("???", 1)]
        self.stars = []
        self.locations = []
        self.mapX = 100000
        self.mapY = 100000
        self.scroll_offset = 0
        self.list_pos = 0
        self.battle_cursor = 0
        self.station_cursor = 0
        self.cursor = 4
        arcade.set_background_color(arcade.color.BLACK)

    def setup(self):
        self.player = Player(5000, 5000, 0, 0, 10, 10)
        self.player.crew.append(Crewman("Captain X", 0, 10))
        self.player.crew.append(Crewman("Officer Y", 0, 5))
        self.player.crew.append(Crewman("Officer Z", 0, 5))
        self.player.crew.append(Crewman("Researcher A", 1, 5))
        self.player.crew.append(Crewman("Engineer B", 2, 5))
        self.player.crew.append(Crewman("Doctor C", 3, 5))
        self.player.crew.append(Crewman("Trooper D", 4, 1))
        self.object_list.append(self.player)
        self.draw_list = arcade.ShapeElementList()
        for j in range(0, 40000):
            rand_x, rand_y = random.randrange(1, self.mapX), random.randrange(1, self.mapY)
            self.stars.append({"x": rand_x, "y": rand_y})
        for i in range(0, 9000):
            size = random.randrange(15, 25)
            new_color = random.randrange(0, 3)
            self.object_list.append(Object(random.randrange(1, self.mapX - 400), random.randrange(1, self.mapY - 400),
                                          random.randrange(-2, 2), random.randrange(-2, 2), size, size, new_color))
            if new_color == 2:
                self.locations.append(Location("#" + str(i), self.default_items))
                self.object_list[i + 1].location = self.locations[len(self.locations) - 1]
        self.player.target["x"], self.player.target["y"] = self.object_list[1].x, self.object_list[1].y

    def stars_render(self):
        for j in range(0, len(self.stars)):
            star = self.stars[j]
            if abs(self.player.x - star["x"]) < 800 and abs(self.player.y - star["y"]) < 800:
                self.draw_list.append(arcade.create_rectangle_filled(400 - (self.player.x - star["x"]), 400 - (self.player.y - star["y"]), 1, 1, colors[0], 0))

    def add_item(self, item):
        added = False
        for i in self.player.cargo:
            if item.name == i.name:
                i.amount += 1
                added = True
        if not added:
            self.player.cargo.append(Cargo(item.name, item.weight))

    def scene1_render(self):
        self.draw_list = arcade.ShapeElementList()
        if self.player.waypoint and self.player.target:
            # self.draw_list.append(arcade.create_ellipse_filled(400 + self.player.target["x"] - self.player.x, 400 + self.player.target["y"] - self.player.y, 10, 10, arcade.color.PINK))
            self.draw_list.append(arcade.create_line(400, 400, 400 + self.player.target["x"] - self.player.x, 400 + self.player.target["y"] - self.player.y, arcade.color.PINK, 1))
        self.player.move(self)
        self.player.draw(self, 400, 400)
        if self.player.x < 400:
            self.draw_list.append(arcade.create_line(400 - self.player.x, 400 - self.player.y, 400 - self.player.x, 800, colors[0], 4))
        if self.player.y < 400:
            self.draw_list.append(arcade.create_line(400 - self.player.x, 400 - self.player.y, 800, 400 - self.player.y, colors[0], 4))
        if self.player.x > self.mapX - 800:
            self.draw_list.append(arcade.create_line(400 + (self.mapX - self.player.x), 0, 400 + (self.mapX - self.player.x),
                             400 + (self.mapY - self.player.y), colors[0], 4))
        if self.player.y > self.mapY - 800:
            self.draw_list.append(arcade.create_line(0, 400 + (self.mapY - self.player.y), 400 + (self.mapX - self.player.x),
                             400 + (self.mapY - self.player.y), colors[0], 4))
        self.stars_render()
        for i in range(1, len(self.object_list)):
            obj = self.object_list[i]
            if (abs(self.player.x - obj.x) < 800) and (abs(self.player.y - obj.y)) < 800:
                if obj.color == 0:
                    obj.move(self)
                obj.draw(self, 400 - (self.player.x - obj.x), 400 - (self.player.y - obj.y))

    def scene1_text(self):
        if self.player.waypoint and self.player.target:
            arcade.draw_text(str((self.player.target["x"] - self.player.x) + (self.player.target["y"] - self.player.y)),
                             380, 380, arcade.color.WHITE)
        arcade.draw_text(str(int(1 / self.draw_time)), 10, 772, arcade.color.WHITE)
        arcade.draw_text(str(self.player.x) + "/" + str(self.player.y), 10, 760, arcade.color.WHITE)
        arcade.draw_text("Credits: " + str(self.player.credits), 10, 748, arcade.color.WHITE)
        arcade.draw_text("Energy: " + str(self.player.energy), 10, 736, arcade.color.WHITE)
        arcade.draw_text("Missiles: " + str(self.player.missiles), 10, 724, arcade.color.WHITE)
        arcade.draw_text("Health: " + str(self.player.health), 10, 712, arcade.color.WHITE)
        arcade.draw_text(str(self.player.mom_x) + "/" + str(self.player.mom_y), 10, 700, arcade.color.WHITE)

    def scene1_key_press(self, key):
        if key == arcade.key.W and self.player.mom_y < 5 * self.player.ship["engine"]:
            if self.player.turbo:
                self.player.turbo = False
                self.player.mom_y = 5 * self.player.ship["engine"]
            else:
                self.player.mom_y += 1
        if key == arcade.key.S and self.player.mom_y > -5 * self.player.ship["engine"]:
            if self.player.turbo:
                self.player.turbo = False
                self.player.mom_y = -5 * self.player.ship["engine"]
            else:
                self.player.mom_y -= 1
        if key == arcade.key.D and self.player.mom_x < 5 * self.player.ship["engine"]:
            if self.player.turbo:
                self.player.turbo = False
                self.player.mom_x = 5 * self.player.ship["engine"]
            else:
                self.player.mom_x += 1
        if key == arcade.key.A and self.player.mom_x > -5 * self.player.ship["engine"]:
            if self.player.turbo:
                self.player.turbo = False
                self.player.mom_x = -5 * self.player.ship["engine"]
            else:
                self.player.mom_x -= 1
        self.player.angle = math.degrees(math.atan2(self.player.mom_y, self.player.mom_x))
        if key == arcade.key.E:
            if (abs(self.player.x - self.player.target["x"]) < 20) and (abs(self.player.y - self.player.target["y"]) < 20):
                new_target = self.object_list[random.randrange(1, len(self.object_list))]
                self.player.target["x"], self.player.target["y"] = new_target.x, new_target.y
                self.player.credits += 100
            for i in range(1, len(self.object_list)):
                obj = self.object_list[i]
                if (abs(self.player.x - obj.x) < (self.player.size_x + obj.size_x)) and (abs(self.player.y - obj.y)) < (
                        self.player.size_y + obj.size_y):
                    if obj.color == 0:
                        mass = obj.size_x + obj.size_y
                        self.battle_cursor = 0
                        self.enemy = None
                        self.enemy = Enemy(mass * 5, math.floor(mass) / 2, mass, mass, mass/2, mass/2)
                    elif obj.color == 1:
                        self.player.health += self.player.ship["hull"] * 50
                        if self.player.health > self.player.ship["hull"] * 200:
                            self.player.health = self.player.ship["hull"] * 200
                    elif obj.color == 2:
                        self.player.location = obj.location
                        self.scene = 4
                    elif obj.color == 3:
                        self.player.credits += 25
                    if obj.color != 2:
                        self.object_list.pop(i)
                        self.object_list.append(Object(random.randrange(1, self.mapX), random.randrange(1, self.mapY),
                                                       random.randrange(-5, 5), random.randrange(-5, 5),
                                                       random.randrange(15, 20), random.randrange(15, 25), random.randrange(0, 3)))
                    break
        if key == arcade.key.SPACE:
            self.player.mom_x = 0
            self.player.mom_y = 0
        if key == arcade.key.G:
            if self.player.waypoint:
                self.player.waypoint = False
            elif not self.player.waypoint:
                self.player.waypoint = True
        if key == arcade.key.R:
            if self.player.turbo:
                self.player.turbo = False
            elif not self.player.turbo:
                self.player.turbo = True

    def scene2_render(self):
        self.draw_list = arcade.ShapeElementList()
        #  self.stars_render()
        #  self.draw_list.append(arcade.create_rectangle_filled(400, 400, 800, 800, arcade.color.DARK_BLUE, 0))
        self.draw_list.append(arcade.create_rectangle_filled(400, 400, 600, 600, colors[0], 0))
        self.draw_list.append(arcade.create_line(300, 100, 300, 700, arcade.color.BLACK, 4))
        self.draw_list.append(arcade.create_rectangle_filled(200, 600, 50, 75, arcade.color.SILVER_LAKE_BLUE))
        self.draw_list.append(arcade.create_rectangle_filled(200, 500, 50, 75, arcade.color.SILVER_LAKE_BLUE))
        self.draw_list.append(arcade.create_rectangle_filled(200, 400, 50, 75, arcade.color.SILVER_LAKE_BLUE))
        self.draw_list.append(arcade.create_rectangle_filled(200, 300, 50, 75, arcade.color.SILVER_LAKE_BLUE))
        self.draw_list.append(arcade.create_rectangle_filled(200, 200, 50, 75, arcade.color.SILVER_LAKE_BLUE))
        self.draw_list.append(arcade.create_rectangle_outline(200, 200 + (self.cursor * 100), 50, 75, arcade.color.BLACK, 3))

    def scene2_text(self):
        arcade.draw_text(self.menu_options[self.cursor], 320, 650, arcade.color.BLACK, font_size=20)
        if self.cursor == 2:
            arcade.draw_text("X: " + str(self.player.x) + " / " + "Y:" + str(self.player.y), 340, 600,
                             arcade.color.BLACK)
            arcade.draw_text("Credits: " + str(self.player.credits), 340, 550, arcade.color.BLACK)
            arcade.draw_text("Energy: " + str(self.player.energy), 340, 500, arcade.color.BLACK)
            arcade.draw_text("Health: " + str(self.player.health), 340, 450, arcade.color.BLACK)
        elif self.cursor == 3:
            for i in range(0, 5):
                if (self.scroll_offset + i) < len(self.player.cargo):
                    cargo = self.player.cargo[self.scroll_offset + i]
                    arcade.draw_rectangle_outline(500, slots[self.list_pos - self.scroll_offset], 350, 100,
                                                  arcade.color.BLACK, 2)
                    arcade.draw_text(str(cargo.name), 340, 600 - (100 * i), arcade.color.BLACK)
                    arcade.draw_text(str(cargo.amount), 340, 575 - (100 * i), arcade.color.BLACK)
                else:
                    break
        elif self.cursor == 1:
            arcade.draw_text("Engine: " + str(self.player.ship["engine"]), 340, 600, arcade.color.BLACK)
            arcade.draw_text("Hull: " + str(self.player.ship["hull"]), 340, 550, arcade.color.BLACK)
            arcade.draw_text("Laser: " + str(self.player.ship["laser"]), 340, 500, arcade.color.BLACK)
            arcade.draw_text("Missile: " + str(self.player.ship["missile"]), 340, 450, arcade.color.BLACK)
        elif self.cursor == 4:
            arcade.draw_text("Roster: " + str(1 + self.list_pos) + "/" + str(len(self.player.crew)), 450, 655,
                             arcade.color.BLACK)
            for i in range(0, 5):
                if (self.scroll_offset + i) < len(self.player.crew):
                    crewman = self.player.crew[self.scroll_offset + i]
                    arcade.draw_rectangle_outline(500, slots[self.list_pos - self.scroll_offset], 350, 100,
                                                  arcade.color.BLACK, 2)
                    arcade.draw_text(str(crewman.name), 340, 600 - (100 * i), arcade.color.BLACK)
                    arcade.draw_text(str(staffs[crewman.staff]), 340, 575 - (100 * i), arcade.color.BLACK)
                    arcade.draw_text("Rank: " + str(crewman.rank) + " / " + str(crewman.experience), 340,
                                     550 - (100 * i), arcade.color.BLACK)
                    arcade.draw_line(500, 550 - (100 * i), 650, 550 - (100 * i), arcade.color.GRAY, 4)
                    arcade.draw_line(500, 550 - (100 * i), 500 + (150 * (crewman.experience / (crewman.rank * 100))),
                                     550 - (100 * i), arcade.color.GREEN, 4)
                else:
                    break

    def scene2_key_press(self, key):
        crew_length = len(self.player.crew)
        cargo_length = len(self.player.cargo)
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
        self.draw_list.append(arcade.create_rectangle_outline(100 + (self.battle_cursor * 200), 50, 175, 75, arcade.color.BLACK, 3))
        self.draw_list.append(arcade.create_rectangle_filled(400, 200, self.player.size_x, self.player.size_y, arcade.color.WHITE))
        self.draw_list.append(arcade.create_rectangle_filled(400, 600, self.enemy.size_x, self.enemy.size_y, arcade.color.WHITE))

    def scene3_text(self):
        if self.enemy:
            arcade.draw_text("Health: " + str(int(self.player.health)), 20, 106, arcade.color.DARK_SPRING_GREEN,
                             font_size=14)
            arcade.draw_text("Attack: " + str(int(self.player.attack)), 150, 106, arcade.color.DARK_RED, font_size=14)
            arcade.draw_text(str(int(self.player.energy)) + " / " + str(int(self.player.missiles)), 280, 106, arcade.color.BLACK, font_size=14)
            arcade.draw_text("Health: " + str(int(self.enemy.health)), 420, 106, arcade.color.DARK_SPRING_GREEN,
                             font_size=14)
            arcade.draw_text("Attack: " + str(int(self.enemy.att)), 610, 105, arcade.color.DARK_RED, font_size=14)
            arcade.draw_text("Laser", 70, 42, arcade.color.BLACK, font_size=20)
            arcade.draw_text("Missile", 270, 42, arcade.color.BLACK, font_size=20)
            arcade.draw_text("Shield", 470, 42, arcade.color.BLACK, font_size=20)
            arcade.draw_text("Retreat", 670, 42, arcade.color.BLACK, font_size=20)

    def scene3_key_press(self, key):
        if self.enemy:
            if key == arcade.key.D and self.battle_cursor < 3:
                self.battle_cursor += 1
            elif key == arcade.key.A and self.battle_cursor > 0:
                self.battle_cursor -= 1
            if key == arcade.key.E:
                if self.battle_cursor == 0 and self.player.energy > 0:
                    self.player.energy -= 1
                    self.enemy.damage(self, self.player.attack * self.player.ship["laser"])
                elif self.battle_cursor == 1 and self.player.missiles > 0:
                    self.player.missiles -= 1
                    self.enemy.damage(self, self.player.attack * self.player.ship["missile"])
                elif self.battle_cursor == 2:
                    self.player.health += 10
                elif self.battle_cursor == 3:
                    if random.randrange(0, 2) == 1:
                        self.scene = 1
                        self.enemy = None
                if self.enemy:
                    if self.enemy.health <= 0:
                        self.player.crew[0].experience += self.enemy.xp
                        self.player.credits += self.enemy.cred
                        self.scene = 1
                        self.enemy = None
                    elif self.enemy.health > 0:
                        self.enemy.attack(self)
                        if self.player.health <= 0:
                            self.enemy = None
                            self.draw_list = arcade.ShapeElementList
                            self.object_list = []
                            self.stars = []
                            self.player = None
                            self.scene = 0
                            self.setup()

    def scene4_render(self):
        self.draw_list = arcade.ShapeElementList()
        self.draw_list.append(arcade.create_rectangle_filled(400, 400, 600, 600, arcade.color.DARK_BLUE_GRAY, 0))
        self.draw_list.append(arcade.create_line(200, 100, 200, 700, arcade.color.DARK_BLUE, 4))
        self.draw_list.append(arcade.create_rectangle_outline(menu_slots[self.station_cursor]["x"], menu_slots[self.station_cursor]["y"], 140, 140, arcade.color.DARK_BLUE, 3))

    def scene4_text(self):
        arcade.draw_text("Station " + self.player.location.name, 350, 725, arcade.color.WHITE, font_size=20)
        arcade.draw_text("Credits: " + str(self.player.credits), 225, 650, arcade.color.WHITE, font_size=16)
        for i in range(0, len(self.player.location.items)):
            item, price = self.player.location.items[i], self.player.location.prices[i]
            arcade.draw_text(item.name + ": " + str(price["buy"]) + "/" + str(price["sell"]), menu_slots[i]["x"] - 40, menu_slots[i]["y"] - 4, arcade.color.WHITE, font_size=12)
            for j in range(0, len(self.player.cargo)):
                if self.player.cargo[j].name == item.name:
                    arcade.draw_text(str(self.player.cargo[j].amount), menu_slots[i]["x"] - 10, menu_slots[i]["y"] - 20, arcade.color.WHITE)

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
                if self.player.credits >= self.player.location.prices[self.station_cursor]["buy"]:
                    self.add_item(self.player.location.items[self.station_cursor])
                    self.player.credits -= self.player.location.prices[self.station_cursor]["buy"]
            except IndexError:
                return
        elif key == arcade.key.R:
            try:
                for i in range(0, len(self.player.cargo)):
                    item = self.player.cargo[i]
                    if item.name == self.player.location.items[self.station_cursor].name and item.amount > 0:
                        item.amount -= 1
                        self.player.credits += self.player.location.prices[self.station_cursor]["sell"]
                        if item.amount <= 0:
                            self.player.cargo.pop(i)
            except IndexError:
                return

    def text_draw(self):
        if self.scene == 0:
            arcade.draw_circle_filled(400, 400, 360, arcade.color.DARK_BLUE)
            arcade.draw_circle_filled(400, 400, 320 - random.randrange(-5, 5), arcade.color.SKY_BLUE)
            arcade.draw_circle_filled(400, 400, 280, arcade.color.DARK_BLUE)
            arcade.draw_circle_filled(400, 400, 240 - random.randrange(-5, 5), arcade.color.SKY_BLUE)
            arcade.draw_circle_filled(400, 400, 200, arcade.color.DARK_BLUE)
            arcade.draw_circle_filled(400, 400, 160 - random.randrange(-5, 5), arcade.color.SKY_BLUE)
            arcade.draw_circle_filled(400, 400, 120, arcade.color.DARK_BLUE)
            arcade.draw_circle_filled(400, 400, 80 - random.randrange(-5, 5), arcade.color.SKY_BLUE)
            arcade.draw_circle_filled(400, 400, 40, arcade.color.DARK_BLUE)
            # arcade.draw_text("Star Gazer", 240, 440, arcade.color.AERO_BLUE, font_size=60)
            arcade.draw_text("Press F to start", 350, 400, arcade.color.WHITE)
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
        self.text_draw()
        self.draw_time = timeit.default_timer() - draw_start_time

    def on_key_press(self, key, modifiers):
        if key == arcade.key.X:
            self.scene = 1
        if key == arcade.key.F:
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

    #  def update(self, delta_time):


def main():
    window = Game()
    window.setup()
    arcade.run()


if __name__ == "__main__":
    main()
