from conans import ConanFile, tools
from conans.errors import ConanInvalidConfiguration

required_conan_version = ">=1.33.0"


class ThreadPoolConan(ConanFile):
    name = "bs-thread-pool"
    description = "Fast, lightweight, and easy-to-use C++17 thread pool library"
    topics = ("thread-pool", "concurrency", "header-only")
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/bshoshany/thread-pool"
    license = "MIT"
    no_copy_source = True

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    @property
    def _minimum_cpp_standard(self):
        return 17

    @property
    def _minimum_compilers_version(self):
        return {
            "apple-clang": "9.3",
            "clang": "5.0",
            "gcc": "8.0",
            "Visual Studio": "19.12"
        }

    def validate(self):
        if self.settings.get_safe("compiler.cppstd"):
            tools.check_min_cppstd(self, self._minimum_cpp_standard)

        compiler = self.settings.compiler
        try:
            min_version = self._minimum_compilers_version[str(compiler)]
            if tools.Version(compiler.version) < min_version:
                msg = (
                    "{} requires C++{} features which are not supported by compiler {} {}."
                ).format(self.name, self._minimum_cpp_standard, compiler, compiler.version)
                raise ConanInvalidConfiguration(msg)
        except KeyError:
            msg = (
                "{} recipe lacks information about the {} compiler, "
                "support for the required C++{} features is assumed"
            ).format(self.name, compiler, self._minimum_cpp_standard)
            self.output.warn(msg)

    def source(self):
        tools.get(**self.conan_data["sources"][self.version],
                  destination=self._source_subfolder, strip_root=True)

    def package_id(self):
        self.info.header_only()

    def package(self):
        self.copy("*.hpp", dst="include/bs_thread_pool",
                  src=self._source_subfolder)
        self.copy("LICENSE.txt", dst="licenses", src=self._source_subfolder)
