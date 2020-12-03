import os
from conans import ConanFile, tools, AutoToolsBuildEnvironment
from conans.errors import ConanInvalidConfiguration


class PciUtilsConan(ConanFile):
    name = "pciutils"
    license = "BSD-3-Clause"
    description = "The PCI Utilities package contains a library for portable access to PCI bus"
    topics = ("conan", "PCI")
    homepage = "https://github.com/pciutils/pciutils"
    url = "https://github.com/conan-io/conan-center-index"
    settings = "os", "compiler", "build_type", "arch"
    options = {"shared": [True, False], "fPIC": [True, False], "with_zlib": [True, False]}
    default_options = {"shared": False, "fPIC": True, "with_zlib": True}

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def configure(self):
        if not self.settings.os in ["Linux"]:
            raise ConanInvalidConfiguration("Platform {} is currently not supported by this recipe".format(self.settings.os))

        if self.options.shared:
            del self.options.fPIC
        del self.settings.compiler.libcxx
        del self.settings.compiler.cppstd

    def requirements(self):
        if self.options.with_zlib:
            self.requires("zlib/1.2.11")

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        extracted_dir = self.name + "-" + self.version
        tools.rename(extracted_dir, self._source_subfolder)

    def build(self):
        yes_no = lambda v: "yes" if v else "no"
        with tools.chdir(self._source_subfolder):
            self.run("make SHARED={} ZLIB={} DNS=no all".format(yes_no(self.options.shared), yes_no(self.options.with_zlib)))

    def package(self):
        yes_no = lambda v: "yes" if v else "no"
        with tools.chdir(self._source_subfolder):
            self.run("make PREFIX={} SHARED={} install install-pcilib".format(self.package_folder, yes_no(self.options.shared)))

        self.copy("COPYING", src=self._source_subfolder, dst="licenses")
        self.copy("*.h", src=self._source_subfolder, dst="include", keep_path=True)

        if self.options.shared:
            tools.rename(src=os.path.join(self._source_subfolder, "lib", "libpci.so.3.7.0"),
                dst=os.path.join(self.package_folder, "lib", "libpci.so"))

        tools.rmdir(os.path.join(self.package_folder, "sbin"))
        tools.rmdir(os.path.join(self.package_folder, "share"))
        tools.rmdir(os.path.join(self.package_folder, "man"))

    def package_info(self):
        self.cpp_info.libs = ["pci"]
