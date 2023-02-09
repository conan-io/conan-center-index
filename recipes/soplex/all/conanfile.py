from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.apple import fix_apple_shared_install_name
from conan.tools.build import check_min_cppstd
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
from conan.tools.files import get, replace_in_file
from conan.tools.microsoft import check_min_vs, is_msvc, is_msvc_static_runtime
from conan.tools.scm import Version

required_conan_version = ">=1.53.0"


class SoPlexConan(ConanFile):
    name = "soplex"
    description = "SoPlex linear programming solver"
    license = "Apache-2.0"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://soplex.zib.de"
    topics = ("soplex", "simplex", "solver", "linear", "programming")
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "BOOST": [True, False],
        "GMP": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "BOOST": False,
        "GMP": False
    }

    @property
    def _min_cppstd(self):
        return 14

    @property
    def _compilers_minimum_version(self):
        return {
            "gcc": "5",
            "clang": "4",
            "apple-clang": "7",
        }

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)
        replace_in_file(self, "CMakeLists.txt", "GMP_INCLUDE_DIRS", "gmp_INCLUDE_DIRS")
        replace_in_file(self, "CMakeLists.txt", "GMP_LIBRARIES", "gmp_LIBRARIES")

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")

    def requirements(self):
        self.requires("zlib/1.2.13")
        if self.options.GMP:
            self.requires("gmp/6.2.1")
        if self.options.BOOST:
            self.requires("boost/1.81.0")  # also update Boost_VERSION_MACRO below!

    def layout(self):
        cmake_layout(self, src_folder="src")

    def generate(self):
        tc = CMakeToolchain(self)
        tc.variables["GMP"] = self.options.GMP
        tc.variables["BOOST"] = self.options.BOOST
        tc.variables["Boost_VERSION_MACRO"] = "108100"
        if is_msvc(self):
            tc.variables["MT"] = is_msvc_static_runtime(self)
        tc.generate()
        tc = CMakeDeps(self)
        tc.generate()

    def _determine_lib_name(self):
        if self.options.shared:
            return "soplexshared"
        elif self.options.get_safe("fPIC"):
            return "soplex-pic"
        else:
            return "soplex"

    def validate(self):
        if self.settings.compiler.cppstd:
            check_min_cppstd(self, self._min_cppstd)
        check_min_vs(self, 191)
        if not is_msvc(self):
            minimum_version = self._compilers_minimum_version.get(str(self.settings.compiler), False)
            if minimum_version and Version(self.settings.compiler.version) < minimum_version:
                raise ConanInvalidConfiguration(
                    f"{self.ref} requires C++{self._min_cppstd}, which your compiler does not support."
                )

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build(target=f"lib{self._determine_lib_name()}")

    def package(self):
        self.copy(pattern="LICENSE", dst="licenses")
        self.copy(pattern="src/soplex.h", dst="include", keep_path=False)
        self.copy(pattern="src/soplex.hpp", dst="include", keep_path=False)
        self.copy(pattern="src/soplex_interface.h", dst="include", keep_path=False)
        self.copy(pattern="src/soplex/*.h", dst="include/soplex", keep_path=False)
        self.copy(pattern="src/soplex/*.hpp", dst="include/soplex", keep_path=False)
        self.copy(pattern="soplex/*.h", dst="include/soplex", keep_path=False)
        if self.options.shared:
            self.copy(pattern="lib/*.so*", symlinks=True)
            self.copy(pattern="lib/*.dylib*", symlinks=True)
            self.copy(pattern="bin/*.dll", dst="lib", keep_path=False)
        else:
            self.copy(pattern="lib/*.a")
            self.copy(pattern="lib/*.lib", dst="lib", keep_path=False)
        fix_apple_shared_install_name(self)

    def package_info(self):
        self.cpp_info.libs = [self._determine_lib_name()]
        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.system_libs.append("m")
