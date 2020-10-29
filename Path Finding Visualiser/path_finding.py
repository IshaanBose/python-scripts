from _datastructs import *
from math import  sqrt

def astar_path(mazegui):
    """
    This function implements the A* path finding algorithm for the maze.
    """
    AVAILABLE = AugList(list())
    VISITED = AugList(list())
    currnode = Node(mazegui.start_node, h=sqrt((mazegui.start_node[0] - mazegui.goal_node[0])**2 + (mazegui.start_node[1] - mazegui.goal_node[1])**2))
    goal = Node(mazegui.goal_node)
    AVAILABLE.append(currnode)
    
    while len(AVAILABLE) != 0:
        if mazegui.stop_path_finding() == 'STOP':
            return
        
        currnode = AVAILABLE[0]
        for node in AVAILABLE:
            if node.f < currnode.f:
                currnode = node
        
        VISITED.append(currnode)
        if mazegui.show_exp:
            mazegui.render_exploration(currnode.pos, 'visited')
        
        if currnode.pos == goal.pos:
            path = list()
            while currnode:
                path.append(currnode.pos)
                currnode = currnode.parent
            return mazegui.show_path(path)
        
        children = list()
        for i in [[-20, -20], [-20, 0], [-20, 20], [0, 20], [20, 20], [20, 0], [20, -20], [0, -20]]:
            if currnode.pos[0] + i[0] < 0 or currnode.pos[1] + i[1] < 0 or currnode.pos[0] + i[0] >= mazegui.width or currnode.pos[1] + i[1] >= mazegui.height:
                continue
            
            if (currnode.pos[0] + i[0], currnode.pos[1] + i[1]) in mazegui.blocked:
                continue
            
            if i in [[-20, -20], [-20, 20], [20, 20], [20, -20]]:
                child = Node((currnode.pos[0] + i[0], currnode.pos[1] + i[1]), currnode, 28.28)
            else:
                child = Node((currnode.pos[0] + i[0], currnode.pos[1] + i[1]), currnode, 20)
            children.append(child)
            
        for child in children:
            if not VISITED.inlist(child)[0]: # heuristic is consistent, so no need to re-visit nodes
                if not AVAILABLE.inlist(child)[0]:
                    child.g += currnode.g
                    child.f = child.g + sqrt((child.pos[0] - goal.pos[0])**2 + (child.pos[1] - goal.pos[1])**2)
                    AVAILABLE.append(child)
                    if mazegui.show_exp:
                        mazegui.render_exploration(child.pos, 'available')
                else:
                    openchild = AVAILABLE[AVAILABLE.inlist(child)[1]] # if the node is already available to visit, we want to check if there is a better path for it
                    if openchild.g > child.g + currnode.g:
                        openchild.g = child.g + currnode.g
                        openchild.f = openchild.g + sqrt((child.pos[0] - goal.pos[0])**2 + (child.pos[1] - goal.pos[1])**2)
                        openchild.parent = currnode
            
        AVAILABLE.remove(currnode)
    
    mazegui.tk_popup('No Path Found!', "No path found! Press 'Space' to clear the screen.")

def bfs(mazegui):
    """
    This function implements the BFS algorithm for the maze.
    """
    Q = Queue()
    VISITED = AugList(list())
    currnode = Node(mazegui.start_node)
    goal = Node(mazegui.goal_node)
    Q.enqueue(currnode)
    
    while not Q.is_empty():
        if mazegui.stop_path_finding() == 'STOP':
            return
        
        currnode = Q.dequeue()
        VISITED.append(currnode)
        if mazegui.show_exp:
            mazegui.render_exploration(currnode.pos, 'visited')
            
        if currnode.pos == goal.pos:
            path = list()
            while currnode:
                path.append(currnode.pos)
                currnode = currnode.parent
            return mazegui.show_path(path)
        
        for i in [[-20, -20], [-20, 0], [-20, 20], [0, 20], [20, 20], [20, 0], [20, -20], [0, -20]]:
            if currnode.pos[0] + i[0] < 0 or currnode.pos[1] + i[1] < 0 or currnode.pos[0] + i[0] >= mazegui.width or currnode.pos[1] + i[1] >= mazegui.height:
                continue
            
            if (currnode.pos[0] + i[0], currnode.pos[1] + i[1]) in mazegui.blocked:
                continue
            
            node = Node((currnode.pos[0] + i[0], currnode.pos[1] + i[1]), currnode)
            if not Q.inlist(node)[0] and not VISITED.inlist(node)[0]:
                Q.enqueue(node)
                if mazegui.show_exp:
                    mazegui.render_exploration(node.pos, 'available')
    
    mazegui.tk_popup('No Path Found!', "No path found! Press 'Space' to clear the screen.")

def dfs(mazegui):
    """
    This function implements the DFS algorithm for the maze.
    """
    stack = Stack()
    VISITED = AugList(list())
    currnode = Node(mazegui.start_node)
    goal = Node(mazegui.goal_node)
    stack.push(currnode)
    
    while not stack.is_empty():
        if mazegui.stop_path_finding() == 'STOP':
            return
        
        currnode = stack.pop()
        VISITED.append(currnode)
        if mazegui.show_exp:
            mazegui.render_exploration(currnode.pos, 'visited')
        
        if currnode.pos == goal.pos:
            path = list()
            while currnode:
                path.append(currnode.pos)
                currnode = currnode.parent
            return mazegui.show_path(path)
        
        for i in [[-20, 20], [-20, 0], [-20, -20], [0, -20], [20, -20], [20, 0], [20, 20], [0, 20]]:
            if currnode.pos[0] + i[0] < 0 or currnode.pos[1] + i[1] < 0 or currnode.pos[0] + i[0] >= mazegui.width or currnode.pos[1] + i[1] >= mazegui.height:
                continue
            
            if (currnode.pos[0] + i[0], currnode.pos[1] + i[1]) in mazegui.blocked:
                continue
            
            node = Node((currnode.pos[0] + i[0], currnode.pos[1] + i[1]), currnode)
            if not stack.inlist(node)[0] and not VISITED.inlist(node)[0]:
                stack.push(node)
                if mazegui.show_exp:
                    mazegui.render_exploration(node.pos, 'available')
    
    mazegui.tk_popup('No Path Found!', "No path found! Press 'Space' to clear the screen.")