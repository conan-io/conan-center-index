from conans import ConanFile, tools, CMake
import os
import stat
import glob
import shutil
from textwrap import dedent

class getSentryCrashpadConan(ConanFile):
    name = "getsentry-crashpad"
    license = "Apache-2.0"
    homepage = "https://github.com/getsentry/crashpad"
    url = "https://github.com/conan-io/conan-center-index"
    description = ("A fork of Google's crashpart with CMake support")
    settings = "os", "arch", "compiler", "build_type"
    options = {"shared": [True, False], "fPIC": [True, False]}
    default_options = {'shared': False, "fPIC": True}
    generators = "cmake", "cmake_find_package"
    topics = ("conan", "crashpad", "crash", "report")
    exports_sources = ["CMakeLists.txt", "patches/*"]
    _cmake = None

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def _configure_cmake(self):
        if not self._cmake:
            self._cmake = CMake(self)
            self._cmake.definitions["CRASHPAD_ENABLE_INSTALL"] = True
            self._cmake.definitions["CRASHPAD_ENABLE_INSTALL_DEV"] = True
            self._cmake.configure()
        return self._cmake

    def requirements(self):
        if self.settings.os == "Linux":
            self.requires("linux-syscall-support/cci.20200813")
        self.requires("zlib/1.2.11")
        self.requires("openssl/1.1.1k")

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        extracted_dir = glob.glob('crashpad-*/')[0]
        os.rename(extracted_dir, self._source_subfolder)

        # mini-chromium is a submodule. We need the sources and not the artifacts so we can't make it a conan package.
        miniChroimiumPath = os.path.join(self._source_subfolder, "third_party", "mini_chromium", "mini_chromium")
        self.run("git clone https://chromium.googlesource.com/chromium/mini_chromium {}".format(miniChroimiumPath))
        with tools.chdir(miniChroimiumPath):
            # Lock to a random commit to get reproducible builds.
            self.run("git checkout 329ca82f73a592d832e79334bed842fba85b9fdd")

    def build(self):
        #TODO make this a conan patch
        # Use conan's linux_syscall_support
        tools.replace_in_file(os.path.join(self._source_subfolder, "third_party","lss", "lss.h"),
        """#include "third_party/lss/lss/linux_syscall_support.h""",
        """#include "linux_syscall_support.h""")

        old = """if(LINUX OR ANDROID)"""
        new = """\
            if(LINUX OR ANDROID)
                find_package(linux-syscall-support REQUIRED)"""
        tools.replace_in_file(os.path.join(self._source_subfolder, "CMakeLists.txt"), dedent(old), dedent(new))

        #TODO make this a patch to the upstream sources
        old = """\
            crashpad_install_dev(DIRECTORY mini_chromium
                DESTINATION "${CMAKE_INSTALL_INCLUDEDIR}/crashpad"
                FILES_MATCHING PATTERN "*.h"
            )"""
        new = """\
            crashpad_install_dev(DIRECTORY mini_chromium
                DESTINATION "${CMAKE_INSTALL_INCLUDEDIR}/crashpad"
                FILES_MATCHING PATTERN "*.h"
            )
            crashpad_install_dev(DIRECTORY build
                DESTINATION "${CMAKE_INSTALL_INCLUDEDIR}/crashpad"
                FILES_MATCHING PATTERN "*.h"
            )"""
        tools.replace_in_file(os.path.join(self._source_subfolder, "third_party", "mini_chromium", "CMakeLists.txt"), dedent(old), dedent(new))
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        self.copy("LICENSE", src=self._source_subfolder, dst="licenses")
        cmake = self._configure_cmake()
        cmake.install()
        tools.rmdir(os.path.join(self.package_folder, "lib", "cmake"))

    def package_info(self):
        # TODO Check if using collect_libs() is safe.
        self.cpp_info.libs = tools.collect_libs(self)
        # TODO Check if sentry if installing this correctly, I think it should be include/crashpad and include/mini_chromium
        self.cpp_info.includedirs = [ os.path.join("include", "crashpad"), os.path.join("include","crashpad", "mini_chromium") ]
        # TODO check if m is needed
        if self.settings.os == "Linux":
            self.cpp_info.system_libs = ["dl", "m", "pthread"]
