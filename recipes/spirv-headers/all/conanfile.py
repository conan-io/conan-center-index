from conans import ConanFile, tools, CMake
import os


class SpirvheadersConan(ConanFile):
    name = "spirv-headers"
    homepage = "https://github.com/KhronosGroup/SPIRV-Headers"
    description = "Header files for the SPIRV instruction set."
    topics = ("conan", "spirv", "spirv-v", "vulkan", "opengl", "opencl", "khronos")
    url = "https://github.com/conan-io/conan-center-index"
    settings = "os", "compiler", "arch", "build_type"
    license = "MIT-KhronosGroup"
    _cmake = None

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        extracted_dir = "SPIRV-Headers-" + self.version
        if self.version == "1.5.1":
            extracted_dir = extracted_dir + ".corrected"
        os.rename(extracted_dir, self._source_subfolder)

    def _configure_cmake(self):
        if self._cmake:
            return self._cmake

        self._cmake = CMake(self)
        self._cmake.definitions["SPIRV_HEADERS_SKIP_EXAMPLES"] = True
        self._cmake.configure(source_folder=self._source_subfolder)
        return self._cmake

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
