// Copyright OpenFX and contributors to the OpenFX project.
// SPDX-License-Identifier: BSD-3-Clause


/*
  Ofx Example plugin that show a very simple plugin that inverts an image.

  It is meant to illustrate certain features of the API, as opposed to being a perfectly
  crafted piece of image processing software.

  The main features are
    - basic plugin definition
    - basic property usage
    - basic image access and rendering
 */
#include <cstring>
#include <stdexcept>
#include <new>
#include "ofxImageEffect.h"
#include "ofxMemory.h"
#include "ofxMultiThread.h"
#include "ofxPixels.h"

#if defined __APPLE__ || defined __linux__ || defined __FreeBSD__
#  define EXPORT __attribute__((visibility("default")))
#elif defined _WIN32
#  define EXPORT OfxExport
#else
#  error Not building on your operating system quite yet
#endif

// pointers to various bits of the host
OfxHost               *gHost;
OfxImageEffectSuiteV1 *gEffectHost = 0;
OfxPropertySuiteV1    *gPropHost = 0;

// look up a pixel in the image, does bounds checking to see if it is in the image rectangle
inline OfxRGBAColourB *
pixelAddress(OfxRGBAColourB *img, OfxRectI rect, int x, int y, int bytesPerLine)
{  
  if(x < rect.x1 || x >= rect.x2 || y < rect.y1 || y > rect.y2)
    return 0;
  OfxRGBAColourB *pix = (OfxRGBAColourB *) (((char *) img) + (y - rect.y1) * bytesPerLine);
  pix += x - rect.x1;  
  return pix;
}

// throws this if it can't fetch an image
class NoImageEx {};

// the process code  that the host sees
static OfxStatus render(OfxImageEffectHandle  instance,
                        OfxPropertySetHandle inArgs,
                        OfxPropertySetHandle /*outArgs*/)
{
  // get the render window and the time from the inArgs
  OfxTime time;
  OfxRectI renderWindow;
  OfxStatus status = kOfxStatOK;
  
  gPropHost->propGetDouble(inArgs, kOfxPropTime, 0, &time);
  gPropHost->propGetIntN(inArgs, kOfxImageEffectPropRenderWindow, 4, &renderWindow.x1);

  // fetch output clip
  OfxImageClipHandle outputClip;
  gEffectHost->clipGetHandle(instance, kOfxImageEffectOutputClipName, &outputClip, 0);
    

  OfxPropertySetHandle outputImg = NULL, sourceImg = NULL;
  try {
    // fetch image to render into from that clip
    OfxPropertySetHandle outputImg;
    if(gEffectHost->clipGetImage(outputClip, time, NULL, &outputImg) != kOfxStatOK) {
      throw NoImageEx();
    }
      
    // fetch output image info from that handle
    int dstRowBytes;
    OfxRectI dstRect;
    void *dstPtr;
    gPropHost->propGetInt(outputImg, kOfxImagePropRowBytes, 0, &dstRowBytes);
    gPropHost->propGetIntN(outputImg, kOfxImagePropBounds, 4, &dstRect.x1);
    gPropHost->propGetInt(outputImg, kOfxImagePropRowBytes, 0, &dstRowBytes);
    gPropHost->propGetPointer(outputImg, kOfxImagePropData, 0, &dstPtr);
      
    // fetch main input clip
    OfxImageClipHandle sourceClip;
    gEffectHost->clipGetHandle(instance, kOfxImageEffectSimpleSourceClipName, &sourceClip, 0);
      
    // fetch image at render time from that clip
    if (gEffectHost->clipGetImage(sourceClip, time, NULL, &sourceImg) != kOfxStatOK) {
      throw NoImageEx();
    }
      
    // fetch image info out of that handle
    int srcRowBytes;
    OfxRectI srcRect;
    void *srcPtr;
    gPropHost->propGetInt(sourceImg, kOfxImagePropRowBytes, 0, &srcRowBytes);
    gPropHost->propGetIntN(sourceImg, kOfxImagePropBounds, 4, &srcRect.x1);
    gPropHost->propGetInt(sourceImg, kOfxImagePropRowBytes, 0, &srcRowBytes);
    gPropHost->propGetPointer(sourceImg, kOfxImagePropData, 0, &srcPtr);

    // cast data pointers to 8 bit RGBA
    OfxRGBAColourB *src = (OfxRGBAColourB *) srcPtr;
    OfxRGBAColourB *dst = (OfxRGBAColourB *) dstPtr;

    // and do some inverting
    for(int y = renderWindow.y1; y < renderWindow.y2; y++) {
      if(gEffectHost->abort(instance)) break;

      OfxRGBAColourB *dstPix = pixelAddress(dst, dstRect, renderWindow.x1, y, dstRowBytes);

      for(int x = renderWindow.x1; x < renderWindow.x2; x++) {
        
        OfxRGBAColourB *srcPix = pixelAddress(src, srcRect, x, y, srcRowBytes);

        if(srcPix) {
          dstPix->r = 255 - srcPix->r;
          dstPix->g = 255 - srcPix->g;
          dstPix->b = 255 - srcPix->b;
          dstPix->a = 255 - srcPix->a;
        }
        else {
          dstPix->r = 0;
          dstPix->g = 0;
          dstPix->b = 0;
          dstPix->a = 0;
        }
        dstPix++;
      }
    }

    // we are finished with the source images so release them
  }
  catch(NoImageEx &) {
    // if we were interrupted, the failed fetch is fine, just return kOfxStatOK
    // otherwise, something weird happened
    if(!gEffectHost->abort(instance)) {
      status = kOfxStatFailed;
    }      
  }

  if(sourceImg)
    gEffectHost->clipReleaseImage(sourceImg);
  if(outputImg)
    gEffectHost->clipReleaseImage(outputImg);
  
  // all was well
  return status;
}

