from conans import ConanFile, tools, AutoToolsBuildEnvironment
from os import path


class OpenmpiConan(ConanFile):
    name = "openmpi"
    license = "3-clause BSD license"
    author = "Conan Community"
    url = "https://github.com/conan-io/conan-center-index"
    description = "A High Performance Message Passing Library"
    topics = ("conan", "openmpi", "mpi")
    homepage = "https://www.open-mpi.org/"
    settings = "os", "compiler", "build_type", "arch"
    options = {"shared": [True, False]}
    default_options = {"shared": False}
    generators = "cmake"

    def source(self):
        self.output.info("Downloading OpenMPI from the mirror")

        url = self.conan_data["sources"][self.version]["url"]
        tools.get(
            url,
            sha1=self.conan_data["sources"][self.version]["sha1"],
            md5=self.conan_data["sources"][self.version]["md5"],
        )

    def build(self):
        autotools = AutoToolsBuildEnvironment(self)

        folder_name = "{name}-{version}".format(
            name=self.name, version=self.version
        )

        autotools.configure(
            configure_dir=path.join(self.build_folder, folder_name)
        )
        autotools.make()
        autotools.install()

    def package_info(self):
        pkg_config_path = path.join(self.package_folder, "lib", "pkgconfig")
        with tools.environment_append({"PKG_CONFIG_PATH": pkg_config_path}):
            pkg_config_c = tools.PkgConfig(
                "ompi-c", static=not self.options.shared
            )
            pkg_config_cxx = tools.PkgConfig(
                "ompi-cxx", static=not self.options.shared
            )
            self.cpp_info.cflags = pkg_config_c.cflags
            self.cpp_info.cxxflags = pkg_config_cxx.cflags
            self.cpp_info.sharedlinkflags = pkg_config_c.libs
            self.cpp_info.exelinkflags = pkg_config_c.libs
