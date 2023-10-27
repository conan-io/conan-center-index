cmake_minimum_required(VERSION 3.23)

project(ohPipeline CXX)

find_package(ohnet REQUIRED COMPONENTS ohNetCore ohNetProxies TestFramework)
find_package(LibreSSL REQUIRED CONFIG)
find_package(libmad REQUIRED CONFIG)
find_package(alac REQUIRED CONFIG)
find_package(fdk-aac REQUIRED CONFIG)
find_package(faac REQUIRED CONFIG)
find_package(flac REQUIRED CONFIG)
find_package(Ogg REQUIRED CONFIG)
find_package(Vorbis REQUIRED CONFIG)

function(generate_upnp_service xml domain type version target)
    add_custom_command(OUTPUT ${CMAKE_CURRENT_BINARY_DIR}/Dv${target}.h
    DEPENDS ${CMAKE_CURRENT_SOURCE_DIR}/${xml}
    COMMAND python ServiceGen.py
        -t DvUpnpCppCoreHeader.py
        -o ${CMAKE_CURRENT_BINARY_DIR}
        -x ${xml}
        -d ${domain}
        -y ${type}
        -v ${version}
    )
endfunction(generate_upnp_service xml domain type version target)

string(TOUPPER "${CMAKE_BUILD_TYPE}" BUILD_TYPE_UPPER)
set(CODEGEN_EXECUTABLE "${ohnet_BUILD_DIRS_${BUILD_TYPE_UPPER}}/ServiceGen.py")
set(GENERATED_FILES "")

find_package(Python3 COMPONENTS Interpreter)

macro(generate_source xml domain type version target)
  set(TEMPLATE_FILES DvUpnpCppCoreHeader.py DvUpnpCppCoreSource.py CpUpnpCppBufferHeader.py CpUpnpCppBufferSource.py)
  set(TEMPLATE_PREFIXES Dv Dv Cp Cp)
  set(TEMPLATE_EXTS ".h" ".cpp" ".h" ".cpp")

  foreach(tmp_file tmp_prefix tmp_ext IN ZIP_LISTS TEMPLATE_FILES TEMPLATE_PREFIXES TEMPLATE_EXTS)
    set(OUTPUT_PATH "${CMAKE_BINARY_DIR}/Generated/${tmp_prefix}${target}${tmp_ext}")

    get_filename_component(abs_xml "${xml}"
      REALPATH BASE_DIR "${CMAKE_SOURCE_DIR}")

    add_custom_command(
      OUTPUT ${OUTPUT_PATH}
      COMMAND ${Python3_EXECUTABLE} ${CODEGEN_EXECUTABLE}
      -t ${tmp_file}
      -o Generated
      -x ${abs_xml}
      -d ${domain}
      -y ${type}
      -v ${version}
      DEPENDS ${CODEGEN_EXECUTABLE} ${abs_xml}
      COMMENT "Generating code for ${target} -> ${OUTPUT_PATH}."
      VERBATIM
    )
    set(GENERATED_FILES ${GENERATED_FILES} ${OUTPUT_PATH})
  endforeach()
endmacro()

generate_source("OpenHome/Av/ServiceXml/Upnp/AVTransport1.xml" "upnp.org" "AVTransport" "1" "UpnpOrgAVTransport1")
generate_source("OpenHome/Av/ServiceXml/Upnp/ConnectionManager1.xml" "upnp.org" "ConnectionManager" "1" "UpnpOrgConnectionManager1")
generate_source("OpenHome/Av/ServiceXml/Upnp/RenderingControl1.xml" "upnp.org" "RenderingControl" "1" "UpnpOrgRenderingControl1")
generate_source("OpenHome/Av/ServiceXml/Upnp/ContentDirectory1.xml" "upnp.org" "ContentDirectory" "1" "UpnpOrgContentDirectory1")
generate_source("OpenHome/Av/ServiceXml/OpenHome/Product3.xml" "av.openhome.org" "Product" "3" "AvOpenhomeOrgProduct3")
generate_source("OpenHome/Av/ServiceXml/OpenHome/Radio2.xml" "av.openhome.org" "Radio" "2" "AvOpenhomeOrgRadio2")
generate_source("OpenHome/Av/ServiceXml/OpenHome/Sender2.xml" "av.openhome.org" "Sender" "2" "AvOpenhomeOrgSender2")
generate_source("OpenHome/Av/ServiceXml/OpenHome/Playlist1.xml" "av.openhome.org" "Playlist" "1" "AvOpenhomeOrgPlaylist1")
generate_source("OpenHome/Av/ServiceXml/OpenHome/Receiver1.xml" "av.openhome.org" "Receiver" "1" "AvOpenhomeOrgReceiver1")
generate_source("OpenHome/Av/ServiceXml/OpenHome/Time1.xml" "av.openhome.org" "Time" "1" "AvOpenhomeOrgTime1")
generate_source("OpenHome/Av/ServiceXml/OpenHome/Info1.xml" "av.openhome.org" "Info" "1" "AvOpenhomeOrgInfo1")
generate_source("OpenHome/Av/ServiceXml/OpenHome/Volume4.xml" "av.openhome.org" "Volume" "4" "AvOpenhomeOrgVolume4")
generate_source("OpenHome/Av/ServiceXml/OpenHome/Config2.xml" "av.openhome.org" "Config" "2" "AvOpenhomeOrgConfig2")
generate_source("OpenHome/Av/ServiceXml/OpenHome/ConfigApp1.xml" "av.openhome.org" "ConfigApp" "1" "AvOpenhomeOrgConfigApp1")
generate_source("OpenHome/Av/ServiceXml/OpenHome/Credentials1.xml" "av.openhome.org" "Credentials" "1" "AvOpenhomeOrgCredentials1")
generate_source("OpenHome/Av/ServiceXml/OpenHome/Debug2.xml" "av.openhome.org" "Debug" "2" "AvOpenhomeOrgDebug2")
generate_source("OpenHome/Av/ServiceXml/OpenHome/Transport1.xml" "av.openhome.org" "Transport" "1" "AvOpenhomeOrgTransport1")
generate_source("OpenHome/Av/ServiceXml/OpenHome/Pins1.xml" "av.openhome.org" "Pins" "1" "AvOpenhomeOrgPins1")
generate_source("OpenHome/Av/ServiceXml/OpenHome/OAuth1.xml" "av.openhome.org" "OAuth" "1" "AvOpenhomeOrgOAuth1")

add_custom_target(
  oh_codegen
  DEPENDS ${GENERATED_FILES}
)

