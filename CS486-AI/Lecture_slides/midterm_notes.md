# Mid term notes

## Graphs
- N no. nodes
- A no. arcs/edges (ordered pairs of nodes)
- $n_2$ is neighbour of $n_1$ if $(n_1,n_2) \in A$
- path <$n_1,n_2,n_3,...,n_k$> is a sequence of node such that $<n_{i-1},n_i> \in A$ 
- cost of path = $\sum$ cost of arcs in path

## Search problem
- Set of states
- Initial state
- Goal state or goal test
    - Boolean function which tells whether a given state is a goal state
- Successor (neighbour) function
    - Function that decides which state to move to next
- cost associated with each action

```python
# Graph search general algorithm
graph = {
    'A': ['B', 'C'],
    'B': ['A', 'D'],
    'C': ['A'],
    'D': ['B']
}
frontier = []
def goal(n,goal_node):
    return n ==  goal_node

def search_algo(start_node,goal_node)
    frontier.append([start_node])
    while len(frontier) != 0:
        #choose first path in frontier
        path = frontier[0] 
        #remove selected path from frontier
        frontier = frontier[1:len(frontier)] 
        #check goal is last node in selected path 
        path_last_node = path[-1]
        if goal(path_last_node,goal_node):
            return path
        else:
            for n in  graph[path_last_node]:
                #pruning can be introduced here
                new_path = path + [n]
                frontier.append(new_path)   
```
- We assume after the search algo returns an answer, it can be asked for more answers and the procedure continues
- The neighbors define the graph structure
- Function that decides which value to select from, and add values to frontier defines the search strategy.
- Goal defines what is the solution.

