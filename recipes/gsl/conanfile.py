from conans import ConanFile, tools, AutoToolsBuildEnvironment
import os


class GslConan(ConanFile):
    name = "gsl"
    license = "GNU GPL"
    url = "http://www.gnu.org/software/gsl/"
    description = "GNU Scientific Library"
    settings = "os", "compiler", "build_type", "arch"
    options = {"shared": [True, False], "fPIC": [True, False]}
    default_options = {"shared": False, "fPIC": True}

    generators = "cmake"

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def source(self):
        tools.get(**self.conan_data["sources"][self.version], strip_root=True,
                  destination=self._source_subfolder)
        tools.replace_in_file(self._source_subfolder + "/configure",
                              r"-install_name \$rpath/",
                              "-install_name @rpath/")

    def build(self):
        autotools = AutoToolsBuildEnvironment(self)

        configure_args = []

        if self.options.shared:
            configure_args.append("--enable-shared")

        if not self.options.shared:
            configure_args.append("--enable-static")

        autotools.configure(args=configure_args,
                            configure_dir=self._source_subfolder)
        autotools.make()
        autotools.install()

    def configure(self):
        del self.settings.compiler.libcxx
        del self.settings.compiler.cppstd

    def package(self):
        tools.rmdir(os.path.join(self.package_folder, "share"))
        tools.rmdir(os.path.join(self.package_folder, "lib", "pkgconfig"))

        tools.remove_files_by_mask(self.package_folder, "*.la")

        self.copy("COPYING", dst="licenses", src=self._source_subfolder)
        self.copy("*.h", dst="include/gsl", src="gsl")
        self.copy("*.dll", dst="bin", keep_path=False)
        self.copy("*.so", dst="lib", keep_path=False)
        self.copy("*.dylib", dst="lib", keep_path=False)
        self.copy("*.a", dst="lib", keep_path=False)
        self.copy("libgsl*.a", dst="lib", keep_path=False)

    def package_info(self):
        self.cpp_info.libs = ["gsl", "gslcblas"]
