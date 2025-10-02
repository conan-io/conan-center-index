from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.cmake import CMake, CMakeToolchain, cmake_layout
from conan.tools.build import check_min_cppstd
from conan.tools.files import copy, get


required_conan_version = ">=2.0.9"


class FoxgloveSdkConan(ConanFile):
    name = "foxglove-sdk"
    version = "0.14.3"
    description = "Foxglove SDK"
    license = "MIT"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/foxglove/foxglove-sdk"
    topics = ("foxglove", "robotics", "visualization")
    package_type = "library"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
    }
    default_options = {
        "shared": False,
    }

    @property
    def _min_cppstd(self):
        return 17

    def export_sources(self):
        copy(self, "CMakeLists.txt", self.recipe_folder, self.export_sources_folder)
        copy(
            self,
            "foxglove-sdk-config.cmake.in",
            self.recipe_folder,
            self.export_sources_folder,
        )

    def validate(self):
        check_min_cppstd(self, self._min_cppstd)

    def layout(self):
        cmake_layout(self)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.variables["FOXGLOVE_SDK_VERSION"] = self.version
        tc.variables["FOXGLOVE_SDK_VERSION_MAJOR"] = self.version.split(".")[0]
        tc.variables["BUILD_SHARED_LIBS"] = self.options.shared
        tc.generate()

    def build(self):
        target_os = str(self.settings.os)
        target_arch = str(self.settings.arch)
        artifacts = (
            self.conan_data["sources"][self.version].get(target_os, {}).get(target_arch)
        )
        if not artifacts:
            raise ConanInvalidConfiguration(
                f"No artifacts found for {target_os} / {target_arch}"
            )

        get(
            self,
            **artifacts,
            strip_root=True,
        )

        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        cmake = CMake(self)
        cmake.install()

    def package_info(self):
        self.cpp_info.libs = ["foxglove_cpp", "foxglove"]

        self.cpp_info.set_property("cmake_file_name", self.name)
        self.cpp_info.set_property("pkg_config_name", self.name)
        self.cpp_info.set_property("cmake_target_name", f"{self.name}::{self.name}")

        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.system_libs.extend(["dl", "m", "pthread"])
        elif self.settings.os == "Windows":
            self.cpp_info.system_libs.extend(["ws2_32"])
