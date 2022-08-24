from conans import ConanFile, Meson, tools
from conan.errors import ConanInvalidConfiguration
from conan.tools.build import cross_building
import os
import functools

class InihConan(ConanFile):
    name = "inih"
    description = "Simple .INI file parser in C, good for embedded systems "
    license = "BSD-3-Clause"
    topics = ("inih", "ini", "configuration", "parser")
    homepage = "https://github.com/benhoyt/inih"
    url = "https://github.com/conan-io/conan-center-index"
    generators = "cmake"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
    }

    default_options = {
        "shared": False,
        "fPIC": True,
    }

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    @property
    def _build_subfolder(self):
        return "build_subfolder"

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            del self.options.fPIC
        del self.settings.compiler.cppstd
        del self.settings.compiler.libcxx

    def validate(self):
        if self.options.shared and self.settings.os == "Windows":
            raise ConanInvalidConfiguration("Shared inih is not supported")
        if hasattr(self, "settings_build") and cross_building(self):
            raise ConanInvalidConfiguration("Cross-building not implemented")

    def build_requirements(self):
        self.build_requires("meson/0.61.2")

    def source(self):
        tools.files.get(self, **self.conan_data["sources"][self.version])
        os.rename("{}-r{}".format(self.name, self.version), self._source_subfolder)

    @functools.lru_cache(1)
    def _configure_meson(self):
        meson = Meson(self)
        meson.options["distro_install"] = True
        meson.options["with_INIReader"] = True
        meson.configure(source_folder=self._source_subfolder, build_folder=self._build_subfolder)
        return meson

    def build(self):
        meson = self._configure_meson()
        meson.build()

    def package(self):
        self.copy("LICENSE.txt", dst="licenses", src=self._source_subfolder)
        meson = self._configure_meson()
        meson.install()
        tools.rmdir(os.path.join(self.package_folder, "lib", "pkgconfig"))

        if self.settings.compiler == "Visual Studio":
            # https://github.com/mesonbuild/meson/issues/7378
            os.rename(os.path.join(self.package_folder, "lib", "libinih.a"),
                      os.path.join(self.package_folder, "lib", "inih.lib"))
            os.rename(os.path.join(self.package_folder, "lib", "libINIReader.a"),
                      os.path.join(self.package_folder, "lib", "INIReader.lib"))

    def package_info(self):
        self.cpp_info.names["cmake_find_package"] = "inih"
        self.cpp_info.names["cmake_find_package_multi"] = "inih"
        self.cpp_info.set_property("cmake_file_name", "inih")

        self.cpp_info.components["libinih"].libs = ["inih"]
        self.cpp_info.components["libinih"].names["cmake_find_package"] = "inih"
        self.cpp_info.components["libinih"].names["cmake_find_package_multi"] = "inih"
        self.cpp_info.components["libinih"].set_property("cmake_target_name", "inih::inih")
        self.cpp_info.components["libinih"].set_property("pkg_config_name", "inih")

        self.cpp_info.components["INIReader"].libs = ["INIReader"]
        self.cpp_info.components["INIReader"].names["cmake_find_package"] = "INIReader"
        self.cpp_info.components["INIReader"].names["cmake_find_package_multi"] = "INIReader"
        self.cpp_info.components["INIReader"].requires = ["libinih"]
        self.cpp_info.components["INIReader"].set_property("cmake_target_name", "inih::INIReader")
        self.cpp_info.components["INIReader"].set_property("pkg_config_name", "INIReader")
