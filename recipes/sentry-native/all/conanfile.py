import os
import glob
from conans import ConanFile, CMake, tools
from conans.errors import ConanInvalidConfiguration


class SentryNativeConan(ConanFile):
    name = "sentry-native"
    description = "The Sentry Native SDK is an error and crash reporting client for native applications,\n" \
                  "optimized for C and C++. Sentry allows to add tags,\n" \
                  "breadcrumbs and arbitrary custom context to enrich error reports."
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/getsentry/sentry-native"
    license = "MIT"
    topics = ("conan", "breakpad", "crashpad",
              "error-reporting", "crash-reporting")
    exports_sources = ["CMakeLists.txt"]
    generators = "cmake", "cmake_find_package"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "backend": ["none", "inproc", "crashpad", "breakpad"],
        "transport": ["none", "curl", "winhttp"],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "backend": "inproc",
        "transport": "curl"
    }

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
        if self.settings.compiler.cppstd:
            tools.check_min_cppstd(self, 11)
        if self.options.backend == "inproc" and self.settings.os == "Windows" and tools.Version(self.version) < "0.4":
            raise ConanInvalidConfiguration("The in-process backend is not supported on Windows")
        if self.options.transport == "winhttp" and self.settings.os != "Windows":
            raise ConanInvalidConfiguration("The winhttp transport is only supported on Windows")

    def requirements(self):
        if self.options.transport == "curl":
            self.requires("libcurl/7.74.0")
        if self.options.backend == "crashpad":
            raise ConanInvalidConfiguration("crashpad not available yet in CCI")
        elif self.options.backend == "breakpad":
            raise ConanInvalidConfiguration("breakpad not available yet in CCI")

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        extracted_dir = self.name + "-" + self.version
        os.rename(extracted_dir, self._source_subfolder)

    def _configure_cmake(self):
        if self._cmake:
            return self._cmake
        self._cmake = CMake(self)
        self._cmake.definitions["SENTRY_BACKEND"] = self.options.backend
        self._cmake.definitions["SENTRY_ENABLE_INSTALL"] = True
        self._cmake.definitions["SENTRY_TRANSPORT"] = self.options.transport
        self._cmake.definitions["SENTRY_PIC"] = self.options.get_safe("fPIC", True)
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
        for pdb in glob.glob(os.path.join(self.package_folder, "bin", "*.pdb")):
            os.unlink(pdb)

    def package_info(self):
        self.cpp_info.names["cmake_find_package"] = "sentry"
        self.cpp_info.names["cmake_find_package_multi"] = "sentry"
        self.cpp_info.libs = ["sentry"]
        if self.settings.os in ("Android", "Linux"):
            self.cpp_info.exelinkflags = ["-Wl,-E,--build-id=sha1"]
            self.cpp_info.sharedlinkflags = ["-Wl,-E,--build-id=sha1"]
        if self.settings.os == "Linux":
            self.cpp_info.system_libs = ["pthread", "dl"]
        elif self.settings.os == "Android":
            self.cpp_info.system_libs = ["dl", "log"]
        elif self.settings.os == "Windows":
            self.cpp_info.system_libs = ["shlwapi", "dbghelp"]
            if self.options.transport == "winhttp":
                self.cpp_info.system_libs.append("winhttp")
        if not self.options.shared:
            self.cpp_info.defines = ["SENTRY_BUILD_STATIC"]
