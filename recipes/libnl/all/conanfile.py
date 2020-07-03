import os, glob
from conans import ConanFile, tools, AutoToolsBuildEnvironment

class LibNlConan(ConanFile):
    name = "libnl"
    description = "A collection of libraries providing APIs to netlink protocol based Linux kernel interfaces."
    topics = "conan", "netlink"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://www.infradead.org/~tgr/libnl/"
    license = "LGPL-2.1-only"
    settings = "os", "arch", "compiler", "build_type"
    options = {"shared": [True, False]}
    default_options = {"shared": False}

    _autotools = None

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        extracted_dir = self.name + "-" + self.version
        os.rename(extracted_dir, self._source_subfolder)

    def configure(self):
        if not tools.os_info.is_linux:
            raise ConanInvalidConfiguration("Libnl is only supported on Linux")
        del self.settings.compiler.libcxx
        del self.settings.compiler.cppstd

    def _configure_autotools(self):
        if self._autotools:
            return self._autotools
        self._autotools = AutoToolsBuildEnvironment(self)
        config_args = [
            "--prefix={}".format(tools.unix_path(self.package_folder)),
        ]
        if self.options.shared:
            config_args.extend(["--enable-shared=yes", "--enable-static=no"])
        else:
            config_args.extend(["--enable-shared=no", "--enable-static=yes"])

        self._autotools.configure(configure_dir=self._source_subfolder, args=config_args)
        return self._autotools

    def build(self):
        autotools = self._configure_autotools()
        autotools.make()

    def package(self):
        autotools = self._configure_autotools()
        autotools.install()
        self.copy("COPYING", dst="licenses", src=self._source_subfolder)
        #tools.remove_files_by_mask causes AttributeError: module 'conans.tools' has no attribute 'remove_files_by_mask'
        #tools.remove_files_by_mask(os.path.join(self.package_folder, "lib"), "*.la")
        la_pattern = os.path.join(self.package_folder, "lib", "**", "*.la")
        la_files = glob.glob(la_pattern, recursive=True)
        for next_file in la_files:
            self.output.info("removing %s" % next_file)
            os.remove(next_file)
        tools.rmdir(os.path.join(self.package_folder, "share"))
        tools.rmdir(os.path.join(self.package_folder, "etc"))
        tools.rmdir(os.path.join(self.package_folder, "lib", "pkgconfig"))

    def package_info(self):
        self.cpp_info.includedirs = [os.path.join('include', 'libnl3')]
        self.cpp_info.libs = ["nl-3", "nl-cli-3", "nl-genl-3", "nl-idiag-3", "nl-nf-3", "nl-route-3"]

