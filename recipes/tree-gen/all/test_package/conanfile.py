import filecmp
import os

from conan import ConanFile
# from conan.tools.build import cross_building


class TreeGenTestConan(ConanFile):
    settings = "os", "compiler", "build_type", "arch"
    generators = "VirtualBuildEnv"
    test_type = "explicit"

    def build_requirements(self):
        self.tool_requires(self.tested_reference_str)

    def test_tree_gen_executable(self):
        tree_file_path = os.path.abspath("./directory.tree")
        actual_header_file_path = os.path.abspath("./directory.actual.hpp")
        actual_source_file_path = os.path.abspath("./directory.actual.cpp")
        actual_python_file_path = os.path.abspath("./directory.actual.py")
        golden_header_file_path = os.path.abspath("./directory.golden.hpp")
        golden_source_file_path = os.path.abspath("./directory.golden.cpp")
        golden_python_file_path = os.path.abspath("./directory.golden.py")

        self.run("tree-gen {} {} {} {}".format(
            tree_file_path,
            actual_header_file_path,
            actual_source_file_path,
            actual_python_file_path))

        header_cmp_result = filecmp.cmp(actual_header_file_path, golden_header_file_path, shallow=False)
        source_cmp_result = filecmp.cmp(actual_source_file_path, golden_source_file_path, shallow=False)
        python_cmp_result = filecmp.cmp(actual_python_file_path, golden_python_file_path, shallow=False)
        if not header_cmp_result:
            print("Error: header files '{}' and '{}' differ".format(actual_header_file_path, actual_source_file_path))
            return False
        if not source_cmp_result:
            print("Error: source files '{}' and '{}' differ".format(actual_header_file_path, actual_source_file_path))
            return False
        if not python_cmp_result:
            print("Error: python files '{}' and '{}' differ".format(actual_python_file_path, actual_python_file_path))
            return False
        print("Success: output header, source, and python files at '{}' are OK".format(os.getcwd()))
        return True

    # def test_tree_gen_library(self):
    #     if not cross_building(self):
    #         bin_path = os.path.join(self.cpp.build.bindir, "example")
    #         self.run(bin_path, env="conanrun")
    
    def test(self):
        self.test_tree_gen_executable()
        # self.test_tree_gen_library()