add_library(ohPipeline
    STATIC
    OpenHome/Media/Pipeline/VolumeRamper.cpp
    OpenHome/Media/Pipeline/AudioDumper.cpp
    OpenHome/Media/Pipeline/AudioReservoir.cpp
    OpenHome/Media/Pipeline/DecodedAudioAggregator.cpp
    OpenHome/Media/Pipeline/DecodedAudioReservoir.cpp
    OpenHome/Media/Pipeline/DecodedAudioValidator.cpp
    OpenHome/Media/Pipeline/Drainer.cpp
    OpenHome/Media/Pipeline/EncodedAudioReservoir.cpp
    OpenHome/Media/Pipeline/Flusher.cpp
    OpenHome/Media/Pipeline/Logger.cpp
    OpenHome/Media/Pipeline/Msg.cpp
    OpenHome/Media/Pipeline/Muter.cpp
    OpenHome/Media/Pipeline/MuterVolume.cpp
    OpenHome/Media/Pipeline/PreDriver.cpp
    OpenHome/Media/Pipeline/Attenuator.cpp
    OpenHome/Media/Pipeline/Ramper.cpp
    OpenHome/Media/Pipeline/Reporter.cpp
    OpenHome/Media/Pipeline/AirplayReporter.cpp
    OpenHome/Media/Pipeline/SpotifyReporter.cpp
    OpenHome/Media/Pipeline/RampValidator.cpp
    OpenHome/Media/Pipeline/Rewinder.cpp
    OpenHome/Media/Pipeline/Router.cpp
    OpenHome/Media/Pipeline/StreamValidator.cpp
    OpenHome/Media/Pipeline/Seeker.cpp
    OpenHome/Media/Pipeline/PhaseAdjuster.cpp
    OpenHome/Media/Pipeline/Skipper.cpp
    OpenHome/Media/Pipeline/StarvationRamper.cpp
    OpenHome/Media/Pipeline/Stopper.cpp
    OpenHome/Media/Pipeline/TrackInspector.cpp
    OpenHome/Media/Pipeline/VariableDelay.cpp
    OpenHome/Media/Pipeline/Waiter.cpp
    OpenHome/Media/Pipeline/Pipeline.cpp
    OpenHome/Media/Pipeline/ElementObserver.cpp
    OpenHome/Media/ClockPuller.cpp
    OpenHome/Media/IdManager.cpp
    OpenHome/Media/Filler.cpp
    OpenHome/Media/Supply.cpp
    OpenHome/Media/SupplyAggregator.cpp
    OpenHome/Media/Utils/AnimatorBasic.cpp
    OpenHome/Media/Utils/ProcessorAudioUtils.cpp
    OpenHome/Media/Utils/ClockPullerManual.cpp
    OpenHome/Media/Codec/Mpeg4.cpp
    OpenHome/Media/Codec/Container.cpp
    OpenHome/Media/Codec/Id3v2.cpp
    OpenHome/Media/Codec/MpegTs.cpp
    OpenHome/Media/Codec/CodecController.cpp
    OpenHome/Media/Protocol/Protocol.cpp
    OpenHome/Media/Protocol/ProtocolHls.cpp
    OpenHome/Media/Protocol/ProtocolHttp.cpp
    OpenHome/Media/Protocol/ProtocolFile.cpp
    OpenHome/Media/Protocol/ProtocolTone.cpp
    OpenHome/Media/Protocol/Icy.cpp
    OpenHome/Media/Protocol/Rtsp.cpp
    OpenHome/Media/Protocol/ProtocolRtsp.cpp
    OpenHome/Media/Protocol/ContentAudio.cpp
    OpenHome/Media/UriProviderRepeater.cpp
    OpenHome/Media/UriProviderSingleTrack.cpp
    OpenHome/Media/PipelineManager.cpp
    OpenHome/Media/PipelineObserver.cpp
    OpenHome/Media/MuteManager.cpp
    OpenHome/Media/FlywheelRamper.cpp
    OpenHome/Media/MimeTypeList.cpp
    OpenHome/Media/Utils/AllocatorInfoLogger.cpp # needed here by MediaPlayer.  Should move back to tests lib
    OpenHome/Configuration/ConfigManager.cpp
    OpenHome/Media/Utils/Silencer.cpp
    OpenHome/SocketHttp.cpp
    OpenHome/SocketSsl.cpp
)
target_link_libraries(ohPipeline PRIVATE libressl::libressl ohNetCore ohNet)
target_include_directories(ohPipeline PRIVATE ${PROJECT_SOURCE_DIR})
set(ohPipeline_HEADERS
    OpenHome/Media/Pipeline/VolumeRamper.h
    OpenHome/Media/Pipeline/AudioDumper.h
    OpenHome/Media/Pipeline/AudioReservoir.h
    OpenHome/Media/Pipeline/DecodedAudioAggregator.h
    OpenHome/Media/Pipeline/DecodedAudioReservoir.h
    OpenHome/Media/Pipeline/DecodedAudioValidator.h
    OpenHome/Media/Pipeline/Drainer.h
    OpenHome/Media/Pipeline/EncodedAudioReservoir.h
    OpenHome/Media/Pipeline/Flusher.h
    OpenHome/Media/Pipeline/Logger.h
    OpenHome/Media/Pipeline/Msg.h
    OpenHome/Media/Pipeline/Muter.h
    OpenHome/Media/Pipeline/MuterVolume.h
    OpenHome/Media/Pipeline/PreDriver.h
    OpenHome/Media/Pipeline/Attenuator.h
    OpenHome/Media/Pipeline/Ramper.h
    OpenHome/Media/Pipeline/Reporter.h
    OpenHome/Media/Pipeline/AirplayReporter.h
    OpenHome/Media/Pipeline/SpotifyReporter.h
    OpenHome/Media/Pipeline/RampValidator.h
    OpenHome/Media/Pipeline/Rewinder.h
    OpenHome/Media/Pipeline/Router.h
    OpenHome/Media/Pipeline/StreamValidator.h
    OpenHome/Media/Pipeline/Seeker.h
    OpenHome/Media/Pipeline/PhaseAdjuster.h
    OpenHome/Media/Pipeline/Skipper.h
    OpenHome/Media/Pipeline/StarvationRamper.h
    OpenHome/Media/Pipeline/Stopper.h
    OpenHome/Media/Pipeline/TrackInspector.h
    OpenHome/Media/Pipeline/VariableDelay.h
    OpenHome/Media/Pipeline/Waiter.h
    OpenHome/Media/Pipeline/Pipeline.h
    OpenHome/Media/Pipeline/ElementObserver.h
    OpenHome/Media/ClockPuller.h
    OpenHome/Media/IdManager.h
    OpenHome/Media/Filler.h
    OpenHome/Media/Supply.h
    OpenHome/Media/SupplyAggregator.h
    OpenHome/Media/Utils/AnimatorBasic.h
    OpenHome/Media/Utils/ProcessorAudioUtils.h
    OpenHome/Media/Utils/ClockPullerManual.h
    OpenHome/Media/Codec/Mpeg4.h
    OpenHome/Media/Codec/Container.h
    OpenHome/Media/Codec/Id3v2.h
    OpenHome/Media/Codec/MpegTs.h
    OpenHome/Media/Codec/CodecController.h
    OpenHome/Media/Protocol/Protocol.h
    OpenHome/Media/Protocol/ProtocolHls.h
    OpenHome/Media/Protocol/ProtocolTone.h
    OpenHome/Media/Protocol/Icy.h
    OpenHome/Media/Protocol/Rtsp.h
    OpenHome/Media/Protocol/ProtocolRtsp.h
    OpenHome/Media/Protocol/ContentAudio.h
    OpenHome/Media/UriProviderRepeater.h
    OpenHome/Media/UriProviderSingleTrack.h
    OpenHome/Media/PipelineManager.h
    OpenHome/Media/PipelineObserver.h
    OpenHome/Media/MuteManager.h
    OpenHome/Media/FlywheelRamper.h
    OpenHome/Media/MimeTypeList.h
    OpenHome/Media/Utils/AllocatorInfoLogger.h # needed here by MediaPlayer.  Should move back to tests lib
    OpenHome/Configuration/ConfigManager.h
    OpenHome/Media/Utils/Silencer.h
    OpenHome/SocketHttp.h
    OpenHome/SocketSsl.h
)
target_sources(ohPipeline PUBLIC FILE_SET HEADERS FILES "${ohPipeline_HEADERS}")
install(TARGETS ohPipeline
    ARCHIVE DESTINATION ${CMAKE_INSTALL_LIBDIR}
    RUNTIME DESTINATION ${CMAKE_INSTALL_BINDIR}
    LIBRARY DESTINATION ${CMAKE_INSTALL_LIBDIR}
    FILE_SET HEADERS
    DESTINATION ${CMAKE_INSTALL_INCLUDEDIR}
    INCLUDES DESTINATION ${CMAKE_INSTALL_INCLUDEDIR}
)

