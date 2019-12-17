from conans import ConanFile, tools
import os


class TestPackageConan(ConanFile):

    def test(self):
        if not tools.cross_building(self.settings):
            output = os.path.join(self.build_folder, "pkix_asn1_tab.c")
            input = os.path.join(self.source_folder, "pkix.asn")
            assert not os.path.isfile(output)
            assert os.path.isfile(input)
            # input = tools.unix_path(os.path.join(self.source_folder, "pkix.asn"))
            self.run("""asn1Parser -o "{}" "{}" """.format(output, input), run_environment=True)
            assert os.path.isfile(output)
