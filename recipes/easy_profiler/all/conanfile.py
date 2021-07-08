from conans import ConanFile, tools, CMake
import os

required_conan_version = ">=1.33.0"


class EasyProfilerConan(ConanFile):
    name = "easy_profiler"
    description = "Lightweight profiler library for c++"
    license = "MIT"
    topics = ("conan", "easy_profiler")
    homepage = "https://github.com/yse/easy_profiler/"
    url = "https://github.com/conan-io/conan-center-index"
    exports_sources = ["CMakeLists.txt", "patches/*"]
    generators = "cmake"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False]
    }
    default_options = {
        "shared": False,
        "fPIC": True
    }

    _cmake = None

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    @property
    def _build_subfolder(self):
        return "build_subfolder"

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            del self.options.fPIC

    def source(self):
        tools.get(**self.conan_data["sources"][self.version],
                  destination=self._source_subfolder, strip_root=True)

    def build(self):
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            tools.patch(**patch)
        cmake = self._configure_cmake()
        cmake.build()

    def _configure_cmake(self):
        if self._cmake:
            return self._cmake
        self._cmake = CMake(self)
        # Don't build the GUI because it is dependent on Qt
        self._cmake.definitions["EASY_PROFILER_NO_GUI"] = True
        self._cmake.definitions["EASY_PROFILER_NO_SAMPLES"] = True
        self._cmake.configure(build_folder=self._build_subfolder)
        return self._cmake

    def package(self):
        self.copy("LICENSE", dst="licenses", src=self._source_subfolder)
        self.copy("LICENSE.MIT", dst="licenses", src=self._source_subfolder)
        self.copy("LICENSE.APACHE", dst="licenses", src=self._source_subfolder)
        cmake = self._configure_cmake()
        cmake.install()
        tools.rmdir(os.path.join(self.package_folder, "lib", "cmake"))
        os.remove(os.path.join(self.package_folder, "LICENSE.MIT"))
        os.remove(os.path.join(self.package_folder, "LICENSE.APACHE"))
        if self.settings.os == "Windows":
            for dll_prefix in ["concrt", "msvcp", "vcruntime"]:
                tools.remove_files_by_mask(os.path.join(self.package_folder, "bin"),
                                           "{}*.dll".format(dll_prefix))

    def package_info(self):
        self.cpp_info.libs = ["easy_profiler"]
        if self.settings.os == "Linux":
            self.cpp_info.system_libs = ["m", "pthread"]
        elif self.settings.os == "Windows":
            self.cpp_info.system_libs = ["psapi", "ws2_32"]
            if not self.options.shared:
                self.cpp_info.defines.append("EASY_PROFILER_STATIC")

        bin_path = os.path.join(self.package_folder, "bin")
        self.output.info("Appending PATH environment variable: {}".format(bin_path))
        self.env_info.PATH.append(bin_path)
