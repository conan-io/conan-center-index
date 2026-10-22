from conan import ConanFile
from conan.tools.build import check_min_cppstd
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
from conan.tools.gnu import PkgConfigDeps
from conan.tools.files import copy, get, rm, rmdir, replace_in_file
import os


required_conan_version = ">=2.4"


class NotCursesConan(ConanFile):
    name = "notcurses"
    description = "blingful character graphics/TUI library. definitely not curses"
    license = "Apache-2.0"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://notcurses.com/"
    topics = ("tui", "ncurses", "terminal")
    package_type = "library"
    settings = "os", "arch", "compiler", "build_type"
    options = {"shared": [True, False], "fPIC": [True, False]}
    default_options = {"shared": False, "fPIC": True}
    implements = ["auto_shared_fpic"]

    def layout(self):
        cmake_layout(self, src_folder="src")

    def requirements(self):
        self.requires("ncurses/6.5")
        self.requires("libunistring/1.1")
        self.requires("zlib/[>=1.2.11 <2]")
        self.requires("ffmpeg/[>=6.0 <8]")

    def validate(self):
        check_min_cppstd(self, 17)

    def build_requirements(self):
        self.tool_requires("cmake/[>=3.21]")
        if not self.conf.get("tools.gnu:pkg_config", default=False, check_type=str):
            # INFO: ncurses is detected via pkg-config
            self.tool_requires("pkgconf/[>=2.1.0 <3]")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)
        replace_in_file(self, os.path.join(self.source_folder, "CMakeLists.txt"), "set(CMAKE_CXX_STANDARD 17)", "")
        replace_in_file(self, os.path.join(self.source_folder, "CMakeLists.txt"), "-fPIC", "")

    def generate(self):
        tc = CMakeToolchain(self)
        tc.cache_variables["USE_PANDOC"] = False
        tc.cache_variables["BUILD_TESTING"] = False
        tc.cache_variables["BUILD_EXECUTABLES"] = False
        tc.cache_variables["USE_POC"] = False
        tc.cache_variables["USE_STATIC"] = not self.options.shared
        tc.cache_variables["USE_MULTIMEDIA"] = "ffmpeg"
        tc.cache_variables["USE_DEFLATE"] = False
        tc.cache_variables["BUILD_FFI_LIBRARY"] = False
        tc.generate()

        deps = CMakeDeps(self)
        deps.generate()
        deps = PkgConfigDeps(self)
        deps.generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, "COPYRIGHT", self.source_folder, os.path.join(self.package_folder, "licenses"))
        cmake = CMake(self)
        cmake.install()
        rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))
        rmdir(self, os.path.join(self.package_folder, "lib", "cmake"))
        rmdir(self, os.path.join(self.package_folder, "share"))
        if not self.options.shared:
            rm(self, "*.dylib", os.path.join(self.package_folder, "lib"), recursive=True)
            rm(self, "*.so", os.path.join(self.package_folder, "lib"), recursive=True)
            rm(self, "*.dll", os.path.join(self.package_folder, "bin"), recursive=True)
            rm(self, "*.dll.a", os.path.join(self.package_folder, "lib"), recursive=True)

    def package_info(self):
        self.cpp_info.components["core"].libs = ["notcurses-core"]
        self.cpp_info.components["core"].set_property("pkg_config_name", "notcurses-core")
        self.cpp_info.components["core"].set_property("cmake_file_name", "NotcursesCore")
        self.cpp_info.components["core"].requires = ["ncurses::ncurses", "libunistring::libunistring", "zlib::zlib", "ffmpeg::avcodec", "ffmpeg::avdevice", "ffmpeg::avformat", "ffmpeg::avutil", "ffmpeg::swscale"]
        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.components["core"].system_libs = ["pthread", "m"]
        elif self.settings.os == "Windows":
            self.cpp_info.components["core"].system_libs = ["secur32"]

        self.cpp_info.components["libnotcurses"].libs = ["notcurses"]
        self.cpp_info.components["libnotcurses"].set_property("pkg_config_name", "notcurses")
        self.cpp_info.components["libnotcurses"].set_property("cmake_file_name", "Notcurses")
        self.cpp_info.components["libnotcurses"].requires = ["core"]

        self.cpp_info.components["notcursespp"].libs = ["notcurses++"]
        self.cpp_info.components["notcursespp"].set_property("pkg_config_name", "notcurses++")
        self.cpp_info.components["notcursespp"].set_property("cmake_file_name", "Notcurses++")
        self.cpp_info.components["notcursespp"].requires = ["libnotcurses"]
