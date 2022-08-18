from conan import ConanFile
from conan.tools.scm import Version
from conan.tools import files
from conans import CMake
from conan.errors import ConanInvalidConfiguration
import os

required_conan_version = ">=1.33.0"


class DoxygenConan(ConanFile):
    name = "doxygen"
    description = "A documentation system for C++, C, Java, IDL and PHP --- Note: Dot is disabled in this package"
    topics = ("doxygen", "installer", "devtool", "documentation")
    homepage = "https://github.com/doxygen/doxygen"
    license = "GPL-2.0-or-later"
    url = "https://github.com/conan-io/conan-center-index"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "enable_parse": [True, False],
        "enable_search": [True, False],
    }
    default_options = {
        "enable_parse": True,
        "enable_search": True,
    }

    exports_sources = "CMakeLists.txt", "patches/*"
    generators = "cmake", "cmake_find_package"
    short_paths = True

    _cmake = None

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    @property
    def _build_subfolder(self):
        return "build_subfolder"

    @property
    def _settings_build(self):
        return getattr(self, "settings_build", self.settings)

    def _minimum_compiler_version(self):
        if Version(self.version) <= "1.9.1":
            return {
                "gcc": 5,
            }.get(str(self.settings.compiler))
        return {
            "gcc": 7,  # https://gcc.gnu.org/bugzilla/show_bug.cgi?id=66297
            "Visual Studio": 15,
        }.get(str(self.settings.compiler))

    def configure(self):
        del self.settings.compiler.cppstd
    def requirements(self):
        if self.options.enable_search:
            self.requires("xapian-core/1.4.19")
            self.requires("zlib/1.2.12")

    def build_requirements(self):
        if self._settings_build.os == "Windows":
            self.build_requires("winflexbison/2.5.24")
        else:
            self.build_requires("flex/2.6.4")
            self.build_requires("bison/3.7.1")

    def validate(self):
        minimum_compiler_version = self._minimum_compiler_version()
        if minimum_compiler_version is not None:
            if Version(self.settings.compiler.version) < minimum_compiler_version:
                raise ConanInvalidConfiguration(f"Compiler version too old. At least {minimum_compiler_version} is required.")
        if (self.settings.compiler == "Visual Studio" and
                Version(self.settings.compiler.version) <= "14" and
                Version(self.version) == "1.8.18"):
            raise ConanInvalidConfiguration(f"Doxygen version {self.version} broken with VS {self.settings.compiler.version}.")

    def package_id(self):
        del self.info.settings.compiler

        # Doxygen doesn't make code. Any package that will run is ok to use.
        # It's ok in general to use a release version of the tool that matches the
        # build os and architecture.
        compatible_pkg = self.info.clone()
        compatible_pkg.settings.build_type = "Release"
        self.compatible_packages.append(compatible_pkg)

    def source(self):
        files.get(**self.conan_data["sources"][self.version],
                  destination=self._source_subfolder, strip_root=True)

    def _configure_cmake(self):
        if self._cmake:
            return self._cmake
        self._cmake = CMake(self)
        self._cmake.definitions["build_parse"] = self.options.enable_parse
        self._cmake.definitions["build_search"] = self.options.enable_search
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
            files.patch(**patch)
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        self.copy("LICENSE", src=self._source_subfolder, dst="licenses")
        cmake = self._configure_cmake()
        cmake.install()

    def package_info(self):
        self.cpp_info.libdirs = []
        bin_path = os.path.join(self.package_folder, "bin")
        self.output.info(f"Appending PATH environment variable: {bin_path}")
        self.env_info.PATH.append(bin_path)
