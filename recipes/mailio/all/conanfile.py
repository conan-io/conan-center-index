from conans import ConanFile, CMake, tools
from conans.errors import ConanInvalidConfiguration
import glob
import os


class mailioConan(ConanFile):
    name = "mailio"
    license = "BSD-2-Clause"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/karastojko/mailio"
    description = "mailio is a cross platform C++ library for MIME format and SMTP, POP3 and IMAP protocols."
    topics = ("conan", "smtp", "imap", "email", "mail", "libraries", "cpp")
    settings = "os", "compiler", "build_type", "arch"
    options = {
        "fPIC": [True, False],
        "shared": [True, False]
    }
    default_options = {
        "fPIC": True,
        "shared": False
    }
    requires = ["boost/1.75.0", "openssl/1.1.1i"]
    generators = "cmake"
    exports_sources = ["CMakeLists.txt", "patches/**"]
    short_paths = True
    _cmake = None

    _compiler_required_cpp17 = {
        "gcc": "7",
        "clang": "6",
        "Visual Studio": "15",
        "apple-clang": "10",
    }

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    @property
    def _build_subfolder(self):
        return "build_subfolder"

    def _configure_cmake(self):
        if not self._cmake:
            self._cmake = CMake(self)
            self._cmake.definitions["MAILIO_BUILD_SHARED_LIBRARY"] = self.options.shared
            self._cmake.definitions["MAILIO_BUILD_DOCUMENTATION"] = False
            self._cmake.definitions["MAILIO_BUILD_EXAMPLES"] = False
            self._cmake.configure(build_folder=self._build_subfolder)
        return self._cmake

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        extracted_dir = glob.glob("mailio-*/")[0]
        os.rename(extracted_dir, self._source_subfolder)

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            del self.options.fPIC

        if self.settings.get_safe("compiler.cppstd"):
            tools.check_min_cppstd(self, "17")
        try:
            minimum_required_compiler_version = self._compiler_required_cpp17[str(self.settings.compiler)]
            if tools.Version(self.settings.compiler.version) < minimum_required_compiler_version:
                raise ConanInvalidConfiguration("This package requires c++17 support. The current compiler does not support it.")
        except KeyError:
            self.output.warn("This recipe has no support for the current compiler. Please consider adding it.")

    def build(self):
        patches = self.conan_data["patches"][self.version]
        for patch in patches:
            tools.patch(**patch)

        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        cmake = self._configure_cmake()
        cmake.install()
        self.copy("LICENSE", dst="licenses", src=self._source_subfolder)
        tools.rmdir(os.path.join(self.package_folder, "lib", "pkgconfig"))

    def package_info(self):
        self.cpp_info.libs = tools.collect_libs(self)
