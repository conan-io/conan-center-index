import os
import shutil
from conans import ConanFile, CMake, tools


class TestPackageConan(ConanFile):
    settings = "os", "compiler", "build_type", "arch"
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
        if not tools.cross_building(self.settings):
            self.output.info("Check working executables")
            for exe in ['gettext', 'ngettext', 'msgcat', 'msgmerge']:
                self.run("%s --version" % exe, run_environment=True)

            self.output.info("Check working library")
            bin_path = os.path.join("bin", "test_package")
            for locale in ["en_US", "ru_RU", "es_ES"]:
                with tools.environment_append({"LANG": locale}):
                    self.run("%s %s" % (bin_path, os.path.abspath(self.source_folder)), run_environment=True)
