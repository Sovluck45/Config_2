import sys

from main import DependencyVisualizer

if __name__ == "__main__":
    config_path = sys.argv[1]  # Первый аргумент
    package_path = sys.argv[2]  # Второй аргумент
    visualizer = DependencyVisualizer(config_path)
    visualizer.run(package_path)