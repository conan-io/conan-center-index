#include <sstream>
#include <svgwrite/writer.hpp>

int main() {
	std::ostringstream os;
	svgw::writer w(os);
	w.start_svg("12cm", "4cm", {{"viewBox", "0 0 1200 400"}});
	w.rect(1, 1, 1198, 398, {{"fill", "none"}, {"stroke", "blue"}, {"stroke-width", "2"}});
	w.start_g({{"stroke", "green"}});
	w.line(100, 300, 300, 100, {{"stroke-width", 5}});
	w.line(300, 300, 500, 100, {{"stroke-width", 10}});
	w.line(500, 300, 700, 100, {{"stroke-width", 15}});
	w.line(700, 300, 900, 100, {{"stroke-width", 20}});
	w.line(900, 300, 1100, 100, {{"stroke-width", 25.2}});
	w.end_g();
	w.end_svg();
}
