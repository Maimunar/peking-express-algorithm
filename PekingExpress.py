from copy import copy
from collections import defaultdict
from timeit import default_timer as timer
import json
import os

# Data structure that acts as the vertex of the graph
class Node:
    def __init__(self, index, isCritical=False):
        self.id = index
        self.isCritical = isCritical
        self.isOccupied = False
        self.connections = {}

    def addConnection(self, connection, weight=0):
        self.connections[connection] = weight

    def deleteConnection(self, connection):
        del self.connections[connection]

    def getConnections(self):
        return self.connections.keys()  

    def getId(self):
        return self.id
    
    def getIsCritical(self):
        return self.isCritical
    
    def setOccupied(self, isOccupied):
        self.isOccupied = isOccupied

    def getOccupied(self):
        return self.isOccupied

    def getWeight(self, connection):
        return self.connections[connection]
    
    def setIsCritical(self, value):
        self.isCritical = value

    
    def isUnavailable(self):
        return (self.isCritical and self.isOccupied)

# Data structure constructed from a combination of nodes and their connections (edges)
class Graph:
    def __init__(self):
        self.nodes = {}
        self.num_nodes = 0
        self.startLocation = None

    def __iter__(self):
        return iter(self.nodes.values())

    def addNode(self, index, isCritical=False):
        self.num_nodes += 1
        self.nodes[index] = Node(index, isCritical)
        return self.nodes[index]

    def getNode(self, index):
        if index in self.nodes:
            return self.nodes[index]
        else:
            return None

    def AddEdge(self, origin, dest, cost):
        if origin not in self.nodes:
            self.addNode(origin)
        if dest not in self.nodes:
            self.addNode(dest)

        self.nodes[origin].addConnection(self.nodes[dest], cost)
        self.nodes[dest].addConnection(self.nodes[origin], cost)

    def RemoveEdge(self, origin, dest):
        self.nodes[origin].deleteConnection(self.nodes[dest])
        self.nodes[dest].deleteConnection(self.nodes[origin])

    def getNodes(self):
        return self.nodes.keys()
    
    def setCritical(self, index, isCritical=True):
        node = self.getNode(index)
        if node:
            node.setIsCritical(isCritical)
    
    # Calculation of the total weight of the provided list
    # E.g. [1,2,3,88] -> All edges between these nodes will be checked and summed
    def calculatePathWeight(self, path: list):
        totalWeight = 0
        for i in range(len(path) - 1):
            currentNode = self.getNode(path[i])
            nextNode = self.getNode(path[i+1])
            totalWeight += currentNode.getWeight(nextNode)
        return totalWeight

    def setStartLocation(self, startIndex):
        self.startLocation = self.getNode(startIndex)
    
    def getStartLocation(self):
        return self.startLocation

### Game Logic --------------------------------------------------------------#

# Initializes the playable area from a json dictionary object
def initMap(jsonMap):

    PekingMap = Graph()

    sourceList = jsonMap['connections']['source']
    targetList = jsonMap['connections']['target']
    priceList = jsonMap['connections']['price']
    
    # Populating the graph from the source, target and price lists
    # Note: The method 'AddEdge' also creates nodes if they are not present in the graph
    for i in range(len(sourceList)):
        PekingMap.AddEdge(sourceList[i], targetList[i], priceList[i])
    
    # Sets all critically listed notes in the JSON file as critical
    for criticalLocation in (jsonMap['locations']['critical']):
        PekingMap.setCritical(criticalLocation)

    return PekingMap

