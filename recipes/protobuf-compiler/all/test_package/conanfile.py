import os

from conans import ConanFile, tools


class TestPackgeConan(ConanFile):
    settings = "os", "arch"

    def build(self):
        pass #nothing to do, not warnings please

    def test(self):
        output_directory = os.getcwd()
        proto_path = os.path.join(os.getcwd(), os.pardir, os.pardir)
        # proto_file = os.path.join(os.getcwd(), os.pardir, os.pardir, "addressbook.proto")
        self.run("protoc --version", run_environment=True)
        self.run("protoc --proto_path {} --cpp_out {} {}".format(proto_path, output_directory, "addressbook.proto"), run_environment=True)
