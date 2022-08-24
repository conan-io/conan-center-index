from conan import ConanFile, tools
from conan.tools.cmake import CMake
from conan.errors import ConanInvalidConfiguration
import os

required_conan_version = ">=1.43.0"


class Iir1Conan(ConanFile):
    name = "iir1"
    license = "MIT"
    description = (
        "An infinite impulse response (IIR) filter library for Linux, Mac OSX "
        "and Windows which implements Butterworth, RBJ, Chebychev filters and "
        "can easily import coefficients generated by Python (scipy)."
    )
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/berndporr/iir1"
    topics = ("dsp", "signals", "filtering")

    settings = "os", "compiler", "build_type", "arch"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "noexceptions": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "noexceptions": False,
    }

    generators = "cmake"
    _cmake = None

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    @property
    def _build_subfolder(self):
        return "build_subfolder"

    @property
    def _min_cppstd(self):
        return "11"

    def export_sources(self):
        self.copy("CMakeLists.txt")
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            self.copy(patch["patch_file"])

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC
        if tools.Version(self.version) < "1.9.1":
            del self.options.noexceptions

    def configure(self):
        if self.options.shared:
            del self.options.fPIC

    def validate(self):
        if self.settings.compiler.get_safe("cppstd"):
            tools.check_min_cppstd(self, self._min_cppstd)

        compiler_version = tools.Version(self.settings.compiler.version)
        if self.settings.compiler == "gcc" and compiler_version <= 5:
            raise ConanInvalidConfiguration("GCC version < 5 not supported")

    def source(self):
        tools.get(**self.conan_data["sources"][self.version],
                  strip_root=True, destination=self._source_subfolder)

    def _configure_cmake(self):
        if self._cmake:
            return self._cmake

        self._cmake = CMake(self)
        self._cmake.definitions['IIR1_NO_EXCEPTIONS'] = self.options.get_safe("noexceptions", False)
        self._cmake.configure(build_folder=self._build_subfolder)
        return self._cmake

    def build(self):
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            tools.patch(**patch)
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        self.copy('COPYING', dst='licenses', src=self._source_subfolder)
        cmake = self._configure_cmake()
        cmake.install()
        tools.rmdir(os.path.join(self.package_folder, "lib", "cmake"))
        tools.rmdir(os.path.join(self.package_folder, "lib", "pkgconfig"))

        if self.options.shared:
            tools.remove_files_by_mask(os.path.join(self.package_folder, "lib"), "libiir_static.*")
            tools.remove_files_by_mask(os.path.join(self.package_folder, "lib"), "iir_static.*")
        else:
            tools.remove_files_by_mask(os.path.join(self.package_folder, "lib"), "iir.*")
            tools.remove_files_by_mask(os.path.join(self.package_folder, "bin"), "iir.*")
            tools.remove_files_by_mask(os.path.join(self.package_folder, "lib"), "libiir.*")
            tools.remove_files_by_mask(os.path.join(self.package_folder, "bin"), "libiir.*")

    def package_info(self):
        name = "iir" if self.options.shared else "iir_static"
        self.cpp_info.set_property("cmake_file_name", "iir")
        self.cpp_info.set_property("cmake_target_name", "iir::{}".format(name))
        self.cpp_info.set_property("pkg_config_name", "iir")

        self.cpp_info.names["cmake_find_package"] = "iir"
        self.cpp_info.names["cmake_find_package_multi"] = "iir"
        self.cpp_info.names["pkg_config"] = "iir"
        self.cpp_info.components["iir"].names["cmake_find_package"] = name
        self.cpp_info.components["iir"].names["cmake_find_package_multi"] = name
        self.cpp_info.components["iir"].set_property("cmake_target_name", "iir::{}".format(name))

        self.cpp_info.components["iir"].libs = [name]

        if self.options.get_safe("noexceptions", False):
            self.cpp_info.components["iir"].defines.append("IIR1_NO_EXCEPTIONS")

