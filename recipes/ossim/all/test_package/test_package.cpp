//----------------------------------------------------------------------------
//
// License:  ossim license (MIT)
//
// Author:  David Burken
//
// Description: Test code for generic ossim test.
//
// $Id: ossim-test.cpp 19751 2011-06-13 15:13:07Z dburken $
//----------------------------------------------------------------------------
#include <iostream>
#include <iomanip>
using namespace std;

#include <ossim/base/ossimConstants.h>
#include <ossim/base/ossimCommon.h>
#include <ossim/base/ossimEnvironmentUtility.h>
#include <ossim/init/ossimInit.h>


int main(int argc, char *argv[])
{
   ossimInit::instance()->initialize(argc, argv);

   cout << "running ossim::isnan test..." << endl;
   double d = ossim::nan();
   if (ossim::isnan(d))
   {
      cout << "ossim::isnan test passed..." << endl;
   }
   else
   {
      cout << "ossim::isnan test failed..." << endl;
   }

   cout << "running ossimEnvironmentUtility test..."
        << "\ngetUserDir(): " 
        << ossimEnvironmentUtility::instance()->getUserDir()
        << "\ngetUserName(): " 
        << ossimEnvironmentUtility::instance()->getUserName()
        << "\ngetUserOssimSupportDir(): " 
        << ossimEnvironmentUtility::instance()->getUserOssimSupportDir()
        << "\ngetUserOssimPreferences(): " 
        << ossimEnvironmentUtility::instance()->getUserOssimPreferences()
        << "\ngetUserOssimPluginDir()" 
        << ossimEnvironmentUtility::instance()->getUserOssimPluginDir()
        << "\ngetInstalledOssimSupportDir(): " 
        << ossimEnvironmentUtility::instance()->getInstalledOssimSupportDir()
        << "\ngetInstalledOssimPluginDir(): " 
        << ossimEnvironmentUtility::instance()->getInstalledOssimPluginDir()
        << "\ngetInstalledOssimPreferences(): "
        << ossimEnvironmentUtility::instance()->getInstalledOssimPreferences()
        << "\ngetCurrentWorkingDir(): "
        << ossimEnvironmentUtility::instance()->getCurrentWorkingDir()
        << endl;

   cout << "ossim::round<> test:";
   ossim_float64 f1 = 8.193933404085605;
   cout << std::setiosflags(ios::fixed) << std::setprecision(15) << "\nf1: " << f1;
   f1 = ossim::round<int>(f1 / 0.000005359188182);
   cout << std::setiosflags(ios::fixed) << std::setprecision(15) << "\nossim::round<int>(d / 0.000005359188182): " << f1 << "\n";
   
   return 0;
}
