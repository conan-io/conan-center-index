from conan import ConanFile
from conan.tools.files import copy, get, rmdir
from conan.tools.build import check_min_cppstd
from conan.tools.apple import fix_apple_shared_install_name
from conan.tools.cmake import CMake, CMakeToolchain, CMakeDeps, cmake_layout
import os


required_conan_version = ">=2.4"


class bgfxConan(ConanFile):
    name = "bgfx"
    license = "BSD-2-Clause"
    homepage = "https://github.com/bkaradzic/bgfx"
    url = "https://github.com/conan-io/conan-center-index"
    description = "Cross-platform rendering library"
    topics = ("rendering", "graphics", "gamedev")
    package_type = "static-library"
    settings = "os", "compiler", "arch", "build_type"
    options = {"fPIC": [True, False], "tools": [True, False]}
    default_options = {"fPIC": True, "tools": False}
    implements = ["auto_shared_fpic"]
    languages = "C++"
    
    @property
    def _tools(self):
        return ["texturec", "texturev", "geometryc", "geometryv", "shaderc"]

    def layout(self):
        cmake_layout(self, src_folder="src")

    def validate(self):
        check_min_cppstd(self, 17)

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.cache_variables["BGFX_LIBRARY_TYPE"] = "STATIC"
        tc.cache_variables["BGFX_BUILD_EXAMPLES"] = False
        tc.cache_variables["BGFX_BUILD_EXAMPLE_COMMON"] = False
        tc.cache_variables["BGFX_BUILD_TESTS"] = False
        tc.cache_variables["BGFX_INSTALL"] = True
        tc.cache_variables["BGFX_BUILD_TOOLS"] = self.options.tools
        tc.cache_variables["BX_AMALGAMATED"] = True
        tc.cache_variables["BGFX_AMALGAMATED"] = True
        tc.cache_variables["BGFX_OPENGLES_VERSION"] = 30
        tc.generate()
        deps = CMakeDeps(self)
        deps.generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, pattern="LICENSE", dst=os.path.join(self.package_folder, "licenses"), src=self.source_folder)
        cmake = CMake(self)
        cmake.install()

        rmdir(self, os.path.join(self.package_folder, "share"))
        fix_apple_shared_install_name(self)

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "bgfx")
        
        self.cpp_info.components["bx"].set_property("cmake_target_name", "bgfx::bx")
        self.cpp_info.components["bx"].libs = ["bx"]
        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.components["bx"].system_libs = ["dl", "rt"]
            self.cpp_info.includedirs.append(os.path.join("include", "bx", "compat", "linux"))
        self.cpp_info.components["bx"].defines = [f"BX_CONFIG_DEBUG={1 if self.settings.build_type == 'Debug' else 0}"]

        self.cpp_info.components["bimg"].set_property("cmake_target_name", "bgfx::bimg")
        self.cpp_info.components["bimg"].libs = ["bimg"]
        self.cpp_info.components["bimg"].requires = ["bx"]
    
        self.cpp_info.components["bimg_decode"].set_property("cmake_target_name", "bgfx::bimg_decode")
        self.cpp_info.components["bimg_decode"].libs = ["bimg_decode"]
        self.cpp_info.components["bimg_decode"].requires = ["bx"]

        self.cpp_info.components["bimg_encode"].set_property("cmake_target_name", "bgfx::bimg_encode")
        self.cpp_info.components["bimg_encode"].libs = ["bimg_encode"]
        self.cpp_info.components["bimg_encode"].requires = ["bx"]

        self.cpp_info.components["bgfx"].set_property("cmake_target_name", "bgfx::bgfx")
        self.cpp_info.components["bgfx"].libs = ["bgfx"]
        self.cpp_info.components["bimg_encode"].requires = ["bx", "bimg"]
        # multithreaded rendering is enabled by default via BGFX_CONFIG_MULTITHREADED
        self.cpp_info.components["bgfx"].defines = ["BGFX_CONFIG_MULTITHREADED=1"]
