from conans import ConanFile, tools, CMake
from conans.errors import ConanInvalidConfiguration
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
            self._cmake.definitions["CRASHPAD_ZLIB_SYSTEM"] = True
            self._cmake.configure()
        return self._cmake

    @property
    def _minimum_cpp_standard(self):
        return 14

    @property
    def _minimum_compilers_version(self):
        #TODO I only know it wont build on conan CCI with gcc < 5.
        # I left the rest of the compilers as place holders, check this.
        return {
            "Visual Studio": "15",
            "gcc": "5",
            "clang": "6",
            "apple-clang": "8",
        }

    def requirements(self):
        if self.settings.os == "Linux":
            self.requires("linux-syscall-support/cci.20200813", private=True)
        self.requires("zlib/1.2.11")
        self.requires("openssl/1.1.1k")

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            del self.options.fPIC
        if self.settings.compiler.cppstd:
            tools.check_min_cppstd(self, self._minimum_cpp_standard)
        min_version = self._minimum_compilers_version.get(str(self.settings.compiler))
        if not min_version:
            self.output.warn("{} recipe lacks information about the {} compiler support.".format(self.name, self.settings.compiler))
        else:
            if tools.Version(self.settings.compiler.version) < min_version:
                raise ConanInvalidConfiguration("{} requires C++{} support. The current compiler {} {} does not support it.".format(
                    self.name, self._minimum_cpp_standard, self.settings.compiler, self.settings.compiler.version))

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
        self.cpp_info.libs = ["crashpad_minidump","crashpad_snapshot","crashpad_client","crashpad_util", "mini_chromium","crashpad_compat"]
        # TODO Check if sentry if installing this correctly, I think it should be include/crashpad and include/mini_chromium
        self.cpp_info.includedirs = [ os.path.join("include", "crashpad"), os.path.join("include","crashpad", "mini_chromium") ]
        # TODO check if m is needed
        if self.settings.os == "Linux":
            self.cpp_info.system_libs = ["dl", "m", "pthread"]
