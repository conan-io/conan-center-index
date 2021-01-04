#include <iostream>
#include <string>

#include <kml/base/math_util.h>
#include <kml/convenience/convenience.h>
#include <kml/dom.h>
#include <kml/engine.h>

void test_kmlbase() {
  double lat_from = 23.27;
  double lng_from = 47.05;
  double alt_from = 10.07;
  double lat_to = -17.80;
  double lng_to = 174.41;
  double alt_to = 89.24;

  std::cout << "#=======================================#\n";
  std::cout << "#             test_kmlbase              #\n";
  std::cout << "#=======================================#\n";
  std::cout << kmlbase::AzimuthBetweenPoints(lat_from, lng_from, lat_to, lng_to) << '\n';
  std::cout << kmlbase::DistanceBetweenPoints(lat_from, lng_from, lat_to, lng_to) << '\n';
  std::cout << kmlbase::DistanceBetweenPoints3d(lat_from, lng_from, alt_from, lat_to, lng_to, alt_to) << '\n';
}

kmldom::PointPtr createPointCoordinates(double lat, double lon) {
  kmldom::KmlFactory *kml_factory = kmldom::KmlFactory::GetFactory();
  kmldom::PointPtr point = kml_factory->CreatePoint();
  kmldom::CoordinatesPtr coordinates = kmldom::KmlFactory::GetFactory()->CreateCoordinates();
  coordinates->add_latlng(lat, lon);
  point->set_coordinates(coordinates);
  return point;
}

void test_kmlengine() {
  const double kLat = -22.22;
  const double kLon = 42.123;

  kmldom::PointPtr point = createPointCoordinates(kLat, kLon);
  double pointLat, pointLon;
  kmlengine::GetPointLatLon(point, &pointLat, &pointLon);

  kmldom::KmlFactory *factory = kmldom::KmlFactory::GetFactory();
  kmldom::PlacemarkPtr placemark = factory->CreatePlacemark();
  placemark->set_geometry(point);
  double placemarkLat, placemarkLon;
  bool resultPlacemark = kmlengine::GetFeatureLatLon(placemark, &placemarkLat, &placemarkLon);

  std::cout << "#=======================================#\n";
  std::cout << "#            test_kmlengine             #\n";
  std::cout << "#=======================================#\n";
  std::cout << "Input (Latitude, Longitude)=(" << kLat << ", " << kLon << ")\n";
  std::cout << "Created Point at (Latitude, Longitude)=(" << pointLat << ", " << pointLon << ")\n";
  std::cout << "Created Placemark at (Latitude, Longitude)=(" << placemarkLat << ", " << placemarkLon << ")\n";
}

void test_kmlconvenience() {
  kmldom::KmlFactory* kml_factory = kmldom::KmlFactory::GetFactory();
  kmldom::FolderPtr folder = kml_factory->CreateFolder();
  folder->set_id("f0");
  folder->set_name("Folder 0");
  kmldom::PlacemarkPtr placemark = kml_factory->CreatePlacemark();
  placemark->set_id("pm0");
  placemark->set_name("Placemark 0");
  folder->add_feature(placemark);
  placemark = kml_factory->CreatePlacemark();
  placemark->set_id("pm1");
  placemark->set_name("Placemark 1");
  folder->add_feature(placemark);
  kmldom::KmlPtr kml = kml_factory->CreateKml();
  kml->set_feature(folder);

  kmlengine::KmlFilePtr kml_file = kmlengine::KmlFile::CreateFromImport(kml);

  kmldom::ChangePtr change = kml_factory->CreateChange();
  placemark = kmlconvenience::CreatePointPlacemark("new name", 38, -120);
  placemark->set_targetid("pm0");
  change->add_object(placemark);
  kmldom::UpdatePtr update = kml_factory->CreateUpdate();
  update->add_updateoperation(change);

  kmlengine::ProcessUpdate(update, kml_file);

  std::string xml;
  kml_file->SerializeToString(&xml);

  std::cout << "#=======================================#\n";
  std::cout << "#          test_kmlconvenience          #\n";
  std::cout << "#=======================================#\n";
  std::cout << xml << std::endl;
}

int main() {
  test_kmlbase();
  test_kmlengine();
  test_kmlconvenience();

  return 0;
}
