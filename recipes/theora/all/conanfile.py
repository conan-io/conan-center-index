from conan import ConanFile
from conan.tools.cmake import CMakeToolchain, CMake, CMakeDeps, cmake_layout
from conan.tools.files import copy, get
from conan.tools.microsoft import is_msvc
from conan.errors import ConanException
import os

required_conan_version = ">=1.52.0"

class TheoraConan(ConanFile):
    name = "theora"
    license = "BSD-3-Clause"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/xiph/theora"
    description = "Theora is a free and open video compression format from the Xiph.org Foundation"
    topics = "video", "video-compressor", "video-format"

    settings = "os", "compiler", "build_type", "arch"
    options = {"shared": [True, False], "fPIC": [True, False]}
    default_options = {"shared": False, "fPIC": True}

    # original theora.def from: "https://raw.githubusercontent.com/xiph/theora/v1.1.1/lib/theora.def"
    # edited to change library name to just "theora"
    def export_sources(self):
        copy(self, "CMakeLists.txt", self.recipe_folder, os.path.join(self.export_sources_folder,"src"))
        copy(self, "conan-theora.def", self.recipe_folder, os.path.join(self.export_sources_folder,"src"))

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            try:
                del self.options.fPIC
            except ConanException:
                pass
        try:
            del self.settings.compiler.libcxx
        except ConanException:
            pass
        try:
            del self.settings.compiler.cppstd
        except ConanException:
            pass

    def layout(self):
        cmake_layout(self, src_folder="src")

    def requirements(self):
        self.requires("ogg/1.3.5")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.variables["USE_X86_32"] = (self.settings.arch == "x86")
        # note: MSVC does not support inline assembly for 64 bit builds
        tc.variables["USE_X86_64"] = (self.settings.arch == "x86_64" and not is_msvc(self))
        tc.generate()
        cd = CMakeDeps(self)
        cd.generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, "COPYING", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        copy(self, "LICENSE", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        cmake = CMake(self)
        cmake.install()

    def package_info(self):
        self.cpp_info.set_property("pkg_config_name", "theora")

        self.cpp_info.components["theora"].libs = ["theora"]
        self.cpp_info.components["theora"].requires = ["ogg::ogg"]

        # theoraenc and theoradec libraries can be built, but are untested,
        # so if someonw wants to use them, then uncomment in CMakeLists.txt,
        # and in the recipe and in theory they'll work.
        # The original conan recipe only built the full theora library.
#
        # self.cpp_info.components["theoraenc"].libs = ["theoraenc"]
        # self.cpp_info.components["theoraenc"].requires = ["ogg::ogg"]
        # self.cpp_info.components["theoradec"].libs = ["theoradec"]
        # self.cpp_info.components["theoradec"].requires = ["ogg::ogg"]

        # TODO: to remove in conan v2 once cmake_find_package_* generators removed
        self.cpp_info.filenames["cmake_find_package"] = "theora"
        self.cpp_info.filenames["cmake_find_package_multi"] = "theora"
        self.cpp_info.names["cmake_find_package"] = "theora"
        self.cpp_info.names["cmake_find_package_multi"] = "theora"
