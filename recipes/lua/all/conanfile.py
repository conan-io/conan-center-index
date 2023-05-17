import os

from conan import ConanFile
from conan.tools.cmake import CMake, CMakeToolchain, cmake_layout
from conan.tools.files import get, copy, load, save, export_conandata_patches, apply_conandata_patches, collect_libs
from conan.tools.apple import fix_apple_shared_install_name


required_conan_version = ">=1.53.0"


class LuaConan(ConanFile):
    name = "lua"
    package_type = "library"
    description = "Lua is a powerful, efficient, lightweight, embeddable scripting language."
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://www.lua.org/"
    topics = ("lua", "scripting")
    license = "MIT"

    settings = "os", "compiler", "arch", "build_type"
    options = {
        "shared": [False, True],
        "fPIC": [True, False],
        "compile_as_cpp": [True, False]
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "compile_as_cpp": False
    }

    def export_sources(self):
        copy(self, "CMakeLists.txt", src=self.recipe_folder, dst=self.export_sources_folder)
        export_conandata_patches(self)

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")
        if not self.options.compile_as_cpp:
            self.options.rm_safe("compiler.libcxx")
            self.options.rm_safe("compiler.cppstd")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], destination=self.source_folder, strip_root=True)

    def layout(self):
        cmake_layout(self, src_folder="src")

    def generate(self):
        tc = CMakeToolchain(self)
        tc.variables["LUA_SRC_DIR"] = self.source_folder.replace("\\", "/")
        tc.variables["SKIP_INSTALL_TOOLS"] = True
        tc.variables["COMPILE_AS_CPP"] = self.options.compile_as_cpp
        tc.generate()

    def build(self):
        apply_conandata_patches(self)
        cmake = CMake(self)
        cmake.configure(build_script_folder=os.path.join(self.source_folder, os.pardir))
        cmake.build()

    def package(self):
        # Extract the License/s from the header to a file
        tmp = load(self, os.path.join(self.source_folder, "src", "lua.h"))
        license_contents = tmp[tmp.find("/***", 1):tmp.find("****/", 1)]
        save(self, os.path.join(self.package_folder, "licenses", "COPYING.txt"), license_contents)
        cmake = CMake(self)
        cmake.install()
        fix_apple_shared_install_name(self)

    def package_info(self):
        self.cpp_info.libs = collect_libs(self)
        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.system_libs = ["dl", "m"]
        if self.settings.os in ["Linux", "FreeBSD", "Macos"]:
            self.cpp_info.defines.extend(["LUA_USE_DLOPEN", "LUA_USE_POSIX"])
        elif self.settings.os == "Windows" and self.options.shared:
            self.cpp_info.defines.append("LUA_BUILD_AS_DLL")
