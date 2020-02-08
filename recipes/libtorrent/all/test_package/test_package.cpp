// From https://www.libtorrent.org/tutorial.html

#include <libtorrent/session.hpp>
#include <libtorrent/add_torrent_params.hpp>
#include <libtorrent/torrent_handle.hpp>
#include <libtorrent/alert_types.hpp>
#include <libtorrent/magnet_uri.hpp>

#include <iostream>
#include <thread>
#include <chrono>

int main(int argc, char const* argv[]) try
{
  if (argc != 2) {
    std::cerr << "usage: " << argv[0] << " <magnet-url>" << std::endl;
    return 1;
  }
  lt::settings_pack p;
  p.set_int(lt::settings_pack::alert_mask, lt::alert::status_notification
    | lt::alert::error_notification);
  lt::session ses(p);

  lt::add_torrent_params atp = lt::parse_magnet_uri(argv[1]);
  atp.save_path = "."; // save in current dir
//  lt::torrent_handle h = ses.add_torrent(std::move(atp));

  std::cout << "skipping download...\n";

//  for (;;) {
//    std::vector<lt::alert*> alerts;
//    ses.pop_alerts(&alerts);
//
//    for (lt::alert const* a : alerts) {
//      std::cout << a->message() << std::endl;
//      // if we receive the finished alert or an error, we're done
//      if (lt::alert_cast<lt::torrent_finished_alert>(a)) {
//        goto done;
//      }
//      if (lt::alert_cast<lt::torrent_error_alert>(a)) {
//        goto done;
//      }
//    }
//    std::this_thread::sleep_for(std::chrono::milliseconds(200));
//  }

  done:
  std::cout << "done, shutting down" << std::endl;
}
catch (std::exception& e)
{
  std::cerr << "Error: " << e.what() << std::endl;
}
