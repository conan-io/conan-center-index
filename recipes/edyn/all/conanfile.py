from conans import CMake, ConanFile, tools
from conans.errors import ConanInvalidConfiguration
from conan.tools.microsoft import msvc_runtime_flag, is_msvc
import functools
import os

required_conan_version = ">=1.45.0"

class EdynConan(ConanFile):
    name = "edyn"
    description = "Edyn is a real-time physics engine organized as an ECS"
    license = "MIT"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/xissburg/edyn"
    topics = ("physics", "game-development", "ecs")
    settings = "os", "arch", "compiler", "build_type"
    
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "floating_type": ["float", "double"],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "floating_type": "float",
    }
    generators = "cmake", "cmake_find_package_multi"

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    @property
    def _build_subfolder(self):
        return "build_subfolder"

    def export_sources(self):
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            self.copy(patch["patch_file"])

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            del self.options.fPIC

    def requirements(self):
        self.requires("entt/3.9.0")

    def validate(self):
        if self.settings.compiler.get_safe("cppstd"):
            tools.check_min_cppstd(self, 17)
   
    def source(self):
        tools.get(**self.conan_data["sources"][self.version],
                  destination=self._source_subfolder, strip_root=True)

    def _patch_sources(self):
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            tools.patch(**patch)

    @functools.lru_cache(1)
    def _configure_cmake(self):
        cmake = CMake(self)
        cmake.configure(source_folder=self._source_subfolder, build_folder=self._build_subfolder)
        return cmake

    def build(self):
        self._patch_sources()
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        self.copy(pattern="LICENSE", dst="licenses", src=self._source_subfolder)
        cmake = self._configure_cmake()
        cmake.install()

        tools.rmdir(os.path.join(self.package_folder, "lib", "pkgconfig"))
        tools.rmdir(os.path.join(self.package_folder, "lib", "cmake"))
        tools.rmdir(os.path.join(self.package_folder, "share"))
        tools.remove_files_by_mask(os.path.join(self.package_folder, "lib"), "*.pdb")

    def package_info(self):
        suffix = "_d" if self.settings.build_type == "Debug" else ""
        self.cpp_info.libs = ["Edyn" + suffix]

        self.cpp_info.set_property("cmake_find_mode", "both")
        self.cpp_info.set_property("cmake_module_file_name", "Edyn")
        self.cpp_info.set_property("cmake_file_name", "Edyn")
        self.cpp_info.set_property("cmake_target_name", "Edyn::Edyn")
        self.cpp_info.set_property("pkg_config_name", "Edyn")

        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.system_libs += ["m", "pthread"]
        elif self.settings.os == "Windows":
            self.cpp_info.system_libs = ["winmm"]

        #  TODO: to remove in conan v2 once cmake_find_package_* generators removed
        self.cpp_info.filenames["cmake_find_package"] = "Edyn"
        self.cpp_info.filenames["cmake_find_package_multi"] = "Edyn"
        self.cpp_info.names["cmake_find_package"] = "Edyn"
        self.cpp_info.names["cmake_find_package_multi"] = "Edyn"