set(OHMEDIAPLAYER_SOURCES
    OpenHome/Av/KvpStore.cpp
    OpenHome/Av/ProviderUtils.cpp
    OpenHome/Av/Product.cpp
    OpenHome/Av/ProviderProduct.cpp
    OpenHome/Av/ProviderTime.cpp
    OpenHome/Av/ProviderInfo.cpp
    OpenHome/Av/TransportControl.cpp
    OpenHome/Av/ProviderTransport.cpp
    OpenHome/Av/Pins/TransportPins.cpp
    OpenHome/Av/Radio/TuneInPins.cpp
    OpenHome/Av/Radio/RadioPins.cpp
    OpenHome/Av/Pins/UrlPins.cpp
    OpenHome/Av/Utils/FaultCode.cpp
    OpenHome/Av/CalmRadio/CalmRadioPins.cpp
    OpenHome/Av/ProviderVolume.cpp
    OpenHome/Av/Source.cpp
    OpenHome/Av/MediaPlayer.cpp
    OpenHome/Av/Logger.cpp
    OpenHome/Json.cpp
    OpenHome/Av/Utils/FormUrl.cpp
    OpenHome/NtpClient.cpp
    OpenHome/UnixTimestamp.cpp
    OpenHome/Configuration/ProviderConfig.cpp
    OpenHome/Configuration/ProviderConfigApp.cpp
    OpenHome/PowerManager.cpp
    OpenHome/ThreadPool.cpp
    OpenHome/FsFlushPeriodic.cpp
    OpenHome/Av/Credentials.cpp
    OpenHome/Av/ProviderCredentials.cpp
    OpenHome/Av/VolumeManager.cpp
    OpenHome/Av/FriendlyNameAdapter.cpp
    OpenHome/Av/ProviderDebug.cpp
    OpenHome/Av/Pins/Pins.cpp
    OpenHome/Av/Pins/ProviderPins.cpp
    OpenHome/Av/OhMetadata.cpp
    Generated/DvAvOpenhomeOrgProduct3.cpp
    Generated/CpAvOpenhomeOrgProduct3.cpp
    Generated/DvAvOpenhomeOrgTime1.cpp
    Generated/DvAvOpenhomeOrgInfo1.cpp
    Generated/DvAvOpenhomeOrgTransport1.cpp
    Generated/CpAvOpenhomeOrgTransport1.cpp
    Generated/CpAvOpenhomeOrgRadio2.cpp
    Generated/DvAvOpenhomeOrgVolume4.cpp
    Generated/DvAvOpenhomeOrgConfig2.cpp
    Generated/DvAvOpenhomeOrgConfigApp1.cpp
    Generated/DvAvOpenhomeOrgCredentials1.cpp
    Generated/DvAvOpenhomeOrgDebug2.cpp
    Generated/DvAvOpenhomeOrgPins1.cpp
    Generated/DvAvOpenhomeOrgOAuth1.cpp
)
set(OHMEDIAPLAYER_HEADERS
    OpenHome/Av/KvpStore.h
    OpenHome/Av/ProviderUtils.h
    OpenHome/Av/Product.h
    OpenHome/Av/ProviderProduct.h
    OpenHome/Av/ProviderTime.h
    OpenHome/Av/ProviderInfo.h
    OpenHome/Av/TransportControl.h
    OpenHome/Av/ProviderTransport.h
    OpenHome/Av/Pins/TransportPins.h
    OpenHome/Av/Radio/TuneInPins.h
    OpenHome/Av/Radio/RadioPins.h
    OpenHome/Av/Pins/UrlPins.h
    OpenHome/Av/Utils/FaultCode.h
    OpenHome/Av/CalmRadio/CalmRadioPins.h
    OpenHome/Av/ProviderVolume.h
    OpenHome/Av/Source.h
    OpenHome/Av/MediaPlayer.h
    OpenHome/Av/Logger.h
    OpenHome/Json.h
    OpenHome/Av/Utils/FormUrl.h
    OpenHome/NtpClient.h
    OpenHome/UnixTimestamp.h
    OpenHome/Configuration/ProviderConfig.h
    OpenHome/Configuration/ProviderConfigApp.h
    OpenHome/PowerManager.h
    OpenHome/ThreadPool.h
    OpenHome/FsFlushPeriodic.h
    OpenHome/Av/Credentials.h
    OpenHome/Av/ProviderCredentials.h
    OpenHome/Av/VolumeManager.h
    OpenHome/Av/FriendlyNameAdapter.h
    OpenHome/Av/ProviderDebug.h
    OpenHome/Av/Pins/Pins.h
    OpenHome/Av/Pins/ProviderPins.h
    OpenHome/Av/OhMetadata.h
)
add_library(ohMediaPlayer STATIC ${OHMEDIAPLAYER_SOURCES})
target_link_libraries(ohMediaPlayer PRIVATE libressl::libressl ohNet ohPipeline)
target_include_directories(ohMediaPlayer PRIVATE ${PROJECT_SOURCE_DIR})
target_include_directories(ohMediaPlayer PUBLIC
  "${CMAKE_BINARY_DIR}"
  "${CMAKE_BINARY_DIR}/Generated"
)
add_dependencies(ohMediaPlayer oh_codegen)
target_sources(ohMediaPlayer PUBLIC FILE_SET HEADERS FILES "${OHMEDIAPLAYER_HEADERS}")
install(TARGETS ohMediaPlayer
    ARCHIVE DESTINATION ${CMAKE_INSTALL_LIBDIR}
    RUNTIME DESTINATION ${CMAKE_INSTALL_BINDIR}
    LIBRARY DESTINATION ${CMAKE_INSTALL_LIBDIR}
    FILE_SET HEADERS
    DESTINATION ${CMAKE_INSTALL_INCLUDEDIR}
    INCLUDES DESTINATION ${CMAKE_INSTALL_INCLUDEDIR}
)

