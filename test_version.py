# This is a sample Python script.
from enum import Enum

import pygame
from heapq import heapify, heappop, heappush
from collections import defaultdict
import graphs

def coord_creation(rows, columns):
    coords = {}
    reverse_coords = {}
    counter = 0
    for row in range(1, rows + 1):
        for column in range(1, columns + 1):
            coords[counter] = (column, row)
            counter += 1
    for key, value in coords.items():
        reverse_coords[value] = key

    return (coords, reverse_coords)


def get_connected_nodes(coord, reverse_coords):
    top_node = (reverse_coords.get((coord[0], coord[1] + 1), None), 10)
    top_left = (reverse_coords.get((coord[0] - 1, coord[1] + 1), None), 14)
    top_right = (reverse_coords.get((coord[0] + 1, coord[1] + 1), None), 14)
    bottom_node = (reverse_coords.get((coord[0], coord[1] - 1), None), 10)
    bottom_left = (reverse_coords.get((coord[0] - 1, coord[1] - 1), None), 14)
    bottom_right = (reverse_coords.get((coord[0] + 1, coord[1] - 1), None), 14)
    right_node = (reverse_coords.get((coord[0] + 1, coord[1]), None), 10)
    left_node = (reverse_coords.get((coord[0] - 1, coord[1]), None), 10)
    return [top_node, top_left, top_right, bottom_node, bottom_left,
             bottom_right, right_node, left_node]


def graph_creation(coords, reverse_coords):
    graph = defaultdict(list)
    for node, coord in coords.items():

        connected_nodes = get_connected_nodes(coord, reverse_coords)
        for connected_node in connected_nodes:
            if connected_node[0] in list(coords.keys()):
                graph[node].append(connected_node)
    return graph


def calculate_heuristic_dist(s_coords, e_coords):
    dx = abs(s_coords[0] - e_coords[0])
    dy = abs(s_coords[1] - e_coords[1])

    D = 10
    D2 = 14
    h = D * (dx + dy) + (D2 - 2 * D) * min(dx, dy)
    return h


def a_star_algorithm(G, coords, walls, s, e):
    # Gets end node coords
    end_coords = coords[e]

    # Initialize collections
    E = {s}
    g_dist = {s: 0}
    heap = []
    path = {}

    # Initialize Heap
    for node in G[s]:
        if node[0] in walls:
            continue
        g = node[1]
        h = calculate_heuristic_dist(coords[node[0]], end_coords)
        f = g + h
        heap_item = (f, s, node[0], (g, h))
        heap.append(heap_item)
    heapify(heap)

    while len(heap) > 0:
        smallest_item = heappop(heap)
        head_node = smallest_item[1]
        tail_node = smallest_item[2]
        if tail_node == e:
            path[tail_node] = head_node
            break

        if tail_node not in E:
            E.add(tail_node)
            path[tail_node] = head_node
            g_cost = smallest_item[3][0]
            g_dist[tail_node] = g_dist[head_node] + g_cost

        for connected_node in G[tail_node]:
            if connected_node[0] in walls:
                continue

            if connected_node[0] == e:
                path[connected_node[0]] = tail_node
                return path

            if connected_node[0] not in E:
                g = g_dist[tail_node] + connected_node[1]
                h = calculate_heuristic_dist(coords[connected_node[0]], end_coords)
                f = g + h
                heap_item = (f, tail_node, connected_node[0], (g, h))
                heappush(heap, heap_item)
    return path

coords2, reverse_coords2 = coord_creation(6, 10)
big_graph = graph_creation(coords2, reverse_coords2)

pygame.init()

SCREEN_WIDTH = 1200
SCREEN_HEIGHT = 1000
screen = pygame.display.set_mode([SCREEN_WIDTH, SCREEN_HEIGHT])

blank_node_color = (0, 100, 0)
wall_node_color = (100, 0, 0)
start_node_color = (0, 0, 100)
end_node_color = (0, 0, 255)

class Character(pygame.sprite.Sprite):
    def __init__(self, x, y, size):
        super().__init__()

        self.image = pygame.Surface([size, size])
        self.image.fill((0, 0, 255))

        self.pos = (x, y)
        self.target_pos = (0, 0)

        self.vector = pygame.Vector2()
        self.vector.xy = self.pos

    def set_target_pos(self, pos):
        self.target_pos = pos

    def move_towards_pos(self):
        target_vector = pygame.Vector2()
        target_vector.xy = self.target_pos
        self.pos = self.vector.move_towards(target_vector, 100)

    def update(self, screen):
        screen.blit(self.image, self.pos)

class Node_State(Enum):
    blank = 1
    wall = 2
    start = 3
    finish = 4


