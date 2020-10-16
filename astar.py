'''
Requires a .txt file (give absolute path if it is not in the same directory as this file) with the format:

S O | O O O ...
O O O | O O ...
O O O | O O ...
O O O O O G ...
...

where S = starting node, G = goal node, | = blocked path, O = open path

Output is shown on terminal but also in an x_path.txt (x is the name of the input file) file created in the same directory as the input .txt file.
Program only works if *all spots are filled*, given multiple starting and ending nodes will result in the program choosing the last occurrences of both.
'''

import math

_MAZE = list()

class Node:
    def __init__(self, pos, parent=None, g=0, h=0):
        self.pos = pos
        self.parent = parent
        self.g = g
        self.h = h
        self.f = self.g + self.h

class AugList(list):
    def __init__(self, l):
        list.__init__(self, l)
        
    def inlist(self, node):
        for i in range(len(self)):
            if self[i].pos == node.pos:
                return [True, i]
        return [False, i]
    
    def inlist2(self, node):
        for i in range(len(self)):
            if self[i].pos == node:
                return True
        return False

def createmaze(maze, path) -> list:
    with open(path, 'r') as f:
        inp = f.read().split('\n')
        for i in range(len(inp)):
            maze.append(inp[i].split())
            
    return maze

def createoutput(maze, path_to_file, results, points):
    blocked = list()
    for i in range(len(maze)):
        for j in range(len(maze[i])):
            if maze[i][j] == '|':
                blocked.append([i, j])

    with open(path_to_file[:path_to_file.rfind('.')] + '_path.txt', 'w') as f:
        output = ''
        for i in range(len(maze)):
            for j in range(len(maze[i])):
                if [i, j] == points[0]: # starting point
                    output += 'S '
                elif [i, j] == points[1]: # ending point
                    output += 'G '
                elif [i, j] in results[0]: # path
                    output += '- '
                elif results[1].inlist2([i, j]): # visited nodes that are not part of the path
                    output += 'x '
                elif results[2].inlist2([i, j]): # nodes still availabe to visit
                    output += 'A '
                elif [i, j] in blocked: # blocked nodes
                    output += '| '
                else: # open paths
                    output += 'O '
            output += '\n'
            
        f.write(output)
    print('Output file created!')

def findstartend(maze) -> list:
    points = list()
    
    for i in range(len(maze)):
        for j in range(len(maze[i])):
            if maze[i][j] == 'S':
                points.insert(0, [i, j])
            elif maze[i][j] == 'G':
                points.insert(1, [i, j])
                
    return points

def findpath(start, end, maze) -> tuple:
    '''
    Heuristic is calculated using Euclidean distance. Diagonals are given g(n) = 1.414, other nodes are given g(n) = 1
    '''
    AVAILABLE = AugList(list())
    VISITED = AugList(list())
    currnode = Node(start, h=(start[0] - end[0])**2 + (start[1] - end[1])**2)
    end = Node(end)
    AVAILABLE.append(currnode)
    
    while len(AVAILABLE) != 0:
        currnode = AVAILABLE[0]
        for node in AVAILABLE:
            if node.f < currnode.f:
                currnode = node
                
        VISITED.append(currnode)
        
        if currnode.pos == end.pos:
            print('Goal test at', currnode.pos, 'successful. f(n) =', currnode.f)
            path = list()
            while currnode:
                path.append(currnode.pos)
                currnode = currnode.parent
            print('Path:', list(reversed(path)))
            return (list(reversed(path)), VISITED, AVAILABLE)
        
        print('Goal test at', currnode.pos, 'unsuccessful.')
        
        children = list()
        for i in [[-1, -1], [-1, 0], [-1, 1], [0, -1], [0, 1], [1, -1], [1, 0], [1, 1]]:
            if currnode.pos[0] + i[0] < 0 or currnode.pos[1] + i[1] < 0 or currnode.pos[0] + i[0] >= len(maze) or currnode.pos[1] + i[1] >= len(maze[0]): # only checking nodes within the bounds of the maze
                continue
            
            if maze[currnode.pos[0] + i[0]][currnode.pos[1] + i[1]] == '|': # skipping over blocked nodes
                continue
            
            if i in [[-1, -1], [-1, 1], [1, -1], [1, 1]]: # diagonals get g(m) = 1.414 based on Pythagoras' theorem
                child = Node([currnode.pos[0] + i[0], currnode.pos[1] + i[1]], currnode, 1.414)
            else:
                child = Node([currnode.pos[0] + i[0], currnode.pos[1] + i[1]], currnode, 1)
            children.append(child)
        
        for child in children:
            if not VISITED.inlist(child)[0]: # heuristic is consistent, so no need to re-visit nodes
                if not AVAILABLE.inlist(child)[0]:
                    child.g += currnode.g
                    child.f = child.g + math.sqrt((child.pos[0] - end.pos[0])**2 + (child.pos[1] - end.pos[1])**2)
                    AVAILABLE.append(child)
                else:
                    openchild = AVAILABLE[AVAILABLE.inlist(child)[1]] # if the node is already available to visit, we want to check if there is a better path for it
                    if openchild.g > child.g + currnode.g:
                        openchild.g = child.g + currnode.g
                        openchild.f = openchild.g + math.sqrt((child.pos[0] - end.pos[0])**2 + (child.pos[1] - end.pos[1])**2)
                        openchild.parent = currnode
        
        AVAILABLE.remove(currnode)
        
    print('No path found.')
    return

mazepath = input('Enter path to maze file: ')
createmaze(_MAZE, mazepath)
points = findstartend(_MAZE)
print(points)
results = findpath(points[0], points[1], _MAZE)
if results:
    createoutput(_MAZE, mazepath, results, points)