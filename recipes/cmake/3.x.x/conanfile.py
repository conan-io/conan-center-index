import os
from conan import ConanFile
from conan.tools.scm import Version
from conan.tools.files import rmdir, get
from conans import tools, AutoToolsBuildEnvironment, CMake
from conan.errors import ConanInvalidConfiguration, ConanException

required_conan_version = ">=1.49.0"

class CMakeConan(ConanFile):
    name = "cmake"
    description = "Conan installer for CMake"
    topics = ("cmake", "build", "installer")
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/Kitware/CMake"
    license = "BSD-3-Clause"
    generators = "cmake"
    settings = "os", "arch", "compiler", "build_type"

    options = {
        "with_openssl": [True, False],
        "bootstrap": [True, False],
    }
    default_options = {
        "with_openssl": True,
        "bootstrap": False,
    }

    _source_subfolder = "source_subfolder"
    _cmake = None

    def config_options(self):
        if self.settings.os == "Windows":
            self.options.with_openssl = False

    def requirements(self):
        if self.options.with_openssl:
            self.requires("openssl/1.1.1q")

    def validate(self):
        if self.settings.os == "Macos" and self.settings.arch == "x86":
            raise ConanInvalidConfiguration("CMake does not support x86 for macOS")

        if self.settings.os == "Windows" and self.options.bootstrap:
            raise ConanInvalidConfiguration("CMake does not support bootstrapping on Windows")

        minimal_cpp_standard = "11"
        if self.settings.compiler.cppstd:
            tools.check_min_cppstd(self, minimal_cpp_standard)

        minimal_version = {
            "gcc": "4.8",
            "clang": "3.3",
            "apple-clang": "9",
            "Visual Studio": "14",
        }

        compiler = str(self.settings.compiler)
        if compiler not in minimal_version:
            self.output.warn(
                "{} recipe lacks information about the {} compiler standard version support".format(self.name, compiler))
            self.output.warn(
                "{} requires a compiler that supports at least C++{}".format(self.name, minimal_cpp_standard))
            return

        version = Version(self.settings.compiler.version)
        if version < minimal_version[compiler]:
            raise ConanInvalidConfiguration(
                "{} requires a compiler that supports at least C++{}".format(self.name, minimal_cpp_standard))

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True, destination=self._source_subfolder)

    def _configure_cmake(self):
        if not self._cmake:
            self._cmake = CMake(self)
            if not self.settings.compiler.cppstd:
                self._cmake.definitions["CMAKE_CXX_STANDARD"] = 11
            self._cmake.definitions["CMAKE_BOOTSTRAP"] = False
            if self.settings.os == "Linux":
                self._cmake.definitions["CMAKE_USE_OPENSSL"] = self.options.with_openssl
                if self.options.with_openssl:
                    self._cmake.definitions["OPENSSL_USE_STATIC_LIBS"] = not self.options["openssl"].shared
            if tools.cross_building(self):
                self._cmake.definitions["HAVE_POLL_FINE_EXITCODE"] = ''
                self._cmake.definitions["HAVE_POLL_FINE_EXITCODE__TRYRUN_OUTPUT"] = ''
            self._cmake.configure(source_folder=self._source_subfolder)

        return self._cmake

    def build(self):
        if self.options.bootstrap:
            with tools.chdir(self._source_subfolder):
                self.run(['./bootstrap', '--prefix={}'.format(self.package_folder), '--parallel={}'.format(tools.cpu_count())])
                autotools = AutoToolsBuildEnvironment(self)
                autotools.make()
        else:
            tools.replace_in_file(os.path.join(self._source_subfolder, "CMakeLists.txt"),
                                  "project(CMake)",
                                  "project(CMake)\ninclude(\"{}/conanbuildinfo.cmake\")\nconan_basic_setup(NO_OUTPUT_DIRS)".format(
                                      self.install_folder.replace("\\", "/")))
            if self.settings.os == "Linux":
                tools.replace_in_file(os.path.join(self._source_subfolder, "Utilities", "cmcurl", "CMakeLists.txt"),
                                      "list(APPEND CURL_LIBS ${OPENSSL_LIBRARIES})",
                                      "list(APPEND CURL_LIBS ${OPENSSL_LIBRARIES} ${CMAKE_DL_LIBS} pthread)")

            cmake = self._configure_cmake()
            cmake.build()

    def package(self):
        self.copy("Copyright.txt", dst="licenses", src=self._source_subfolder)
        if self.options.bootstrap:
            with tools.chdir(self._source_subfolder):
                autotools = AutoToolsBuildEnvironment(self)
                autotools.install()
        else:
            cmake = self._configure_cmake()
            cmake.install()
        rmdir(self, os.path.join(self.package_folder, "doc"))

    def package_id(self):
        del self.info.settings.compiler

    def package_info(self):
        module_version = "{}.{}".format(Version(self.version).major, Version(self.version).minor)

        bindir = os.path.join(self.package_folder, "bin")
        self.output.info("Appending PATH environment variable: {}".format(bindir))
        self.env_info.PATH.append(bindir)

        self.buildenv_info.prepend_path("CMAKE_ROOT", self.package_folder)
        self.env_info.CMAKE_ROOT = self.package_folder
        mod_path = os.path.join(self.package_folder, "share", f"cmake-{module_version}", "Modules")
        self.buildenv_info.prepend_path("CMAKE_MODULE_PATH", mod_path)
        self.env_info.CMAKE_MODULE_PATH = mod_path
        if not os.path.exists(mod_path):
            raise ConanException("Module path not found: %s" % mod_path)

        self.cpp_info.includedirs = []
