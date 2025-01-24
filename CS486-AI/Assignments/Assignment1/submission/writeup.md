# CS486 Assingment 1 submission

Name: Amos Sng  
Student Number: 21175177

## 1. Shortest Route to Waterloo

### 1.1
The Euclidean distance, h(C), is the shortest distance between 2 nodes as it is the straight line segment between the 2 nodes.  
Therefore the Euclidean distance function never overestimates the cost of reaching the goal it is already the lowest possible value.  
For func(C) is a function that calculates the actual distance between 2 nodes, h(C) <= func(C).  
Therefore Euclidean distance is a consistent heuristic function.

## 1.2
**Full Diagram:**   
![alt text](diagrams/Assignment1Q1.2FullDiagram.png)  
**Final Diagram (for ease of viewing):**
![alt text](diagrams/Assignment1Q1.2FinalDiag.png)
The expansion path taken is
```
Tor (Start)--> Mis --> Mil --> Gue --> Kit --> Wat (Goal)
```

## 2. Travelling Salesperson

### 2.a
Representing the above graph in a python dictionary format:

```
graph = {
    "W": [("G", 36), ("T", 121), ("B", 169), ("H", 73)],
    "G": [("W", 36), ("H", 49), ("T", 99), ("B", 143)],
    "H": [("G", 49), ("T", 77), ("B", 146), ("W", 73)],
    "T": [("H", 77), ("G", 99), ("W", 121), ("B", 107)],
    "B": [("T", 107), ("H", 146), ("W", 169), ("G", 143)]
}
```
To represent a general TSP problem suitable for A*, each state of the search will have to consist of (current city, [List of visited cities], total cost). For example a state could be in the form of ("T", ["T","G"], 99), in other words, the current node is Toronto, The salesman has travelled through Toronto and Guelph, and the total cost of this traversal so far is 99.  
The inital state is when the salesman starts at any city in the given graph, with an empty visit history set other than the city he started in. For example, ("T", ["T"], 0) indicates that the salesman started this traversal at Toronto with the total travel cost of 0.  
The goal state of the TSP problem represented for A* is when all the cities in the graph have been visited at least once and the salesman returns to the starting city. For example, ("T", ["T","G","H","B","W"],584) indicates the sales person has started from Toronto, then traversed through Guelph, Hamilton, Barrie, Waterloo, then back to Toronto in that order, thus completing the TSP traversal.  
To generate the neighbours from any current city, move to any unvisited city (i.e check the list of visited cities and travel to any city not in the list), then add that city into the visited city list, and increase the total cost based on the cost of the edge betwwen the current city and the neighbour that will be traversed.  
