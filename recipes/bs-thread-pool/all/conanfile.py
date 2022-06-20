from conans import ConanFile, tools

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

    def source(self):
        tools.get(**self.conan_data["sources"][self.version],
                  destination=self._source_subfolder, strip_root=True)

    def package_id(self):
        self.info.header_only()

    def package(self):
        self.copy("*.hpp", dst="include/bs_thread_pool", src=self._source_subfolder)
        self.copy("LICENSE.txt", dst="licenses", src=self._source_subfolder)