add_library(Odp
    OpenHome/Net/Odp/Odp.cpp
    OpenHome/Net/Odp/DviOdp.cpp
    OpenHome/Net/Odp/DviProtocolOdp.cpp
    OpenHome/Net/Odp/DviServerOdp.cpp
    OpenHome/Net/Odp/CpiOdp.cpp
    OpenHome/Net/Odp/CpiDeviceOdp.cpp
    OpenHome/Net/Odp/CpDeviceOdp.cpp
)
target_link_libraries(Odp PRIVATE ohNet)
target_include_directories(Odp PRIVATE ${PROJECT_SOURCE_DIR})
set(ODP_HEADERS
    OpenHome/Net/Odp/Odp.h
    OpenHome/Net/Odp/DviOdp.h
    OpenHome/Net/Odp/DviProtocolOdp.h
    OpenHome/Net/Odp/DviServerOdp.h
    OpenHome/Net/Odp/CpiOdp.h
    OpenHome/Net/Odp/CpiDeviceOdp.h
    OpenHome/Net/Odp/CpDeviceOdp.h
)
target_sources(Odp PUBLIC FILE_SET HEADERS FILES "${ODP_HEADERS}")
install(TARGETS Odp
    ARCHIVE DESTINATION ${CMAKE_INSTALL_LIBDIR}
    RUNTIME DESTINATION ${CMAKE_INSTALL_BINDIR}
    LIBRARY DESTINATION ${CMAKE_INSTALL_LIBDIR}
    FILE_SET HEADERS
    DESTINATION ${CMAKE_INSTALL_INCLUDEDIR}
    INCLUDES DESTINATION ${CMAKE_INSTALL_INCLUDEDIR}
)

add_library(SourcePlaylist
    Generated/DvAvOpenhomeOrgPlaylist1.cpp
    Generated/CpAvOpenhomeOrgPlaylist1.cpp
    OpenHome/Av/Playlist/ProviderPlaylist.cpp
    OpenHome/Av/Playlist/SourcePlaylist.cpp
    OpenHome/Av/Playlist/TrackDatabase.cpp
    OpenHome/Av/Playlist/UriProviderPlaylist.cpp
    OpenHome/Av/Tidal/Tidal.cpp
    OpenHome/Av/Tidal/TidalMetadata.cpp
    OpenHome/Av/Tidal/TidalPins.cpp
    OpenHome/Av/Tidal/ProtocolTidal.cpp
    OpenHome/Av/Qobuz/Qobuz.cpp
    OpenHome/Av/Qobuz/QobuzMetadata.cpp
    OpenHome/Av/Qobuz/QobuzPins.cpp
    OpenHome/Av/Qobuz/ProtocolQobuz.cpp
    Generated/CpAvOpenhomeOrgTransport1.cpp
    OpenHome/Av/Playlist/PinInvokerPlaylist.cpp
    OpenHome/Av/Playlist/DeviceListMediaServer.cpp
    OpenHome/Av/Playlist/PinInvokerKazooServer.cpp
    OpenHome/Av/Playlist/PinInvokerUpnpServer.cpp
    Generated/CpUpnpOrgContentDirectory1.cpp
)
target_link_libraries(SourcePlaylist PRIVATE ohNet ohMediaPlayer Podcast SSL)
target_include_directories(SourcePlaylist PRIVATE ${PROJECT_SOURCE_DIR})
set(SOURCE_PLAYLIST_HEADERS
    OpenHome/Av/Playlist/ProviderPlaylist.h
    OpenHome/Av/Playlist/TrackDatabase.h
    OpenHome/Av/Playlist/UriProviderPlaylist.h
    OpenHome/Av/Tidal/Tidal.h
    OpenHome/Av/Tidal/TidalMetadata.h
    OpenHome/Av/Tidal/TidalPins.h
    OpenHome/Av/Qobuz/Qobuz.h
    OpenHome/Av/Qobuz/QobuzMetadata.h
    OpenHome/Av/Qobuz/QobuzPins.h
    OpenHome/Av/Playlist/PinInvokerPlaylist.h
    OpenHome/Av/Playlist/DeviceListMediaServer.h
    OpenHome/Av/Playlist/PinInvokerKazooServer.h
    OpenHome/Av/Playlist/PinInvokerUpnpServer.h
)
target_sources(SourcePlaylist PUBLIC FILE_SET HEADERS FILES "${SOURCE_PLAYLIST_HEADERS}")
install(TARGETS SourcePlaylist
    ARCHIVE DESTINATION ${CMAKE_INSTALL_LIBDIR}
    RUNTIME DESTINATION ${CMAKE_INSTALL_BINDIR}
    LIBRARY DESTINATION ${CMAKE_INSTALL_LIBDIR}
    FILE_SET HEADERS
    DESTINATION ${CMAKE_INSTALL_INCLUDEDIR}
    INCLUDES DESTINATION ${CMAKE_INSTALL_INCLUDEDIR}
)

add_library(SourceRadio
    OpenHome/Av/Radio/SourceRadio.cpp
    OpenHome/Av/Radio/PresetDatabase.cpp
    OpenHome/Av/Radio/UriProviderRadio.cpp
    OpenHome/Av/Radio/Presets.cpp
    OpenHome/Av/Radio/TuneIn.cpp
    OpenHome/Av/CalmRadio/CalmRadio.cpp
    OpenHome/Av/CalmRadio/ProtocolCalmRadio.cpp
    OpenHome/Av/Radio/ContentAsx.cpp
    OpenHome/Av/Radio/ContentM3u.cpp
    OpenHome/Av/Radio/ContentM3uX.cpp
    OpenHome/Av/Radio/ContentOpml.cpp
    OpenHome/Av/Radio/ContentPls.cpp
    Generated/DvAvOpenhomeOrgRadio2.cpp
    OpenHome/Av/Radio/ProviderRadio.cpp
)
target_link_libraries(SourceRadio PRIVATE ohNet ohMediaPlayer Podcast)
target_include_directories(SourceRadio PRIVATE ${PROJECT_SOURCE_DIR})
set(SOURCE_RADIO_HEADERS
    OpenHome/Av/Radio/SourceRadio.h
    OpenHome/Av/Radio/PresetDatabase.h
    OpenHome/Av/Radio/UriProviderRadio.h
    OpenHome/Av/Radio/Presets.h
    OpenHome/Av/Radio/TuneIn.h
    OpenHome/Av/CalmRadio/CalmRadio.h
    OpenHome/Av/Radio/ProviderRadio.h
)
target_sources(SourceRadio PUBLIC FILE_SET HEADERS FILES "${SOURCE_RADIO_HEADERS}")
install(TARGETS SourceRadio
    ARCHIVE DESTINATION ${CMAKE_INSTALL_LIBDIR}
    RUNTIME DESTINATION ${CMAKE_INSTALL_BINDIR}
    LIBRARY DESTINATION ${CMAKE_INSTALL_LIBDIR}
    FILE_SET HEADERS
    DESTINATION ${CMAKE_INSTALL_INCLUDEDIR}
    INCLUDES DESTINATION ${CMAKE_INSTALL_INCLUDEDIR}
)

