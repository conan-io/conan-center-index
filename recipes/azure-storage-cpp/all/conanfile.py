import os

from conan import ConanFile
from conan.tools.build import check_min_cppstd
from conan.tools.cmake import CMakeToolchain, CMakeDeps, CMake
from conan.tools.files import get, collect_libs, copy
from conan.tools.microsoft import check_min_vs

required_conan_version = ">=1.33.0"


class AzureStorageCppConan(ConanFile):
    name = "azure-storage-cpp"
    license = "Apache-2.0"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/Azure/azure-storage-cpp"
    description = "Microsoft Azure Storage Client Library for C++"
    topics = ("azure", "cpp", "cross-platform", "microsoft", "cloud")
    settings = "os", "compiler", "build_type", "arch"
    exports_sources = ["CMakeLists.txt", "patches/**"]
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
    }
    short_paths = True

    @property
    def _min_cppstd(self):
        return 11

    @property
    def _minimum_compiler_version(self):
        return {
            "gcc": "5",
            "Visual Studio": "14",
            "clang": "3.4",
            "apple-clang": "5.1",
        }

    def requirements(self):
        self.requires("cpprestsdk/2.10.18", transitive_headers=True)
        if self.settings.os != "Windows":
            self.requires("boost/[>=1.76.0 <2]")
            self.requires("libxml2/[>=2.9.10 <3]")
            self.requires("util-linux-libuuid/2.39", transitive_headers=True)
        if self.settings.os == "Macos":
            self.requires("libgettext/[>=0.20.1 <2]")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        toolchain = CMakeToolchain(self)
        toolchain.variables["CMAKE_FIND_FRAMEWORK"] = "LAST"
        toolchain.variables["BUILD_TESTS"] = False
        toolchain.variables["BUILD_SAMPLES"] = False
        if not self.settings.compiler.cppstd:
            toolchain.variables["CMAKE_CXX_STANDARD"] = self._min_cppstd
        if self.settings.os == "Macos":
            toolchain.variables["GETTEXT_LIB_DIR"] = os.path.join(self.dependencies['libgettext'].package_folder, 'lib', '')
        toolchain.generate()

        deps = CMakeDeps(self)
        deps.generate()

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            del self.options.fPIC

        # workaround for https://github.com/conan-io/conan-center-index/issues/10332
        if self.settings.os == "Linux" and self.settings.compiler == "gcc":
            self.options["boost"].without_stacktrace = True

    def validate(self):
        if self.settings.compiler.get_safe("cppstd"):
            check_min_cppstd(self, self._min_cppstd)

        # FIXME: Visual Studio 2015 & 2017 are supported but CI of CCI lacks several Win SDK components
        # https://github.com/conan-io/conan-center-index/issues/4195
        check_min_vs(self, "193")
        # if not is_msvc_static_runtime(self):
        #     raise ConanInvalidConfiguration("Visual Studio build for shared library with MT runtime is not supported")

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, "LICENSE.txt", dst="licenses", src=".")
        cmake = CMake(self)
        cmake.install()

    def package_info(self):
        self.cpp_info.libs = collect_libs(self)
        if self.settings.os == "Windows":
            self.cpp_info.system_libs = ["ws2_32", "rpcrt4", "xmllite", "bcrypt"]
            if not self.options.shared:
                self.cpp_info.defines = ["_NO_WASTORAGE_API"]
