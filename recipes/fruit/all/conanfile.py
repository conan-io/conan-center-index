from conans import ConanFile, tools, CMake
from conan.errors import ConanInvalidConfiguration
from conans.tools import Version
from fnmatch import fnmatch
import os
import tarfile


class FruitConan(ConanFile):
    name = "fruit"
    description = "C++ dependency injection framework"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/google/fruit"
    license = "Apache-2.0"
    topics = ("conan", "fruit", "injection")
    settings = "os", "compiler", "build_type", "arch"
    options = {"shared": [True, False],
               "use_boost": [True, False],
               "fPIC": [True, False]}
    default_options = {"shared": False, "use_boost": True, "fPIC": True}
    generators = "cmake", "cmake_find_package"
    exports_sources = ["CMakeLists.txt", "patches/*"]
    _cmake = None

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    @property
    def _build_subfolder(self):
        return "build_subfolder"

    def build_requirements(self):
        if self.options.use_boost:
            self.build_requires("boost/1.72.0")

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            del self.options.fPIC

        compiler = str(self.settings.compiler)
        compiler_version = Version(self.settings.compiler.version.value)

        minimal_version = {
            "gcc": "5",
            "clang": "3.5",
            "apple-clang": "7.3",
            "Visual Studio": "14"
        }

        if compiler in minimal_version and \
           compiler_version < minimal_version[compiler]:
            raise ConanInvalidConfiguration("%s requires a compiler that supports"
                                            " at least C++11. %s %s is not"
                                            " supported." % (self.name, compiler, compiler_version))

        if self.settings.compiler.cppstd:
            tools.check_min_cppstd(self, "11")

    @property
    def _extracted_dir(self):
        return self.name + "-" + self.version

    def _get_source(self):
        if Version(self.version) == "3.4.0":
            filename = os.path.basename(self.conan_data["sources"][self.version]["url"])
            tools.download(filename=filename, **self.conan_data["sources"][self.version])

            with tarfile.TarFile.open(filename, 'r:*') as tarredgzippedFile:
                # NOTE: In fruit v3.4.0, The archive file contains the file names
                # build and BUILD in the extras/bazel_root/third_party/fruit directory.
                # Extraction fails on a case-insensitive file system due to file
                # name conflicts.
                # Exclude build as a workaround.
                exclude_pattern = "%s/extras/bazel_root/third_party/fruit/build" % (self._extracted_dir,)
                members = list(filter(lambda m: not fnmatch(m.name, exclude_pattern),
                                    tarredgzippedFile.getmembers()))
                tarredgzippedFile.extractall(".", members=members)
        else:
            tools.get(**self.conan_data["sources"][self.version])

    def source(self):
        self._get_source()

        os.rename(self._extracted_dir, self._source_subfolder)

    def _configure_cmake(self):
        if not self._cmake:
            self._cmake = CMake(self)
            self._cmake.definitions["FRUIT_USES_BOOST"] = self.options.use_boost
            self._cmake.definitions["FRUIT_ENABLE_COVERAGE"] = False
            self._cmake.definitions["RUN_TESTS_UNDER_VALGRIND"] = False
            self._cmake.definitions["FRUIT_ENABLE_CLANG_TIDY"] = False

            self._cmake.configure(build_folder=self._build_subfolder)
        return self._cmake

    def _patch_files(self):
        if self.version in self.conan_data["patches"]:
            for patch in self.conan_data["patches"][self.version]:
                tools.patch(**patch)

    def build(self):
        self._patch_files()

        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        self.copy("COPYING", dst="licenses", src=self._source_subfolder)

        cmake = self._configure_cmake()
        cmake.install()

    def package_info(self):
        self.cpp_info.libs = tools.collect_libs(self)
        if self.settings.os == "Linux":
            self.cpp_info.system_libs = ["m"]
