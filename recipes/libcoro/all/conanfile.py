from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.build import check_min_cppstd
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
from conan.tools.files import apply_conandata_patches, copy, export_conandata_patches, get, rmdir
from conan.tools.scm import Version
import os

required_conan_version = ">=1.53.0"


class LibcoroConan(ConanFile):
    name = "libcoro"
    description = "C++20 coroutine library"
    topics = ("coroutines", "concurrency", "tasks", "executors", "networking")
    license = "Apache-2.0"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/jbaldwin/libcoro"
    package_type = "library"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "with_networking": [True, False],
        "with_ssl": [True, False],
        "with_threading": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "with_networking": True,
        "with_ssl": True,
        "with_threading": True,
    }

    @property
    def _min_cppstd(self):
        return "20"

    @property
    def _minimum_compilers_version(self):
        return {
            "gcc": "10.2.1",
        }

    def export_sources(self):
        export_conandata_patches(self)

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC
        if Version(self.version) < "0.8":
            del self.options.with_networking
        if Version(self.version) < "0.9":
            del self.options.with_ssl
            del self.options.with_threading

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")

    def layout(self):
        cmake_layout(self, src_folder="src")

    def requirements(self):
        if "with_ssl" not in self.options or self.options.with_ssl:
            self.requires("openssl/[>=1.1 <4]", transitive_headers=True)
        self.requires("c-ares/1.19.1", transitive_headers=True)
        self.requires("tl-expected/1.1.0", transitive_headers=True)

    def validate(self):
        if self.settings.compiler.get_safe("cppstd"):
            check_min_cppstd(self, self._min_cppstd)
        if self.settings.os not in ["Linux", "FreeBSD", "Macos"]:
            raise ConanInvalidConfiguration(f"{self.ref} is not supported on {self.settings.os}.")
        if self.settings.compiler != "gcc":
            raise ConanInvalidConfiguration("gcc is the only compiler supported by libcoro.")

        minimum_version = self._minimum_compilers_version.get(str(self.settings.compiler), False)
        if minimum_version and Version(self.settings.compiler.version) < minimum_version:
            raise ConanInvalidConfiguration(
                f"{self.ref} requires C++{self._min_cppstd}, which your compiler does not support."
            )

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.variables["LIBCORO_BUILD_TESTS"] = False
        tc.variables["LIBCORO_BUILD_EXAMPLES"] = False
        if Version(self.version) >= "0.8":
            tc.variables["LIBCORO_EXTERNAL_DEPENDENCIES"] = True
            tc.variables["LIBCORO_FEATURE_NETWORKING"] = self.options.with_networking
        if Version(self.version) >= "0.9":
            tc.variables["LIBCORO_FEATURE_THREADING"] = self.options.with_threading
            tc.variables["LIBCORO_FEATURE_SSL"] = self.options.with_ssl
        tc.generate()
        deps = CMakeDeps(self)
        deps.generate()

    def build(self):
        apply_conandata_patches(self)
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, "LICENSE", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        cmake = CMake(self)
        cmake.install()
        rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "libcoro")
        self.cpp_info.set_property("cmake_target_name", "libcoro::libcoro")
        if Version(self.version) >= "0.8":
            self.cpp_info.libs = ["coro"]
        else:
            self.cpp_info.libs = ["libcoro"]
        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.system_libs = ["pthread", "m"]

        if Version(self.version) >= "0.9":
            if self.options.with_networking:
                self.cpp_info.defines.append("LIBCORO_FEATURE_NETWORKING")
            if self.options.with_ssl:
                self.cpp_info.defines.append("LIBCORO_FEATURE_SSL")
            if self.options.with_threading:
                self.cpp_info.defines.append("LIBCORO_FEATURE_THREADING")
