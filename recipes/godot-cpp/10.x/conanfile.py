import os

from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.build import check_min_cppstd
from conan.tools.cmake import CMake, CMakeToolchain, cmake_layout
from conan.tools.files import copy, get, rename
from conan.tools.microsoft import is_msvc
from conan.tools.scm import Version

required_conan_version = ">=2.0.0"


class GodotCppConan(ConanFile):
    name = "godot-cpp"
    description = "C++ bindings for the Godot Engine's GDExtension API"
    license = "MIT"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/godotengine/godot-cpp"
    topics = ("godot", "game-engine", "gdextension", "bindings")
    package_type = "static-library"
    settings = "os", "arch", "compiler", "build_type"

    options = {
        "api_version": ["4.3", "4.4", "4.5", "4.6", "4.7"],
        "target": ["template_debug", "template_release", "editor"],
    }
    default_options = {
        "api_version": "4.7",
        "target": "template_debug",
    }

    def layout(self):
        cmake_layout(self, src_folder="src")

    def validate(self):
        if self.settings.os not in ("Windows", "Linux", "Macos", "iOS", "Android", "Emscripten"):
            raise ConanInvalidConfiguration(f"{self.ref} does not support {self.settings.os}")
        if self.settings.os == "Emscripten" and self.settings.arch != "wasm":
            raise ConanInvalidConfiguration(f"{self.ref} on Emscripten requires arch=wasm")
        if self.settings.os == "Android" and Version(str(self.settings.os.api_level)) < "24":
            raise ConanInvalidConfiguration(f"{self.ref} on Android requires os.api_level >= 24 (upstream minimum)")

        check_min_cppstd(self, 17)

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.cache_variables["GODOTCPP_API_VERSION"] = str(self.options.api_version)
        tc.cache_variables["GODOTCPP_TARGET"] = str(self.options.target)
        tc.generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, "LICENSE.md", self.source_folder, os.path.join(self.package_folder, "licenses"))
        copy(self, "*", os.path.join(self.source_folder, "include"),
             os.path.join(self.package_folder, "include"))
        copy(self, "*", os.path.join(self.build_folder, "gen", "include"),
             os.path.join(self.package_folder, "include"))

        lib_folder = os.path.join(self.package_folder, "lib")
        copy(self, "*.a", os.path.join(self.build_folder, "bin"), lib_folder, keep_path=False)
        copy(self, "*.lib", os.path.join(self.build_folder, "bin"), lib_folder, keep_path=False)

        # The built library carries a platform/target/arch suffix, drop it for a stable name
        for built_lib in os.listdir(lib_folder):
            ext = os.path.splitext(built_lib)[1]
            prefix = "" if ext == ".lib" else "lib"
            rename(self, os.path.join(lib_folder, built_lib),
                   os.path.join(lib_folder, f"{prefix}godot-cpp{ext}"))

    def package_info(self):
        self.cpp_info.libs = ["godot-cpp"]

        defines = ["GDEXTENSION", "THREADS_ENABLED"]

        if self.settings.os == "Windows":
            defines.append("WINDOWS_ENABLED")
        elif self.settings.os == "Linux":
            defines.extend(["LINUX_ENABLED", "UNIX_ENABLED"])
        elif self.settings.os == "Android":
            defines.extend(["ANDROID_ENABLED", "UNIX_ENABLED"])
        elif self.settings.os == "iOS":
            defines.extend(["IOS_ENABLED", "UNIX_ENABLED"])
        elif self.settings.os == "Emscripten":
            defines.extend(["WEB_ENABLED", "UNIX_ENABLED"])
        elif self.settings.os == "Macos":
            defines.extend(["MACOS_ENABLED", "UNIX_ENABLED"])

        if is_msvc(self):
            defines.extend(["TYPED_METHOD_BIND", "NOMINMAX", "_HAS_EXCEPTIONS=0"])
            self.cpp_info.cxxflags = ["/Zc:__cplusplus", "/utf-8"]

        if self.options.target != "template_release":
            defines.append("DEBUG_ENABLED")

        self.cpp_info.defines = defines

        if self.settings.os == "Emscripten":
            # Recreates the PUBLIC compile / link flags of upstream cmake/web.cmake
            # so consumer GDExtensions link as wasm side modules.
            self.cpp_info.cxxflags = ["-sSIDE_MODULE=1", "-sSUPPORT_LONGJMP=wasm", "-sUSE_PTHREADS=1"]
            web_linkflags = ["-sWASM_BIGINT", "-sSUPPORT_LONGJMP=wasm", "-sUSE_PTHREADS=1",
                             "-fvisibility=hidden"]
            self.cpp_info.sharedlinkflags = web_linkflags + ["-shared"]
            self.cpp_info.exelinkflags = web_linkflags

        self.cpp_info.set_property("cmake_target_name", "godot-cpp")
        self.cpp_info.set_property("cmake_target_aliases", ["godot::cpp"])