add_library(SourceSongcast
    Generated/DvAvOpenhomeOrgSender2.cpp
    OpenHome/Av/Songcast/Ohm.cpp
    OpenHome/Av/Songcast/OhmMsg.cpp
    OpenHome/Av/Songcast/OhmSender.cpp
    OpenHome/Av/Songcast/OhmSocket.cpp
    OpenHome/Av/Songcast/ProtocolOhBase.cpp
    OpenHome/Av/Songcast/ProtocolOhu.cpp
    OpenHome/Av/Songcast/ProtocolOhm.cpp
    Generated/DvAvOpenhomeOrgReceiver1.cpp
    OpenHome/Av/Songcast/ProviderReceiver.cpp
    OpenHome/Av/Songcast/ZoneHandler.cpp
    OpenHome/Av/Songcast/SourceReceiver.cpp
    OpenHome/Av/Songcast/Splitter.cpp
    OpenHome/Av/Songcast/Sender.cpp
    OpenHome/Av/Songcast/SenderThread.cpp
    OpenHome/Av/Utils/DriverSongcastSender.cpp
)
target_link_libraries(SourceSongcast PRIVATE ohNet ohMediaPlayer)
target_include_directories(SourceSongcast PRIVATE ${PROJECT_SOURCE_DIR})
set(SOURCE_SONGCAST_HEADERS
    OpenHome/Av/Songcast/Ohm.h
    OpenHome/Av/Songcast/OhmMsg.h
    OpenHome/Av/Songcast/OhmSender.h
    OpenHome/Av/Songcast/OhmSocket.h
    OpenHome/Av/Songcast/ProtocolOhBase.h
    OpenHome/Av/Songcast/ProtocolOhu.h
    OpenHome/Av/Songcast/ProtocolOhm.h
    OpenHome/Av/Songcast/ProviderReceiver.h
    OpenHome/Av/Songcast/ZoneHandler.h
    OpenHome/Av/Songcast/Splitter.h
    OpenHome/Av/Songcast/Sender.h
    OpenHome/Av/Songcast/SenderThread.h
    OpenHome/Av/Utils/DriverSongcastSender.h
)
target_sources(SourceSongcast PUBLIC FILE_SET HEADERS FILES "${SOURCE_SONGCAST_HEADERS}")
install(TARGETS SourceSongcast
    ARCHIVE DESTINATION ${CMAKE_INSTALL_LIBDIR}
    RUNTIME DESTINATION ${CMAKE_INSTALL_BINDIR}
    LIBRARY DESTINATION ${CMAKE_INSTALL_LIBDIR}
    FILE_SET HEADERS
    DESTINATION ${CMAKE_INSTALL_INCLUDEDIR}
    INCLUDES DESTINATION ${CMAKE_INSTALL_INCLUDEDIR}
)

add_library(SourceScd
    OpenHome/Av/Scd/ScdMsg.cpp
    OpenHome/Av/Scd/Receiver/ProtocolScd.cpp
    OpenHome/Av/Scd/Receiver/SupplyScd.cpp
    OpenHome/Av/Scd/Receiver/UriProviderScd.cpp
)
target_link_libraries(SourceScd PRIVATE ohNet ohMediaPlayer)
target_include_directories(SourceScd PRIVATE ${PROJECT_SOURCE_DIR})
set(SOURCE_SCD_HEADERS
    OpenHome/Av/Scd/ScdMsg.h
    OpenHome/Av/Scd/Receiver/ProtocolScd.h
    OpenHome/Av/Scd/Receiver/SupplyScd.h
    OpenHome/Av/Scd/Receiver/UriProviderScd.h
)
target_sources(SourceScd PUBLIC FILE_SET HEADERS FILES "${SOURCE_SCD_HEADERS}")
install(TARGETS SourceScd
    ARCHIVE DESTINATION ${CMAKE_INSTALL_LIBDIR}
    RUNTIME DESTINATION ${CMAKE_INSTALL_BINDIR}
    LIBRARY DESTINATION ${CMAKE_INSTALL_LIBDIR}
    FILE_SET HEADERS
    DESTINATION ${CMAKE_INSTALL_INCLUDEDIR}
    INCLUDES DESTINATION ${CMAKE_INSTALL_INCLUDEDIR}
)

add_library(SourceRaop
    OpenHome/Av/Raop/Raop.cpp
    OpenHome/Av/Raop/SourceRaop.cpp
    OpenHome/Av/Raop/ProtocolRaop.cpp
    OpenHome/Av/Raop/UdpServer.cpp
    OpenHome/Av/Raop/CodecRaopApple.cpp
)
target_link_libraries(SourceRaop PRIVATE LibreSSL::Crypto ohNet ohMediaPlayer alac::alac)
target_include_directories(SourceRaop PRIVATE ${PROJECT_SOURCE_DIR})
set(SOURCE_RAOP_HEADERS
    OpenHome/Av/Raop/Raop.h
    OpenHome/Av/Raop/SourceRaop.h
    OpenHome/Av/Raop/ProtocolRaop.h
    OpenHome/Av/Raop/UdpServer.h
    OpenHome/Av/Raop/CodecRaopApple.h
)
target_sources(SourceRaop PUBLIC FILE_SET HEADERS FILES "${SOURCE_RAOP_HEADERS}")
install(TARGETS SourceRaop
    ARCHIVE DESTINATION ${CMAKE_INSTALL_LIBDIR}
    RUNTIME DESTINATION ${CMAKE_INSTALL_BINDIR}
    LIBRARY DESTINATION ${CMAKE_INSTALL_LIBDIR}
    FILE_SET HEADERS
    DESTINATION ${CMAKE_INSTALL_INCLUDEDIR}
    INCLUDES DESTINATION ${CMAKE_INSTALL_INCLUDEDIR}
)

add_library(SourceUpnpAv
    Generated/DvUpnpOrgAVTransport1.cpp
    OpenHome/Av/UpnpAv/ProviderAvTransport.cpp
    Generated/DvUpnpOrgConnectionManager1.cpp
    OpenHome/Av/UpnpAv/ProviderConnectionManager.cpp
    Generated/DvUpnpOrgRenderingControl1.cpp
    OpenHome/Av/UpnpAv/ProviderRenderingControl.cpp
    OpenHome/Av/UpnpAv/UpnpAv.cpp
    OpenHome/Av/UpnpAv/FriendlyNameUpnpAv.cpp
)
target_link_libraries(SourceUpnpAv PRIVATE ohNet ohMediaPlayer)
target_include_directories(SourceUpnpAv PRIVATE ${PROJECT_SOURCE_DIR})
set(SOURCE_UPNP_AV_HEADERS
    OpenHome/Av/UpnpAv/ProviderAvTransport.h
    OpenHome/Av/UpnpAv/ProviderConnectionManager.h
    OpenHome/Av/UpnpAv/ProviderRenderingControl.h
    OpenHome/Av/UpnpAv/UpnpAv.h
    OpenHome/Av/UpnpAv/FriendlyNameUpnpAv.h
)
target_sources(SourceUpnpAv PUBLIC FILE_SET HEADERS FILES "${SOURCE_UPNP_AV_HEADERS}")
install(TARGETS SourceUpnpAv
    ARCHIVE DESTINATION ${CMAKE_INSTALL_LIBDIR}
    RUNTIME DESTINATION ${CMAKE_INSTALL_BINDIR}
    LIBRARY DESTINATION ${CMAKE_INSTALL_LIBDIR}
    FILE_SET HEADERS
    DESTINATION ${CMAKE_INSTALL_INCLUDEDIR}
    INCLUDES DESTINATION ${CMAKE_INSTALL_INCLUDEDIR}
)

