import os
from conans import ConanFile, AutoToolsBuildEnvironment, tools
from conans.errors import ConanInvalidConfiguration
import shutil

required_conan_version = ">=1.29.1"

class TreeSitterConan(ConanFile):
    name = "tree-sitter"
    description = "Tree-sitter is a parser generator tool and an incremental parsing library. It can build a concrete syntax tree for a source file and efficiently update the syntax tree as the source file is edited."
    topics = ("parser", "incremental", "rust")
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://tree-sitter.github.io/tree-sitter"
    license = "MIT"
    settings = "os", "compiler", "build_type", "arch"
    options = {"fPIC": [True, False],
               "shared": [True, False]}
    default_options = {"fPIC": True,
                       "shared": False}
    _autotools = None


    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def configure(self):
        if self.settings.os == "Windows":
            raise ConanInvalidConfiguration("tree-sitter is not support on {}.".format(self.settings.os))

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        os.rename("{}-{}".format(self.name, self.version), self._source_subfolder)

    def _configure_autotools(self):
        if not self._autotools:
            self._autotools = AutoToolsBuildEnvironment(self)

        return self._autotools

    def build(self):
        autotools = self._configure_autotools()

        with tools.chdir(self._source_subfolder):
            autotools.make()

    def package(self):
        self.copy("LICENSE", src=self._source_subfolder, dst="licenses")

        autotools = self._configure_autotools()
        with tools.chdir(self._source_subfolder):
            autotools.install(args=["PREFIX={}".format(self.package_folder)])

            if self.options.shared:
                tools.remove_files_by_mask(os.path.join(self.package_folder, "lib"), "*.a")
            else:
                tools.remove_files_by_mask(os.path.join(self.package_folder, "lib"), "*.so*")
                tools.remove_files_by_mask(os.path.join(self.package_folder, "lib"), "*.dylib*")

        tools.rmdir(os.path.join(self.package_folder, os.path.join("lib", "pkgconfig")))


    def package_info(self):
        self.cpp_info.names["pkg_config"] = "tree-sitter"
        self.cpp_info.libs = ["tree-sitter"]
