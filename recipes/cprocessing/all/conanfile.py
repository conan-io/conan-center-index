import os
import re

from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.build import check_min_cppstd
from conan.tools.files import copy, get, load, replace_in_file, save
from conan.tools.layout import basic_layout
from conan.tools.scm import Version

required_conan_version = ">=1.52.0"


class CProcessingConan(ConanFile):
    name = "cprocessing"
    description = "Processing programming for C++ "
    license = "MIT"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/maksmakuta/CProcessing"
    topics = ("processing", "opengl", "sketch", "header-only")
    package_type = "header-library"
    settings = "os", "arch", "compiler", "build_type"

    @property
    def _min_cppstd(self):
        return 20

    @property
    def _compilers_minimum_version(self):
        return {
            "gcc": "9",
            "Visual Studio": "16.2",
            "msvc": "192",
            "clang": "10",
            "apple-clang": "11",
        }

    def layout(self):
        basic_layout(self, src_folder="src")

    def requirements(self):
        self.requires("glfw/3.3.8")
        self.requires("glm/0.9.9.8")
        self.requires("glew/2.2.0")
        self.requires("stb/cci.20220909")
        self.requires("opengl/system")

    def package_id(self):
        self.info.clear()

    def validate(self):
        if self.settings.compiler.get_safe("cppstd"):
            check_min_cppstd(self, self._min_cppstd)
        minimum_version = self._compilers_minimum_version.get(str(self.settings.compiler), False)
        if minimum_version and Version(self.settings.compiler.version) < minimum_version:
            raise ConanInvalidConfiguration(
                f"{self.ref} requires some C++{self._min_cppstd} features, which your compiler does not support."
            )

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def build(self):
        replace_in_file(self, os.path.join(self.source_folder, "lib", "PImage.h"), "stb/stb_image.h", "stb_image.h")

    def _extract_license(self):
        # Extract the License/s from README.md to a file
        tmp = load(self, os.path.join(self.source_folder, "README.md"))
        license_contents = re.search("(## Author.*)", tmp, re.DOTALL)[1]
        save(self, os.path.join(self.package_folder, "licenses", "LICENSE.md"), license_contents)

    def package(self):
        self._extract_license()
        copy(self, "*.h",
             dst=os.path.join(self.package_folder, "include"),
             src=os.path.join(self.source_folder, "lib"))

    def package_info(self):
        self.cpp_info.bindirs = []
        self.cpp_info.libdirs = []
