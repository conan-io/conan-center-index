import os

from conans import ConanFile, CMake, tools
from conans.errors import ConanInvalidConfiguration


class ConanRecipe(ConanFile):
    name = "entt"

    description = "Gaming meets modern C++ - a fast and reliable entity-component system (ECS) and much more"
    topics = ("conan," "entt", "gaming", "entity", "ecs")

    homepage = "https://github.com/skypjack/entt"
    url = "https://github.com/conan-io/conan-center-index"

    license = "MIT"

    settings = "os", "compiler", "build_type", "arch"
    generators = "cmake", "cmake_find_package_multi"

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    @property
    def _build_subfolder(self):
        return "build_subfolder"

    def configure(self):
        version = tools.Version(self.settings.compiler.version)
        compiler = str(self.settings.compiler)

        if self.settings.compiler.cppstd:
            tools.check_min_cppstd(self, "17")
            return

        minimal_version = {
            "Visual Studio": "16",
            "gcc": "7",
            "clang": "5",
            "apple-clang": "10"
        }

        if compiler not in minimal_version:
            self.output.warn(
                "%s recipe lacks information about the %s compiler standard version support" % (self.name, compiler))
            self.output.warn(
                "%s requires a compiler that supports at least C++17" % self.name)
            return

        if version < minimal_version[compiler]:
            raise ConanInvalidConfiguration(
                "%s requires a compiler that supports at least C++17" % self.name)

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        extracted_dir = "entt-" + self.version
        os.rename(extracted_dir, self._source_subfolder)

    def _configure_cmake(self):
        cmake = CMake(self)
        cmake.definitions["BUILD_TESTING"] = "OFF"
        cmake.definitions["USE_LIBCPP"] = "OFF"
        cmake.configure(
            source_folder=self._source_subfolder,
            build_folder=self._build_subfolder
        )
        return cmake

    def build(self):
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        self.copy(pattern="LICENSE", dst="licenses",
                  src=self._source_subfolder)
        cmake = self._configure_cmake()
        cmake.install()
        tools.rmdir(os.path.join(self.package_folder, "cmake"))
        tools.rmdir(os.path.join(self.package_folder, "lib", "cmake"))

    def package_id(self):
        self.info.header_only()

    def package_info(self):
        self.cpp_info.name = "EnTT"
