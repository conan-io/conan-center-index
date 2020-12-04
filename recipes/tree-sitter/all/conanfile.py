import os
from conans import ConanFile, AutoToolsBuildEnvironment, tools
import shutil

required_conan_version = ">=1.29.1"

class TreeSitterConan(ConanFile):
    name = "tree-sitter"
    description = "Tree-sitter is a parser generator tool and an incremental parsing library. It can build a concrete syntax tree for a source file and efficiently update the syntax tree as the source file is edited."
    topics = ("parser")
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://tree-sitter.github.io/tree-sitter"
    license = "MIT"
    settings = "os", "compiler", "build_type", "arch"
    _autotools = None

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def build_requirements(self):
        if tools.os_info.is_windows:
            if "CONAN_BASH_PATH" not in os.environ and tools.os_info.detect_windows_subsystem() != 'msys2':
                self.build_requires("msys2/20190524")

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
        shutil.copytree(os.path.join(self._source_subfolder, "lib/include"), os.path.join(self.package_folder, "include"))
        self.copy("libtree-sitter.a", src=self._source_subfolder, dst=os.path.join(self.package_folder, "lib"))
        self.copy("libtree-sitter.so*", src=self._source_subfolder, dst=os.path.join(self.package_folder, "lib"))

    def package_info(self):
        self.cpp_info.libs = ["libtree-sitter.a"]
        lib_path = os.path.join(self.package_folder, "lib")
        self.output.info("Appending PATH environment variable: {}".format(lib_path))
        self.env_info.PATH.append(lib_path)
