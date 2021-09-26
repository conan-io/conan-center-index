from conans import ConanFile, CMake, tools
import os

required_conan_version = ">=1.33.0"


class FlecsConan(ConanFile):
    name = "flecs"
    description = "A fast entity component system (ECS) for C & C++"
    license = "MIT"
    topics = ("gamedev", "cpp", "data-oriented-design", "c99",
              "game-development", "ecs", "entity-component-system",
              "cpp11", "ecs-framework")
    homepage = "https://github.com/SanderMertens/flecs"
    url = "https://github.com/conan-io/conan-center-index"

    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
    }

    exports_sources = "CMakeLists.txt"
    generators = "cmake"
    _cmake = None

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            del self.options.fPIC
        del self.settings.compiler.libcxx
        del self.settings.compiler.cppstd

    def source(self):
        tools.get(**self.conan_data["sources"][self.version],
                  destination=self._source_subfolder, strip_root=True)

    def _configure_cmake(self):
        if self._cmake:
            return self._cmake
        self._cmake = CMake(self)
        self._cmake.definitions["FLECS_STATIC_LIBS"] = not self.options.shared
        self._cmake.definitions["FLECS_PIC"] = self.options.get_safe("fPIC", True)
        self._cmake.definitions["FLECS_SHARED_LIBS"] = self.options.shared
        self._cmake.definitions["FLECS_DEVELOPER_WARNINGS"] = False
        self._cmake.configure()
        return self._cmake

    def build(self):
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        self.copy("LICENSE", dst="licenses", src=self._source_subfolder)
        cmake = self._configure_cmake()
        cmake.install()
        tools.rmdir(os.path.join(self.package_folder, "lib", "cmake"))

    def package_info(self):
        self.cpp_info.names["cmake_find_package"] = "flecs"
        self.cpp_info.names["cmake_find_package_multi"] = "flecs"
        target_and_lib_name = "flecs" if self.options.shared else "flecs_static"
        self.cpp_info.components["_flecs"].names["cmake_find_package"] = target_and_lib_name
        self.cpp_info.components["_flecs"].names["cmake_find_package_multi"] = target_and_lib_name
        self.cpp_info.components["_flecs"].libs = [target_and_lib_name]
        if not self.options.shared:
            self.cpp_info.components["_flecs"].defines.append("flecs_STATIC")