class Node(pygame.sprite.Sprite):
    def __init__(self, node, x, y, size, node_state=Node_State.blank):
        super().__init__()

        self.node_state = node_state

        self.node = node
        self.image = pygame.Surface([size, size])
        self.image = pygame.image.load(
            "/Users/tanner/Github-Projects/pathfinding/venv/grass_tile.png")
        self.image = pygame.transform.scale(self.image, (size, size))
        self.size = size

        pygame.draw.rect(self.image,
                         (255, 255, 255),
                         pygame.Rect(x, y, size, size))

        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.position = (x, y)
        self.node_text = font.render(str(node), False, (0, 255, 255))

    def update(self, screen):
        screen.blit(self.image, self.position)

    def reset_color(self):
        match self.node_state:
            case Node_State.blank:
                self.image = pygame.image.load(
                    "/Users/tanner/Github-Projects/pathfinding/venv/grass_tile.png")
            case Node_State.wall:
                self.image = pygame.image.load(
                    "/Users/tanner/Github-Projects/pathfinding/venv/dungeon_wall.png")
            case Node_State.start:
                self.image = pygame.image.load(
                    "/Users/tanner/Github-Projects/pathfinding/venv/house_tile.png")
            case Node_State.finish:
                self.image = pygame.image.load(
                    "/Users/tanner/Github-Projects/pathfinding/venv/target_tile.png")
        self.image = pygame.transform.scale(self.image,
                                            (self.size, self.size))

    def draw(self, surface):
        surface.blit(self.image, self.position)

    def update_state(self, node_state):
        self.node_state = node_state
        self.reset_color()

def draw_path(s, e, path, node_sprites):
    node_path = []
    current_node = e
    if e not in path.keys():
        for node_sprite in node_sprites:
            node_sprite.image.set_alpha(255)
        return

    for node_sprite in node_sprites:
        node_sprite.reset_color()

    while path[current_node] != s:
        next_node = path[current_node]
        node_path.append(next_node)
        current_node = next_node

        for node_sprite in node_sprites:
            if node_sprite.node == current_node:
                node_sprite.image.set_alpha(100)
    return node_path[::-1]

def update_clicked_sprite(clicked_sprite, start_node, end_node):
    path_changed = False
    if clicked_sprite is not None:
        path_changed = True
        if clicked_sprite.node in wall_list:
            wall_list.remove(clicked_sprite.node)

        if keys[pygame.K_LSHIFT]:
            if start_node is not None:
                start_node.update_state(Node_State.blank)
            start_node = clicked_sprite
            start_node.update_state(Node_State.start)
        elif keys[pygame.K_LCTRL]:
            if end_node is not None:
                end_node.update_state(Node_State.blank)
            end_node = clicked_sprite
            end_node.update_state(Node_State.finish)
        elif keys[pygame.K_LALT]:
            wall_node = clicked_sprite
            wall_list.append(clicked_sprite.node)
            wall_node.update_state(Node_State.wall)
        else:
            blank_node = clicked_sprite
            blank_node.update_state(Node_State.blank)
    return path_changed, start_node, end_node

running = True

pygame.font.init()
font = pygame.font.SysFont('Comic Sans MS', 30)

distance_multiplier = 100
clock = pygame.time.Clock()

wall_list = []

sprites = pygame.sprite.Group()
for node, node_coords in coords2.items():
    x = node_coords[0] * distance_multiplier
    y = node_coords[1] * distance_multiplier
    node_size = 100
    node_sprite = Node(node, x, y, node_size)
    sprites.add(node_sprite)

start_node = None
end_node = None
line_positions = []

# ----------------- TEST CASES ------------------------

# 1. Graph
test_coords = coord_creation(3, 4)
assert test_coords[0] == graphs.coords, "Coord Creation func not working"
assert graph_creation(test_coords[0], test_coords[1]).keys() == graphs.graph3.keys(), "Graph Creation func not working"

# ----------------- TEST CASES ------------------------

character = None
node_path = []
path_i = 0

while running:
    clicked_sprite = None
    path_changed = False

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.MOUSEBUTTONDOWN:
            for sprite in sprites:
                if sprite.rect.collidepoint(pygame.mouse.get_pos()):
                    clicked_sprite = sprite
    screen.fill((0, 0, 0))

    keys = pygame.key.get_pressed()

    path_changed, start_node, end_node = update_clicked_sprite(clicked_sprite, start_node, end_node)

    for sprite in sprites:
        sprite.update(screen)

    if start_node is not None and end_node is not None and path_changed is True:
        path = a_star_algorithm(big_graph, coords2, wall_list, start_node.node, end_node.node)
        node_path = draw_path(start_node.node, end_node.node, path, sprites)
        if character == None:
            character = Character(0, 0, 50)
        for sprite in sprites:
            if sprite.node == node_path[path_i]:
                character.set_target_pos(sprite.position)

    if node_path is not None and character is not None:
        character.move_towards_pos()
        character.update(screen)
        arrive_dist = 0.1
        if character.target_pos[1] - character.pos[0] < arrive_dist and character.target_pos[1] - character.pos[1] < arrive_dist:
            path_i += 1

            if path_i == len(node_path):
                path_i = 0

            for sprite in sprites:
                if sprite.node == node_path[path_i]:
                    character.set_target_pos(sprite.position)
                    print("CHANGED TARGET")

    pygame.display.flip()
    clock.tick(30)

pygame.quit()
