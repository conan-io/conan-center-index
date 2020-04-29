from conans import ConanFile, CMake, tools
import os

class LevelDBConan(ConanFile):
    name = "leveldb"
    description = "TODO"
    license = "https://github.com/google/leveldb/blob/master/LICENSE"
    topics = ("conan", "leveldb", "google", "db")
    url = "https://github.com/conan-io/conan-center-index "
    homepage = "https://github.com/google/leveldb"
    settings = "os", "compiler", "build_type", "arch"
    options = {
            "shared": [True, False],
            "fPIC": [True, False],
            "with_crc32": [True, False],
            "with_snappy": [True, False],
            "with_tcmalloc": [True, False],
    }
    default_options = {
            "shared": False,
            "fPIC": False,
            "with_crc32": False,
            "with_snappy": False,
            "with_tcmalloc": False
    }
    generators = "cmake"

    _cmake = None

    def _get_cmake(self):
        if self._cmake:
            return self._cmake
        self._cmake = CMake(self)
        self._cmake.definitions["LEVELDB_BUILD_TESTS"] = False
        if self.options.fPIC:
            self._cmake.definitions["CMAKE_POSITION_INDEPENDENT_CODE"] = True
        return self._cmake

    # note: crc32, tcmalloc are also conditionally included in leveldb, but
    # there are no "official" conan packages yet

    optional_snappy_requirement = "snappy/1.1.7"

    def requirements(self):
        if self.options.with_snappy:
            self.requires(self.optional_snappy_requirement)
    
    @property
    def _source_subfolder(self):
        return "source_subfolder"

    @property
    def _build_subfolder(self):
        return "build_subfolder"

    def source(self):
       tools.get(**self.conan_data["sources"][self.version])
       downloaded_name = "%s-%s" % (self.name, self.version)
       os.rename(downloaded_name, self._source_subfolder)
       with tools.chdir(self._source_subfolder):
           if not self.options.with_snappy:
               tools.replace_in_file("CMakeLists.txt",
                       '''check_library_exists(snappy snappy_compress "" HAVE_SNAPPY)''',
                       '''check_library_exists(snappy snappy_compress "" IGNORE_HAVE_SNAPPY)''')


    def build(self):
        cmake = self._get_cmake()
        cmake.configure(source_folder=self._source_subfolder)
        cmake.build()

    def package(self):
        cmake = self._get_cmake()
        self.copy("LICENSE", src=self._source_subfolder, dst="licenses", keep_path=False)
        cmake.install()
        tools.rmdir(os.path.join(self.package_folder, "lib", "cmake"))


    def package_info(self):
        self.cpp_info.libs = tools.collect_libs(self)
        if self.settings.os == "Linux":
            self.cpp_info.system_libs = ["pthread"]
