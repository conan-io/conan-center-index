from conans import ConanFile, CMake, tools
from conan.tools.files import copy, rename
import os
import shutil


class TestPackageConan(ConanFile):
    settings = "os", "arch", "compiler", "build_type"
    generators = "cmake", "cmake_find_package_multi"

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()
        for locale in ["en", "ru", "es"]:
            directory = os.path.join(self.source_folder, locale, "LC_MESSAGES")
            if not os.path.isdir(directory):
                os.makedirs(directory)
            po_folder = os.path.join(self.source_folder, "..", "test_package", "po", locale)
            dest_folder = os.path.join(self.source_folder, locale, "LC_MESSAGES")
            copy(self, "conan.mo.workaround_git_ignore", po_folder, dest_folder)
            mo_file = os.path.join(dest_folder, "conan.mo")
            if not os.path.exists(mo_file):
                rename(self, os.path.join(dest_folder, "conan.mo.workaround_git_ignore"), mo_file)

    def test(self):
        if not tools.cross_building(self):
            bin_path = os.path.join("bin", "test_package")
            for locale in ["en_US", "ru_RU", "es_ES"]:
                with tools.environment_append({"LANG": locale}):
                    self.run(f"{bin_path} {os.path.abspath(self.source_folder)}", run_environment=True)