//  describe the plugin in context
static OfxStatus
describeInContext( OfxImageEffectHandle  effect,  OfxPropertySetHandle /*inArgs*/)
{
  OfxPropertySetHandle props;
  // define the single output clip in both contexts
  gEffectHost->clipDefine(effect, kOfxImageEffectOutputClipName, &props);

  // set the component types we can handle on out output
  gPropHost->propSetString(props, kOfxImageEffectPropSupportedComponents, 0, kOfxImageComponentRGBA);

  // define the single source clip in both contexts
  gEffectHost->clipDefine(effect, kOfxImageEffectSimpleSourceClipName, &props);

  // set the component types we can handle on our main input
  gPropHost->propSetString(props, kOfxImageEffectPropSupportedComponents, 0, kOfxImageComponentRGBA);

  return kOfxStatOK;
}

////////////////////////////////////////////////////////////////////////////////
// the plugin's description routine
static OfxStatus
describe(OfxImageEffectHandle effect)
{
  // get the property handle for the plugin
  OfxPropertySetHandle effectProps;
  gEffectHost->getPropertySet(effect, &effectProps);

  // say we cannot support multiple pixel depths and let the clip preferences action deal with it all.
  gPropHost->propSetInt(effectProps, kOfxImageEffectPropSupportsMultipleClipDepths, 0, 0);
  
  // set the bit depths the plugin can handle
  gPropHost->propSetString(effectProps, kOfxImageEffectPropSupportedPixelDepths, 0, kOfxBitDepthByte);

  // set plugin label and the group it belongs to
  gPropHost->propSetString(effectProps, kOfxPropLabel, 0, "OFX Invert Example");
  gPropHost->propSetString(effectProps, kOfxImageEffectPluginPropGrouping, 0, "OFX Example");

  // define the contexts we can be used in
  gPropHost->propSetString(effectProps, kOfxImageEffectPropSupportedContexts, 0, kOfxImageEffectContextFilter);
  
  return kOfxStatOK;
}

////////////////////////////////////////////////////////////////////////////////
// Called at load
static OfxStatus
onLoad(void)
{
    // fetch the host suites out of the global host pointer
    if(!gHost) return kOfxStatErrMissingHostFeature;
    
    gEffectHost     = (OfxImageEffectSuiteV1 *) gHost->fetchSuite(gHost->host, kOfxImageEffectSuite, 1);
    gPropHost       = (OfxPropertySuiteV1 *)    gHost->fetchSuite(gHost->host, kOfxPropertySuite, 1);
    if(!gEffectHost || !gPropHost)
        return kOfxStatErrMissingHostFeature;
    return kOfxStatOK;
}

////////////////////////////////////////////////////////////////////////////////
// The main entry point function
static OfxStatus
pluginMain(const char *action,  const void *handle, OfxPropertySetHandle inArgs,  OfxPropertySetHandle outArgs)
{
  try {
  // cast to appropriate type
  OfxImageEffectHandle effect = (OfxImageEffectHandle) handle;

  if(strcmp(action, kOfxActionLoad) == 0) {
    return onLoad();
  }
  else if(strcmp(action, kOfxActionDescribe) == 0) {
    return describe(effect);
  }
  else if(strcmp(action, kOfxImageEffectActionDescribeInContext) == 0) {
    return describeInContext(effect, inArgs);
  }
  else if(strcmp(action, kOfxImageEffectActionRender) == 0) {
    return render(effect, inArgs, outArgs);
  }    
  } catch (std::bad_alloc) {
    // catch memory
    //std::cout << "OFX Plugin Memory error." << std::endl;
    return kOfxStatErrMemory;
  } catch ( const std::exception& e ) {
    // standard exceptions
    //std::cout << "OFX Plugin error: " << e.what() << std::endl;
    return kOfxStatErrUnknown;
  } catch (int err) {
    // ho hum, gone wrong somehow
    return err;
  } catch ( ... ) {
    // everything else
    //std::cout << "OFX Plugin error" << std::endl;
    return kOfxStatErrUnknown;
  }
    
  // other actions to take the default value
  return kOfxStatReplyDefault;
}

// function to set the host structure
static void
setHostFunc(OfxHost *hostStruct)
{
  gHost = hostStruct;
}

////////////////////////////////////////////////////////////////////////////////
// the plugin struct 
static OfxPlugin basicPlugin = 
{       
  kOfxImageEffectPluginApi,
  1,
  "uk.co.thefoundry.OfxInvertExample",
  1,
  0,
  setHostFunc,
  pluginMain
};
   
// the two mandated functions
EXPORT OfxPlugin *
OfxGetPlugin(int nth)
{
  if(nth == 0)
    return &basicPlugin;
  return 0;
}
 
EXPORT int
OfxGetNumberOfPlugins(void)
{       
  return 1;
}
