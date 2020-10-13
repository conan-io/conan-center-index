import os
from conans import tools, ConanFile, CMake
from conans.errors import ConanInvalidConfiguration, ConanException


class CMakeConan(ConanFile):
    name = "cmake"
    description = "Conan installer for CMake"
    topics = ("conan", "cmake", "build", "installer")
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/Kitware/CMake"
    license = "BSD-3-Clause"
    generators = "cmake"
    settings = "os", "arch", "compiler", "build_type"

    options = {
        "with_openssl": [True, False, "auto"],
    }
    default_options = {
        "with_openssl": "auto",
    }

    _source_subfolder = "source_subfolder"
    _cmake = None

    def _minor_version(self):
        return ".".join(str(self.version).split(".")[:2])

    @property
    def _with_openssl(self):
        if self.options.with_openssl == "auto":
            return self.settings.os != "Windows"
        return self.options.with_openssl

    def configure(self):
        if self.settings.os == "Macos" and self.settings.arch == "x86":
            raise ConanInvalidConfiguration("CMake does not support x86 for macOS")

        minimal_cpp_standard = "11"
        if self.settings.compiler.cppstd:
            tools.check_min_cppstd(self, minimal_cpp_standard)

        minimal_version = {
            "gcc": "5",
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

        version = tools.Version(self.settings.compiler.version)
        if version < minimal_version[compiler]:
            raise ConanInvalidConfiguration(
                "{} requires a compiler that supports at least C++{}".format(self.name, minimal_cpp_standard))

    def requirements(self):
        if self._with_openssl:
            self.requires("openssl/1.1.1h")

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        extracted_dir = self.name + "-" + self.version
        os.rename(extracted_dir, self._source_subfolder)

    def _configure_cmake(self):
        if not self._cmake:
            self._cmake = CMake(self)
            if not self.settings.compiler.cppstd:
                self._cmake.definitions["CMAKE_CXX_STANDARD"] = 11
            self._cmake.definitions["CMAKE_BOOTSTRAP"] = False
            if self.settings.os == "Linux":
                self._cmake.definitions["CMAKE_USE_OPENSSL"] = self._with_openssl
                if self._with_openssl:
                    self._cmake.definitions["OPENSSL_USE_STATIC_LIBS"] = not self.options["openssl"].shared
            self._cmake.configure(source_folder=self._source_subfolder)
        return self._cmake

    def build(self):
        tools.replace_in_file(os.path.join(self._source_subfolder, "CMakeLists.txt"),
                              "project(CMake)",
                              "project(CMake)\ninclude(\"{}/conanbuildinfo.cmake\")\nconan_basic_setup()".format(
                                  self.build_folder.replace("\\", "/")))
        if self.settings.os == "Linux":
            tools.replace_in_file(os.path.join(self._source_subfolder, "Utilities", "cmcurl", "CMakeLists.txt"),
                                  "list(APPEND CURL_LIBS ${OPENSSL_LIBRARIES})",
                                  "list(APPEND CURL_LIBS ${OPENSSL_LIBRARIES} -ldl -lpthread)")
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        self.copy("Copyright.txt", dst="licenses", src=self._source_subfolder)
        cmake = self._configure_cmake()
        cmake.install()
        tools.rmdir(os.path.join(self.package_folder, "doc"))

    def package_id(self):
        self.info.options.with_openssl = self._with_openssl
        del self.info.settings.compiler

    def package_info(self):
        minor = self._minor_version()

        bindir = os.path.join(self.package_folder, "bin")
        self.output.info("Appending PATH environment variable: {}".format(bindir))
        self.env_info.PATH.append(bindir)

        self.env_info.CMAKE_ROOT = self.package_folder
        mod_path = os.path.join(self.package_folder, "share", "cmake-%s" % minor, "Modules")
        self.env_info.CMAKE_MODULE_PATH = mod_path
        if not os.path.exists(mod_path):
            raise ConanException("Module path not found: %s" % mod_path)
