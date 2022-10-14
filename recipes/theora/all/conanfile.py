from conan import ConanFile
from conan.tools.cmake import CMakeToolchain, CMake, CMakeDeps, cmake_layout
from conan.tools.files import chdir, copy, download, get, rename, replace_in_file, rm, rmdir
from conan.tools.microsoft import is_msvc
import os

required_conan_version = ">=1.52.0"

class TheoraConan(ConanFile):
    name = "theora"
    license = "BSD-3-Clause"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/xiph/theora"
    description = "Theora is a free and open video compression format from the Xiph.org Foundation"
    topics = ("theora", "video", "video-compressor", "video-format")

    settings = "os", "compiler", "build_type", "arch"
    options = {"shared": [True, False], "fPIC": [True, False]}
    default_options = {"shared": False, "fPIC": True}

    # Sources are located in the same place as this recipe, copy them to the recipe
    exports_sources = "CMakeLists.txt"

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            del self.options.fPIC
        self.settings.rm_safe("compiler.libcxx")
        self.settings.rm_safe("compiler.cppstd")

    def layout(self):
        cmake_layout(self)

    def requirements(self):
        self.requires("ogg/1.3.5")

    def source(self):
        get(self, **self.conan_data["sources"][self.version][0], strip_root=True)

        def_file = self.conan_data["sources"][self.version][1]
        url = def_file["url"]
        filename = url[url.rfind("/") + 1:]
        download(self, **def_file, filename=os.path.join(self.source_folder, "lib", filename))

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
        self.cpp_info.set_property("cmake_file_name", "theora")
        self.cpp_info.set_property("cmake_target_name", "theora::theora")
        self.cpp_info.set_property("pkg_config_name", "theora")

        self.cpp_info.components["theora"].libs = ["theora"]
        self.cpp_info.components["theoraenc"].libs = ["theoraenc"]
        self.cpp_info.components["theoradec"].libs = ["theoradec"]

        self.cpp_info.components["theora"].requires = ["ogg::ogg"]
        self.cpp_info.components["theoraenc"].requires = ["ogg::ogg"]
        self.cpp_info.components["theoradec"].requires = ["ogg::ogg"]
