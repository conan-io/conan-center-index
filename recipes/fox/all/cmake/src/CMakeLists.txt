include(CheckIncludeFileCXX)
include(CheckCXXSourceCompiles)
include(CheckCXXSymbolExists)
include(CMakePushCheckState)

option(WITH_XIM "Compile with X Input Method support" ON)
option(WITH_JPEG "Compile with JPEG support" ON)
option(WITH_PNG "Compile with PNG support" ON)
option(WITH_TIFF "Compile with TIFF support" ON)
option(WITH_ZLIB "Compile with zlib support" ON)
option(WITH_BZ2LIB "Compile with bz2lib support" ON)
option(WITH_WEBP "Compile with webp support" ON)
option(WITH_OPENJPEG "Compile with OpenJPEG support" ON)
option(WITH_OPENGL "Compile with OpenGL support" ON)

# libdir name to allow overriding to lib32 / lib64
set(CMAKE_INSTALL_LIBDIR "lib" CACHE STRING "Specify the name of the directory where libraries are meant to be installed")

set(HEADERS
  ../include/fx3d.h
  ../include/FX4Splitter.h
  ../include/FX7Segment.h
  ../include/FX885910Codec.h
  ../include/FX885911Codec.h
  ../include/FX885913Codec.h
  ../include/FX885914Codec.h
  ../include/FX885915Codec.h
  ../include/FX885916Codec.h
  ../include/FX88591Codec.h
  ../include/FX88592Codec.h
  ../include/FX88593Codec.h
  ../include/FX88594Codec.h
  ../include/FX88595Codec.h
  ../include/FX88596Codec.h
  ../include/FX88597Codec.h
  ../include/FX88598Codec.h
  ../include/FX88599Codec.h
  ../include/FXAccelTable.h
  ../include/FXApp.h
  ../include/FXArray.h
  ../include/FXArrowButton.h
  ../include/fxascii.h
  ../include/FXBitmapFrame.h
  ../include/FXBitmap.h
  ../include/FXBitmapView.h
  ../include/FXBMPIcon.h
  ../include/FXBMPImage.h
  ../include/FXButton.h
  ../include/FXBZFileStream.h
  ../include/FXCanvas.h
  ../include/FXCheckButton.h
  ../include/FXChoiceBox.h
  ../include/FXColorBar.h
  ../include/FXColorDialog.h
  ../include/FXColorList.h
  ../include/FXColorRing.h
  ../include/FXColorSelector.h
  ../include/FXColorWell.h
  ../include/FXColorWheel.h
  ../include/FXComboBox.h
  ../include/FXComposeContext.h
  ../include/FXComposite.h
  ../include/FXCP1250Codec.h
  ../include/FXCP1251Codec.h
  ../include/FXCP1252Codec.h
  ../include/FXCP1253Codec.h
  ../include/FXCP1254Codec.h
  ../include/FXCP1255Codec.h
  ../include/FXCP1256Codec.h
  ../include/FXCP1257Codec.h
  ../include/FXCP1258Codec.h
  ../include/FXCP437Codec.h
  ../include/FXCP850Codec.h
  ../include/FXCP852Codec.h
  ../include/FXCP855Codec.h
  ../include/FXCP856Codec.h
  ../include/FXCP857Codec.h
  ../include/FXCP860Codec.h
  ../include/FXCP861Codec.h
  ../include/FXCP862Codec.h
  ../include/FXCP863Codec.h
  ../include/FXCP864Codec.h
  ../include/FXCP865Codec.h
  ../include/FXCP866Codec.h
  ../include/FXCP869Codec.h
  ../include/FXCP874Codec.h
  ../include/FXCURCursor.h
  ../include/FXCursor.h
  ../include/FXDataTarget.h
  ../include/FXDate.h
  ../include/FXDC.h
  ../include/FXDCPrint.h
  ../include/FXDCWindow.h
  ../include/FXDebugTarget.h
  ../include/fxdefs.h
  ../include/FXDelegator.h
  ../include/FXDial.h
  ../include/FXDialogBox.h
  ../include/FXDict.h
  ../include/FXDirBox.h
  ../include/FXDirDialog.h
  ../include/FXDir.h
  ../include/FXDirList.h
  ../include/FXDirSelector.h
  ../include/FXDLL.h
  ../include/FXDockBar.h
  ../include/FXDockHandler.h
  ../include/FXDockSite.h
  ../include/FXDockTitle.h
  ../include/FXDocument.h
  ../include/FXDragCorner.h
  ../include/FXDrawable.h
  ../include/FXDriveBox.h
  ../include/FXElement.h
  ../include/FXException.h
  ../include/FXExpression.h
  ../include/FXExtentd.h
  ../include/FXExtentf.h
  ../include/FXFileDialog.h
  ../include/FXFileDict.h
  ../include/FXFile.h
  ../include/FXFileList.h
  ../include/FXFileSelector.h
  ../include/FXFileStream.h
  ../include/FXFoldingList.h
  ../include/FXFontDialog.h
  ../include/FXFont.h
  ../include/FXFontSelector.h
  ../include/FXFrame.h
  ../include/FXGIFCursor.h
  ../include/FXGIFIcon.h
  ../include/FXGIFImage.h
  ../include/FXGLCanvas.h
  ../include/FXGLCone.h
  ../include/FXGLContext.h
  ../include/FXGLCube.h
  ../include/FXGLCylinder.h
  ../include/FXGLObject.h
  ../include/FXGLShape.h
  ../include/FXGLSphere.h
  ../include/FXGLTriangleMesh.h
  ../include/FXGLViewer.h
  ../include/FXGLVisual.h
  ../include/FXGradientBar.h
  ../include/FXGroupBox.h
  ../include/FXGUISignal.h
  ../include/FXGZFileStream.h
  ../include/fx.h
  ../include/FXHash.h
  ../include/FXHeader.h
  ../include/FXHorizontalFrame.h
  ../include/FXICOIcon.h
  ../include/FXICOImage.h
  ../include/FXIconDict.h
  ../include/FXIcon.h
  ../include/FXIconList.h
  ../include/FXIconSource.h
  ../include/FXId.h
  ../include/FXIFFIcon.h
  ../include/FXIFFImage.h
  ../include/FXImageFrame.h
  ../include/FXImage.h
  ../include/FXImageView.h
  ../include/FXInputDialog.h
  ../include/FXIO.h
  ../include/FXJPGIcon.h
  ../include/FXJPGImage.h
  ../include/fxkeys.h
  ../include/FXKnob.h
  ../include/FXKOI8RCodec.h
  ../include/FXLabel.h
  ../include/FXListBox.h
  ../include/FXList.h
  ../include/FXMainWindow.h
  ../include/FXMat3d.h
  ../include/FXMat3f.h
  ../include/FXMat4d.h
  ../include/FXMat4f.h
  ../include/FXMatrix.h
  ../include/FXMDIButton.h
  ../include/FXMDIChild.h
  ../include/FXMDIClient.h
  ../include/FXMemMap.h
  ../include/FXMemoryStream.h
  ../include/FXMenuBar.h
  ../include/FXMenuButton.h
  ../include/FXMenuCaption.h
  ../include/FXMenuCascade.h
  ../include/FXMenuCheck.h
  ../include/FXMenuCommand.h
  ../include/FXMenuPane.h
  ../include/FXMenuRadio.h
  ../include/FXMenuSeparator.h
  ../include/FXMenuTitle.h
  ../include/FXMessageBox.h
  ../include/FXObject.h
  ../include/FXObjectList.h
  ../include/FXOptionMenu.h
  ../include/FXPacker.h
  ../include/FXPath.h
  ../include/FXPCXIcon.h
  ../include/FXPCXImage.h
  ../include/FXPicker.h
  ../include/FXPipe.h
  ../include/FXPNGIcon.h
  ../include/FXPNGImage.h
  ../include/FXPoint.h
  ../include/FXPopup.h
  ../include/FXPPMIcon.h
  ../include/FXPPMImage.h
  ../include/FXPrintDialog.h
  ../include/FXProgressBar.h
  ../include/FXProgressDialog.h
  ../include/FXQuatd.h
  ../include/FXQuatf.h
  ../include/FXRadioButton.h
  ../include/FXRanged.h
  ../include/FXRangef.h
  ../include/FXRASIcon.h
  ../include/FXRASImage.h
  ../include/FXRealSlider.h
  ../include/FXRealSpinner.h
  ../include/FXRecentFiles.h
  ../include/FXRectangle.h
  ../include/FXRegion.h
  ../include/FXRegistry.h
  ../include/FXReplaceDialog.h
  ../include/FXRex.h
  ../include/FXRGBIcon.h
  ../include/FXRGBImage.h
  ../include/FXRootWindow.h
  ../include/FXRuler.h
  ../include/FXRulerView.h
  ../include/FXScrollArea.h
  ../include/FXScrollBar.h
  ../include/FXScrollPane.h
  ../include/FXScrollWindow.h
  ../include/FXSearchDialog.h
  ../include/FXSeparator.h
  ../include/FXSettings.h
  ../include/FXShell.h
  ../include/FXShutter.h
  ../include/FXSize.h
  ../include/FXSlider.h
  ../include/FXSocket.h
  ../include/FXSphered.h
  ../include/FXSpheref.h
  ../include/FXSpinner.h
  ../include/FXSplashWindow.h
  ../include/FXSplitter.h
  ../include/FXSpring.h
  ../include/FXStat.h
  ../include/FXStatusBar.h
  ../include/FXStatusLine.h
  ../include/FXStream.h
  ../include/FXStringDict.h
  ../include/FXString.h
  ../include/FXSwitcher.h
  ../include/FXSystem.h
  ../include/FXTabBar.h
  ../include/FXTabBook.h
  ../include/FXTabItem.h
  ../include/FXTable.h
  ../include/FXTextCodec.h
  ../include/FXTextField.h
  ../include/FXText.h
  ../include/FXTGAIcon.h
  ../include/FXTGAImage.h
  ../include/FXThread.h
  ../include/FXTIFIcon.h
  ../include/FXTIFImage.h
  ../include/FXToggleButton.h
  ../include/FXToolBarGrip.h
  ../include/FXToolBar.h
  ../include/FXToolBarShell.h
  ../include/FXToolBarTab.h
  ../include/FXToolTip.h
  ../include/FXTopWindow.h
  ../include/FXTranslator.h
  ../include/FXTreeListBox.h
  ../include/FXTreeList.h
  ../include/FXTriStateButton.h
  ../include/FXUndoList.h
  ../include/fxunicode.h
  ../include/FXURL.h
  ../include/FXUTF16Codec.h
  ../include/FXUTF32Codec.h
  ../include/FXUTF8Codec.h
  ../include/FXVec2d.h
  ../include/FXVec2f.h
  ../include/FXVec3d.h
  ../include/FXVec3f.h
  ../include/FXVec4d.h
  ../include/FXVec4f.h
  ../include/fxver.h
  ../include/FXVerticalFrame.h
  ../include/FXVisual.h
  ../include/FXWindow.h
  ../include/FXWizard.h
  ../include/FXXBMIcon.h
  ../include/FXXBMImage.h
  ../include/FXXPMIcon.h
  ../include/FXXPMImage.h
  ../include/xincs.h
  fxpriv.h)

