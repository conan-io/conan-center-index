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
        actual_header_file_path = os.path.abspath("./cqasm-functions-gen.actual.hpp")
        actual_source_file_path = os.path.abspath("./cqasm-functions-gen.actual.cpp")
        golden_header_file_path = os.path.abspath("./cqasm-functions-gen.golden.hpp")
        golden_source_file_path = os.path.abspath("./cqasm-functions-gen.golden.cpp")

        self.run("func-gen {} {} v1x".format(actual_header_file_path, actual_source_file_path))

        header_cmp_result = filecmp.cmp(actual_header_file_path, golden_header_file_path, shallow=False)
        source_cmp_result = filecmp.cmp(actual_source_file_path, golden_source_file_path, shallow=False)
        if not header_cmp_result:
            print("Error: header files '{}' and '{}' differ".format(actual_header_file_path, actual_source_file_path))
            return False
        if not source_cmp_result:
            print("Error: source files '{}' and '{}' differ".format(actual_header_file_path, actual_source_file_path))
            return False
        print("Success: output header and source files at '{}' are OK".format(os.getcwd()))
        return True
