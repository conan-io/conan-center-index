from conan import ConanFile
from conan.tools.files import get, copy, save
from conan.errors import ConanInvalidConfiguration
import textwrap
import os

required_conan_version = ">=1.46.0"


class ArchicadApidevkitConan (ConanFile):
    name = "archicad-apidevkit"
    description = "The General API Development Kit enables software developers to extend the functionality of Archicad"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://archicadapi.graphisoft.com/"
    license = "LicenseRef-LICENSE"
    settings = "os", "arch", "build_type", "compiler"
    no_copy_source = True
    topics = "api, Archicad, development"
    short_paths = True

    @property
    def _acdevkit_arch(self):
        return str(self.settings.arch)

    def package_id(self):
        del self.info.settings.compiler
        del self.info.settings.build_type

    def build(self):
        get(self, **self.conan_data["sources"][self.version][str(self.settings.os)][self._acdevkit_arch], destination=self.build_folder, strip_root=True)

    def package(self):
        copy(self, "*", dst=self.package_folder, src=self.build_folder)
        save(self, os.path.join(self.package_folder, "licenses", "LICENSE"), textwrap.dedent('''\
            License Agreement
            IMPORTANT

            PLEASE READ THIS AGREEMENT CAREFULLY. BY USING THE GENERAL API DEVELOPMENT KIT WHICH INCLUDES COMPUTER SOFTWARE AND MAY INCLUDE ASSOCIATED MEDIA, PRINTED MATERIALS, AND “ONLINE” OR ELECTRONIC DOCUMENTATION (CALLED THE “SOFTWARE PRODUCT”), YOU INDICATE YOUR ACCEPTANCE OF THE Graphisoft LICENSE AGREEMENT INCLUDING THE LIMITED WARRANTY AND DISCLAIMERS BY INSTALLING, COPYING, DOWNLOADING, ACCESSING, OR OTHERWISE USING THE SOFTWARE PRODUCT, YOU AGREE TO BE BOUND BY THE TERMS OF THIS SOFTWARE LICENSE AGREEMENT. IF YOU DO NOT AGREE TO THE TERMS OF THIS SOFTWARE LICENSE AGREEMENT, DO NOT INSTALL, COPY, OR USE THE SOFTWARE PRODUCT.

            GRAPHISOFT SOFTWARE LICENSE AGREEMENT
            This Agreement constitutes a non-exclusive license for you, the End-user, to use the Software Product. The Software Product is licensed, not sold, to you for your own use under the terms and conditions of this Agreement. The Software Product is an original work and protected by copyright laws protecting the author’s rights and intellectual property. All title and intellectual property rights in and to the content which may be accessed through the use of the Software Product is the property of Graphisoft and/or the respective content owner and may be protected by applicable copyright or other intellectual property laws and treaties. This Agreement grants you no rights to use such content.

            THE LICENSE
            You may use the Software Product on an unlimited number of computers provided that you are the only individual using the Software Product. You are expressly prohibited from diffusing or commercializing the Software Product either alone or as part of another product.
            You may install copies of the Software Product on an unlimited number of computers provided that you are the only individual using the Software Product. You may make and use an unlimited number of copies of the documentation, provided that such copies shall be used only for personal purposes and are not to be republished or distributed (either in hard copy or electronic form).
            You may store or install a copy of the SOFTWARE PRODUCT on a storage device, such as a network server, used only to install or run the SOFTWARE PRODUCT on computers used by a licensed user in accordance with the provisions set forth herein. A single license for the SOFTWARE PRODUCT may not be shared or used concurrently by other end users.
            You may transfer the Software Product and all rights associated to it under this license to another party together with a copy of this Agreement, provided that the other party reads and accepts the terms and conditions of this Agreement, that you do not keep any copies of the Software in whole or in part and the transferee agrees to be bound by the terms of this Agreement.
            RESTRICTIONS
            You may not sell, distribute, cede, sublicense, rent, lease or assign the right to use the Software Product (except as allowed above) nor transfer it by network for commercial use, either in whole or in part.
            You are expressly prohibited from decompiling, disassembling, reverse engineering, or reducing the Software Product for any purposes whatsoever.
            TERMINATION
            This Agreement remains in effect until it is terminated. You may terminate the Agreement at any time by destroying the Software Product and all copies of it. Graphisoft may terminate the Agreement without notice following breach of any part of the Agreement. Upon termination, you must destroy the Software Product and all copies of it.
            LIMITED WARRANTY
            Although Graphisoft has tested the Software Product, the Software Product is sold “AS IS,” without any warranty; expressed or implied, as to its conformity to or fitness for any particular purpose, or that the Software Product will perform uninterrupted and without errors. Graphisoft disclaims all other warranties, expressed or implied, including warranties of merchantability, fitness for a particular purpose, quality, completeness, or precision of the Software Product’s functions.
            No advice or information given by Graphisoft employees, its distributors, resellers, agents, or consultants shall constitute a warranty by Graphisoft or extend the warranty in this Agreement.
            In no event shall Graphisoft be liable for any damages whatsoever, including but not limited to any special, incidental, indirect, or consequential damages whatsoever (including but not limited to lost income, business interruption, loss of business information, or other pecuniary loss) arising from the use or misuse of the Software Product, even if Graphisoft or its employees, resellers, or agents have been advised of the possibility of such damages.
            GENERAL CONDITIONS
            This Agreement DOES NOT give you the right to any technical support for, or upgrades to, the Software Product which Graphisoft may offer from time to time. Graphisoft may, at its option and as part of its sales policy, make such technical support and upgrades available to registered users of the Software Product under terms to be determined from time to time by Graphisoft.
            This Agreement constitutes the full, complete, and exclusive agreement between you and Graphisoft concerning the Software Product and supersedes all prior agreements and understandings, either written or oral.
            If any part or provision of this Agreement is found to be contrary to law by a competent jurisdiction, that part or provision shall be enforced to the maximum extent allowed, and the remaining Agreement shall remain in full force and effect.
            This Agreement is governed by the Austrian law. Any disputes arising from this Agreement, including those disputes relating to the validity, interpretation or termination of the Agreement shall be exclusively and finally settled by an arbitrate tribunal formed beside the Austrian Federal Economic Chamber, Vienna according to its own rules of procedure. Place of jurisdiction shall be in Vienna.

            INQUIRIES
            All inquiries regarding this Agreement should be directed to

            GRAPHISOFT SE
            H-1031 Budapest, Záhony utca 7. (Graphisoft Park 1.),
            Hungary
            '''))
