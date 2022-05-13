from conans import ConanFile, CMake, tools
from conans.errors import ConanInvalidConfiguration
import os
import functools
from conan.tools.microsoft import is_msvc

required_conan_version = ">=1.33.0"

class TrantorConan(ConanFile):
    name = "trantor"
    description = "a non-blocking I/O tcp network lib based on c++14/17"
    topics = ("tcp-server", "asynchronous-programming", "non-blocking-io")
    license = "BSD-3-Clause"
    homepage = "https://github.com/an-tao/trantor"
    url = "https://github.com/conan-io/conan-center-index"
    exports_sources = ["CMakeLists.txt"]
    generators = "cmake", "cmake_find_package"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "fPIC": [True, False],
        "shared": [True, False],
        "with_c_ares": [True, False],
    }
    default_options = {
        "fPIC": True,
        "shared": False,
        "with_c_ares": True,
    }

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    @property
    def _build_subfolder(self):
        return "build_subfolder"

    @property
    def _compilers_minimum_version(self):
        return {
            "gcc": "5",
            "Visual Studio": "15.0",
            "clang": "5",
            "apple-clang": "10",
        }

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            del self.options.fPIC

    def validate(self):
        if self.settings.compiler.get_safe("cppstd"):
            tools.check_min_cppstd(self, "14")

        minimum_version = self._compilers_minimum_version.get(str(self.settings.compiler), False)
        if minimum_version:
            if tools.Version(self.settings.compiler.version) < minimum_version:
                raise ConanInvalidConfiguration("trantor requires C++14, which your compiler does not support.")
        else:
            self.output.warn("trantor requires C++14. Your compiler is unknown. Assuming it supports C++14.")

        # TODO: Compilation succeeds, but execution of test_package fails on Visual Studio 16 MDd
        if is_msvc(self) and tools.Version(self.settings.compiler.version) == "16" and \
           self.options.shared == True and self.settings.compiler.runtime == "MDd":
            raise ConanInvalidConfiguration("trantor does not support the MDd runtime on Visual Studio 16.")

    def requirements(self):
        if self.options.with_c_ares:
            self.requires("c-ares/1.18.1")

    def source(self):
        tools.get(**self.conan_data["sources"][self.version],
            destination=self._source_subfolder, strip_root=True)

    @functools.lru_cache(1)
    def _configure_cmake(self):
        cmake = CMake(self)
        cmake.definitions["BUILD_TRANTOR_SHARED"] = self.options.shared
        cmake.definitions["BUILD_C-ARES"] = self.options.with_c_ares
        cmake.configure(build_folder=self._build_subfolder)

        return cmake

    def build(self):
        if self.options.with_c_ares:
            tools.replace_in_file(os.path.join(self._source_subfolder, "CMakeLists.txt"), 
                "target_link_libraries(${PROJECT_NAME} PRIVATE c-ares_lib)", 
                "target_link_libraries(${PROJECT_NAME} PRIVATE c-ares::cares)")
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        self.copy("LICENSE", dst="licenses", src=self._source_subfolder)
        cmake = self._configure_cmake()
        cmake.install()
        tools.rmdir(os.path.join(self.package_folder, "pkgconfig"))
        tools.rmdir(os.path.join(self.package_folder, "lib", "cmake"))

    def package_info(self):
        self.cpp_info.libs = ["trantor"]

        if self.settings.os == "Windows":
            self.cpp_info.system_libs.append("ws2_32")
        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.system_libs.append("pthread")
