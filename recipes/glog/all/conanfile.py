from conans import ConanFile, CMake, tools
import os


class GlogConan(ConanFile):
    name = "glog"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/google/glog/"
    description = "Google logging library"
    license = "BSD 3-Clause"
    exports_sources = ["CMakeLists.txt"]
    generators = "cmake", "cmake_find_package"
    settings = "os", "arch", "compiler", "build_type"
    options = {"shared": [True, False], "fPIC": [True, False], "with_gflags": [True, False], "with_threads": [True, False]}
    default_options = {"shared": False, "fPIC": True, "with_gflags": True, "with_threads": True}

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.with_gflags:
            self.options["gflags"].shared = self.options.shared

    def requirements(self):
        if self.options.with_gflags:
            self.requires("gflags/2.2.2")

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        extracted_dir = self.name + "-" + self.version
        os.rename(extracted_dir, self._source_subfolder)

    def _configure_cmake(self):
        cmake = CMake(self)
        cmake.definitions["WITH_GFLAGS"] = self.options.with_gflags
        cmake.definitions["WITH_THREADS"] = self.options.with_threads
        cmake.definitions["BUILD_TESTING"] = False
        cmake.configure()
        return cmake

    def build(self):
        if self.options.with_gflags:
            tools.replace_in_file(os.path.join(self._source_subfolder, "CMakeLists.txt"),
                                  "gflags 2.2.0", "gflags 2.2.1 REQUIRED")
            tools.replace_in_file(os.path.join(self._source_subfolder, "CMakeLists.txt"),
                                  "target_link_libraries (glog PUBLIC gflags)",
                                  "target_link_libraries (glog PUBLIC ${CONAN_LIBS})")
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        self.copy("COPYING", dst="licenses", src=self._source_subfolder)
        cmake = self._configure_cmake()
        cmake.install()
        tools.rmdir(os.path.join(self.package_folder, "lib", "cmake"))

    def package_info(self):
        self.cpp_info.libs = tools.collect_libs(self)
        if self.settings.os == "Linux":
            self.cpp_info.system_libs.append("pthread")
        self.cpp_info.names["cmake_find_package"] = "GLOG"
        self.cpp_info.names["cmake_find_package_multi"] = "GLOG"
