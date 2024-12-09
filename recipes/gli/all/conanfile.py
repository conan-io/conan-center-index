from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.files import copy, get, load, save
from conan.tools.layout import basic_layout
from conan.tools.build import check_min_cppstd
from conan.tools.scm import Version
import os

required_conan_version = ">=1.52.0"


class GliConan(ConanFile):
    name = "gli"
    description = "OpenGL Image (GLI)"
    topics = ("opengl", "image")
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/g-truc/gli"
    license = "LicenseRef-copying.txt"
    package_type = "header-library"
    settings = "os", "arch", "compiler", "build_type"
    no_copy_source = True

    @property
    def _min_cppstd(self):
        return 11

    @property
    def _compilers_minimum_version(self):
        return {
            "gcc": "4.7",
            "clang": "3.4",
            "apple-clang": "6",
            "Visual Studio": "12",
            "msvc": "180",
        }

    def layout(self):
        basic_layout(self, src_folder="src")

    def requirements(self):
        self.requires("glm/1.0.1")

    def package_id(self):
        self.info.clear()

    def validate(self):
        if self.settings.compiler.cppstd:
            check_min_cppstd(self, self._min_cppstd)

        minimum_version = self._compilers_minimum_version.get(str(self.settings.compiler), False)
        if minimum_version and Version(self.settings.compiler.version) < minimum_version:
            raise ConanInvalidConfiguration(
                f"{self.ref} requires C++{self._min_cppstd}, which your compiler does not support."
            )

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def build(self):
        pass

    def package(self):
        save(self, os.path.join(self.package_folder, "licenses", "copying.txt"), self._get_license())
        for headers in ("*.hpp", "*.inl", "*.h"):
            copy(self, headers, src=os.path.join(self.source_folder, "gli"),
                                dst=os.path.join(self.package_folder, "include", "gli"))

    def _get_license(self):
        manual = load(self, os.path.join(self.source_folder, "manual.md"))
        begin = manual.find("### The Happy Bunny License (Modified MIT License)")
        end = manual.find("\n![](https://github.com/g-truc/glm/blob/manual/doc/manual/frontpage2.png)", begin)
        return manual[begin:end]

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "gli")
        self.cpp_info.set_property("cmake_target_name", "gli")
        self.cpp_info.bindirs = []
        self.cpp_info.libdirs = []
