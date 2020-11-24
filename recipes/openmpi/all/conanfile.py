from conans import ConanFile, tools, AutoToolsBuildEnvironment
from conans.errors import ConanInvalidConfiguration
from os import path, rename


class OpenmpiConan(ConanFile):
    name = "openmpi"
    license = "BSD-3-Clause"
    url = "https://github.com/conan-io/conan-center-index"
    description = "A High Performance Message Passing Library"
    topics = ("conan", "openmpi", "mpi")
    homepage = "https://www.open-mpi.org/"
    settings = "os", "compiler", "build_type", "arch"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
    }
    default_options = {"shared": False, "fPIC": True}
    generators = "cmake"
    _autotools = None


    @property
    def _build_subfolder(self):
        return path.join(self.build_folder, "build_subfolder")

    @property
    def _source_subfolder(self):
        return path.join(self.build_folder, "source_subfolder")



    def _configure_autotools(self):
        if self._autotools:
            return self._autotools

        configure_folder = path.join(self.build_folder, self._source_subfolder)
        self._autotools = AutoToolsBuildEnvironment(self)
        self._autotools.fpic = self.options.fPIC

        args = ["--prefix={}".format(self._build_subfolder)]
        args.append("--with-pic" if self.options.fPIC else "--without-pic")

        if self.settings.build_type == "Debug":
            args.append("--enable-debug")
        if self.options.shared:
            args.extend(["--enable-shared", "--disable-static"])
        else:
            args.extend(["--enable-static", "--disable-shared"])

        self._autotools.configure(
            configure_dir=configure_folder,
            args=args
        )

        return self._autotools

    def config_options(self):
        if self.settings.os == "Windows":
            raise ConanInvalidConfiguration(
                "OpenMPI is not supported on Windows systems"
            )


    def source(self):
        self.output.info("Downloading OpenMPI from the mirror")

        tools.get(**self.conan_data["sources"][self.version])
        rename(
            "{name}-{version}".format(
                name=self.name, version=self.version
            ),
            "source_subfolder"
        )

    def build(self):
        autotools = self._configure_autotools()
        autotools.make()
        autotools.install()

    def package(self):
        bin_dir = path.join(self._build_subfolder, "bin")
        lib_dir = path.join(self._build_subfolder, "lib")
        include_dir = path.join(self._build_subfolder, "include")

        self.copy("LICENSE", src=self._source_subfolder, dst="licenses")

        self.copy("*", src=bin_dir, dst="bin")
        self.copy("*so", src=lib_dir, dst="lib")
        self.copy("*", src=include_dir, dst="include")

    def package_info(self):
        self.cpp_info.libs = ["mpi", "open-rte", "open-pal"]
        if self.settings.os == "Linux":
            self.cpp_info.system_libs = ["dl", "pthread", "rt", "util"]
        self.env_info.MPI_HOME = self.package_folder
        mpi_bin = path.join(self.package_folder, "bin")
        self.env_info.MPI_BIN = mpi_bin
        self.env_info.PATH.append(mpi_bin)