# Rest of Game Logic
class Game:

    # Main Function
    def __init__(self, jsonMap:dict, startLocation, occupiedLocations, budget):
        self.budget = budget
        self.occupiedLocations = occupiedLocations

        # Loads all relevant graph data from a JSON file
        self.PekingMap = initMap(jsonMap)
        print(self.PekingMap.getNode(1))
        # with open(os.path.join(os.path.dirname(os.path.realpath(__file__)), f'{fileName}.json'), 'r', encoding="utf_8") as json_file:
        #     self.PekingMap = initMap(json.load(json_file))
        # json_file.close()

        self.PekingMap.setStartLocation(startLocation)
     
        # Due to ambiguity in the description of the assignment, we assume that Peking is the node with the maximum value
        # This can be changed to be provided by the system before the game begins
        
        if self.PekingMap.getNode(88):
            self.targetLocation = 88
        else:
            self.targetLocation = max(self.PekingMap.getNodes())
        print(self.targetLocation)
        self.currentLocation = startLocation       

    # Simulates the 'Peking Express' game
    def playGame(self):
        myPath = []
        currentTurnIndex = 0

        print(f"Turn {currentTurnIndex+1}: My current position is {self.currentLocation}")

        # Adds the starting location to the path as first element
        myPath.append(self.currentLocation)

        try:
            while self.currentLocation is not self.targetLocation:
                # Adds the next location of the minimum route in the list
                myPath.append(self.nextMove())

                # Update location occupation status as long as the current turn does not exceed the occupiedLocatons list
                # This prevents the software from running into issues when the list does not have occupation status for all turns
                if currentTurnIndex < len(self.occupiedLocations):
                    self.updateOccupiedLocations(self.occupiedLocations[currentTurnIndex])

                currentTurnIndex += 1

                # Moves the current location of the player to the last found destination by the nextMove() method
                self.currentLocation = myPath[-1]
                print(f"Turn {currentTurnIndex+1}: My current position is {self.currentLocation}")
        except Exception as e:
            print('Invalid player budget:', e)
            raise e

        return myPath

    # Updates the occupation status for all nodes in the graph
    def updateOccupiedLocations(self, locationList):
        for node in self.PekingMap.getNodes():
            self.PekingMap.getNode(node).setOccupied(node in locationList or node == self.currentLocation)

    # Performs the next player move
    def nextMove(self):
        # Gathering all available routes
        routes = shortPathsAlgorithm(self.PekingMap, self.currentLocation, self.targetLocation, self.budget)

        # If there are no available routes, the player will stay in the same location
        nextNode = self.currentLocation
        if routes:
            # Else, the method will return the next location of the player and deduct the needed cost from his budget
            # The abovementioned location is taken from the route with the minimum length
            minPath = min(routes, key=len)
            currentNode = minPath[0]
            nextNode = minPath[1]
            self.budget -= self.PekingMap.getNode(currentNode).getWeight(self.PekingMap.getNode(nextNode))

        return nextNode

# Returns all routes that meet the budget and critical/occupation location criteria
def shortPathsAlgorithm(graph: Graph, startLocation, targetLocation, budget):

    routes = computeAllPaths(graph, startLocation, targetLocation)
    validRoutes = copy(routes)
    print(validRoutes)
    # Removing all routes that exceed the provided budget
    for route in routes:
        if graph.calculatePathWeight(route) > budget:
            validRoutes.remove(route)
    routes = copy(validRoutes)
    if validRoutes:
        # Removing all routes where the next destination in the path is currently unavailable (Critical node and currently occupied)
        for route in routes:
            nextNode = graph.getNode(route[1])
            if nextNode.isUnavailable():
                validRoutes.remove(route)
    else:
        # If there are no routes in the given budget, then the budget is unsifficient to travel to terminal point
        raise ValueError("The provided budget is unssufficient to get the player to the target destination!")

    return validRoutes

# Helper function for path computation that uses recursion
def computeAllPathsUtil(graph, current_node, destination, visited, path, routes): 

        # Mark the current node as visited and store in path 
        visited[current_node]= True
        path.append(current_node) 

        if current_node == destination:
            routes.append(copy(path))
        else: 
            # If current vertex is not destination 
            # Recur for all the vertices adjacent to this vertex
            nodes = [x.getId() for x in graph.getNode(current_node).getConnections()]
            for i in nodes: 
                if visited[i] == False: 
                    computeAllPathsUtil(graph, i, destination, visited, path, routes)
                    
        # Remove current vertex from path[] and mark it as unvisited 
        path.pop() 
        visited[current_node] = False
        return routes

# Computing all possible paths from starting location to target location
def computeAllPaths(graph, startingLocation, targetLocation): 

    # Marking all vertices as not visited 
    visited = defaultdict(lambda: False)

    # Storing all paths and valid routes
    path = []
    routes = []

    # Calling the recursive helper function to retrieve all possible paths
    return computeAllPathsUtil(graph, startingLocation, targetLocation, visited, path, routes)

if __name__ == '__main__':
    text_file = None
    with open(os.path.join(os.path.dirname(os.path.realpath(__file__)), f'testfile.txt'), 'r', encoding="utf_8") as f:
        text_file = f.read()
    f.close()
    inputFile = text_file.split('\n')
    occupiedLocations = json.loads(inputFile.pop())
    budget = int(inputFile.pop())
    startLocation = int(inputFile.pop())
    jsonMap = json.loads(''.join(inputFile)) 

    init_start = timer()
    game = Game(jsonMap, startLocation, occupiedLocations, budget)
    init_end = timer()

    print(f"Game initalization finished in: {'%.3f' % ((init_end - init_start)*1000)} ms")

    play_start = timer()
    path = game.playGame()
    play_end = timer()

    print(f"My path : {path}")

    print(f"Game session simulation finished in: {'%.3f' % ((play_end - play_start)*1000)} ms")

