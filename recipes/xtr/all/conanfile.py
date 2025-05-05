import os

from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.build import check_min_cppstd
from conan.tools.cmake import CMakeToolchain, CMakeDeps, CMake
from conan.tools.files import copy, get, replace_in_file
from conan.tools.layout import basic_layout
from conan.tools.scm import Version

required_conan_version = ">=1.53.0"


class XtrConan(ConanFile):
    name = "xtr"
    description = "C++ Logging Library for Low-latency or Real-time Environments"
    license = "MIT"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/choll/xtr"
    topics = ("logging", "logger")

    package_type = "library"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "enable_exceptions": [True, False],
        "enable_lto": [True, False],
        "enable_io_uring": ["auto", True, False],
        "enable_io_uring_sqpoll": [True, False],
        "sink_capacity_kb": [None, "ANY"],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "enable_exceptions": True,
        "enable_lto": False,
        "enable_io_uring": "auto",
        "enable_io_uring_sqpoll": False,
        "sink_capacity_kb": None,
    }

    @property
    def _min_cppstd(self):
        return 20

    @property
    def _compilers_minimum_version(self):
        return {
            "gcc": "10",
            "clang": "12",
        }


    def config_options(self):
        if Version(self.version) >= "2.0.0" and self.settings.os == "Linux":
            # Require liburing on any Linux system by default as a run-time check will be
            # done to detect if the host kernel supports io_uring.
            self.options.enable_io_uring = True
        else:
            del self.options.enable_io_uring
            del self.options.enable_io_uring_sqpoll

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")

    def layout(self):
        basic_layout(self, src_folder="src")

    def requirements(self):
        # INFO: https://github.com/choll/xtr/blob/2.1.0/include/xtr/detail/buffer.hpp#L27
        self.requires("fmt/10.1.1", transitive_headers=True, transitive_libs=True)
        if self.options.get_safe("enable_io_uring"):
            self.requires("liburing/2.4")

    def validate(self):
        if self.settings.os not in ["FreeBSD", "Linux"]:
            raise ConanInvalidConfiguration(f"Unsupported os={self.settings.os}")
        if self.settings.arch not in ["x86_64"]:
            raise ConanInvalidConfiguration(f"Unsupported arch={self.settings.arch}")

        if self.settings.compiler.cppstd:
            check_min_cppstd(self, self._min_cppstd)
        minimum_version = self._compilers_minimum_version.get(str(self.settings.compiler), False)
        if minimum_version and Version(self.settings.compiler.version) < minimum_version:
            raise ConanInvalidConfiguration(f"{self.ref} requires C++{self._min_cppstd}, which your compiler does not support.")
        if Version(self.version) < "2.0.0" and str(self.settings.compiler.libcxx) == "libc++":
            raise ConanInvalidConfiguration("Use at least version 2.0.0 for libc++ compatibility")

        if self.options.get_safe("enable_io_uring_sqpoll") and not self.options.get_safe("enable_io_uring"):
            raise ConanInvalidConfiguration("io_uring must be enabled if io_uring_sqpoll is enabled")
        if self.options.get_safe("sink_capacity_kb") and not str(self.options.get_safe("sink_capacity_kb")).isdigit():
            raise ConanInvalidConfiguration("The option 'sink_capacity_kb' must be an integer")

        if Version(self.dependencies["fmt"].ref.version) < 6:
            raise ConanInvalidConfiguration("The version of fmt must be >= 6.0.0")
        if Version(self.dependencies["fmt"].ref.version) == "8.0.0" and self.settings.compiler == "clang":
            raise ConanInvalidConfiguration("fmt/8.0.0 is known to not work with clang (https://github.com/fmtlib/fmt/issues/2377)")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def _get_defines(self):
        defines = []
        enable_io_uring = self.options.get_safe("enable_io_uring")
        if enable_io_uring in (True, False):
            defines += [f"XTR_USE_IO_URING={int(bool(enable_io_uring))}"]
        if self.options.get_safe("enable_io_uring_sqpoll"):
            defines += ["XTR_IO_URING_POLL=1"]
        capacity = self.options.get_safe("sink_capacity_kb")
        if capacity:
            defines += [f"XTR_SINK_CAPACITY={int(capacity) * 1024}"]
        return defines

    def generate(self):
        tc = CMakeToolchain(self)
        tc.cache_variables["ENABLE_EXCEPTIONS"] = self.options.enable_exceptions
        tc.cache_variables["ENABLE_LTO"] = self.options.enable_lto
        tc.cache_variables["BUILD_SINGLE_HEADER"] = False
        tc.cache_variables["BUILD_BENCHMARK"] = False
        tc.cache_variables["BUILD_TESTING"] = False
        tc.cache_variables["INSTALL_DOCS"] = False
        tc.generate()
        deps = CMakeDeps(self)
        deps.generate()

    def _patch_sources(self):
        if Version(self.version) >= "2.0.0":
            # Ensure that liburing from Conan is used
            replace_in_file(self, os.path.join(self.source_folder, "CMakeLists.txt"),
                            "find_package(liburing)",
                            "find_package(liburing REQUIRED NO_DEFAULT_PATH PATHS ${CMAKE_PREFIX_PATH})"
                            if self.options.get_safe("enable_io_uring") else
                            "")
        # Non-single header installation is broken as of 2.1.0
        # https://github.com/choll/xtr/pull/4
        replace_in_file(self, os.path.join(self.source_folder, "CMakeLists.txt"),
                        "        PUBLIC_HEADER DESTINATION include)",
                        ")\ninstall(DIRECTORY ${CMAKE_SOURCE_DIR}/include/ DESTINATION include)")

    def build(self):
        self._patch_sources()
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, "LICENSE", self.source_folder, os.path.join(self.package_folder, "licenses"))
        cmake = CMake(self)
        cmake.install()

    def package_info(self):
        self.cpp_info.libs = ["xtr"]
        self.cpp_info.system_libs = ["pthread"]
        self.cpp_info.defines = self._get_defines()

        # TODO: Legacy, to be removed on Conan 2.0
        bin_path = os.path.join(self.package_folder, "bin")
        self.env_info.PATH.append(bin_path)
