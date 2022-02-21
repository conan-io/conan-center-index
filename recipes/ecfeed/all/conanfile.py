from conans import ConanFile, tools

required_conan_version = ">=1.33.0"

class EcFeedConan(ConanFile):
    name = "ecfeed"
    version = "1.1.0"
    license = "EPL-1.0"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://ecfeed.com/"
    description = "An open library used to connect to the ecFeed service. \
        It can be integrated with the most common testing frameworks \
        and generates a stream of test cases using a selected algorithm \
        (e.g. Cartesian, N-Wise)."
    topics = ("test", "ecfeed", "nwise")
    build_policy = 'missing'
    requires = "libcurl/7.72.0", "openssl/1.1.1c"
    no_copy_source = True

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])

    def package(self):
        self.copy("ecfeed.cpp-1.1.0/src/ecfeed.hpp", 
                  dst="include", keep_path=False)
        self.copy("ecfeed.cpp-1.1.0/license.txt", 
                  dst="licenses", keep_path=False)

    def package_id(self):
        self.info.header_only()
