from conan import ConanFile
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
from conan.tools.files import collect_libs, get
from conan.tools.microsoft import is_msvc

required_conan_version = ">=1.53.0"


class HiGHSConan(ConanFile):
    name = "highs"
    description = "high performance serial and parallel solver for large scale sparse linear optimization problems"
    license = "MIT"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://www.highs.dev/"
    topics = ("highs", "simplex", "interior point", "solver", "linear", "programming")
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
    }

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")

    def requirements(self):
        self.requires("zlib/1.2.13")

    def layout(self):
        cmake_layout(self, src_folder="src")

    def generate(self):
        tc = CMakeToolchain(self)
        tc.variables["SHARED"] = self.options.shared
        tc.variables["BUILD_TESTING"] = False
        tc.variables["PYTHON"] = False
        tc.variables["FORTRAN"] = False
        tc.variables["CSHARP"] = False
        tc.generate()
        tc = CMakeDeps(self)
        tc.generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build(target="libhighs")

    def package(self):
        self.copy(pattern="LICENSE", dst="licenses")
        self.copy(pattern="*.h", dst="include", src="src")
        self.copy(pattern="HConfig.h", dst="include")
        # unix
        self.copy(pattern="lib/*.a")
        self.copy(pattern="lib/*.so*", symlinks=True)
        # mac
        self.copy(pattern="lib/*.dylib*", symlinks=True)
        # win
        self.copy(pattern="bin/*.dll", dst="lib", keep_path=False)
        self.copy(pattern="lib/*.lib", dst="lib", keep_path=False)

    def package_info(self):
        self.cpp_info.libs = collect_libs(self)
        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.system_libs.append("m")
            self.cpp_info.system_libs.append("pthread")
        if is_msvc(self):
            self.cpp_info.defines.append("_CRT_SECURE_NO_WARNINGS")
            self.cpp_info.defines.append("_ITERATOR_DEBUG_LEVEL=0")