add_library(Podcast
    OpenHome/Av/Pins/PodcastPins.cpp
    OpenHome/Av/Pins/PodcastPinsITunes.cpp
    OpenHome/Av/Pins/PodcastPinsTuneIn.cpp
)
target_link_libraries(Podcast PRIVATE ohNet ohMediaPlayer)
target_include_directories(Podcast PRIVATE ${PROJECT_SOURCE_DIR})
set(PODCAST_HEADERS
    OpenHome/Av/Pins/PodcastPins.h
    OpenHome/Av/Pins/PodcastPinsITunes.h
    OpenHome/Av/Pins/PodcastPinsTuneIn.h
)
target_sources(Podcast PUBLIC FILE_SET HEADERS FILES "${PODCAST_HEADERS}")
install(TARGETS Podcast
    ARCHIVE DESTINATION ${CMAKE_INSTALL_LIBDIR}
    RUNTIME DESTINATION ${CMAKE_INSTALL_BINDIR}
    LIBRARY DESTINATION ${CMAKE_INSTALL_LIBDIR}
    FILE_SET HEADERS
    DESTINATION ${CMAKE_INSTALL_INCLUDEDIR}
    INCLUDES DESTINATION ${CMAKE_INSTALL_INCLUDEDIR}
)

set(SCDSENDER_SOURCES
  OpenHome/Av/Scd/ScdMsg.cpp
  OpenHome/Av/Scd/Sender/ScdSupply.cpp
  OpenHome/Av/Scd/Sender/ScdServer.cpp
)
set(SCD_SENDER_HEADERS
  OpenHome/Av/Scd/ScdMsg.h
  OpenHome/Av/Scd/Sender/ScdSupply.h
  OpenHome/Av/Scd/Sender/ScdServer.h
)
add_library(ScdSender STATIC ${SCDSENDER_SOURCES})
target_include_directories(ScdSender PUBLIC ${CMAKE_SOURCE_DIR})
target_include_directories(ScdSender PUBLIC
  ${CMAKE_BINARY_DIR}
)
target_link_libraries(ScdSender PUBLIC ohNet)
target_sources(ScdSender PUBLIC FILE_SET HEADERS FILES "${SCD_SENDER_HEADERS}")
install(TARGETS ScdSender
    ARCHIVE DESTINATION ${CMAKE_INSTALL_LIBDIR}
    RUNTIME DESTINATION ${CMAKE_INSTALL_BINDIR}
    LIBRARY DESTINATION ${CMAKE_INSTALL_LIBDIR}
    FILE_SET HEADERS
    DESTINATION ${CMAKE_INSTALL_INCLUDEDIR}
    INCLUDES DESTINATION ${CMAKE_INSTALL_INCLUDEDIR}
)

set(CODECWAV_SOURCES
  OpenHome/Media/Codec/Wav.cpp
)
add_library(CodecWav STATIC ${CODECWAV_SOURCES})
target_include_directories(CodecWav PUBLIC ${CMAKE_SOURCE_DIR})
target_include_directories(CodecWav PUBLIC
  ${CMAKE_BINARY_DIR}
)
target_link_libraries(CodecWav PUBLIC ohNet)
install(TARGETS CodecWav
    ARCHIVE DESTINATION ${CMAKE_INSTALL_LIBDIR}
    RUNTIME DESTINATION ${CMAKE_INSTALL_BINDIR}
    LIBRARY DESTINATION ${CMAKE_INSTALL_LIBDIR}
)

set(CODECPCM_SOURCES
  OpenHome/Media/Codec/Pcm.cpp
)
add_library(CodecPcm STATIC ${CODECPCM_SOURCES})
target_include_directories(CodecPcm PUBLIC ${CMAKE_SOURCE_DIR})
target_include_directories(CodecPcm PUBLIC
  ${CMAKE_BINARY_DIR}
)
target_link_libraries(CodecPcm PUBLIC ohNet)
install(TARGETS CodecPcm
    ARCHIVE DESTINATION ${CMAKE_INSTALL_LIBDIR}
    RUNTIME DESTINATION ${CMAKE_INSTALL_BINDIR}
    LIBRARY DESTINATION ${CMAKE_INSTALL_LIBDIR}
)

set(CODECDSDDSF_SOURCES
  OpenHome/Media/Codec/DsdDsf.cpp
)
add_library(CodecDsdDsf STATIC ${CODECDSDDSF_SOURCES})
target_include_directories(CodecDsdDsf PUBLIC ${CMAKE_SOURCE_DIR})
target_include_directories(CodecDsdDsf PUBLIC
  ${CMAKE_BINARY_DIR}
)
target_link_libraries(CodecDsdDsf PUBLIC ohNet)
install(TARGETS CodecDsdDsf
    ARCHIVE DESTINATION ${CMAKE_INSTALL_LIBDIR}
    RUNTIME DESTINATION ${CMAKE_INSTALL_BINDIR}
    LIBRARY DESTINATION ${CMAKE_INSTALL_LIBDIR}
)

set(CODECDSDDFF_SOURCES
  OpenHome/Media/Codec/DsdDff.cpp
)
add_library(CodecDsdDff STATIC ${CODECDSDDFF_SOURCES})
target_include_directories(CodecDsdDff PUBLIC ${CMAKE_SOURCE_DIR})
target_include_directories(CodecDsdDff PUBLIC
  ${CMAKE_BINARY_DIR}
)
target_link_libraries(CodecDsdDff PUBLIC ohNet)
install(TARGETS CodecDsdDff
    ARCHIVE DESTINATION ${CMAKE_INSTALL_LIBDIR}
    RUNTIME DESTINATION ${CMAKE_INSTALL_BINDIR}
    LIBRARY DESTINATION ${CMAKE_INSTALL_LIBDIR}
)

set(CODECDSDRAW_SOURCES
  OpenHome/Media/Codec/DsdRaw.cpp
)
add_library(CodecDsdRaw STATIC ${CODECDSDRAW_SOURCES})
target_include_directories(CodecDsdRaw PUBLIC ${CMAKE_SOURCE_DIR})
target_include_directories(CodecDsdRaw PUBLIC
  ${CMAKE_BINARY_DIR}
)
target_link_libraries(CodecDsdRaw PUBLIC ohNet)
install(TARGETS CodecDsdRaw
    ARCHIVE DESTINATION ${CMAKE_INSTALL_LIBDIR}
    RUNTIME DESTINATION ${CMAKE_INSTALL_BINDIR}
    LIBRARY DESTINATION ${CMAKE_INSTALL_LIBDIR}
)

set(CODECAIFFBASE_SOURCES
  OpenHome/Media/Codec/AiffBase.cpp
)
set(CODECAIFFBASE_HEADERS
  OpenHome/Media/Codec/AiffBase.h
)
add_library(CodecAiffBase STATIC ${CODECAIFFBASE_SOURCES})
target_include_directories(CodecAiffBase PUBLIC ${CMAKE_SOURCE_DIR})
target_include_directories(CodecAiffBase PUBLIC
  ${CMAKE_BINARY_DIR}
)
target_link_libraries(CodecAiffBase PUBLIC ohNet)
target_sources(CodecAiffBase PUBLIC FILE_SET HEADERS FILES "${CODECAIFFBASE_HEADERS}")
install(TARGETS CodecAiffBase
    ARCHIVE DESTINATION ${CMAKE_INSTALL_LIBDIR}
    RUNTIME DESTINATION ${CMAKE_INSTALL_BINDIR}
    LIBRARY DESTINATION ${CMAKE_INSTALL_LIBDIR}
    FILE_SET HEADERS
    DESTINATION ${CMAKE_INSTALL_INCLUDEDIR}
    INCLUDES DESTINATION ${CMAKE_INSTALL_INCLUDEDIR}
)

