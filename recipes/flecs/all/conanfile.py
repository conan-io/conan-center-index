from conans import ConanFile, CMake, tools
import os


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
    options = {"shared": [True, False], "fPIC": [True, False]}
    default_options = {"shared": False, "fPIC": True}

    exports_sources = "CMakeLists.txt"
    generators = "cmake"

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
        tools.get(**self.conan_data["sources"][self.version])
        os.rename(self.name + "-" + self.version, self._source_subfolder)

    def _patch_sources(self):
        tools.replace_in_file(os.path.join(self._source_subfolder, "cmake", "target_default_compile_options.cmake"),
                              "-fPIC", "")

    def build(self):
        self._patch_sources()
        cmake = CMake(self)
        cmake.configure()
        cmake.build(target="flecs" if self.options.shared else "flecs_static")

    def package(self):
        self.copy("LICENSE", dst="licenses", src=self._source_subfolder)
        self.copy("*", dst="include", src=os.path.join(self._source_subfolder, "include"))
        self.copy("*.lib", dst="lib", src="lib")
        self.copy("*.dll", dst="bin", src="bin")
        self.copy("*.a", dst="lib", src="lib")
        self.copy("*.so*", dst="lib", src="lib", symlinks=True)
        self.copy("*.dylib", dst="lib", src="lib", symlinks=True)

    def package_info(self):
        self.cpp_info.libs = ["flecs"] if self.options.shared else ["flecs_static"]
        if not self.options.shared:
            self.cpp_info.defines.append("flecs_STATIC")
