import os
from conan import ConanFile
from conan.tools.build import check_min_cppstd
from conan.tools.cmake import CMake, CMakeToolchain, cmake_layout
from conan.tools.files import rmdir, get, copy
from conan.tools.microsoft import is_msvc
from conan.tools.scm import Version
from conan.errors import ConanInvalidConfiguration

required_conan_version = ">=1.53.0"

class AndreasbuhrCppCoroConan(ConanFile):
    name = "andreasbuhr-cppcoro"
    description = "A library of C++ coroutine abstractions for the coroutines TS"
    topics = ("cpp", "async", "coroutines")
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/andreasbuhr/cppcoro"
    license = "MIT"
    settings = "os", "compiler", "build_type", "arch"
    provides = "cppcoro"
    package_type = "library"

    options = {
        "shared": [True, False],
        "fPIC": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
    }

    @property
    def _minimum_compilers_version(self):
        return {
            "Visual Studio": "15",
            "msvc": "191",
            "gcc": "10",
            "clang": "8",
            "apple-clang": "10",
        }

    @property
    def _min_cppstd(self):
        # Clang with libstdc++ always requires C++20
        # Clang 17+ always requires C++20
        # Otherwise, require C++17
        compiler = self.settings.compiler
        requires_cpp20 = compiler == "clang" and ("libstdc++" in compiler.get_safe("libcxx", "") or compiler.version >= Version("17"))
        return 20 if requires_cpp20 else 17

    def layout(self):
        cmake_layout(self, src_folder="src")

    def config_options(self):
        if self.settings.os == "Windows":
            self.options.rm_safe("fPIC")

    def validate(self):
        if self.settings.compiler.cppstd:
            check_min_cppstd(self, self._min_cppstd)
        
        # We can't simply check for C++20, because clang and MSVC support the coroutine TS despite not having labeled (__cplusplus macro) C++20 support
        min_version = self._minimum_compilers_version.get(str(self.settings.compiler))
        if not min_version:
            self.output.warning(f"{self.name} recipe lacks information about the {self.settings.compiler} compiler support.")
        else:
            if Version(self.settings.compiler.version) < min_version:
                raise ConanInvalidConfiguration(
                    f"{self.name} requires coroutine TS support. The current compiler {self.settings.compiler} {self.settings.compiler.version} does not support it."
                )

        # Older versions of clang expects coroutine to be put under std::experimental::, while libstdc++ puts them under std::,
        # See https://bugs.llvm.org/show_bug.cgi?id=48172 for more context.
        if self.settings.compiler == "clang" and "libstdc++" in self.settings.compiler.get_safe("libcxx", ""):
            if self.settings.compiler.version < Version("14"):
                raise ConanInvalidConfiguration("{self.name} does not support clang<14 with libstdc++. Use libc++ or upgrade to clang 14+ instead.")
            if self.settings.compiler.version == Version("14"):
                self.output.warning("This build may fail if using libstdc++13 or greater")

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.variables["CMAKE_WINDOWS_EXPORT_ALL_SYMBOLS"] = "ON"
        tc.generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, "LICENSE.txt", dst=os.path.join(self.package_folder, "licenses"), src=self.source_folder)
        cmake = CMake(self)
        cmake.install()
        rmdir(self, os.path.join(self.package_folder, "lib", "cmake"))

    @property
    def _needs_fcoroutines_ts_flag(self):
        version = Version(self.settings.compiler.version)
        if self.settings.compiler == "clang":
            # clang 5: Coroutines support added
            # somewhere between clang 5 and 11: the requirement to add -fcoroutines-ts was dropped, at least in the context of this recipe.
            return version < 11
        elif self.settings.compiler == "apple-clang":
            # At some point before apple-clang 13, in the context of this recipe, the requirement for this flag was dropped.
            return version < 13
        else:
            return False

    def package_info(self):
        self.cpp_info.libs = ["cppcoro"]

        if self.settings.os in ["Linux", "FreeBSD"] and self.options.shared:
            self.cpp_info.system_libs = ["pthread", "m"]
        if self.settings.os == "Windows":
            self.cpp_info.system_libs = ["synchronization", "ws2_32", "mswsock"]

        if is_msvc(self):
            self.cpp_info.cxxflags.append("/await")
        elif self.settings.compiler == "gcc":
            self.cpp_info.cxxflags.append("-fcoroutines")
            self.cpp_info.defines.append("CPPCORO_COMPILER_SUPPORTS_SYMMETRIC_TRANSFER=1")
        elif self._needs_fcoroutines_ts_flag:
            self.cpp_info.cxxflags.append("-fcoroutines-ts")

        self.cpp_info.set_property("cmake_file_name", "cppcoro")
        self.cpp_info.set_property("cmake_target_name", "cppcoro::cppcoro")

        # TODO: to remove in conan v2 once cmake_find_package_* generators removed
        self.cpp_info.filenames["cmake_find_package"] = "cppcoro"
        self.cpp_info.filenames["cmake_find_package_multi"] = "cppcoro"
        self.cpp_info.names["cmake_find_package"] = "cppcoro"
        self.cpp_info.names["cmake_find_package_multi"] = "cppcoro"
