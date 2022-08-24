import os
from conan import ConanFile
from conan.tools.files import rename, get
from conans import tools
from conan.errors import ConanInvalidConfiguration


class AclConan(ConanFile):
    name = "nfrechette-acl"
    description = "Animation Compression Library"
    topics = ("animation", "compression")
    license = "MIT"
    homepage = "https://github.com/nfrechette/acl"
    url = "https://github.com/conan-io/conan-center-index"
    no_copy_source = True
    settings = "compiler"

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def requirements(self):
        self.requires("rtm/2.1.4")

    def configure(self):
        minimal_cpp_standard = "11"
        if self.settings.compiler.cppstd:
            tools.check_min_cppstd(self, minimal_cpp_standard)

        if self.settings.compiler == "gcc" and tools.Version(self.settings.compiler.version) < "5":
            raise ConanInvalidConfiguration("acl can't be compiled by {0} {1}".format(self.settings.compiler,
                                                                                      self.settings.compiler.version))

    def source(self):
        get(self, **self.conan_data["sources"][self.version])
        extracted_dir = "acl-" + self.version
        rename(self, extracted_dir, self._source_subfolder)

    def package(self):
        self.copy("LICENSE", dst="licenses", src=self._source_subfolder)
        self.copy("*.h", dst="include", src=os.path.join(self._source_subfolder, "includes"))

    def package_id(self):
        self.info.header_only()
