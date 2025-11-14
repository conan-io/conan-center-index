// ofx
#include "ofxCore.h"
#include "ofxImageEffect.h"
#include "ofxPixels.h"

// ofx host
#include "ofxhBinary.h"
#include "ofxhPropertySuite.h"
#include "ofxhClip.h"
#include "ofxhParam.h"
#include "ofxhMemory.h"
#include "ofxhImageEffect.h"
#include "ofxhPluginAPICache.h"
#include "ofxhPluginCache.h"
#include "ofxhHost.h"

#include <iostream>

int main() {
   // Empty file test to check OFX HostSupport include and link works
   auto binary = OFX::Binary("");
   std::cout << "Test function return value: " << binary.isInvalid() << std::endl;
   return 0;
}
