from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.build import check_min_cppstd
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
from conan.tools.files import apply_conandata_patches, copy, export_conandata_patches, get, rmdir
from conan.tools.scm import Version
import os

required_conan_version = ">=1.53.0"


class BackwardCppConan(ConanFile):
    name = "backward-cpp"
    description = "A beautiful stack trace pretty printer for C++"
    homepage = "https://github.com/bombela/backward-cpp"
    url = "https://github.com/conan-io/conan-center-index"
    topics = ("backward-cpp", "stack-trace")
    license = "MIT"

    package_type = "library"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "stack_walking": ["unwind", "libunwind", "backtrace"],
        "stack_details": ["dw", "bfd", "dwarf", "backtrace_symbol"],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "stack_walking": "unwind",
        "stack_details": "dwarf",
    }

    @property
    def _supported_os(self):
        supported_os = ["Linux", "Macos", "Android"]
        if Version(self.version) >= "1.5":
            supported_os.append("Windows")
        return supported_os

    def _has_stack_walking(self, type):
        return self.options.stack_walking == type

    def _has_stack_details(self, type):
        return False if self.settings.os == "Windows" else self.options.stack_details == type

    def export_sources(self):
        export_conandata_patches(self)

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC
            del self.options.stack_details
        # default option
        if self.settings.os == "Macos":
            self.options.stack_details = "backtrace_symbol"

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")

    def layout(self):
        cmake_layout(self, src_folder="src")

    def requirements(self):
        if self.settings.os in ["Linux", "Android"]:
            if self._has_stack_walking("libunwind"):
                self.requires("libunwind/1.6.2")
            if self._has_stack_details("dwarf"):
                self.requires("libdwarf/20191104", transitive_headers=True, transitive_libs=True)
                self.requires("libelf/0.8.13")
            if self._has_stack_details("dw"):
                self.requires("elfutils/0.186", transitive_headers=True, transitive_libs=True)
            if self._has_stack_details("bfd"):
                self.requires("binutils/2.38", transitive_headers=True, transitive_libs=True)

    def validate(self):
        if self.settings.os not in self._supported_os:
            raise ConanInvalidConfiguration(f"{self.ref} is not supported on {self.settings.os}.")
        if self.settings.compiler.get_safe("cppstd"):
            check_min_cppstd(self, 11)
        if self._has_stack_walking("libunwind"):
            if Version(self.version) < "1.6":
                raise ConanInvalidConfiguration("Support for libunwind is only available as of 1.6.")
            if self.settings.os == "Windows":
                raise ConanInvalidConfiguration("Support for libunwind is only available on Linux and macOS.")
        if self.settings.os == "Macos":
            if self.settings.arch == "armv8" and Version(self.version) < "1.6":
                raise ConanInvalidConfiguration("Support for Apple Silicon is only available as of 1.6.")
            if not self._has_stack_details("backtrace_symbol"):
                raise ConanInvalidConfiguration("Stack details other than backtrace_symbol are not supported on macOS.")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.variables["STACK_WALKING_UNWIND"] = self._has_stack_walking("unwind")
        tc.variables["STACK_WALKING_LIBUNWIND"] = self._has_stack_walking("libunwind")
        tc.variables["STACK_WALKING_BACKTRACE"] = self._has_stack_walking("backtrace")
        tc.variables["STACK_DETAILS_AUTO_DETECT"] = False
        tc.variables["STACK_DETAILS_BACKTRACE_SYMBOL"] = self._has_stack_details("backtrace_symbol")
        tc.variables["STACK_DETAILS_DW"] = self._has_stack_details("dw")
        tc.variables["STACK_DETAILS_BFD"] = self._has_stack_details("bfd")
        tc.variables["STACK_DETAILS_DWARF"] = self._has_stack_details("dwarf")
        tc.variables["BACKWARD_SHARED"] = self.options.shared
        tc.variables["BACKWARD_TESTS"] = False
        tc.variables["CMAKE_WINDOWS_EXPORT_ALL_SYMBOLS"] = True
        tc.generate()
        deps = CMakeDeps(self)
        deps.generate()

    def build(self):
        apply_conandata_patches(self)
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, "LICENSE*", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        cmake = CMake(self)
        cmake.install()
        rmdir(self, os.path.join(self.package_folder, "lib", "backward"))

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "Backward")
        self.cpp_info.set_property("cmake_target_name", "Backward::Backward")

        self.cpp_info.defines.append(f"BACKWARD_HAS_UNWIND={int(self._has_stack_walking('unwind'))}")
        self.cpp_info.defines.append(f"BACKWARD_HAS_LIBUNWIND={int(self._has_stack_walking('libunwind'))}")
        self.cpp_info.defines.append(f"BACKWARD_HAS_BACKTRACE={int(self._has_stack_walking('backtrace'))}")

        self.cpp_info.defines.append(f"BACKWARD_HAS_BACKTRACE_SYMBOL={int(self._has_stack_details('backtrace_symbol'))}")
        self.cpp_info.defines.append(f"BACKWARD_HAS_DW={int(self._has_stack_details('dw'))}")
        self.cpp_info.defines.append(f"BACKWARD_HAS_BFD={int(self._has_stack_details('bfd'))}")
        self.cpp_info.defines.append(f"BACKWARD_HAS_DWARF={int(self._has_stack_details('dwarf'))}")
        self.cpp_info.defines.append(f"BACKWARD_HAS_PDB_SYMBOL={int(self.settings.os == 'Windows')}")

        self.cpp_info.libs = ["backward"]
        if self.settings.os == "Linux":
            self.cpp_info.system_libs.extend(["dl"])
        if self.settings.os == "Windows":
            self.cpp_info.system_libs.extend(["psapi", "dbghelp"])

        # TODO: to remove in conan v2 once cmake_find_package* generators removed
        self.cpp_info.names["cmake_find_package"] = "Backward"
        self.cpp_info.names["cmake_find_package_multi"] = "Backward"
