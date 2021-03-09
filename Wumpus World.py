"""
If you want to hardcode the world, then use the following code as an example:
lst = [[Node(), Node(env=['S']), Node(), Node()],
        [Node(env=['S']), Node('W', env=['B']), Node('G', env=['g', 'S']), Node()],
        [Node(env=['B']), Node('P'), Node(env=['B]), Node()],
        [Node(), Node(env=['B']), Node(), Node()]]
lst.gold = [x] # where x is a tuple containing the co-ordinates of all gold placed in the world. For ex: lst.gold = [(1, 2)] for this world

Simply replace `lst = None` with the above two lines of code.

The agent has a solve rate of 68.858% out of 1,000,000 random (but solvable) test cases. These test cases were conducted on 4x4 world's with 3 pits, 1 wumpus, 1 gold and 1 arrow for the agent.
Solve rate will vary depending on world state.
"""

from random import randint
from copy import deepcopy
from time import sleep

lst = None

class Node():
    def __init__(self, ntype='0', env=None):
        self.type = ntype
        if not env:
            self.env = list()
        else:
            self.env = env
        self.markers = list()
        self.score = float('-inf')

class GraphNode():
    def __init__(self, pos, parent=None, g=0, h=0):
        self.pos = pos
        self.g = g
        self.h = h
        self.f = self.g + self.h
        self.parent = parent
    
    def __str__(self):
        return 'Pos: ' + str(self.pos) + ' h: ' + str(self.h) + ' f: ' + str(self.f)

class AugList(list):
    def __init__(self, l):
        list.__init__(self, l)
    
    def inlist(self, node):
        for i in range(len(self)):
            if self[i].pos == node.pos:
                return [True, i]
        return [False, i]

class World():
    def __init__(self, dimensions=4, cwumpus=1, cpits=3, cgold=1, world_lst=None):
        self.wumpus = list()
        self.pits = list()
        self.gold = list()
        
        if world_lst: # for hard-coded world
            self.world = world_lst
        else:
            self.world = [[Node() for i in range(0, dimensions)] for j in range(0, dimensions)]
            self.initial_safety = [(len(self.world) - 1, 0), (len(self.world) - 1, 1), (len(self.world) - 2, 0)] # to make sure agent has at least two viable paths at the beginning
            self.place_wumpus(cwumpus)
            self.place_pits(cpits)
            self.place_gold(cgold)
        
    def in_world(self, point):
        return (point[0] >= 0 and point[1] >= 0 and point[0] < len(self.world) and point[1] < len(self.world))
    
    def place_wumpus(self, count):
        while count != 0:
            while True:
                x, y = randint(0, len(self.world) - 1), randint(0, len(self.world) - 1)
                if not (x, y) in self.wumpus and not (x, y) in self.initial_safety:
                    self.world[x][y].type = 'W'
                    self.wumpus.append((x, y))
                    
                    for i in [(-1, 0), (0, 1), (1, 0), (0, -1)]:
                        if self.in_world((x + i[0], y + i[1])):
                            if not 'S' in self.world[x + i[0]][y + i[1]].env and self.world[x + i[0]][y + i[1]].type != ' ':
                                self.world[x + i[0]][y + i[1]].env.append('S')
                    break
            count -= 1
    
    def place_pits(self, count):
        while count != 0:
            while True:
                x, y = randint(0, len(self.world) - 1), randint(0, len(self.world) - 1)
                if not (x, y) in self.pits and not (x, y) in self.wumpus and not (x, y) in self.initial_safety:
                    self.world[x][y].type = ' '
                    self.world[x][y].env = list()
                    self.pits.append((x, y))
                    
                    for i in [(-1, 0), (0, 1), (1, 0), (0, -1)]:
                        if self.in_world((x + i[0], y + i[1])):
                            if not 'B' in self.world[x + i[0]][y + i[1]].env and self.world[x + i[0]][y + i[1]].type != ' ':
                                self.world[x + i[0]][y + i[1]].env.append('B')
                    break
            count -= 1
    
    def place_gold(self, count):
        while count != 0:
            while True:
                x, y = randint(0, len(self.world) - 1), randint(0, len(self.world) - 1)
                if not (x, y) in self.gold and not (x, y) in self.pits and not (x, y) in self.wumpus and not (x, y) in self.initial_safety:
                    safe_cnt = 4 # to make sure gold isn't surrounded by pits. This doesn't mean there will always be a path to gold, but decreases the chances of unsolvable cases.
                    for i in [(-1, 0), (0, 1), (1, 0), (0, -1)]:
                        tx, ty = x + i[0], y + i[1]
                        if self.in_world((tx, ty)):
                            if (tx, ty) in self.pits:
                                safe_cnt -= 1
                        else:
                            safe_cnt -= 1
                    if safe_cnt != 0:
                        self.world[x][y].type = 'G'
                        self.world[x][y].env.append('g')
                        self.gold.append((x, y))
                        break
            count -= 1
    
    def __getitem__(self, item):
        return self.world[item]
    
    def __len__(self):
        return len(self.world)
    
    def __str__(self):
        string = ""
        for i in self.world:
            for j in i:
                print(j.type, end='  ')
            print()
        return string

