from conans import ConanFile, ConanFile, tools
import os, glob

class HippomocksConan(ConanFile):
    name = 'hippomocks'
    version = '10960d0' # This library is not versioned
    description = 'Single-header mocking framework.'
    topics = ("conan", "hippomocks", "mock", "framework")
    url = "https://github.com/conan-io/conan-center-index"
    homepage = 'https://github.com/dascandy/hippomocks.git'
    license = 'LGPL-2.1'
    settings = None
    short_paths = True
    no_copy_source = True

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        extracted_dir = glob.glob("%s-%s*" % (self.name, self.version))[0]
        os.rename(extracted_dir, self._source_subfolder)

    def build(self):
        # This is a header-only library so no build step required
        pass

    def package(self):
        self.copy('*.h', dst='include/hippomocks', src='%s/HippoMocks/' % self._source_subfolder)
        self.copy('LICENSE', dst='licenses', src=self._source_subfolder)

    def package_id(self):
        self.info.header_only()

    def package_info(self):
        self.cpp_info.names["cmake_find_package"] = "Hippomocks"
        self.cpp_info.names["cmake_find_package_multi"] = "Hippomocks"

