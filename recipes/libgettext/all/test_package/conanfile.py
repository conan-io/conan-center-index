from conan import ConanFile
from conan.tools.build import can_run
from conan.tools.env import Environment, VirtualRunEnv
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
from conan.tools.files import copy, rename

import os


class TestPackageConan(ConanFile):
    settings = "os", "arch", "compiler", "build_type"
    test_type = "explicit"

    def requirements(self):
        self.requires(self.tested_reference_str)

    def layout(self):
        cmake_layout(self)

    def generate(self):
        CMakeDeps(self).generate()
        CMakeToolchain(self).generate()
        for locale, lang in [("en", "en_US"), ("ru", "ru_RU"), ("es", "es_ES")]:
            env = Environment()
            env.define("LANG", lang)
            env.vars(self, scope=f"run_{locale}").save_script(f"locale_{locale}")

            VirtualRunEnv(self).generate(scope=f"run_{locale}")

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()
        for locale in ["en", "ru", "es"]:
            directory = os.path.join(self.source_folder, locale, "LC_MESSAGES")
            if not os.path.isdir(directory):
                os.makedirs(directory)
            po_folder = os.path.join(self.source_folder, "po", locale)
            dest_folder = os.path.join(self.source_folder, locale, "LC_MESSAGES")
            copy(self, "conan.mo.workaround_git_ignore", po_folder, dest_folder)
            mo_file = os.path.join(dest_folder, "conan.mo")
            if not os.path.exists(mo_file):
                rename(self, os.path.join(dest_folder, "conan.mo.workaround_git_ignore"), mo_file)

    def test(self):
        if can_run(self):
            bin_path = os.path.join(self.cpp.build.bindirs[0], "test_package")
            for locale in ["en", "ru", "es"]:
                self.run(f"{bin_path} {os.path.abspath(self.source_folder)}", env=f"conanrun_{locale}")
