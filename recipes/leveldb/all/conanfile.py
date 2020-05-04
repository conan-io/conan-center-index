from conans import ConanFile, CMake, tools
import os


class LevelDBConan(ConanFile):
    name = "leveldb"
    description = ("LevelDB is a fast key-value storage library written at "
                   "Google that provides an ordered mapping from string keys "
                   "to string values")
    license = ("BSD-3-Clause",)
    topics = ("conan", "leveldb", "google", "db")
    url = "https://github.com/conan-io/conan-center-index "
    homepage = "https://github.com/google/leveldb"
    settings = "os", "compiler", "build_type", "arch"
    options = {
            "shared": [True, False],
            "fPIC": [True, False],
            "with_snappy": [True, False],
    }
    default_options = {
            "shared": False,
            "fPIC": False,
            "with_snappy": False,
    }
    generators = "cmake"

    _cmake = None

    def _get_cmake(self):
        if self._cmake:
            return self._cmake
        self._cmake = CMake(self)
        self._cmake.definitions["LEVELDB_BUILD_TESTS"] = False
        return self._cmake

    # FIXME: crc32, tcmalloc are also conditionally included in leveldb, but
    # there are no "official" conan packages yet; when those are available, we
    # can add similar with options for those

    def requirements(self):
        if self.options.with_snappy:
            self.requires("snappy/1.1.7")

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
        
    def _patch_sources(self):
        if not self.options.with_snappy:
            tools.replace_in_file(
                os.path.join(self._source_subfolder, "CMakeLists.txt"),
                ('''check_library_exists(snappy snappy_compress '''
                 '''"" HAVE_SNAPPY)'''),
                ('''check_library_exists(snappy snappy_compress '''
                    '''"" IGNORE_HAVE_SNAPPY)'''))

    def build(self):
        self._patch_sources()
        cmake = self._get_cmake()
        cmake.configure(source_folder=self._source_subfolder)
        cmake.build()

    def package(self):
        cmake = self._get_cmake()
        self.copy("LICENSE", src=self._source_subfolder,
                  dst="licenses", keep_path=False)
        cmake.install()
        tools.rmdir(os.path.join(self.package_folder, "lib", "cmake"))

    def package_info(self):
        self.cpp_info.libs = tools.collect_libs(self)
        if self.settings.os == "Linux":
            self.cpp_info.system_libs = ["pthread"]
