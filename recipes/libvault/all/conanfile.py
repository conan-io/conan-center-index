from conans import ConanFile, tools, CMake
from conans.errors import ConanInvalidConfiguration
from conans.tools import Version
import os

required_conan_version = ">=1.33.0"


class LibvaultConan(ConanFile):
    name = "libvault"
    license = "MIT"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/abedra/libvault"
    description = "A C++ library for Hashicorp Vault"
    topics = ("vault", "libvault", "secrets", "passwords")
    settings = "os", "compiler", "build_type", "arch"
    generators = "cmake", "cmake_find_package"

    _cmake = None

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    @property
    def _build_subfolder(self):
        return "build_subfolder"

    @property
    def _mac_os_minimum_required_version(self):
        return "10.15"

    def requirements(self):
        self.requires("libcurl/7.80.0")
        self.requires("catch2/2.13.7")

    def validate(self):
        compiler = str(self.settings.compiler)
        compiler_version = Version(self.settings.compiler.version.value)

        lib_version = Version(self.version)
        minimum_compiler_version = {
            "Visual Studio": "19",
            "gcc": "8",
            "clang": "3.8",
            "apple-clang": "10"
        }

        minimum_cpp_standard = 17

        if compiler in minimum_compiler_version and \
           compiler_version < minimum_compiler_version[compiler]:
            raise ConanInvalidConfiguration("{} requires a compiler that supports"
                                            " at least C++{}. {} {} is not"
                                            " supported."
                                            .format(self.name, minimum_cpp_standard, compiler, compiler_version))

        if self.settings.os == "Macos":
            os_version = self.settings.get_safe("os.version")
            if os_version and Version(os_version) < self._mac_os_minimum_required_version:
                raise ConanInvalidConfiguration(
                    "Macos Mojave (10.14) and earlier cannot to be built because C++ standard library too old.")

        if self.settings.compiler.get_safe("cppstd"):
            tools.check_min_cppstd(self, minimum_cpp_standard)

    def package_id(self):
        self.info.header_only()

    def source(self):
        tools.get(
            **self.conan_data["sources"][self.version],
            destination=self._source_subfolder,
            strip_root=True
        )

    def _configure_cmake(self):
        if not self._cmake:
            self._cmake = CMake(self)
            self._cmake.definitions["ENABLE_TEST"] = False
            self._cmake.definitions["ENABLE_INTEGRATION_TEST"] = False
            self._cmake.definitions["ENABLE_COVERAGE"] = False
            self._cmake.definitions["LINK_CURL"] = False
            # Set `-mmacosx-version-min` to enable C++17 standard library support.
            self._cmake.definitions['CMAKE_OSX_DEPLOYMENT_TARGET'] = self._mac_os_minimum_required_version
            self._cmake.configure(build_folder=self._build_subfolder)
        return self._cmake

    def build(self):
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        self.copy("LICENSE", dst="licenses", src=self._source_subfolder)

        cmake = self._configure_cmake()
        cmake.install()

        self.copy("*", dst="bin", src=os.path.join(self._source_subfolder, "scripts"))

    def package_info(self):
        self.cpp_info.filenames["cmake_find_package"] = "Libvault"
        self.cpp_info.filenames["cmake_find_package_multi"] = "Libvault"

        bindir = os.path.join(self.package_folder, "bin")
        self.output.info("Appending PATH environment variable: {}".format(bindir))
        self.env_info.PATH.append(bindir)
