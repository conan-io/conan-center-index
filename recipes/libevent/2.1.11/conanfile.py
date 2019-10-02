from conans import ConanFile, CMake, tools
import os
import shutil


class LibeventConan(ConanFile):
    name = "libevent"
    description = "libevent - an event notification library"
    topics = ("conan", "libevent", "event")
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/libevent/libevent"
    author = "Bincrafters <bincrafters@gmail.com>"
    license = "BSD-3-Clause"
    exports_sources = ["CMakeLists.txt"]
    settings = "os", "compiler", "build_type", "arch"
    options = {"shared": [True, False],
               "fPIC": [True, False],
               "with_openssl": [True, False],
               "disable_threads": [True, False]}
    default_options = {"shared": False,
                       "fPIC": True,
                       "with_openssl": True,
                       "disable_threads": False}
    generators = "cmake"
    _source_subfolder = "source_subfolder"

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        del self.settings.compiler.libcxx
        del self.settings.compiler.cppstd
        if self.options.with_openssl and self.options.shared:
            # static OpenSSL cannot be properly detected because libevent picks up system ssl first
            # so enforce shared openssl
            self.output.warn("Enforce shared OpenSSL for shared build")
            self.options["openssl"].shared = self.options.shared

    def requirements(self):
        if self.options.with_openssl:
            self.requires.add("openssl/1.1.1d")

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        # temporary fix due to missing files in dist package for 2.1.11, see upstream bug 863
        # for other versions "libevent-{0}-stable".format(self.version) is enough
        extracted_folder = "libevent-release-{0}-stable".format(self.version)
        os.rename(extracted_folder, self._source_subfolder)

        os.rename(os.path.join(self._source_subfolder, "CMakeLists.txt"),
                  os.path.join(self._source_subfolder, "CMakeListsOriginal.txt"))
        shutil.copy("CMakeLists.txt",
                    os.path.join(self._source_subfolder, "CMakeLists.txt"))

        # patch 'beta' to 'stable' because there is no git repository which cmake uses to determine stage name
        # needed for 2.1.10, not needed for 2.1.11 so marked as non-strict
        tools.replace_in_file(os.path.join(self._source_subfolder, "cmake", "VersionViaGit.cmake"),
                              'set(EVENT_GIT___VERSION_STAGE "beta")',
                              'set(EVENT_GIT___VERSION_STAGE "stable")',
                              strict=False)

    def imports(self):
        # Copy shared libraries for dependencies to fix DYLD_LIBRARY_PATH problems
        #
        # Configure script creates conftest that cannot execute without shared openssl binaries.
        # Ways to solve the problem:
        # 1. set *LD_LIBRARY_PATH (works with Linux with RunEnvironment
        #     but does not work on OS X 10.11 with SIP)
        # 2. copying dylib's to the build directory (fortunately works on OS X)

        if self.settings.os == "Macos":
            self.copy("*.dylib*", dst=self._source_subfolder, keep_path=False)

    def _configure_cmake(self):
        cmake = CMake(self)
        cmake.definitions["EVENT__LIBRARY_TYPE"] = "SHARED" if self.options.shared else "STATIC"
        cmake.definitions["EVENT__DISABLE_DEBUG_MODE"] = self.settings.build_type == "Release"
        cmake.definitions["EVENT__DISABLE_OPENSSL"] = not self.options.with_openssl
        cmake.definitions["EVENT__DISABLE_THREAD_SUPPORT"] = self.options.disable_threads
        cmake.definitions["EVENT__DISABLE_BENCHMARK"] = True
        cmake.definitions["EVENT__DISABLE_TESTS"] = True
        cmake.definitions["EVENT__DISABLE_REGRESS"] = True
        cmake.definitions["EVENT__DISABLE_SAMPLES"] = True
        # libevent uses static runtime (MT) for static builds by default
        cmake.definitions["EVENT__MSVC_STATIC_RUNTIME"] = self.settings.compiler == "Visual Studio" and \
                self.settings.compiler.runtime == "MT"
        cmake.configure(source_folder=self._source_subfolder)
        return cmake

    def build(self):
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        self.copy("LICENSE", src=self._source_subfolder, dst="licenses")
        cmake = self._configure_cmake()
        cmake.install()
        # drop pc and cmake file
        tools.rmdir(os.path.join(self.package_folder, 'lib', 'pkgconfig'))
        tools.rmdir(os.path.join(self.package_folder, 'lib', 'cmake'))
        tools.rmdir(os.path.join(self.package_folder, 'cmake'))

    def package_info(self):
        self.cpp_info.libs = tools.collect_libs(self)
        if self.settings.os == "Linux":
            self.cpp_info.libs.extend(["rt"])

        if self.settings.os == "Windows":
            self.cpp_info.libs.append('ws2_32')
            if self.options.with_openssl:
                self.cpp_info.defines.append('EVENT__HAVE_OPENSSL=1')
