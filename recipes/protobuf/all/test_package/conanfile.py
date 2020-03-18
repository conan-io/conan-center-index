import os
import shutil
from conans import ConanFile, CMake, tools


class TestPackageConan(ConanFile):
    settings = "os", "compiler", "build_type", "arch"
    generators = "cmake"

    def build(self):
        if os.path.exists(os.path.join(self.source_folder, "addressbook.pb.cc")):
            os.remove(os.path.join(self.source_folder, "addressbook.pb.cc"))
        if os.path.exists(os.path.join(self.source_folder, "addressbook.pb.h")):
            os.remove(os.path.join(self.source_folder, "addressbook.pb.h"))
        shutil.copy(os.path.join(self.source_folder, "addressbook.pb.cc." + self.requires['protobuf'].ref.version), os.path.join(self.source_folder, "addressbook.pb.cc"))
        shutil.copy(os.path.join(self.source_folder, "addressbook.pb.h." + self.requires['protobuf'].ref.version), os.path.join(self.source_folder, "addressbook.pb.h"))
        cmake = CMake(self)
        cmake.configure()
        cmake.build()
        os.remove(os.path.join(self.source_folder, "addressbook.pb.h"))
        os.remove(os.path.join(self.source_folder, "addressbook.pb.cc"))

    def test(self):
        if not tools.cross_building(self.settings):
            bin_path = os.path.abspath(os.path.join("bin", "test_package"))
            self.run(bin_path, run_environment=True)