set(SOURCES
  FX4Splitter.cpp
  FX7Segment.cpp
  FX885910Codec.cpp
  FX885911Codec.cpp
  FX885913Codec.cpp
  FX885914Codec.cpp
  FX885915Codec.cpp
  FX885916Codec.cpp
  FX88591Codec.cpp
  FX88592Codec.cpp
  FX88593Codec.cpp
  FX88594Codec.cpp
  FX88595Codec.cpp
  FX88596Codec.cpp
  FX88597Codec.cpp
  FX88598Codec.cpp
  FX88599Codec.cpp
  FXAccelTable.cpp
  FXApp.cpp
  FXArrowButton.cpp
  fxascii.cpp
  FXBitmap.cpp
  FXBitmapFrame.cpp
  FXBitmapView.cpp
  FXBMPIcon.cpp
  FXBMPImage.cpp
  fxbmpio.cpp
  FXButton.cpp
  FXBZFileStream.cpp
  FXCanvas.cpp
  FXCheckButton.cpp
  FXChoiceBox.cpp
  FXColorBar.cpp
  FXColorDialog.cpp
  FXColorList.cpp
  FXColorNames.cpp
  FXColorRing.cpp
  FXColorSelector.cpp
  FXColorWell.cpp
  FXColorWheel.cpp
  FXComboBox.cpp
  FXComposeContext.cpp
  FXComposite.cpp
  FXCP1250Codec.cpp
  FXCP1251Codec.cpp
  FXCP1252Codec.cpp
  FXCP1253Codec.cpp
  FXCP1254Codec.cpp
  FXCP1255Codec.cpp
  FXCP1256Codec.cpp
  FXCP1257Codec.cpp
  FXCP1258Codec.cpp
  FXCP437Codec.cpp
  FXCP850Codec.cpp
  FXCP852Codec.cpp
  FXCP855Codec.cpp
  FXCP856Codec.cpp
  FXCP857Codec.cpp
  FXCP860Codec.cpp
  FXCP861Codec.cpp
  FXCP862Codec.cpp
  FXCP863Codec.cpp
  FXCP864Codec.cpp
  FXCP865Codec.cpp
  FXCP866Codec.cpp
  FXCP869Codec.cpp
  FXCP874Codec.cpp
  FXCURCursor.cpp
  FXCursor.cpp
  FXDataTarget.cpp
  FXDate.cpp
  FXDC.cpp
  FXDCPrint.cpp
  FXDCWindow.cpp
  FXDebugTarget.cpp
  FXDelegator.cpp
  FXDial.cpp
  FXDialogBox.cpp
  FXDict.cpp
  FXDirBox.cpp
  FXDir.cpp
  FXDirDialog.cpp
  FXDirList.cpp
  FXDirSelector.cpp
  FXDLL.cpp
  FXDockBar.cpp
  FXDockHandler.cpp
  FXDockSite.cpp
  FXDockTitle.cpp
  FXDocument.cpp
  FXDragCorner.cpp
  FXDrawable.cpp
  FXDriveBox.cpp
  FXException.cpp
  FXExpression.cpp
  FXExtentd.cpp
  FXExtentf.cpp
  fxezquantize.cpp
  FXFile.cpp
  FXFileDialog.cpp
  FXFileDict.cpp
  FXFileList.cpp
  fxfilematch.cpp
  FXFileSelector.cpp
  FXFileStream.cpp
  FXFoldingList.cpp
  FXFont.cpp
  FXFontDialog.cpp
  FXFontSelector.cpp
  FXFrame.cpp
  fxfsquantize.cpp
  FXGIFCursor.cpp
  FXGIFIcon.cpp
  FXGIFImage.cpp
  fxgifio.cpp
  FXGLCanvas.cpp
  FXGLCone.cpp
  FXGLContext.cpp
  FXGLCube.cpp
  FXGLCylinder.cpp
  FXGLObject.cpp
  FXGLShape.cpp
  FXGLSphere.cpp
  FXGLTriangleMesh.cpp
  FXGLViewer.cpp
  FXGLVisual.cpp
  FXGradientBar.cpp
  FXGroupBox.cpp
  FXGUISignal.cpp
  FXGZFileStream.cpp
  FXHash.cpp
  FXHeader.cpp
  FXHorizontalFrame.cpp
  FXICOIcon.cpp
  FXICOImage.cpp
  fxicoio.cpp
  FXIcon.cpp
  FXIconDict.cpp
  FXIconList.cpp
  FXIconSource.cpp
  FXId.cpp
  FXIFFIcon.cpp
  FXIFFImage.cpp
  fxiffio.cpp
  FXImage.cpp
  FXImageFrame.cpp
  FXImageView.cpp
  FXInputDialog.cpp
  FXIO.cpp
  fxjpegio.cpp
  FXJPGIcon.cpp
  FXJPGImage.cpp
  fxkeyboard.cpp
  fxkeysym.cpp
  FXKnob.cpp
  FXKOI8RCodec.cpp
  FXLabel.cpp
  FXListBox.cpp
  FXList.cpp
  FXMainWindow.cpp
  FXMat3d.cpp
  FXMat3f.cpp
  FXMat4d.cpp
  FXMat4f.cpp
  FXMatrix.cpp
  FXMDIButton.cpp
  FXMDIChild.cpp
  FXMDIClient.cpp
  FXMemMap.cpp
  FXMemoryStream.cpp
  FXMenuBar.cpp
  FXMenuButton.cpp
  FXMenuCaption.cpp
  FXMenuCascade.cpp
  FXMenuCheck.cpp
  FXMenuCommand.cpp
  FXMenuPane.cpp
  FXMenuRadio.cpp
  FXMenuSeparator.cpp
  FXMenuTitle.cpp
  FXMessageBox.cpp
  FXObject.cpp
  FXObjectList.cpp
  FXOptionMenu.cpp
  FXPacker.cpp
  fxparsegeometry.cpp
  FXPath.cpp
  FXPCXIcon.cpp
  FXPCXImage.cpp
  fxpcxio.cpp
  FXPicker.cpp
  FXPipe.cpp
  FXPNGIcon.cpp
  FXPNGImage.cpp
  fxpngio.cpp
  FXPoint.cpp
  FXPopup.cpp
  FXPPMIcon.cpp
  FXPPMImage.cpp
  fxppmio.cpp
  FXPrintDialog.cpp
  fxpriv.cpp
  FXProgressBar.cpp
  FXProgressDialog.cpp
  fxpsio.cpp
  FXQuatd.cpp
  FXQuatf.cpp
  FXRadioButton.cpp
  FXRanged.cpp
  FXRangef.cpp
  FXRASIcon.cpp
  FXRASImage.cpp
  fxrasio.cpp
  FXRealSlider.cpp
  FXRealSpinner.cpp
  FXRecentFiles.cpp
  FXRectangle.cpp
  FXRegion.cpp
  FXRegistry.cpp
  FXReplaceDialog.cpp
  FXRex.cpp
  FXRGBIcon.cpp
  FXRGBImage.cpp
  fxrgbio.cpp
  FXRootWindow.cpp
  FXRuler.cpp
  FXRulerView.cpp
  FXScrollArea.cpp
  FXScrollBar.cpp
  FXScrollPane.cpp
  FXScrollWindow.cpp
  FXSearchDialog.cpp
  FXSeparator.cpp
  FXSettings.cpp
  FXShell.cpp
  FXShutter.cpp
  FXSize.cpp
  FXSlider.cpp
  FXSocket.cpp
  FXSphered.cpp
  FXSpheref.cpp
  FXSpinner.cpp
  FXSplashWindow.cpp
  FXSplitter.cpp
  FXSpring.cpp
  FXStat.cpp
  FXStatusBar.cpp
  FXStatusLine.cpp
  FXStream.cpp
  FXString.cpp
  FXStringDict.cpp
  FXSwitcher.cpp
  FXSystem.cpp
  FXTabBar.cpp
  FXTabBook.cpp
  FXTabItem.cpp
  FXTable.cpp
  fxtargaio.cpp
  FXTextCodec.cpp
  FXText.cpp
  FXTextField.cpp
  FXTGAIcon.cpp
  FXTGAImage.cpp
  FXThread.cpp
  FXTIFIcon.cpp
  FXTIFImage.cpp
  fxtifio.cpp
  FXToggleButton.cpp
  FXToolBar.cpp
  FXToolBarGrip.cpp
  FXToolBarShell.cpp
  FXToolBarTab.cpp
  FXToolTip.cpp
  FXTopWindow.cpp
  FXTranslator.cpp
  FXTreeListBox.cpp
  FXTreeList.cpp
  FXTriStateButton.cpp
  FXUndoList.cpp
  fxunicode.cpp
  FXURL.cpp
  FXUTF16Codec.cpp
  FXUTF32Codec.cpp
  FXUTF8Codec.cpp
  fxutils.cpp
  FXVec2d.cpp
  FXVec2f.cpp
  FXVec3d.cpp
  FXVec3f.cpp
  FXVec4d.cpp
  FXVec4f.cpp
  FXVerticalFrame.cpp
  FXVisual.cpp
  FXWindow.cpp
  FXWizard.cpp
  fxwuquantize.cpp
  FXXBMIcon.cpp
  FXXBMImage.cpp
  fxxbmio.cpp
  FXXPMIcon.cpp
  FXXPMImage.cpp
  fxxpmio.cpp
  icons.cpp
  strtoll.cpp
  vsscanf.cpp)

