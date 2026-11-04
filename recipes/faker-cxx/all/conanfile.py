from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.files import get, copy, rmdir
from conan.tools.build import check_min_cppstd
from conan.tools.scm import Version
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
import os

required_conan_version = ">=2"

class FakerCXXConan(ConanFile):
    name = "faker-cxx"
    description = "C++ Faker library based on faker-js/faker. "
    license = "MIT"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/cieslarmichal/faker-cxx"
    topics = ("faker", "fake",)
    package_type = "library"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "with_std_format": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "with_std_format": False,
    }

    implements = ["auto_shared_fpic"]

    @property
    def _compilers_minimum_version(self):
        return {
            "gcc": "12",
            "clang": "16",
            "apple-clang": "16",
            "Visual Studio": "17",
            "msvc": "193",
        }
    @property
    def _min_std_format_support(self):
        return {
            "gcc": "13",
            "clang": "17",
            # These two are actually earlier, but older versions fail for other reasons
            "apple-clang": "16",
            "msvc": "193"
        }

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

        if Version(self.version) >= "4.0.0":
            del self.options.with_std_format

    @property
    def _with_std_format(self):
        return self.options.get_safe("with_std_format", True)

    def requirements(self):
        if not self._with_std_format:
            self.requires("fmt/10.2.1")

    def layout(self):
        cmake_layout(self, src_folder="src")

    def validate(self):
        check_min_cppstd(self, 20)
        minimum_version = self._compilers_minimum_version.get(str(self.settings.compiler), False)
        if minimum_version and Version(self.settings.compiler.version) < minimum_version:
            raise ConanInvalidConfiguration(
                f"{self.ref} requires C++20, which your compiler does not support."
            )

        if Version(self.version) >= "4.0.0":
            format_minimum_version = self._min_std_format_support.get(str(self.settings.compiler), False)
            if format_minimum_version and Version(self.settings.compiler.version) < format_minimum_version:
                raise ConanInvalidConfiguration(
                    f"{self.ref} requires std::format, which your compiler does not support."
                )
        elif self.settings.os == "Windows" and self.options.shared:
            # https://github.com/cieslarmichal/faker-cxx/issues/753
            raise ConanInvalidConfiguration(f"{self.ref} is not prepared to generated shared library on Windows.")

    def build_requirements(self):
        self.tool_requires("cmake/[>=3.22 <4]")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.cache_variables["USE_SYSTEM_DEPENDENCIES"] = True
        tc.cache_variables["BUILD_TESTING"] = False
        tc.cache_variables["WARNINGS_AS_ERRORS"] = False
        tc.cache_variables["USE_STD_FORMAT"] = self._with_std_format
        tc.generate()
        deps = CMakeDeps(self)
        deps.generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, pattern="LICENSE*", dst=os.path.join(self.package_folder, "licenses"), src=self.source_folder)
        cmake = CMake(self)
        cmake.install()
        rmdir(self, os.path.join(self.package_folder, "lib", "cmake"))
        rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))

    def package_info(self):
        self.cpp_info.libs = ["faker-cxx"]

        self.cpp_info.set_property("cmake_file_name", "faker-cxx")
        self.cpp_info.set_property("cmake_target_name", "faker-cxx::faker-cxx")
