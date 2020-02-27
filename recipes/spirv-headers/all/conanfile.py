from conans import ConanFile, tools, CMake
import os


class SpirvheadersConan(ConanFile):
    name = "spirv-headers"
    homepage = "https://github.com/KhronosGroup/SPIRV-Headers"
    description = "SPIRV-Headers"
    topics = ("conan", "sprv","vulkan")
    url = "https://github.com/conan-io/conan-center-index"
    settings = "os", "compiler", "arch", "build_type"

    license = "BSD"

    def requirements(self):
        pass

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        extracted_dir = "SPIRV-Headers-" + self.version
        os.rename(extracted_dir, self._source_subfolder)

    def _configure_cmake(self):
        cmake = CMake(self)
        cmake.definitions["SPIRV_HEADERS_SKIP_EXAMPLES"] = True
        cmake.configure(source_folder=self._source_subfolder)
        return cmake

    def build(self):
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        self.copy(pattern="LICENSE*", dst="licenses", src=self._source_subfolder)
        cmake = self._configure_cmake()
        cmake.install()

        # Error KB-H016, complaining that Cmake config files are found
        tools.rmdir(os.path.join(self.package_folder, "lib"))


    def package_id(self):
        self.info.header_only()