set(ICONS
arrownext.gif
arrowprev.gif
bigapp.gif
bigcdrom.gif
bigcomputer.gif
bigdesktop.gif
bigdoc.gif
bigfloppy.gif
bigfolder.gif
bigfolderopen.gif
bignetdrive.gif
bignethood.gif
bookclr.gif
bookset.gif
cmymode.gif
deleteicon.gif
dialmode.gif
dirupicon.gif
dockbottom.gif
dockflip.gif
dockfree.gif
dockleft.gif
dockright.gif
docktop.gif
entericon.gif
erroricon.gif
eyedrop.gif
filecopy.gif
filedelete.gif
filehidden.gif
filelink.gif
filemove.gif
filerename.gif
fileshown.gif
foldernew.gif
gotohome.gif
gotoicon.gif
gotowork.gif
hsvmode.gif
infoicon.gif
landscape.gif
listmode.gif
miniapp.gif
minicdrom.gif
minicomputer.gif
minidesktop.gif
minidoc.gif
minifloppy.gif
minifolder.gif
minifolderopen.gif
miniharddisk.gif
mininetdrive.gif
mininethood.gif
minizipdrive.gif
portrait.gif
questionicon.gif
rgbmode.gif
searchicon.gif
showbigicons.gif
showdetails.gif
showsmallicons.gif
warningicon.gif
winclose.gif
winmaximize.gif
winminimize.gif
winrestore.gif)

