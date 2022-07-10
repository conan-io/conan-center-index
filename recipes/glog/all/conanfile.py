from conans import ConanFile, CMake, tools
import os

required_conan_version = ">=1.33.0"


class GlogConan(ConanFile):
    name = "glog"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/google/glog/"
    description = "Google logging library"
    topics = ("conan", "glog", "logging")
    license = "BSD-3-Clause"

    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "with_gflags": [True, False],
        "with_threads": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "with_gflags": True,
        "with_threads": True,
    }

    exports_sources = ["CMakeLists.txt", "patches/**"]
    generators = "cmake", "cmake_find_package"
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
        if self.options.with_gflags:
            self.options["gflags"].shared = self.options.shared

    def requirements(self):
        if self.options.with_gflags:
            self.requires("gflags/2.2.2")

    def build_requirements(self):
        if tools.Version(self.version) >= "0.6.0":
            self.build_requires("cmake/3.22.3")

    def source(self):
        tools.get(**self.conan_data["sources"][self.version],
                  destination=self._source_subfolder, strip_root=True)

    def _patch_sources(self):
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            tools.patch(**patch)
        # do not force PIC
        if tools.Version(self.version) <= "0.5.0":
            tools.replace_in_file(os.path.join(self._source_subfolder, "CMakeLists.txt"),
                                  "set_target_properties (glog PROPERTIES POSITION_INDEPENDENT_CODE ON)",
                                  "")

    def _configure_cmake(self):
        if self._cmake:
            return self._cmake
        self._cmake = CMake(self)
        self._cmake.definitions["WITH_GFLAGS"] = self.options.with_gflags
        self._cmake.definitions["WITH_THREADS"] = self.options.with_threads
        if tools.Version(self.version) >= "0.5.0":
            self._cmake.definitions["WITH_PKGCONFIG"] = True
            if self.settings.os == "Emscripten":
                self._cmake.definitions["WITH_SYMBOLIZE"] = False
                self._cmake.definitions["HAVE_SYSCALL_H"] = False
                self._cmake.definitions["HAVE_SYS_SYSCALL_H"] = False
            else:
                self._cmake.definitions["WITH_SYMBOLIZE"] = True
            self._cmake.definitions["WITH_UNWIND"] = True
        self._cmake.definitions["BUILD_TESTING"] = False
        self._cmake.configure()
        return self._cmake

    def build(self):
        self._patch_sources()
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        self.copy("COPYING", dst="licenses", src=self._source_subfolder)
        cmake = self._configure_cmake()
        cmake.install()
        tools.rmdir(os.path.join(self.package_folder, "lib", "cmake"))
        tools.rmdir(os.path.join(self.package_folder, "lib", "pkgconfig"))

    def package_info(self):
        self.cpp_info.names["cmake_find_package"] = "glog"
        self.cpp_info.names["cmake_find_package_multi"] = "glog"
        self.cpp_info.names["pkgconfig"] = "libglog"
        postfix = "d" if self.settings.build_type == "Debug" else ""
        self.cpp_info.libs = ["glog" + postfix]
        if self.settings.os == "Linux":
            self.cpp_info.system_libs = ["pthread"]
        elif self.settings.os == "Windows":
            self.cpp_info.system_libs = ["dbghelp"]
            self.cpp_info.defines = ["GLOG_NO_ABBREVIATED_SEVERITIES"]
            decl = "__declspec(dllimport)" if self.options.shared else ""
            self.cpp_info.defines.append("GOOGLE_GLOG_DLL_DECL={}".format(decl))
        if self.options.with_gflags and not self.options.shared:
            self.cpp_info.defines.extend(["GFLAGS_DLL_DECLARE_FLAG=", "GFLAGS_DLL_DEFINE_FLAG="])
