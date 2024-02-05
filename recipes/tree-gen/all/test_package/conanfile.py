import filecmp
import os

from conan import ConanFile


class TreeGenTestConan(ConanFile):
    settings = "os", "compiler", "build_type", "arch"
    generators = "VirtualBuildEnv"
    test_type = "explicit"

    def build_requirements(self):
        self.tool_requires(self.tested_reference_str)

    def test(self):
        output_files_folder = os.path.dirname(__file__)
        tree_file_path = os.path.join(output_files_folder, "directory.tree")
        actual_header_file_path = os.path.join(output_files_folder, "directory.actual.hpp")
        actual_source_file_path = os.path.join(output_files_folder, "directory.actual.cpp")
        actual_python_file_path = os.path.join(output_files_folder, "directory.actual.py")
        golden_header_file_path = os.path.join(output_files_folder, "directory.golden.hpp")
        golden_source_file_path = os.path.join(output_files_folder, "directory.golden.cpp")
        golden_python_file_path = os.path.join(output_files_folder, "directory.golden.py")

        self.run(f"tree-gen {tree_file_path} {actual_header_file_path} {actual_source_file_path} {actual_python_file_path}")

        header_cmp_result = filecmp.cmp(actual_header_file_path, golden_header_file_path, shallow=False)
        source_cmp_result = filecmp.cmp(actual_source_file_path, golden_source_file_path, shallow=False)
        python_cmp_result = filecmp.cmp(actual_python_file_path, golden_python_file_path, shallow=False)
        if not header_cmp_result:
            self.output.error(f"Error: header files '{actual_header_file_path}' and '{golden_header_file_path}' differ")
            return False
        if not source_cmp_result:
            self.output.error(f"Error: source files '{actual_source_file_path}' and '{golden_source_file_path}' differ")
            return False
        if not python_cmp_result:
            self.output.error(f"Error: python files '{actual_python_file_path}' and '{golden_python_file_path}' differ")
            return False
        self.output.error(f"Success: output header, source, and python files at '{output_files_folder}' are OK")
        return True