add_library(fox ${SOURCES})

if (NOT MSVC)
  find_package(PkgConfig)
  find_package(Threads)
  find_package(X11)
  find_package(Freetype)
  pkg_check_modules(FONTCONFIG fontconfig)
endif()

if(WITH_OPENGL)
  find_package(OpenGL)
endif()

check_cxx_source_compiles( "#include <immintrin.h>
int main(int argc,char *argv) { return 0; }" HAVE_IMMINTRIN_H)
if(HAVE_IMMINTRIN_H)
  add_definitions(-DHAVE_IMMINTRIN_H)
endif()


check_cxx_symbol_exists(localtime_r "time.h" HAVE_LOCALTIME_R)
if(HAVE_LOCALTIME_R)
  add_definitions(-DHAVE_LOCALTIME_R)
endif()

check_cxx_symbol_exists(clock_gettime "time.h" HAVE_CLOCK_GETTIME_NORT)
if(NOT HAVE_CLOCK_GETTIME_NORT)
  cmake_push_check_state()
  set(CMAKE_REQUIRED_LIBRARIES -lrt)
  check_cxx_symbol_exists(clock_gettime "time.h" HAVE_CLOCK_GETTIME)
  if(HAVE_CLOCK_GETTIME)
    list(APPEND LIBRARIES -lrt)
  endif()
  cmake_pop_check_state()
endif()

cmake_push_check_state()
  check_include_file_cxx(dlfcn.h HAVE_DLFCN_H)
  if(HAVE_DLFCN_H)
    add_definitions(-DHAVE_DLFCN_H)
  endif()
  set(CMAKE_REQUIRED_LIBRARIES -ldl)
  check_cxx_symbol_exists(dlopen "dlfcn.h" HAVE_DLOPEN)
  if(HAVE_DLOPEN)
    list(APPEND LIBRARIES -ldl)
  endif()
cmake_pop_check_state()


cmake_push_check_state()
set(CMAKE_REQUIRED_LIBRARIES -ldld)
check_cxx_symbol_exists(shl_load "" HAVE_SHL_LOAD)
if(HAVE_DLOPEN_NODL)
  add_definitions(-DHAVE_SHL_LOAD)
  list(APPEND LIBRARIES -ldld)
endif()
cmake_pop_check_state()

check_cxx_symbol_exists(gmtime_r "time.h" HAVE_GMTIME_R)
if(HAVE_GMTIME_R)
  add_definitions(-DHAVE_GMTIME_R)
endif()

check_cxx_symbol_exists(readdir_r "dirent.h" HAVE_READDIR_R)
if(HAVE_READDIR_R)
  add_definitions(-DHAVE_READDIR_R)
endif()

check_cxx_symbol_exists(getpwuid_r "sys/types.h;pwd.h" HAVE_GETPWUID_R)
if(HAVE_GETPWUID_R)
  add_definitions(-DHAVE_GETPWUID_R)
endif()

check_cxx_symbol_exists(getpwnam_r "sys/types.h;pwd.h" HAVE_GETPWNAM_R)
if(HAVE_GETPWNAM_R)
  add_definitions(-DHAVE_GETPWNAM_R)
endif()

check_cxx_symbol_exists(getgrgid_r "sys/types.h;grp.h" HAVE_GETGRGID_R)
if(HAVE_GETGRGID_R)
  add_definitions(-DHAVE_GETGRGID_R)
endif()

check_cxx_symbol_exists(vsscanf "stdio.h" HAVE_VSSCANF)
if(HAVE_VSSCANF)
  add_definitions(-DHAVE_VSSCANF)
endif()

cmake_push_check_state()
  set(CMAKE_REQUIRED_DEFINITIONS -D_GNU_SOURCE)
  set(CMAKE_REQUIRED_LIBRARIES -pthread)
  set(CMAKE_REQUIRED_FLAGS -pthread)
  check_cxx_symbol_exists(pthread_setaffinity_np "pthread.h" HAVE_PTHREAD_SETAFFINITY_NP)
  if(HAVE_PTHREAD_SETAFFINITY_NP)
    add_definitions(-DHAVE_PTHREAD_SETAFFINITY_NP)
  endif()
cmake_pop_check_state()

cmake_push_check_state()
  set(CMAKE_REQUIRED_DEFINITIONS -D_GNU_SOURCE)
  check_cxx_symbol_exists(pipe2 "fcntl.h;unistd.h" HAVE_PIPE2)
  if(HAVE_PIPE2)
    add_definitions(-DHAVE_PIPE2)
  endif()
cmake_pop_check_state()

check_cxx_symbol_exists(sched_getcpu "sched.h" HAVE_SCHED_GETCPU)
if(HAVE_SCHED_GETCPU)
  add_definitions(-DHAVE_SCHED_GETCPU)
endif()

check_cxx_symbol_exists(epoll_create1 "sys/epoll.h" HAVE_EPOLL_CREATE1)
if(HAVE_EPOLL_CREATE1)
  add_definitions(-DHAVE_EPOLL_CREATE1)
endif()

check_cxx_symbol_exists(timerfd_create "sys/timerfd.h" HAVE_TIMERFD_CREATE)
if(HAVE_TIMERFD_CREATE)
  add_definitions(-DHAVE_TIMERFD_CREATE)
endif()

check_cxx_symbol_exists(statvfs "sys/statvfs.h" HAVE_STATVFS)
if(HAVE_STATVFS)
  add_definitions(-DHAVE_STATVFS)
endif()

if(FREETYPE_FOUND)
  include_directories(${FREETYPE_INCLUDE_DIRS})
endif()

if(X11_XShm_FOUND)
  add_definitions(-DHAVE_XSHM_H)
endif()

if(X11_Xcursor_FOUND)
  add_definitions(-DHAVE_XCURSOR_H)
  list(APPEND LIBRARIES ${X11_Xcursor_LIB})
endif()

if(X11_Xft_FOUND AND FREETYPE_FOUND AND FONTCONFIG_FOUND)
  add_definitions(-DHAVE_XFT_H)
  include_directories(${X11_Xft_INCLUDE_PATH})
  list(APPEND LIBRARIES ${X11_Xft_LIB} ${FONTCONFIG_LIBRARIES} ${FREETYPE_LIBRARIES})
endif()

if(X11_Xshape_FOUND)
  add_definitions(-DHAVE_XSHAPE_H)
  list(APPEND LIBRARIES ${X11_Xshape_LIB})
endif()

if(X11_Xrandr_FOUND)
  add_definitions(-DHAVE_XRANDR_H)
  list(APPEND LIBRARIES ${X11_Xrandr_LIB})
endif()

if(X11_Xfixes_FOUND)
  add_definitions(-DHAVE_XFIXES_H)
  list(APPEND LIBRARIES ${X11_Xfixes_LIB})
endif()

if(X11_Xrender_FOUND)
  add_definitions(-DHAVE_XRENDER_H)
  list(APPEND LIBRARIES ${X11_Xrender_LIB})
endif()

# check for xinput2
# find_path(X11_Xi2_INCLUDE_PATH X11/extensions/XInput2.h ${X11_INC_SEARCH_PATH})
#if (X11_Xi2_INCLUDE_PATH AND X11_Xi_LIB)
#  set(X11_INCLUDE_DIR ${X11_INCLUDE_DIR} ${X11_Xi2_INCLUDE_PATH})
#  list(REMOVE_DUPLICATES X11_INCLUDE_DIR)
#  add_definitions(-DHAVE_XINPUT2_H)
#  list(APPEND LIBRARIES ${X11_Xi_LIB})
#endif ()

#
# AC_HEADER_DIRENT
# This macro is obsolescent, as all current systems with directory libraries have <dirent.h>.
# New programs need not use this macro.
#
# Not checking for the SCO Xenix dir and x libraries.
#
check_cxx_source_compiles("#include <dirent.h>\nint main(int argc,char *argv[]) { DIR * d; return 0; }" HAVE_DIRENT_H)
if(HAVE_DIRENT_H)
  add_definitions(-DHAVE_DIRENT_H)
else()
  check_cxx_source_compiles("#include <sys/ndir.h>\nint main(int argc,char *argv[]) { DIR * d; return 0; }" HAVE_SYS_NDIR_H)
  if(HAVE_SYS_NDIR_H)
    add_definitions(-DHAVE_SYS_NDIR_H)
  else()
    check_cxx_source_compiles("#include <sys/dir.h>\nint main(int argc,char *argv[]) { DIR * d; return 0; }" HAVE_SYS_DIR_H)
    if(HAVE_SYS_DIR_H)
      add_definitions(-DHAVE_SYS_DIR_H)
    else()
      check_cxx_source_compiles("#include <ndir.h>\nint main(int argc,char *argv[]) { DIR * d; return 0; }" HAVE_NDIR_H)
      if(HAVE_NDIR_H)
        add_definitions(-DHAVE_NDIR_H)
      endif()
    endif()
  endif()
endif()

check_cxx_source_compiles("#include <stdlib.h>\nint main(int argc, char *argv[]) { long long int x = strtoll(\"1234\", NULL, 10); return 0;}" HAVE_STRTOLL)
if (HAVE_STRTOLL)
  add_definitions(-DHAVE_STRTOLL)
endif()

check_cxx_source_compiles("#include <stdlib.h>\nint main(int argc, char *argv[]) { long long int x = strtoull(\"1234\", NULL, 10); return 0;}" HAVE_STRTOULL)
if (HAVE_STRTOULL)
  add_definitions(-DHAVE_STRTOULL)
endif()

#
# AC_HEADER_TIME
#
# This macro is obsolescent, as current systems can include both files when they exist.
# New programs need not use this macro.
#
check_include_file_cxx(sys/time.h HAVE_SYS_TIME_H)
if(HAVE_SYS_TIME_H)
  add_definitions(-DHAVE_SYS_TIME_H)
  check_cxx_source_compiles("#include <sys/time.h>\n#include <time.h>\nint main(int arc,char * argv[]) { return 0; }" TIME_WITH_SYS_TIME)
  if(TIME_WITH_SYS_TIME)
    add_definitions(-DTIME_WITH_SYS_TIME)
  endif()
endif()

#
# AC_HEADER_SYS_WAIT
#
# If sys/wait.h is not Posix compatible, then instead of including it, define the Posix macros with their usual interpretations.
# This macro is obsolescent, as current systems are compatible with Posix. New programs need not use this macro.
# New programs need not use this macro.
#
# cmake: only check for header file since FOX doesn't define the alternative macros
check_include_file_cxx(sys/wait.h HAVE_SYS_WAIT_H)
if(HAVE_SYS_WAIT_H)
  add_definitions(-DHAVE_SYS_WAIT_H)
endif()

check_include_file_cxx(semaphore.h HAVE_SEMAPHORE_H)
if(HAVE_SEMAPHORE_H)
  add_definitions(-DHAVE_SEMAPHORE_H)
endif()

check_include_file_cxx(unistd.h HAVE_UNISTD_H)
if(HAVE_UNISTD_H)
  add_definitions(-DHAVE_UNISTD_H)
endif()

check_include_file_cxx(sys/dir.h HAVE_SYS_DIR_H)
if(HAVE_SYS_DIR_H)
  add_definitions(-DHAVE_SYS_DIR_H)
endif()

check_include_file_cxx(sys/filio.h HAVE_SYS_FILIO_H)
if(HAVE_SYS_FILIO_H)
  add_definitions(-DHAVE_SYS_FILIO_H)
endif()

check_include_file_cxx(sys/mman.h HAVE_SYS_MMAN_H)
if(HAVE_SYS_MMAN_H)
  add_definitions(-DHAVE_SYS_MMAN_H)
endif()

check_include_file_cxx(sys/mount.h HAVE_SYS_MOUNT_H)
if(HAVE_SYS_MOUNT_H)
  add_definitions(-DHAVE_SYS_MOUNT_H)
endif()

check_include_file_cxx(sys/param.h HAVE_SYS_PARAM_H)
if(HAVE_SYS_PARAM_H)
  add_definitions(-DHAVE_SYS_PARAM_H)
endif()

check_include_file_cxx(sys/select.h HAVE_SYS_SELECT_H)
if(HAVE_SYS_SELECT_H)
  add_definitions(-DHAVE_SYS_SELECT_H)
endif()

check_include_file_cxx(sys/epoll.h HAVE_SYS_EPOLL_H)
if(HAVE_SYS_EPOLL_H)
  add_definitions(-DHAVE_SYS_EPOLL_H)
endif()

check_include_file_cxx(sys/shm.h HAVE_SYS_SHM_H)
if(HAVE_SYS_SHM_H)
  add_definitions(-DHAVE_SYS_SHM_H)
endif()

check_include_file_cxx(sys/statvfs.h HAVE_SYS_STATVFS_H)
if(HAVE_SYS_STATVFS_H)
  add_definitions(-DHAVE_SYS_STATVFS_H)
endif()

check_include_file_cxx(sys/pstat.h HAVE_SYS_PSTAT_H)
if(HAVE_SYS_PSTAT_H)
  add_definitions(-DHAVE_SYS_PSTAT_H)
endif()

if(WITH_JPEG)
  find_package(JPEG)
  if(JPEG_FOUND)
    list(APPEND LIBRARIES ${JPEG_LIBRARIES})
    add_definitions(-DHAVE_JPEG_H)
  endif()
endif()

if(WITH_PNG)
  find_package(PNG)
  if(TARGET PNG::PNG)
    list(APPEND LIBRARIES PNG::PNG)
    add_definitions(-DHAVE_PNG_H)
  endif()
endif()

if(WITH_ZLIB)
  find_package(ZLIB)
  if(TARGET ZLIB::ZLIB)
    list(APPEND LIBRARIES ZLIB::ZLIB)
    add_definitions(-DHAVE_ZLIB_H)
  endif()
endif()

if(WITH_BZ2LIB)
  find_package(BZip2)
  if(TARGET BZip2::BZip2)
    list(APPEND LIBRARIES BZip2::BZip2)
    add_definitions(-DHAVE_BZ2LIB_H)
  endif()
endif()

if(WITH_TIFF)
  find_package(TIFF)
  if(TARGET TIFF::TIFF)
    list(APPEND LIBRARIES TIFF::TIFF)
    add_definitions(-DHAVE_TIFF_H)
  endif()
endif()

if(WITH_WEBP)
  find_package(WebP)
  if(WebP_FOUND)
    list(APPEND LIBRARIES WebP::webp)
    add_definitions(-DHAVE_WEBP_H)
  endif()
endif()

if(WITH_OPENJPEG)
  find_package(OpenJPEG)
  if(OpenJPEG_FOUND)
    list(APPEND LIBRARIES openjp2)
    add_definitions(-DHAVE_JP2_H)
  endif()
endif()

if(WITH_OPENGL)
  find_package(OpenGL REQUIRED)
  target_compile_definitions(fox PUBLIC -DHAVE_GL_H)
  list(APPEND LIBRARIES OpenGL::GL OpenGL::GLU)
endif()

if (OPENGL_GLU_FOUND)
  add_definitions(-DHAVE_GLU_H)
  list(APPEND LIBRARIES ${OPENGL_glu_LIBRARY})
endif()

if(NOT WITH_XIM)
  add_definitions(-DNO_XIM)
endif()

target_include_directories(fox PUBLIC ${PROJECT_SOURCE_DIR}/include)
target_link_libraries(fox PRIVATE ${X11_LIBRARIES} ${LIBRARIES} ${CMAKE_THREAD_LIBS_INIT})
if(MSVC)
  target_link_libraries(fox PRIVATE
    ws2_32 gdi32 user32 comctl32 winspool mpr imm32 shell32 ole32 uuid advapi32)
endif()

add_custom_command(
  OUTPUT ${CMAKE_CURRENT_SOURCE_DIR}/icons.cpp ${CMAKE_CURRENT_SOURCE_DIR}/icons.h
  COMMAND reswrap -i -n FX -o icons.h ${ICONS}
  COMMAND reswrap -e -n FX -o icons.cpp ${ICONS}
  WORKING_DIRECTORY ${CMAKE_CURRENT_SOURCE_DIR}
  DEPENDS reswrap
  VERBATIM
  )

set_target_properties(fox PROPERTIES VERSION ${fox-toolkit_VERSION} SOVERSION ${fox-toolkit_VERSION_PATCH})
set_target_properties(fox PROPERTIES OUTPUT_NAME fox-${fox-toolkit_VERSION_MAJOR}.${fox-toolkit_VERSION_MINOR})
set_target_properties(fox PROPERTIES WINDOWS_EXPORT_ALL_SYMBOLS ON)

install(TARGETS fox
        RUNTIME DESTINATION ${CMAKE_INSTALL_BINDIR}
        ARCHIVE DESTINATION ${CMAKE_INSTALL_LIBDIR}
        LIBRARY DESTINATION ${CMAKE_INSTALL_LIBDIR}
        )
install(FILES ${HEADERS} DESTINATION include/fox-${fox-toolkit_VERSION_MAJOR}.${fox-toolkit_VERSION_MINOR})
