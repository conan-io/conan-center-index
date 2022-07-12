import os
from conans import ConanFile, tools
from conan.tools.cmake import CMake
from conan.tools.microsoft import is_msvc
from conans.errors import ConanInvalidConfiguration


required_conan_version = ">=1.45.0"


class BeautyConan(ConanFile):
    name = "beauty"
    homepage = "https://github.com/dfleury2/beauty"
    description = "HTTP Server above Boost.Beast"
    topics = ("http", "server", "boost.beast")
    url = "https://github.com/conan-io/conan-center-index"
    license = "MIT"
    settings = "os", "compiler", "build_type", "arch"
    options = {"shared": [True, False], "fPIC": [True, False]}
    default_options = {"shared": False, "fPIC": True}
    generators = "CMakeDeps", "CMakeToolchain"

    requires = ("boost/1.79.0",
                "openssl/1.1.1o")

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    @property
    def _compilers_minimum_version(self):
        return {
            "gcc": "8",
            "clang": "11",
            "Visual Studio": "16",
        }

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            del self.options.fPIC

    def validate(self):
        if self.settings.compiler.get_safe("cppstd"):
            tools.check_min_cppstd(self, "20")

        minimum_version = self._compilers_minimum_version.get(str(self.settings.compiler), False)
        if minimum_version and tools.Version(self.settings.compiler.version) < minimum_version:
            raise ConanInvalidConfiguration(
                f"Compiler {self.name} must be at least {minimum_version}")

        if self.settings.compiler == "clang" and self.settings.compiler.libcxx != "libc++":
            raise ConanInvalidConfiguration("Only libc++ is supported for clang")

        if self.settings.compiler == "apple-clang" and self.options.shared:
            raise ConanInvalidConfiguration("shared is not supported on apple-clang")

        if is_msvc and self.options.shared:
            raise ConanInvalidConfiguration("shared is not supported on Visual Studio")

    def source(self):
        tools.get(**self.conan_data["sources"][self.version],
                  destination=self._source_subfolder, strip_root=True)

    def build(self):
        cmake = CMake(self)
        cmake.configure(build_script_folder=self._source_subfolder)
        cmake.build(target="beauty")

    def package(self):
        self.copy("LICENSE", dst="licenses", src=self._source_subfolder)
        cmake = CMake(self)
        cmake.install()
        tools.rmdir(os.path.join(self.package_folder, "lib", "cmake"))

    def package_info(self):
        self.cpp_info.libs = ["beauty"]
        self.cpp_info.requires = ["boost::headers", "openssl::openssl"]
        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.system_libs = ["m"]
