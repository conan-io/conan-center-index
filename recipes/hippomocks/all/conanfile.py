from conans import CMake, ConanFile, ConanFile, tools
import os, glob

class HippomocksConan(ConanFile):
    name = 'hippomocks'
    libname = 'HippoMocks'
    description = 'Single-header mocking framework.'
    topics = ("conan", "hippomocks", "mock", "framework")
    url = "https://github.com/conan-io/conan-center-index"
    homepage = 'https://github.com/dascandy/hippomocks.git'
    license = 'LGPL-2.1'
    no_copy_source = True
    _cmake = None

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        extracted_dir = glob.glob("%s-*" % (self.name))[0]
        os.rename(extracted_dir, self._source_subfolder)

    def _configure_cmake(self):
        if self._cmake:
            return self._cmake
        self._cmake = CMake(self)
        self._cmake.configure(source_folder=self._source_subfolder)
        return self._cmake

    def build(self):
        cmake = self._configure_cmake()
        cmake.build()
        cmake.install()
        cmake.test()

    def package(self):
        self.copy('LICENSE', dst='licenses', src=self._source_subfolder)
        self.copy('*.h', dst=os.path.join('include', self.name), src=os.path.join(self._source_subfolder, self.libname))

    def package_id(self):
        self.info.header_only()