class Agent:
    def __init__(self, world: World, arrows=1):
        self.world = world
        self.pos = (len(world) - 1, 0)
        self.percepts = {'Stench' : False, 'Breeze' : False, 'Glitter' : False, 'Bump' : False, 'Scream' : False}
        self.objectives = {'Get Gold' : False}
        self.orientations = ((-1, 0), (0, 1), (1, 0), (0, -1)) # (N, E, S, W)
        self.orientation = self.orientations[1]
        self.gold = 0
        self.arrows = arrows
        self.escape_point = self.pos
        self.tentative_nodes = list()
        self.visited = [self.pos]
        
        # placing agent into the initial position
        self.world[self.pos[0]][self.pos[1]].type = 'A'
        self.world[self.pos[0]][self.pos[1]].markers = 'V'
        self.world[self.pos[0]][self.pos[1]].score = float('inf')
    
    def turn(self, direction):
        '''Turns the agent left or right, changing its orientation.'''
        alpha_orientation = ('N', 'E', 'S', 'W')
        if direction == 'R':
            self.orientation = self.orientations[(self.orientations.index(self.orientation) + 1) % 4]
            print('Turning right. Orientation:', alpha_orientation[self.orientations.index(self.orientation)])
        else:
            self.orientation = self.orientations[(self.orientations.index(self.orientation) - 1) % 4]
            print('Turning left. Orientation:', alpha_orientation[self.orientations.index(self.orientation)])
    
    def check_percepts(self):
        '''Checking the environment for anything the agent can perceive.'''
        if 'g' in self.world[self.pos[0]][self.pos[1]].env:
            self.percepts['Glitter'] = True
        else:
            self.percepts['Glitter'] = False
        if 'B' in self.world[self.pos[0]][self.pos[1]].env:
            self.percepts['Breeze'] = True
        else:
            self.percepts['Breeze'] = False
        if 'S' in self.world[self.pos[0]][self.pos[1]].env:
            self.percepts['Stench'] = True
        else:
            self.percepts['Stench'] = False
    
    def pickup(self):
        '''Agent picks up gold'''
        self.gold += 1
        self.world[self.pos[0]][self.pos[1]].type = '0'
        self.world[self.pos[0]][self.pos[1]].env.remove('g')
    
    def face(self, point):
        '''Makes agent face the direction of the given point/node.'''
        if self.pos[0] - point[0] == 0:
            if abs(self.orientation[1]) == 1:
                if abs((self.pos[1] + self.orientation[1]) - point[1]) < abs(self.pos[1] - point[1]):
                    pass
                else:
                    self.turn('L')
                    self.turn('L')
            else:
                self.turn('R')
                if abs((self.pos[1] + self.orientation[1]) - point[1]) < abs(self.pos[1] - point[1]):
                    pass
                else:
                    self.turn('L')
                    self.turn('L')
        else:
            if abs(self.orientation[0]) == 1:
                if abs((self.pos[0] + self.orientation[0]) - point[0]) < abs(self.pos[0] - point[0]):
                    pass
                else:
                    self.turn('L')
                    self.turn('L')
            else:
                self.turn('R')
                if abs((self.pos[0] + self.orientation[0]) - point[0]) < abs(self.pos[0] - point[0]):
                    pass
                else:
                    self.turn('L')
                    self.turn('L')
    
    def go_forward(self):
        '''Makes agent go forward'''
        self.percepts['Bump'] = not (self.world.in_world((self.pos[0] + self.orientation[0], self.pos[1] + self.orientation[1])))
        
        if not self.percepts['Bump']:
            self.world[self.pos[0]][self.pos[1]].type = '0'
            self.pos = (self.pos[0] + self.orientation[0], self.pos[1] + self.orientation[1])
            print('Moving to:', self.pos)
            
            if self.pos in self.world.wumpus or self.pos in self.world.pits:
                print('Death')
                exit(0)
            
            self.world[self.pos[0]][self.pos[1]].type = 'A'
            
            if not self.pos in self.visited:
                self.update_on_move()
                self.world[self.pos[0]][self.pos[1]].markers = 'V'
                self.world[self.pos[0]][self.pos[1]].score = float('inf')
                self.tentative_nodes.remove((self.pos[0], self.pos[1]))
                self.visited.append((self.pos[0], self.pos[1]))
        else:
            print('B U M P') # this is a placeholder, this part of the code will never be reached as the agent never attempts to step out of the world boundary, but was created nonetheless as the practical sheet demanded it.
    
    def shoot_at(self, pos):
        '''Makes agent shoot at the given position'''
        self.face(pos)
        arrow_pos = (self.pos[0] + self.orientation[0], self.pos[1] + self.orientation[1])
        
        while self.world.in_world(arrow_pos):
            if self.world[arrow_pos[0]][arrow_pos[1]].type == 'W':
                self.percepts['Scream'] = True
                self.world[arrow_pos[0]][arrow_pos[1]].type = '0'
                self.world.wumpus.remove(arrow_pos)
                for i in [(1, 0), (0, 1), (-1, 0), (0, -1)]:
                    if self.world.in_world((arrow_pos[0] + i[0], arrow_pos[1] + i[1])):
                        if 'S' in self.world[arrow_pos[0] + i[0]][arrow_pos[1] + i[1]].env:
                            self.world[arrow_pos[0] + i[0]][arrow_pos[1] + i[1]].env.remove('S')
                break
            arrow_pos = (arrow_pos[0] + self.orientation[0], arrow_pos[1] + self.orientation[1])
        
        self.arrows -= 1
        if self.percepts['Scream']:
            print('Wumpus killed.')
            if self.world[arrow_pos[0]][arrow_pos[1]] in self.tentative_nodes:
                self.world[arrow_pos[0]][arrow_pos[1]].markers = 'OK'
                self.world[arrow_pos[0]][arrow_pos[1]].score = float('-inf')
                for i in self.tentative_nodes:
                    while 'W?' in self.world[i[0]][i[1]].markers:
                        self.world[i[0]][i[1]].markers.remove('W?')
                        if self.world[i[0]][i[1]].score > len(self.world[i[0]][i[1]].markers):
                            self.world[i[0]][i[1]].score = len(self.world[i[0]][i[1]].markers)
            print(self.world, end='\n\n')
            self.follow_path(self.find_path(arrow_pos))
        else:
            print('Wumpus missed.')
    
    def follow_path(self, path):
        '''Makes agent follow a given path'''
        for node in path:
            self.face(node.pos)
            self.go_forward()
            print(self.world, end='\n\n')
            sleep(1)
    
    def update_on_move(self):
        '''Updates nodes as agent moves into a new space'''
        for i in [(1, 1), (1, -1), (-1, 1), (-1, -1)]:
            if self.world.in_world((self.pos[0] + i[0], self.pos[1] + i[1])):
                if type(self.world[self.pos[0] + i[0]][self.pos[1] + i[1]].markers) != str:
                    for marker in self.world[self.pos[0]][self.pos[1]].markers:
                        if marker in self.world[self.pos[0] + i[0]][self.pos[1] + i[1]].markers:
                            self.world[self.pos[0] + i[0]][self.pos[1] + i[1]].markers.append(marker)
    
    def update_knowledge(self):
        '''Main function responsible for calculating scores for each node'''
        markers = list()
        if self.percepts['Breeze']:
            markers.append('P?')
        if self.percepts['Stench']:
            markers.append('W?')
        
        if len(markers) == 0:
            markers = 'OK'
        
        temp_markers = None
        update_nodes = list()
        adjacent_nodes = list()
        
        # applying markers
        for i in [(-1, 0), (0, 1), (1, 0), (0, -1)]:
            if self.world.in_world((self.pos[0] + i[0], self.pos[1] + i[1])):
                if type(self.world[self.pos[0] + i[0]][self.pos[1] + i[1]].markers) != str:
                    if type(markers) == str:
                        if type(self.world[self.pos[0] + i[0]][self.pos[1] + i[1]].markers) == list and len(self.world[self.pos[0] + i[0]][self.pos[1] + i[1]].markers) != 0:
                            temp_markers = self.world[self.pos[0] + i[0]][self.pos[1] + i[1]].markers
                            update_nodes.append((self.pos[0] + i[0], self.pos[1] + i[1]))
                        self.world[self.pos[0] + i[0]][self.pos[1] + i[1]].markers = markers
                    else:
                        for j in markers:
                            self.world[self.pos[0] + i[0]][self.pos[1] + i[1]].markers.append(j)
                    if not (self.pos[0] + i[0], self.pos[1] + i[1]) in self.tentative_nodes and not (self.pos[0] + i[0], self.pos[1] + i[1]) in self.visited:
                        self.tentative_nodes.append((self.pos[0] + i[0], self.pos[1] + i[1]))
                    adjacent_nodes.append((self.pos[0] + i[0], self.pos[1] + i[1]))
        
        # updating markers if a node that was thought to be dangerous previously turned out to be safe.
        if len(update_nodes) != 0:
            for node in update_nodes:
                for i in [(1, 1), (1, -1), (-1, 1), (-1, -1)]:
                    if self.world.in_world((node[0] + i[0], node[1] + i[1])):
                        if type(self.world[node[0] + i[0]][node[1] + i[1]].markers) != str:
                            temp = deepcopy(self.world[node[0] + i[0]][node[1] + i[1]].markers)
                            for marker in temp:
                                if marker in temp_markers:
                                    self.world[node[0] + i[0]][node[1] + i[1]].markers.append(marker)
        
        # updating scores
        for i in range(len(adjacent_nodes)):
            if type(self.world[adjacent_nodes[i][0]][adjacent_nodes[i][1]].markers) == str:
                self.world[adjacent_nodes[i][0]][adjacent_nodes[i][1]].score = float('-inf')
            else:
                if len(self.world[adjacent_nodes[i][0]][adjacent_nodes[i][1]].markers) == 1:
                    self.world[adjacent_nodes[i][0]][adjacent_nodes[i][1]].score = 1
                else:
                    count = dict()
                    
                    for j in self.world[adjacent_nodes[i][0]][adjacent_nodes[i][1]].markers:
                        if count.get(j, -1) == -1:
                            count[j] = 1
                        else:
                            count[j] += 1
                    
                    count = dict(sorted(count.items(), key=lambda item: item[1]))
                    
                    if len(count) == 1:
                        self.world[adjacent_nodes[i][0]][adjacent_nodes[i][1]].score = list(count.values())[0]
                        
                        for j in [(1, 1), (1, -1), (-1, 1), (-1, -1)]:
                            if self.world.in_world((adjacent_nodes[i][0] + j[0], adjacent_nodes[i][1] + j[1])):
                                if type(self.world[adjacent_nodes[i][0] + j[0]][adjacent_nodes[i][1] + j[1]].markers) != str:
                                    self.world[adjacent_nodes[i][0] + j[0]][adjacent_nodes[i][1] + j[1]].score -= 0.5
                    else:
                        if count[list(count.keys())[0]] == count[list(count.keys())[1]]:
                            self.world[adjacent_nodes[i][0]][adjacent_nodes[i][1]].score = 1.5
                        else:
                            self.world[adjacent_nodes[i][0]][adjacent_nodes[i][1]].markers.remove(list(count.keys())[0])
                            self.world[adjacent_nodes[i][0]][adjacent_nodes[i][1]].score = 2
                            
                            for j in [(1, 1), (1, -1), (-1, 1), (-1, -1)]:
                                if self.world.in_world((adjacent_nodes[i][0] + j[0], adjacent_nodes[i][1] + j[1])):
                                    if type(self.world[adjacent_nodes[i][0] + j[0]][adjacent_nodes[i][1] + j[1]].markers) != str and list(count.keys())[0] in self.world[adjacent_nodes[i][0] + j[0]][adjacent_nodes[i][1] + j[1]].markers:
                                        self.world[adjacent_nodes[i][0] + j[0]][adjacent_nodes[i][1] + j[1]].markers.append(list(count.keys())[0])
                                        self.world[adjacent_nodes[i][0] + j[0]][adjacent_nodes[i][1] + j[1]].score = len(self.world[adjacent_nodes[i][0] + j[0]][adjacent_nodes[i][1] + j[1]].markers)
    
    def closest_node(self, node):
        '''Finds the closest visited node to the given node.'''
        move_direction = 1
        temp_pos = self.pos
        if abs(self.pos[0] - node[0]) <= abs(self.pos[1] - node[1]):
            while True:
                temp_pos = (temp_pos[0] + move_direction, temp_pos[1])
                if not self.world.in_world(temp_pos):
                    move_direction = -(move_direction)
                    temp_pos = self.pos
                    if move_direction == 1:
                        break
                    else:
                        continue
                if temp_pos[0] - node[0] == 0 and temp_pos in self.visited:
                    return temp_pos
        while True:
            temp_pos = (temp_pos[0], temp_pos[1] + move_direction)
            if not self.world.in_world(temp_pos):
                move_direction = -(move_direction)
                temp_pos = self.pos
                if move_direction == 1:
                    break
                else:
                    continue
            if temp_pos[1] - node[1] == 0 and temp_pos in self.visited:
                return temp_pos
        while True:
            temp_pos = (temp_pos[0] + move_direction, temp_pos[1])
            if not self.world.in_world(temp_pos):
                move_direction = -(move_direction)
                temp_pos = self.pos
                if move_direction == 1:
                    break
                else:
                    continue
            if temp_pos[0] - node[0] == 0 and temp_pos in self.visited:
                return temp_pos
        for i in self.visited:
            if i[0] - node[0] == 0 or i[1] - node[1] == 0:
                return i
    
    def best_action(self):
        '''Returns the best possible action that the agent can perform'''
        min_score = float('inf')
        
        for i in self.tentative_nodes:
            if min_score > self.world[i[0]][i[1]].score:
                min_score = self.world[i[0]][i[1]].score
        
        best_nodes = [i for i in self.tentative_nodes if self.world[i[0]][i[1]].score == min_score]
        
        if self.arrows != 0:
            wumpus_nodes = list()
            if min_score >= 1:
                for i in self.tentative_nodes:
                    if 'W?' in self.world[i[0]][i[1]].markers:
                        wumpus_nodes.append(i)
            
            max_score = float('-inf')
            if len(wumpus_nodes) != 0:
                best_wumpus = None
                for i in wumpus_nodes:
                    if max_score < self.world[i[0]][i[1]].score:
                        max_score = self.world[i[0]][i[1]].score
                        best_wumpus = i
                if self.pos[0] - best_wumpus[0] == 0 or self.pos[1] - best_wumpus[1] == 0:
                    return ['Shoot', best_wumpus]
                else:
                    return ['Shoot', best_wumpus, self.closest_node(best_wumpus)]
        
        return ['Move', best_nodes[randint(0, len(best_nodes) - 1)]]
    
    def find_path(self, goal):
        '''Finds the optimal path to the given goal node'''
        graph = deepcopy(self.visited)
        graph.append(goal)
        AVAILABLE = AugList(list())
        VISITED = AugList(list())
        curr_node = GraphNode(self.pos, h=(abs(self.pos[0] - goal[0]) + abs(self.pos[1] - goal[1])))
        AVAILABLE.append(curr_node)
        
        while len(AVAILABLE) != 0:
            curr_node = AVAILABLE[0]
            for node in AVAILABLE:
                if node.f < curr_node.f:
                    curr_node = node
            
            VISITED.append(curr_node)
            
            if curr_node.pos == goal:
                path = list()
                while True:
                    if not curr_node.parent:
                        break
                    path.insert(0, curr_node)
                    curr_node = curr_node.parent
                return path
            
            neighbours = list()
            for i in [(1, 0), (0, 1), (-1, 0), (0, -1)]:
                npos = (curr_node.pos[0] + i[0], curr_node.pos[1] + i[1])
                if self.world.in_world(npos):
                    if npos in graph:
                        neighbours.append(GraphNode(npos, g=1, h=abs(npos[0] - goal[0]) + abs(npos[1] - goal[1])))
            
            for node in neighbours:
                if not VISITED.inlist(node)[0]:
                    if not AVAILABLE.inlist(node)[0]:
                        node.g += curr_node.g
                        node.f = node.g + node.h
                        node.parent = curr_node
                        AVAILABLE.append(node)
                    else:
                        open_node = AVAILABLE[AVAILABLE.inlist(node)[1]]
                        if open_node.g > node.g + curr_node.g:
                            open_node.g = node.g + curr_node.g
                            open_node.f = open_node.g + open_node.h
                            open_node.parent = curr_node
            
            AVAILABLE.remove(curr_node)
    
    def escape(self):
        '''Lets agent esacpe safely from the world.'''
        self.follow_path(self.find_path(self.escape_point))
        print('Escaped.')
        exit(0)
    
    def do_actions(self):
        '''Performs all actions the agent can do'''
        while True:
            self.check_percepts()
            
            if self.percepts['Glitter']:
                self.pickup()
                if self.gold == len(self.world.gold):
                    self.objectives['Get Gold'] = True
                    return self.escape()
            
            self.update_knowledge()
            
            best_action = self.best_action()
            if best_action[0] == 'Shoot':
                if len(best_action) == 2:
                    self.shoot_at(best_action[1])
                else:
                    self.follow_path(self.find_path(best_action[2]))
                    self.shoot_at(best_action[1])
            else:
                self.follow_path(self.find_path(best_action[1]))

if __name__ == "__main__":
    world = World(world_lst=lst)
    agent = Agent(world)

    print(world)

    if agent.do_actions():
        print('Solved')
    else:
        print('Died')
