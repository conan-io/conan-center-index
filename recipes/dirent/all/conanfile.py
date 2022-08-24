import os
from conan import ConanFile, tools$
from conan.errors import ConanInvalidConfiguration


class DirEntConan(ConanFile):
    name = "dirent"
    description = "Dirent is a C/C++ programming interface that allows programmers to retrieve information about " \
                  "files and directories under Linux/UNIX"
    topics = ("conan", "dirent", "directory", "file system")
    homepage = "https://github.com/tronkko/dirent"
    url = "https://github.com/conan-io/conan-center-index"
    license = "MIT"
    settings = "os", "compiler"
    no_copy_source = True

    _source_subfolder = "source_subfolder"

    def configure(self):
        if self.settings.os != "Windows":
            raise ConanInvalidConfiguration("Only Windows builds are supported")
        if self.settings.compiler == "gcc":
            raise ConanInvalidConfiguration("mingw has a dirent.h implementation")

    def source(self):
        tools.files.get(self, **self.conan_data["sources"][self.version])
        os.rename("dirent-{}".format(self.version), self._source_subfolder)

    def package(self):
        self.copy(pattern="LICENSE", src=self._source_subfolder, dst="licenses")
        self.copy(pattern="dirent.h", src=os.path.join(self._source_subfolder, "include"), dst="include")

    def package_id(self):
        self.info.header_only()
