import filecmp
import os

from conan import ConanFile


class FuncGenTestConan(ConanFile):
    settings = "os", "compiler", "build_type", "arch"
    generators = "VirtualBuildEnv"
    test_type = "explicit"

    def build_requirements(self):
        self.tool_requires(self.tested_reference_str)

    def test(self):
        output_files_folder = os.path.dirname(__file__)
        actual_header_file_path = os.path.join(output_files_folder, "cqasm-functions-gen.actual.hpp")
        actual_source_file_path = os.path.join(output_files_folder, "cqasm-functions-gen.actual.cpp")
        golden_header_file_path = os.path.join(output_files_folder, "cqasm-functions-gen.golden.hpp")
        golden_source_file_path = os.path.join(output_files_folder, "cqasm-functions-gen.golden.cpp")

        self.run(f"func-gen {actual_header_file_path} {actual_source_file_path} v1x")

        header_cmp_result = filecmp.cmp(actual_header_file_path, golden_header_file_path, shallow=False)
        source_cmp_result = filecmp.cmp(actual_source_file_path, golden_source_file_path, shallow=False)
        if not header_cmp_result:
            print(f"Error: header files '{actual_header_file_path}' and '{golden_header_file_path}' differ")
            return False
        if not source_cmp_result:
            print(f"Error: source files '{actual_source_file_path}' and '{golden_source_file_path}' differ")
            return False
        print(f"Success: output header and source files at '{output_files_folder}' are OK")
        return True
