from conan import ConanFile, tools
from conans import CMake
import os
import shutil


class TestPackageConan(ConanFile):
    settings = "os", "arch", "compiler", "build_type"
    generators = "cmake", "cmake_find_package"

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()
        for locale in ["en", "ru", "es"]:
            directory = os.path.join(self.source_folder, locale, "LC_MESSAGES")
            if not os.path.isdir(directory):
                os.makedirs(directory)
            shutil.copy(os.path.join(self.source_folder, "po", locale, "conan.mo.workaround_git_ignore"),
                        os.path.join(self.source_folder, locale, "LC_MESSAGES", "conan.mo"))

    def test(self):
        if not tools.cross_building(self):
            bin_path = os.path.join("bin", "test_package")
            for locale in ["en_US", "ru_RU", "es_ES"]:
                with tools.environment_append({"LANG": locale}):
                    self.run("%s %s" % (bin_path, os.path.abspath(self.source_folder)), run_environment=True)

