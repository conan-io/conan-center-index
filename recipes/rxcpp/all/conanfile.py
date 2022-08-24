import os

from conan import ConanFile, tools$

class RxcppConan(ConanFile):
    name = "rxcpp"
    description = "C++11 library for composing operations on streams of asynchronous events."
    license = "Apache-2.0"
    topics = ("conan", "rxcpp", "reactivex", "asynchronous", "event", "observable", "values-distributed-in-time")
    homepage = "https://github.com/ReactiveX/RxCpp"
    url = "https://github.com/conan-io/conan-center-index"
    no_copy_source = True

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def source(self):
        tools.files.get(self, **self.conan_data["sources"][self.version])
        os.rename("RxCpp-" + self.version, self._source_subfolder)

    def package(self):
        self.copy("license.md", dst="licenses", src=self._source_subfolder)
        self.copy(pattern="*.hpp", dst="include", src=os.path.join(self._source_subfolder, "Rx", "v2", "src"))

    def package_id(self):
        self.info.header_only()
