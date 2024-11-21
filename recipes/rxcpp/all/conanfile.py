from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.files import copy, get
from conan.tools.layout import basic_layout
from conan.tools.scm import Version
import os

required_conan_version = ">=2.1"


class RxcppConan(ConanFile):
    name = "rxcpp"
    description = "C++11 library for composing operations on streams of asynchronous events."
    license = "Apache-2.0"
    topics = ("rxcpp", "reactivex", "asynchronous", "event", "observable", "values-distributed-in-time")
    homepage = "https://github.com/ReactiveX/RxCpp"
    url = "https://github.com/conan-io/conan-center-index"
    settings = "os", "arch", "compiler", "build_type"
    package_type = "header-library"
    no_copy_source = True

    def package_id(self):
        self.info.clear()

    def layout(self):
        basic_layout(self, src_folder="src")
    
    def validate_build(self):
        if self.settings.compiler == "gcc" and Version(self.settings.compiler.version) >= "14":
            raise ConanInvalidConfiguration("This package can't be built for gcc >= 14. "
                                            "You can compile it with a lower version and consume it later with your compiler.")

    def source(self):
        get(self, **self.conan_data["sources"][self.version],
            destination=self.source_folder, strip_root=True)

    def build(self):
        pass

    def package(self):
        copy(self, "license.md", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        copy(self, "*.hpp", src=os.path.join(self.source_folder, "Rx", "v2", "src"), dst=os.path.join(self.package_folder, "include"))

    def package_info(self):
        self.cpp_info.bindirs = []
        self.cpp_info.frameworkdirs = []
        self.cpp_info.libdirs = []
        self.cpp_info.resdirs = []
