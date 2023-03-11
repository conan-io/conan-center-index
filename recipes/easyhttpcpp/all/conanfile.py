from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.build import check_min_cppstd, valid_min_cppstd
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
from conan.tools.files import apply_conandata_patches, copy, export_conandata_patches, get, rmdir
import os

required_conan_version = ">=1.53.0"


class EasyhttpcppConan(ConanFile):
    name = "easyhttpcpp"
    description = "A cross-platform HTTP client library with a focus on usability and speed"
    license = "MIT"
    topics = ("http", "client", "protocol")
    homepage = "https://github.com/sony/easyhttpcpp"
    url = "https://github.com/conan-io/conan-center-index"

    package_type = "library"
    settings = "os", "arch", "compiler", "build_type"
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
        return "11"

    def export_sources(self):
        export_conandata_patches(self)

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")

    def layout(self):
        cmake_layout(self, src_folder="src")

    def requirements(self):
        self.requires("poco/1.12.4", transitive_headers=True, transitive_libs=True)

    @property
    def _required_poco_components(self):
        comps = ["enable_data", "enable_data_sqlite", "enable_net"]
        if self.settings.os == "Windows":
            comps.append("enable_netssl_win")
        else:
            comps.append("enable_netssl")
        return comps

    def validate(self):
        if any([not self.dependencies["poco"].options.get_safe(comp, False) for comp in self._required_poco_components]):
            raise ConanInvalidConfiguration(
                f"{self.ref} requires the following poco options enabled: {', '.join(self._required_poco_components)}"
            )
        if self.settings.compiler.get_safe("cppstd"):
            check_min_cppstd(self, self._min_cppstd)

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.variables["FORCE_SHAREDLIB"] = self.options.shared
        if not valid_min_cppstd(self, self._min_cppstd):
            tc.variables["CMAKE_CXX_STANDARD"] = self._min_cppstd
        if self.settings.os == "Windows" and self.options.shared:
            tc.preprocessor_definitions["EASYHTTPCPP_DLL"] = "1"
            tc.preprocessor_definitions["EASYHTTPCPP_API_EXPORTS"] = "1"
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
        rmdir(self, os.path.join(self.package_folder, "lib", "cmake"))

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "easyhttpcppeasyhttp")
        self.cpp_info.set_property("cmake_target_name", "easyhttpcpp::easyhttp")
        # TODO: back to global scope in conan v2
        libsuffix = ""
        if self.settings.build_type == "Debug":
            if self.settings.os == "Windows" and not self.options.shared:
                libsuffix += "md"
            libsuffix += "d"
        self.cpp_info.components["easyhttp"].libs = [f"easyhttp{libsuffix}"]
        if self.settings.os == "Windows" and self.options.shared:
            self.cpp_info.components["easyhttp"].defines.append("EASYHTTPCPP_DLL")
        self.cpp_info.components["easyhttp"].requires = [
            "poco::poco_foundation", "poco::poco_data",
            "poco::poco_datasqlite", "poco::poco_net",
        ]
        if self.settings.os == "Windows":
            self.cpp_info.components["easyhttp"].requires.append("poco::poco_netsslwin")
        else:
            self.cpp_info.components["easyhttp"].requires.append("poco::poco_netssl")

        # TODO: to remove in conan v2
        self.cpp_info.filenames["cmake_find_package"] = "easyhttpcppeasyhttp"
        self.cpp_info.filenames["cmake_find_package_multi"] = "easyhttpcppeasyhttp"
        self.cpp_info.names["cmake_find_package"] = "easyhttpcpp"
        self.cpp_info.names["cmake_find_package_multi"] = "easyhttpcpp"
        self.cpp_info.components["easyhttp"].names["cmake_find_package"] = "easyhttp"
        self.cpp_info.components["easyhttp"].names["cmake_find_package_multi"] = "easyhttp"
        self.cpp_info.components["easyhttp"].set_property("cmake_target_name", "easyhttpcpp::easyhttp")
