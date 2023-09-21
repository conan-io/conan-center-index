import os

from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.build import check_min_cppstd
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
from conan.tools.files import collect_libs, copy, get, replace_in_file
from conan.tools.microsoft import check_min_vs
from conan.tools.scm import Version

required_conan_version = ">=1.53.0"


class STXConan(ConanFile):
    name = "stx"
    description = "C++17 & C++ 20 error-handling and utility extensions."
    license = "MIT"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/lamarrr/STX"
    topics = ("error-handling", "result", "option", "backtrace", "panic")

    package_type = "library"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "backtrace": [True, False],
        "panic_handler": [None, "default", "backtrace"],
        "visible_panic_hook": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "backtrace": False,
        "panic_handler": "default",
        "visible_panic_hook": False,
    }

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")

    def layout(self):
        cmake_layout(self, src_folder="src")

    def requirements(self):
        if self.options.backtrace:
            self.requires("abseil/20230125.3")

    def validate(self):
        if self.options.panic_handler == "backtrace" and not self.options.backtrace:
            raise ConanInvalidConfiguration("panic_handler=backtrace requires backtrace=True")

        compiler = self.settings.compiler
        compiler_version = Version(self.settings.compiler.version)

        if compiler.get_safe("cppstd"):
            check_min_cppstd(self, 17)

        check_min_vs(self, 192)

        if compiler == "gcc" and compiler_version < 8:
            raise ConanInvalidConfiguration(
                "STX requires C++17 language and standard library features which GCC < 8 lacks"
            )

        if (
            compiler == "clang"
            and compiler.libcxx
            and compiler.libcxx in ["libstdc++", "libstdc++11"]
            and compiler_version < 9
        ):
            raise ConanInvalidConfiguration(
                "STX requires C++17 language and standard library features which clang < 9 with libc++ lacks"
            )

        if compiler == "clang" and compiler.libcxx and compiler.libcxx == "libc++" and compiler_version < 10:
            raise ConanInvalidConfiguration(
                "STX requires C++17 language and standard library features which clang < 10 with libc++ lacks"
            )

        if compiler == "apple-clang" and compiler_version < 12:
            raise ConanInvalidConfiguration(
                "STX requires C++17 language and standard library features "
                "which apple-clang < 12 with libc++ lacks"
            )

        # if is_msvc(self) and self.options.shared and Version(self.version) <= "1.0.1":
        #     raise ConanInvalidConfiguration(
        #         "shared library build does not work on windows with STX version <= 1.0.1"
        #     )

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.cache_variables["STX_BUILD_SHARED"] = self.options.shared
        tc.cache_variables["STX_ENABLE_BACKTRACE"] = self.options.backtrace
        tc.cache_variables["STX_ENABLE_PANIC_BACKTRACE"] = self.options.panic_handler == "backtrace"
        tc.cache_variables["STX_OVERRIDE_PANIC_HANDLER"] = self.options.panic_handler == None
        tc.cache_variables["STX_VISIBLE_PANIC_HOOK"] = self.options.visible_panic_hook
        tc.cache_variables["CMAKE_WINDOWS_EXPORT_ALL_SYMBOLS"] = self.options.shared
        tc.generate()
        tc = CMakeDeps(self)
        tc.generate()

    def _patch_sources(self):
        # Let Conan control static/shared build
        replace_in_file(self, os.path.join(self.source_folder, "CMakeLists.txt"),
                        " STATIC ", " ")
        replace_in_file(self, os.path.join(self.source_folder, "cmake-modules", "add_project_library.cmake"),
                        " STATIC ", " ")

    def build(self):
        self._patch_sources()
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, "*.h",
            dst=os.path.join(self.package_folder, "include"),
            src=os.path.join(self.source_folder, "include"))
        for pattern in ["*.lib", "*.so", "*.dylib", "*.a"]:
            copy(self, pattern, dst=os.path.join(self.package_folder, "lib"), src=self.build_folder, keep_path=False)
        copy(self, "*.dll", dst=os.path.join(self.package_folder, "bin"), src=self.build_folder, keep_path=False)
        copy(self, "LICENSE", dst=os.path.join(self.package_folder, "licenses"), src=self.source_folder)

    def package_info(self):
        self.cpp_info.libs = collect_libs(self)

        if self.options.backtrace:
            self.cpp_info.requires = ["abseil::absl_stacktrace", "abseil::absl_symbolize"]

        if self.options.visible_panic_hook:
            self.cpp_info.defines.append("STX_VISIBLE_PANIC_HOOK")

        if self.options.panic_handler == None:
            self.cpp_info.defines.append("STX_OVERRIDE_PANIC_HANDLER")

        if self.options.panic_handler == "backtrace":
            self.cpp_info.defines.append("STX_ENABLE_PANIC_BACKTRACE")

        if self.settings.os == "Android":
            self.cpp_info.system_libs = ["atomic"]
