from conans import ConanFile, CMake, tools

required_conan_version = ">=1.43.0"

class SbgEComConan(ConanFile):
    name = "sbgecom"
    description = "C library used to communicate with SBG Systems IMU, AHRS and INS"
    license = "MIT"
    topics = ("sbg", "imu", "ahrs", "ins")
    homepage = "https://github.com/SBG-Systems/sbgECom"
    url = "https://github.com/conan-io/conan-center-index"

    settings = "os", "arch", "compiler", "build_type"
    generators = "cmake"

    _cmake = None

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    @property
    def _build_subfolder(self):
        return "build_subfolder"

    def source(self):
        tools.get(**self.conan_data["sources"][self.version], strip_root=True, destination=self._source_subfolder)

    def build(self):
        cmake = self._configure_cmake()
        cmake.build()

    def _configure_cmake(self):
        if self._cmake:
            return self._cmake
        self._cmake = CMake(self)
        # TODO: update source_folder until main CMakeLists goes back to root dir.
        self._cmake.configure(build_folder=self._build_subfolder, source_folder=self._source_subfolder + "/cmake")
        return self._cmake

    # TODO: Remove once a proper cmake install command is done.
    def package(self):
        self.copy("*.h", dst="include", src=self._source_subfolder + "/common")
        self.copy("*.h", dst="include", src=self._source_subfolder + "/src")
        self.copy("*.a", dst="lib", src=self._source_subfolder, keep_path=False)
        self.copy("*.lib", dst="lib", src=self._source_subfolder, keep_path=False)

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "sbgECom")
        self.cpp_info.set_property("cmake_target_name", "sbgECom")
        self.cpp_info.libs = tools.collect_libs(self)
