import unittest
from main import DependencyVisualizer


class TestDependencyVisualizer(unittest.TestCase):
    def setUp(self):
        self.visualizer = DependencyVisualizer("test_config.ini")
        self.visualizer.dependencies = {
            "PackageA": ["PackageB", "PackageC"],
            "PackageB": [],
            "PackageC": ["PackageD"],
            "PackageD": []
        }

    def test_generate_mermaid_graph(self):
        graph = self.visualizer.generate_mermaid_graph()
        expected_graph = (
            "graph TD\n"
            "    PackageA --> PackageB\n"
            "    PackageA --> PackageC\n"
            "    PackageC --> PackageD"
        )
        self.assertEqual(graph.strip(), expected_graph.strip())