set(CODECAIFC_SOURCES
  OpenHome/Media/Codec/Aifc.cpp
)
add_library(CodecAifc STATIC ${CODECAIFC_SOURCES})
target_include_directories(CodecAifc PUBLIC ${CMAKE_SOURCE_DIR})
target_include_directories(CodecAifc PUBLIC
  ${CMAKE_BINARY_DIR}
)
target_link_libraries(CodecAifc PUBLIC CodecAiffBase ohNet)
install(TARGETS CodecAifc
    ARCHIVE DESTINATION ${CMAKE_INSTALL_LIBDIR}
    RUNTIME DESTINATION ${CMAKE_INSTALL_BINDIR}
    LIBRARY DESTINATION ${CMAKE_INSTALL_LIBDIR}
)

set(CODECAIFF_SOURCES
  OpenHome/Media/Codec/Aiff.cpp
)
add_library(CodecAiff STATIC ${CODECAIFF_SOURCES})
target_include_directories(CodecAiff PUBLIC ${CMAKE_SOURCE_DIR})
target_include_directories(CodecAiff PUBLIC
  ${CMAKE_BINARY_DIR}
)
target_link_libraries(CodecAiff PUBLIC CodecAiffBase ohNet)
install(TARGETS CodecAiff
    ARCHIVE DESTINATION ${CMAKE_INSTALL_LIBDIR}
    RUNTIME DESTINATION ${CMAKE_INSTALL_BINDIR}
    LIBRARY DESTINATION ${CMAKE_INSTALL_LIBDIR}
)

set(CODECFLAC_SOURCES
  OpenHome/Media/Codec/Flac.cpp
)
add_library(CodecFlac STATIC ${CODECFLAC_SOURCES})
target_include_directories(CodecFlac PUBLIC ${CMAKE_SOURCE_DIR})
target_include_directories(CodecFlac PUBLIC
  ${CMAKE_BINARY_DIR}
)
target_link_libraries(CodecFlac PUBLIC
  ohNet
  flac::flac
  Ogg::ogg
)
install(TARGETS CodecFlac
    ARCHIVE DESTINATION ${CMAKE_INSTALL_LIBDIR}
    RUNTIME DESTINATION ${CMAKE_INSTALL_BINDIR}
    LIBRARY DESTINATION ${CMAKE_INSTALL_LIBDIR}
)

set(CODECALACAPPLEBASE_SOURCES
  OpenHome/Media/Codec/AlacAppleBase.cpp
)
set(CODECALACAPPLEBASE_HEADERS
  OpenHome/Media/Codec/AlacAppleBase.h
)
add_library(CodecAlacAppleBase STATIC ${CODECALACAPPLEBASE_SOURCES})
target_include_directories(CodecAlacAppleBase PUBLIC ${CMAKE_SOURCE_DIR})
target_include_directories(CodecAlacAppleBase PUBLIC
  ${CMAKE_BINARY_DIR}
)
target_link_libraries(CodecAlacAppleBase PUBLIC alac::alac ohNet ohMediaPlayer)
target_sources(CodecAlacAppleBase PUBLIC FILE_SET HEADERS FILES "${CODECALACAPPLEBASE_HEADERS}")
install(TARGETS CodecAlacAppleBase
    ARCHIVE DESTINATION ${CMAKE_INSTALL_LIBDIR}
    RUNTIME DESTINATION ${CMAKE_INSTALL_BINDIR}
    LIBRARY DESTINATION ${CMAKE_INSTALL_LIBDIR}
    FILE_SET HEADERS
    DESTINATION ${CMAKE_INSTALL_INCLUDEDIR}
    INCLUDES DESTINATION ${CMAKE_INSTALL_INCLUDEDIR}
)

set(CODECALACAPPLE_SOURCES
  OpenHome/Media/Codec/AlacApple.cpp
)
add_library(CodecAlacApple STATIC ${CODECALACAPPLE_SOURCES})
target_include_directories(CodecAlacApple PUBLIC ${CMAKE_SOURCE_DIR})
target_include_directories(CodecAlacApple PUBLIC
  ${CMAKE_BINARY_DIR}
)
target_link_libraries(CodecAlacApple PUBLIC CodecAlacAppleBase ohNet)
install(TARGETS CodecAlacApple
    ARCHIVE DESTINATION ${CMAKE_INSTALL_LIBDIR}
    RUNTIME DESTINATION ${CMAKE_INSTALL_BINDIR}
    LIBRARY DESTINATION ${CMAKE_INSTALL_LIBDIR}
)

set(CODECAACFDKBASE_SOURCES
  OpenHome/Media/Codec/AacFdkBase.cpp
)
set(CODECAACFDKBASE_HEADERS
  OpenHome/Media/Codec/AacFdkBase.h
)
add_library(CodecAacFdkBase STATIC ${CODECAACFDKBASE_SOURCES})
target_include_directories(CodecAacFdkBase PUBLIC ${CMAKE_SOURCE_DIR})
target_include_directories(CodecAacFdkBase PUBLIC
  ${CMAKE_BINARY_DIR}
)
target_link_libraries(CodecAacFdkBase PUBLIC
  ohNet
  FDK-AAC::fdk-aac
)
target_sources(CodecAacFdkBase PUBLIC FILE_SET HEADERS FILES "${CODECAACFDKBASE_HEADERS}")
install(TARGETS CodecAacFdkBase
    ARCHIVE DESTINATION ${CMAKE_INSTALL_LIBDIR}
    RUNTIME DESTINATION ${CMAKE_INSTALL_BINDIR}
    LIBRARY DESTINATION ${CMAKE_INSTALL_LIBDIR}
    FILE_SET HEADERS
    DESTINATION ${CMAKE_INSTALL_INCLUDEDIR}
    INCLUDES DESTINATION ${CMAKE_INSTALL_INCLUDEDIR}
)

set(CODECAACFDKMP4_SOURCES
  OpenHome/Media/Codec/AacFdkMp4.cpp
)
add_library(CodecAacFdkMp4 STATIC ${CODECAACFDKMP4_SOURCES})
target_include_directories(CodecAacFdkMp4 PUBLIC ${CMAKE_SOURCE_DIR})
target_include_directories(CodecAacFdkMp4 PUBLIC
  ${CMAKE_BINARY_DIR}
)
target_link_libraries(CodecAacFdkMp4 PUBLIC ohNetCore CodecAacFdkBase ohNet)
install(TARGETS CodecAacFdkMp4
    ARCHIVE DESTINATION ${CMAKE_INSTALL_LIBDIR}
    RUNTIME DESTINATION ${CMAKE_INSTALL_BINDIR}
    LIBRARY DESTINATION ${CMAKE_INSTALL_LIBDIR}
)

set(CODECAACFDKADTS_SOURCES
  OpenHome/Media/Codec/AacFdkAdts.cpp
)
add_library(CodecAacFdkAdts STATIC ${CODECAACFDKADTS_SOURCES})
target_include_directories(CodecAacFdkAdts PUBLIC ${CMAKE_SOURCE_DIR})
target_include_directories(CodecAacFdkAdts PUBLIC
  ${CMAKE_BINARY_DIR}
)
target_link_libraries(CodecAacFdkAdts PUBLIC CodecAacFdkBase ohNet)
install(TARGETS CodecAacFdkAdts
    ARCHIVE DESTINATION ${CMAKE_INSTALL_LIBDIR}
    RUNTIME DESTINATION ${CMAKE_INSTALL_BINDIR}
    LIBRARY DESTINATION ${CMAKE_INSTALL_LIBDIR}
)

