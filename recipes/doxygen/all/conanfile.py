from conans import CMake, ConanFile, tools
from conans.errors import ConanInvalidConfiguration
import os


class DoxygenConan(ConanFile):
    name = "doxygen"
    description = "A documentation system for C++, C, Java, IDL and PHP --- Note: Dot is disabled in this package"
    topics = ("conan", "doxygen", "installer", "devtool", "documentation")
    homepage = "https://github.com/doxygen/doxygen"
    license = "GPL-2.0-or-later"
    url = "https://github.com/conan-io/conan-center-index"
    settings = "os", "arch", "compiler", "build_type"
    exports_sources = "CMakeLists.txt", "patches/**"
    generators = "cmake", "cmake_find_package"
    short_paths = True

    _cmake = None

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    @property
    def _build_subfolder(self):
        return "build_subfolder"

    _minimum_compiler_version = {
        "gcc": 5,
    }

    def configure(self):
        minimum_compiler_version = self._minimum_compiler_version.get(str(self.settings.compiler))
        if minimum_compiler_version is not None:
            if tools.Version(self.settings.compiler.version) < minimum_compiler_version:
                raise ConanInvalidConfiguration("Compiler version too old. At least {} is required.".format(minimum_compiler_version))
        if (self.settings.compiler == "Visual Studio" and
            tools.Version(self.settings.compiler.version.value) <= 14 and
                tools.Version(self.version) == "1.8.18"):
            raise ConanInvalidConfiguration("Doxygen version {} broken with VS {}.".format(self.version,
                                                                                           self.settings.compiler.version))
        del self.settings.compiler.cppstd

    def requirements(self):
        self.requires("xapian-core/1.4.18")
        self.requires("zlib/1.2.11")

    def build_requirements(self):
        if tools.os_info.is_windows:
            self.build_requires("winflexbison/2.5.22")
        else:
            self.build_requires("flex/2.6.4")
            self.build_requires("bison/3.7.1")

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        os.rename("{}-{}".format(self.name, self.version), self._source_subfolder)

    def _configure_cmake(self):
        if self._cmake:
            return self._cmake
        self._cmake = CMake(self)
        self._cmake.definitions["build_parse"] = True
        self._cmake.definitions["build_search"] = True
        self._cmake.definitions["use_libc++"] = self.settings.compiler.get_safe("libcxx") == "libc++"
        self._cmake.definitions["win_static"] = "MT" in self.settings.compiler.get_safe("runtime", "")
        self._cmake.configure(build_folder=self._build_subfolder)
        return self._cmake

    def build(self):
        if os.path.isfile("Findflex.cmake"):
            os.unlink("Findflex.cmake")
        if os.path.isfile("Findbison.cmake"):
            os.unlink("Findbison.cmake")
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            tools.patch(**patch)
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        self.copy("LICENSE", src=self._source_subfolder, dst="licenses")
        cmake = self._configure_cmake()
        cmake.install()

    def package_id(self):
        del self.info.settings.compiler

    def package_info(self):
        bin_path = os.path.join(self.package_folder, "bin")
        self.output.info("Appending PATH environment variable: {}".format(bin_path))
        self.env_info.PATH.append(bin_path)
