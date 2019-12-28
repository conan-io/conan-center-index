import os

from conans import ConanFile, CMake, tools


class ConanRecipe(ConanFile):
    name = "entt"

    description = "Gaming meets modern C++ - a fast and reliable entity-component system (ECS) and much more"
    topics = ("conan," "entt", "gaming", "entity", "ecs")

    homepage = "https://github.com/skypjack/entt"
    url = "https://github.com/conan-io/conan-center-index"

    license = "MIT"

    settings = "os", "compiler", "build_type", "arch"
    generators = "cmake"

    _source_subfolder = "source_subfolder"
    _build_subfolder = "build_subfolder"

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        extracted_dir = "entt-" + self.version
        os.rename(extracted_dir, self._source_subfolder)

    def configure(self):
        tools.check_min_cppstd(self, "17")

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

    def package_id(self):
        self.info.header_only()

    def package_info(self):
        self.cpp_info.name = "EnTT"