set(CODECMP3_SOURCES
  OpenHome/Media/Codec/Mp3.cpp
)
add_library(CodecMp3 STATIC ${CODECMP3_SOURCES})
target_include_directories(CodecMp3 PUBLIC ${CMAKE_SOURCE_DIR})
target_include_directories(CodecMp3 PUBLIC
  ${CMAKE_BINARY_DIR}
)
target_link_libraries(CodecMp3 PUBLIC
  ohNet
  libmad::libmad
)
install(TARGETS CodecMp3
    ARCHIVE DESTINATION ${CMAKE_INSTALL_LIBDIR}
    RUNTIME DESTINATION ${CMAKE_INSTALL_BINDIR}
    LIBRARY DESTINATION ${CMAKE_INSTALL_LIBDIR}
)

set(CODECVORBIS_SOURCES
  OpenHome/Media/Codec/Vorbis.cpp
)
add_library(CodecVorbis STATIC ${CODECVORBIS_SOURCES})
target_include_directories(CodecVorbis PUBLIC ${CMAKE_SOURCE_DIR})
target_include_directories(CodecVorbis PUBLIC
    thirdparty/Tremor
  ${CMAKE_BINARY_DIR}
)
target_link_libraries(CodecVorbis PUBLIC
  ohnet::ohnet
  Ogg::ogg
  vorbis::vorbis
)
install(TARGETS CodecVorbis
    ARCHIVE DESTINATION ${CMAKE_INSTALL_LIBDIR}
    RUNTIME DESTINATION ${CMAKE_INSTALL_BINDIR}
    LIBRARY DESTINATION ${CMAKE_INSTALL_LIBDIR}
)

set(WEBAPPFRAMEWORK_SOURCES
  OpenHome/Web/ResourceHandler.cpp
  OpenHome/Web/WebAppFramework.cpp
)
set(WEBAPPFRAMEWORK_HEADERS
  OpenHome/Web/ResourceHandler.h
  OpenHome/Web/WebAppFramework.h
)
add_library(WebAppFramework STATIC ${WEBAPPFRAMEWORK_SOURCES})
target_include_directories(WebAppFramework PUBLIC ${CMAKE_SOURCE_DIR})
target_include_directories(WebAppFramework PUBLIC
  ${CMAKE_BINARY_DIR}
)
target_link_libraries(WebAppFramework PUBLIC ohNet)
target_sources(WebAppFramework PUBLIC FILE_SET HEADERS FILES "${WEBAPPFRAMEWORK_HEADERS}")
install(TARGETS WebAppFramework
    ARCHIVE DESTINATION ${CMAKE_INSTALL_LIBDIR}
    RUNTIME DESTINATION ${CMAKE_INSTALL_BINDIR}
    LIBRARY DESTINATION ${CMAKE_INSTALL_LIBDIR}
    FILE_SET HEADERS
    DESTINATION ${CMAKE_INSTALL_INCLUDEDIR}
    INCLUDES DESTINATION ${CMAKE_INSTALL_INCLUDEDIR}
)

# TODO: Install and add resdir?
# Copy ConfigUi resources to 'build' and 'install/bin'.
# file(
#   COPY ${CMAKE_SOURCE_DIR}/OpenHome/Web/ConfigUi/res
#   DESTINATION ${CMAKE_BINARY_DIR}
# )

set(WEBAPPFRAMEWORKTESTUTILS_SOURCES
  OpenHome/Web/Tests/TestWebAppFramework.cpp
)
add_library(WebAppFrameworkTestUtils STATIC ${WEBAPPFRAMEWORKTESTUTILS_SOURCES})
target_include_directories(WebAppFrameworkTestUtils PUBLIC ${CMAKE_SOURCE_DIR})
target_include_directories(WebAppFrameworkTestUtils PUBLIC
  ${CMAKE_BINARY_DIR}
)
target_link_libraries(WebAppFrameworkTestUtils PUBLIC WebAppFramework ohNet)
install(TARGETS WebAppFrameworkTestUtils
    ARCHIVE DESTINATION ${CMAKE_INSTALL_LIBDIR}
    RUNTIME DESTINATION ${CMAKE_INSTALL_BINDIR}
    LIBRARY DESTINATION ${CMAKE_INSTALL_LIBDIR}
)

set(CONFIGUI_SOURCES
  OpenHome/Web/ConfigUi/ConfigUi.cpp
  OpenHome/Web/ConfigUi/FileResourceHandler.cpp
  OpenHome/Web/ConfigUi/ConfigUiMediaPlayer.cpp
)
set(CONFIGUI_HEADERS
  OpenHome/Web/ConfigUi/ConfigUi.h
  OpenHome/Web/ConfigUi/FileResourceHandler.h
  OpenHome/Web/ConfigUi/ConfigUiMediaPlayer.h
)
add_library(ConfigUi STATIC ${CONFIGUI_SOURCES})
target_include_directories(ConfigUi PUBLIC ${CMAKE_SOURCE_DIR})
target_include_directories(ConfigUi PUBLIC
  ${CMAKE_BINARY_DIR}
)
target_link_libraries(ConfigUi PUBLIC WebAppFramework ohNet)
target_sources(ConfigUi PUBLIC FILE_SET HEADERS FILES "${CONFIGUI_HEADERS}")
install(TARGETS ConfigUi
    ARCHIVE DESTINATION ${CMAKE_INSTALL_LIBDIR}
    RUNTIME DESTINATION ${CMAKE_INSTALL_BINDIR}
    LIBRARY DESTINATION ${CMAKE_INSTALL_LIBDIR}
    FILE_SET HEADERS
    DESTINATION ${CMAKE_INSTALL_INCLUDEDIR}
    INCLUDES DESTINATION ${CMAKE_INSTALL_INCLUDEDIR}
)

set(CONFIGUITESTUTILS_SOURCES
  OpenHome/Web/ConfigUi/Tests/TestConfigUi.cpp
)
set(CONFIGUITESTUTILS_HEADERS
  OpenHome/Web/ConfigUi/Tests/TestConfigUi.h
)
add_library(ConfigUiTestUtils STATIC ${CONFIGUITESTUTILS_SOURCES})
target_include_directories(ConfigUiTestUtils PUBLIC ${CMAKE_SOURCE_DIR})
target_include_directories(ConfigUiTestUtils PUBLIC
  ${CMAKE_BINARY_DIR}
)
target_link_libraries(ConfigUiTestUtils PUBLIC
  ConfigUi
  WebAppFramework
  ohNet
  libressl::libressl
)
target_sources(ConfigUiTestUtils PUBLIC FILE_SET HEADERS FILES "${CONFIGUITESTUTILS_HEADERS}")
install(TARGETS ConfigUiTestUtils
    ARCHIVE DESTINATION ${CMAKE_INSTALL_LIBDIR}
    RUNTIME DESTINATION ${CMAKE_INSTALL_BINDIR}
    LIBRARY DESTINATION ${CMAKE_INSTALL_LIBDIR}
    FILE_SET HEADERS
    DESTINATION ${CMAKE_INSTALL_INCLUDEDIR}
    INCLUDES DESTINATION ${CMAKE_INSTALL_INCLUDEDIR}
)