## Search types
- Uninformed (frontier selection function doesn't care about characteristic of nodes)
- Heuristic (frontier selection function uses some characteristic of nodes to make a "informed" decision)

### Depth first search
- Frontier uses a stack / Implemented using recursion
- Frontier selection function pops the element at the top of stack
- Cycle checking: 
    - Check if the end node is already in the path, the prune. 
    - O(1) time using hashing


```python
# Implementation of DFS with stack
graph = {
    'A': ['B', 'C'],
    'B': ['A', 'D'],
    'C': ['A'],
    'D': ['B']
}
frontier = []
def goal(n,goal_node):
    return n == goal_node

def dfs(start_node,goal_node)
    frontier.append([start_node])
    while frontier:
        #pop the last path from frontier
        path = frontier.pop()
        #check goal is last node in selected path 
        path_last_node = path[-1]
        if goal(path_last_node,goal_node):
            return path
        else:
            for n in  graph[path_last_node]:
                if n not in path: # pruning step
                    new_path = path + [n]
                    frontier.append(new_path)   
    return None #return None if no path found
```

```python
# Implementation of DFS with recursion 
graph = {
    'A': ['B', 'C'],
    'B': ['A', 'D'],
    'C': ['A'],
    'D': ['B']
}

def goal(n,goal_node):
    return n == goal_node

def recursive_dfs(current, goal_node, path=None):
    # Initialize the path if this is the first call.
    if path is None:
        path = []
    
    # Append the current node to the path.
    path = path + [current] 
    # Check if the goal has been reached.
    if goal(current,goal_node):
        return path
    
    # Explore each neighbor of the current node.
    for neighbor in graph[current]:
        #pruning step
        if neighbor not in path:
            result = recursive_dfs(neighbor, goal, path)
            if result is not None:
                return result  # Return the path as soon as we find the goal.
    
    # If no path leads to the goal, return None.
    return None
```
Properties of DFS:
- Space Complexity: O(b*m)
    - b is branching factor (max no. children of any node)
    - m is max depth of search tree
- Time Complexity: O(b<sup>m</sup>)
    - Visit the entire search tree in worst case
- Not complete
    - not guaranteed to find a solution if it exists
    - can get stuck on infinite path
- Not optimal
    - Doesn't guarantee an optimal solution if it terminates
    - pays no attention to costs and makes no guarantee of solution's quality. (blind search algorithm)
- Uses:
    - Space restricted (not infinite)
    - Many solutions exists, each with long paths
    - Singular/ few paths to each node

### Breadth first search
- Treats frontier as queue
- Frontier selection function dequeues next node from queue
- Multiple path pruning:
    - Checks previously discovered paths if they end in n, consider it a new path if none of the previous paths end in n.
        - this means BFS only remembers the first path to discover a node, all subsequent discoveries of path to this same node are disregarded
    - Subsumes cycle checking since it remembers all the nodes visited in that path, if the same node is visited, that path of traversal is disregarded, eliminating any occurrence of cycles.
    - Guarantees the first path found to a node is confirmed to be the shallowest path to that node, but this does NOT mean optimality.



```python

graph = {
'A': ['B', 'C'],
'B': ['A', 'D'],
'C': ['A'],
'D': ['B']
}

def goal(n,goal_node):
    return n == goal_node

def bfs(graph, start, goal):
    # Initialize the queue with the starting path.
    frontier = [[start]]
    
    # Set to store nodes that have already been reached by some path.
    visited = set([start])
    
    while queue:
        # Get the next path from the queue.
        path = frontier[0]
        frontier = frontier[1:]
        current_node = path[-1]
        
        # Check if we have reached the goal.
        if goal(current_node,goal):
            return path
        # Expand the current node by iterating over its neighbors.
        for neighbor in graph[current_node]:
            # If the neighbor has not been reached before, add it to the queue.
            if neighbor not in visited:
                # Prune all future paths that reach 'neighbor'
                visited.add(neighbor)
                new_path = path + [neighbor]
                queue.append(new_path)
    
    # Return None if no path is found.
    return None
```
Properties of BFS:
- Space Complexity: O(b<sup>d</sup>)
    - b is branching factor
    - d is depth of shallowest goal node
- Time Complexity: O(b<sup>d</sup>)
    - Visit whole search tree in worst case
- Complete
    - Explores the search tree level by level until a solution is found
- Not Optimal
    - Only guaranteed to find the shallowest goal, not the most optimal
- Uses:
    - Space not concern
    - Want to find solution with least edge traversed
    - Many solutions shallow in the tree
    - Problem is small and graph is static (noy dynamically generated)

### Iterative Deepening Search
- Combines the best of BFS and DFS
- Frontier search function takes extra parameter (max_level), then stops popping nodes from stack once a node with max_level-1 search tree level is reached.

Properties of IDS:
- Space Complexity: O(b*d)
    - b is branching factor
    - d is depth of shallowest goal node
    - same as DFS
- Time complexity: O(b<sup>d</sup>)
    - same as BFS

- Complete
    - Will find solution if solution exists (same as BFS)
    - Explores the tree level by level until it finds the goal

- Optimality
    - Not guaranteed to return optimal solution
        - A blind search algo after all
    - Guaranteed to find shallowest goal node (same as BFS)


### Lowest-Cost-First Search
- Frontier search function selects path on the frontier with lowest cost
    - Implemented with priority queue, sorted by path cost (ascending)
    - BFS when edges have equal cost
- Finds least-cost path to goal node
- Uninformed/blind search (doesn't take goal into account)

Properties of LCFS:
- Space Complexity:
    - exponential
- Time Complexity:
    - exponential
- Complete
    - Will always return a solution if it exists
- Optimal
    - Will return the most optimal solution, contingent on
        - branching factor is finite
        - cost of every edge is strictly positive

### Dijkstra's Algorithm
- A form of LCFS with multiple path pruning
- Frontier search function selects path on frontier with lowest cost
    - implemented with priority queue, sorted by path cost
- For every node in graph, keep track of the lowest cost to reach it so far
    - If we find a lower cost path to a node, update that value, then resort priority queue
- A form of dynamic programming since we trade space for time