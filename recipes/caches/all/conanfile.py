from conan import ConanFile
from conan.tools.files import copy
from conan.tools.scons import SConsDeps

required_conan_version = ">=2.0.0"


class CachesConan(ConanFile):
    name = "caches"
    description = "Extensible cache templates."

    version = "0.3.1"
    license = "MIT"

    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/JoelLefkowitz/caches"

    topics = (
        "cache",
        "fifo",
        "lifo",
        "lru",
    )

    def package_id(self):
        self.info.clear()

    def package_info(self):
        self.cpp_info.libs = []

    def build_requirements(self):
        self.test_requires("gtest/1.12.1")

    def export_sources(self):
        for source in [
            "conanfile.py",
            "LICENSE.md",
            "SConstruct.py",
            "src/*.[cht]pp",
        ]:
            copy(
                self,
                source,
                self.recipe_folder,
                self.export_sources_folder,
            )

    def generate(self):
        SConsDeps(self).generate()

    def package(self):
        copy(
            self,
            "LICENSE.md",
            f"{self.build_folder}",
            f"{self.package_folder}/licenses",
        )
        copy(
            self,
            "*.[ht]pp",
            f"{self.build_folder}/src",
            f"{self.package_folder}/include/{self.name}",
        )
