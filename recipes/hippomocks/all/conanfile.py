from conans import ConanFile, ConanFile, tools
import os, glob

class HippomocksConan(ConanFile):
    name = 'hippomocks'
    _libname = 'HippoMocks'
    description = 'Single-header mocking framework.'
    topics = ("conan", "hippomocks", "mock", "framework")
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/dascandy/hippomocks"
    license = 'LGPL-2.1'
    no_copy_source = True

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def source(self):
        tools.files.get(self, **self.conan_data["sources"][self.version])
        extracted_dir = glob.glob("%s-*" % (self.name))[0]
        os.rename(extracted_dir, self._source_subfolder)

    def package(self):
        self.copy('LICENSE', dst='licenses', src=self._source_subfolder)
        self.copy('*.h', dst=os.path.join('include', self._libname), src=os.path.join(self._source_subfolder, self._libname))

    def package_id(self):
        self.info.header_only()
