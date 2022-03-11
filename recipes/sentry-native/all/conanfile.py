import os
from conans import ConanFile, CMake, tools
from conans.errors import ConanInvalidConfiguration

required_conan_version = ">=1.33.0"


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
    exports_sources = ["CMakeLists.txt", "patches/*"]
    generators = "cmake", "cmake_find_package", "cmake_find_package_multi", "pkg_config"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "backend": ["none", "inproc", "crashpad", "breakpad"],
        "transport": ["none", "curl", "winhttp"],
        "qt": [True, False],
        "with_crashpad": ["google", "sentry"],
        "with_breakpad": ["google", "sentry"],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "backend": "inproc",  # overwritten in config_options
        "transport": "curl",  # overwritten in config_options
        "qt": False,
        "with_crashpad": "sentry",
        "with_breakpad": "sentry",

    }

    _cmake = None

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    @property
    def _minimum_compilers_version(self):
        return {
            "Visual Studio": "15",
            "gcc": "5",
            "clang": "3.4",
            "apple-clang": "5.1",
        }

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

        # Configure default transport
        if self.settings.os == "Windows":
            self.options.transport = "winhttp"
        elif self.settings.os in ("FreeBSD", "Linux") or self.settings.os == "Macos":  # Don't use tools.is_apple_os(os) here
            self.options.transport = "curl"
        else:
            self.options.transport = "none"

        # Configure default backend
        if self.settings.os == "Windows" or self.settings.os == "Macos":  # Don't use tools.is_apple_os(os) here
            # FIXME: for self.version < 0.4: default backend is "breakpad" when building with MSVC for Windows xp; else: backend=none
            self.options.backend = "crashpad"
        elif self.settings.os in ("FreeBSD", "Linux"):
            self.options.backend = "breakpad"
        elif self.settings.os == "Android":
            self.options.backend = "inproc"
        else:
            self.options.backend = "inproc"

    def configure(self):
        if self.options.shared:
            del self.options.fPIC

    def validate(self):
        if self.settings.compiler.cppstd:
            tools.check_min_cppstd(self, 14)

        minimum_version = self._minimum_compilers_version.get(str(self.settings.compiler), False)
        if not minimum_version:
            self.output.warn("Compiler is unknown. Assuming it supports C++14.")
        elif tools.Version(self.settings.compiler.version) < minimum_version:
            raise ConanInvalidConfiguration("Build requires support for C++14. Minimum version for {} is {}"
                .format(str(self.settings.compiler), minimum_version))

        if self.options.backend == "inproc" and self.settings.os == "Windows" and tools.Version(self.version) < "0.4":
            raise ConanInvalidConfiguration("The in-process backend is not supported on Windows")
        if self.options.backend != "crashpad":
            del self.options.with_crashpad
        if self.options.backend != "breakpad":
            del self.options.with_breakpad
        if self.options.transport == "winhttp" and self.settings.os != "Windows":
            raise ConanInvalidConfiguration("The winhttp transport is only supported on Windows")
        if tools.Version(self.version) >= "0.4.7" and self.settings.compiler == "apple-clang" and tools.Version(self.settings.compiler.version) < "10.0":
            raise ConanInvalidConfiguration("apple-clang < 10.0 not supported")
        if self.options.backend == "crashpad" and tools.Version(self.version) < "0.4.7" and self.settings.os == "Macos" and self.settings.arch == "armv8":
            raise ConanInvalidConfiguration("This version doesn't support ARM compilation")

    def build_requirements(self):
        if self.options.backend == "breakpad":
            self.build_requires("pkgconf/1.7.4")

    def requirements(self):
        if self.options.transport == "curl":
            self.requires("libcurl/7.78.0")
        if self.options.backend == "crashpad":
            if self.options.with_crashpad == "sentry":
                self.requires("sentry-crashpad/{}".format(self.version))
            if self.options.with_crashpad == "google":
                self.requires("crashpad/cci.20210507")
        elif self.options.backend == "breakpad":
            if self.options.with_breakpad == "sentry":
                self.requires("sentry-breakpad/{}".format(self.version))
            if self.options.with_breakpad == "google":
                self.requires("breakpad/cci.20210521")
        if self.options.qt:
            self.requires("qt/5.15.2")
            self.requires("openssl/1.1.1l")
            if tools.Version(self.version) < "0.4.5":
                raise ConanInvalidConfiguration("Qt integration available from version 0.4.5")

    def source(self):
        tools.get(**self.conan_data["sources"][self.version], destination=self._source_subfolder)

    def _configure_cmake(self):
        if self._cmake:
            return self._cmake
        self._cmake = CMake(self)
        self._cmake.definitions["SENTRY_BACKEND"] = self.options.backend
        self._cmake.definitions["SENTRY_CRASHPAD_SYSTEM"] = True
        self._cmake.definitions["SENTRY_BREAKPAD_SYSTEM"] = True
        self._cmake.definitions["SENTRY_ENABLE_INSTALL"] = True
        self._cmake.definitions["SENTRY_TRANSPORT"] = self.options.transport
        self._cmake.definitions["SENTRY_PIC"] = self.options.get_safe("fPIC", True)
        self._cmake.definitions["SENTRY_INTEGRATION_QT"] = self.options.qt
        self._cmake.configure()
        return self._cmake

    def build(self):
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            tools.patch(**patch)
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        self.copy("LICENSE", dst="licenses", src=self._source_subfolder)
        cmake = self._configure_cmake()
        cmake.install()
        tools.rmdir(os.path.join(self.package_folder, "lib", "cmake"))
        tools.remove_files_by_mask(os.path.join(self.package_folder, "bin"), "*pdb")

    def package_info(self):
        self.cpp_info.names["cmake_find_package"] = "sentry"
        self.cpp_info.names["cmake_find_package_multi"] = "sentry"
        self.cpp_info.libs = ["sentry"]
        if self.settings.os in ("Android", "FreeBSD", "Linux"):
            self.cpp_info.exelinkflags = ["-Wl,-E,--build-id=sha1"]
            self.cpp_info.sharedlinkflags = ["-Wl,-E,--build-id=sha1"]
        if self.settings.os in ("FreeBSD", "Linux"):
            self.cpp_info.system_libs = ["pthread", "dl"]
        elif self.settings.os == "Android":
            self.cpp_info.system_libs = ["dl", "log"]
        elif self.settings.os == "Windows":
            self.cpp_info.system_libs = ["shlwapi", "dbghelp"]
            if tools.Version(self.version) >= "0.4.7":
                self.cpp_info.system_libs.append("Version")
            if self.options.transport == "winhttp":
                self.cpp_info.system_libs.append("winhttp")

        if not self.options.shared:
            self.cpp_info.defines = ["SENTRY_BUILD_STATIC"]
