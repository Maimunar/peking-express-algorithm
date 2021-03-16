import unittest
import PekingExpress

class TestPekingExpress(unittest.TestCase):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.json = {
            "locations": {"number":4, "critical": [3]},
            "connections": {
                "source": [1, 1, 1, 2, 3], 
                "target": [2, 3, 88, 3, 88],
                "price": [1, 3, 7, 1, 1]
        }}

    def test_graph_initialization(self):
        # Arrange     
        graph = PekingExpress.initMap(self.json)

        # Act
        nodes = list(graph.getNodes())

        criticalNode = graph.getNode(3).getIsCritical()

        sourceNode = graph.getNode(1)
        targetNode = graph.getNode(88)
        edgeWeight = sourceNode.getWeight(targetNode)

        # Assert
        self.assertEqual(nodes, [1,2,3,88], "Should be [1,2,3,88]")
        self.assertTrue(criticalNode, "Node with index 3 should be critical")
        self.assertEqual(edgeWeight, 7, "The edge weight between nodes 1 and 88 should be 7")

    def test_calculating_graph_path_weight(self):
        # Arrange
        graph = PekingExpress.initMap(self.json)
        path = [1, 3, 88]

        # Act
        length = graph.calculatePathWeight(path)
        expectedLength = 4

        # Assert
        self.assertEqual(length, expectedLength, f"The length of {path} should be {expectedLength}")

    def test_compute_all_paths_in_graph(self):
        # Arrange
        graph = PekingExpress.initMap(self.json)
        startingLocation = 1
        targetLocation = 88

        # Act
        routes = PekingExpress.computeAllPaths(graph, startingLocation, targetLocation)
        expected_routes = [[1,2,3,88], [1,3,88], [1,88]]

        # Assert
        self.assertEqual(routes, expected_routes, f"The expected routes should be {expected_routes}")

    def test_simulate_peking_express_game_with_no_budget(self):
        # Arrange
        startLocation = 1
        occupiedLocations = [[2,3],[3],[88],[88]]
        budget = 1

        game = PekingExpress.Game('input', startLocation, occupiedLocations, budget)

        # Act/Assert
        self.assertRaises(ValueError, game.playGame)

    def test_simulate_peking_express_game_with_budget_3(self):
        # Arrange
        startLocation = 1
        occupiedLocations = [[2,3],[3],[88],[88]]
        budget = 3

        game = PekingExpress.Game('input', startLocation, occupiedLocations, budget)

        # Act
        path = game.playGame()
        expectedPath = [1,2,2,2,3,88]

        # Assert
        self.assertEqual(path, expectedPath, f"Expected path from game simulation should be {expectedPath}")

    def test_simulate_peking_express_game_with_budget_5(self):
        # Arrange
        startLocation = 1
        occupiedLocations = [[2,3],[3],[88],[88]]
        budget = 5

        game = PekingExpress.Game('input', startLocation, occupiedLocations, budget)

        # Act
        path = game.playGame()
        expectedPath = [1,3,88]

        # Assert
        self.assertEqual(path, expectedPath, f"Expected path from game simulation should be {expectedPath}")

    def test_simulate_peking_express_game_with_budget_8(self):
        # Arrange
        startLocation = 1
        occupiedLocations = [[2,3],[3],[88],[88]]
        budget = 8

        game = PekingExpress.Game('input', startLocation, occupiedLocations, budget)

        # Act
        path = game.playGame()
        expectedPath = [1,88]

        # Assert
        self.assertEqual(path, expectedPath, f"Expected path from game simulation should be {expectedPath}")

    def test_simulate_peking_express_game2_with_no_budget(self):
        # Arrange
        startLocation = 1
        occupiedLocations = [[2,5],[4,6],[5],[6]]
        budget = 3

        game = PekingExpress.Game('input2', startLocation, occupiedLocations, budget)

        # Act/Assert
        self.assertRaises(ValueError, game.playGame)

    def test_simulate_peking_express_game2_with_budget_9(self):
        # Arrange
        startLocation = 1
        occupiedLocations = [[2,5],[4,6],[5],[6]]
        budget = 9

        game = PekingExpress.Game('input2', startLocation, occupiedLocations, budget)

        # Act
        path = game.playGame()
        expectedPath = [1,2,4,5,6]

        # Assert
        self.assertEqual(path, expectedPath, f"Expected path from game simulation should be {expectedPath}")

    def test_simulate_peking_express_game2_with_budget_9(self):
        # Arrange
        startLocation = 1
        occupiedLocations = [[2,5],[4,6],[5],[6]]
        budget = 10

        game = PekingExpress.Game('input2', startLocation, occupiedLocations, budget)

        # Act
        path = game.playGame()
        expectedPath = [1,2,3,6]

        # Assert
        self.assertEqual(path, expectedPath, f"Expected path from game simulation should be {expectedPath}")

    def test_simulate_peking_express_game2_with_budget_15(self):
        # Arrange
        startLocation = 1
        occupiedLocations = [[2,5],[4,6],[5],[6]]
        budget = 15

        game = PekingExpress.Game('input2', startLocation, occupiedLocations, budget)

        # Act
        path = game.playGame()
        expectedPath = [1,2,6]

        # Assert
        self.assertEqual(path, expectedPath, f"Expected path from game simulation should be {expectedPath}")

if __name__ == '__main__':
    unittest.main()