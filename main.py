import os
import sys
import configparser
import subprocess
import zipfile
import xml.etree.ElementTree as ET
from pathlib import Path


class DependencyVisualizer:
    def __init__(self, config_path):
        self.config = self._load_config(config_path)
        self.package_name = self.config['main']['PackageName']
        self.output_path = Path(self.config['main']['OutputPath'])
        self.visualizer_path = self.config['main']['VisualizerPath']
        self.dependencies = {}

    def _load_config(self, path):
        config = configparser.ConfigParser()
        config.read(path)
        return config

    def extract_dependencies(self, package_path):
        print(f"Извлечение зависимостей из {package_path}")

        # Распаковка nupkg файла
        with zipfile.ZipFile(package_path, 'r') as archive:
            # Находим .nuspec файл
            nuspec_file = next((f for f in archive.namelist() if f.endswith('.nuspec')), None)
            if not nuspec_file:
                raise FileNotFoundError(f".nuspec файл не найден в {package_path}")

            # Извлекаем содержимое .nuspec файла
            with archive.open(nuspec_file) as nuspec:
                tree = ET.parse(nuspec)
                root = tree.getroot()

                # Пространства имён могут быть в XML, учитываем это
                namespace = {'ns0': 'http://schemas.microsoft.com/packaging/2013/05/nuspec.xsd'}

                print("Корневой элемент XML:", ET.tostring(root, encoding="unicode"))

                dependencies_node = root.find(".//ns0:dependencies", namespace)
                if dependencies_node is not None:
                    print(f"Найден узел <dependencies>: {ET.tostring(dependencies_node, encoding='unicode')}")
                else:
                    print("Узел <dependencies> не найден")

                self.dependencies = {}
                if dependencies_node is not None:
                    for group in dependencies_node.findall("ns0:group", namespace):
                        target_framework = group.get('targetFramework', 'Unknown Framework')
                        print(f"Обрабатываем группу для targetFramework: {target_framework}")

                        for dependency in group.findall("ns0:dependency", namespace):
                            package = dependency.get('id')
                            version = dependency.get('version')
                            print(f"Найдена зависимость: {package} ({version})")

                            self.dependencies.setdefault(target_framework, []).append(f"{package} ({version})")

        print(f"Найденные зависимости: {self.dependencies}")

    def generate_mermaid_graph(self):
        lines = ["graph TD"]
        for framework, dependencies in self.dependencies.items():
            framework_node = f"{framework.replace('.', '_').replace('-', '_')}"  # Для Mermaid имена узлов без точек
            lines.append(f"    {framework_node}[[{framework}]]")
            for dependency in dependencies:
                dependency_node = dependency.replace(" ", "_").replace("(", "").replace(")", "").replace(".", "_")
                lines.append(f"    {framework_node} --> {dependency_node}")
        return "\n".join(lines)

    def save_mermaid_file(self, mermaid_graph, output_file):
        with open(output_file, 'w') as f:
            f.write(mermaid_graph)

    def generate_image(self, mermaid_file):
        # Увеличиваем разрешение с помощью флагов --width и --height
        command = [
            self.visualizer_path, "-i", mermaid_file, "-o", self.output_path,
            "--width", "2000",  # Увеличиваем ширину изображения
            "--height", "1500",  # Увеличиваем высоту изображения
        ]
        subprocess.run(command, check=True)

    def run(self, package_path):
        print("Запуск процесса анализа зависимостей...")
        self.extract_dependencies(package_path)  # Убедитесь, что метод вызывается
        mermaid_graph = self.generate_mermaid_graph()
        temp_mermaid_file = "temp_graph.mmd"
        self.save_mermaid_file(mermaid_graph, temp_mermaid_file)
        self.generate_image(temp_mermaid_file)
        os.remove(temp_mermaid_file)
        print(f"Граф сохранен в {self.output_path}")


if __name__ == "__main__":
    try:
        # Получаем аргументы командной строки
        config_path = sys.argv[1]  # Путь к конфигурационному файлу
        package_path = sys.argv[2]  # Путь к пакету для анализа

        # Выводим полученные параметры для проверки
        print(f"Конфигурация: {config_path}, Пакет: {package_path}")

        # Создаем объект DependencyVisualizer и запускаем анализ
        visualizer = DependencyVisualizer(config_path)
        visualizer.run(package_path)

    except Exception as e:
        # Если возникает ошибка, выводим её сообщение
        print(f"Произошла ошибка: {e}")
