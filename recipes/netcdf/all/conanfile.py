import os
import glob
from conans import ConanFile, AutoToolsBuildEnvironment, tools


class NetcdfConan(ConanFile):
    name = "netcdf"
    description = ("NetCDF is a set of software libraries and "
                   "self-describing, machine-independent data "
                   "formats that support the creation, access, "
                   "and sharing of array-oriented scientific data.")
    license = "BSD-3-Clause"
    homepage = "https://www.unidata.ucar.edu/software/netcdf/"
    url = "https://github.com/conan-io/conan-center-index"
    topics = ("array", "dataset", "scientific")

    settings = "os", "compiler", "build_type", "arch"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "with_netcdf4": [True, False],
        "with_dap": [True, False],
        "with_utilities": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "with_netcdf4": True,
        "with_dap": True,
        "with_utilities": True,
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
        del self.settings.compiler.libcxx
        del self.settings.compiler.cppstd

    def requirements(self):
        if self.options.with_netcdf4:
            self.requires("hdf5/[>=1.8.9]")
        if self.options.with_dap:
            self.requires("libcurl/[>=7.18.0]")

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        extracted_dir = "netcdf-c-{}".format(self.version)
        os.rename(extracted_dir, self._source_subfolder)

    def build(self):
        args = [
            "--prefix={}".format(self.package_folder),
        ]

        if self.options.shared:
            args.append("--enable-shared")
            args.append("--disable-static")
        else:
            args.append("--disable-shared")
            args.append("--enable-static")

        if self.options.with_netcdf4:
            args.append("--enable-netcdf4")
        else:
            args.append("--disable-netcdf4")

        if self.options.with_dap:
            args.append("--enable-dap")
        else:
            args.append("--disable-netcdf4")

        if self.options.with_utilities:
            args.append("--enable-utilities")
        else:
            args.append("--disable-utilities")

        if self.options.get_safe("fPIC"):
            args.append('--with-pic')

        env_build = AutoToolsBuildEnvironment(self)
        env_build.configure(self._source_subfolder, args=args)
        env_build.make()

    def package(self):
        self.copy("COPYRIGHT", dst="licenses", src=self._source_subfolder)
        env_build = AutoToolsBuildEnvironment(self)
        env_build.make(["install"])
        tools.rmdir(os.path.join(self.package_folder, "lib", "pkgconfig"))
        for filename in glob.glob(
                os.path.join(self.package_folder, "lib", "*.la")):
            os.remove(filename)
        for filename in glob.glob(
                os.path.join(self.package_folder, "lib", "*.settings")):
            os.remove(filename)
        tools.rmdir(os.path.join(self.package_folder, "share"))

    def package_info(self):
        self.cpp_info.libs = ["netcdf"]

        self.env_info.PATH.append(os.path.join(self.package_folder, "bin"))
        if self.options.shared:
            self.env_info.LD_LIBRARY_PATH.append(
                    os.path.join(self.package_folder, "lib"))
            self.env_info.DYLD_LIBRARY_PATH.append(
                    os.path.join(self.package_folder, "lib"))
