#include <agg_basics.h>
#include <agg_platform_support.h>
enum flip_y_e { flip_y = true };

int agg_main(int argc, char* argv[]) {
	agg::platform_support app(agg::pix_format_bgr24, flip_y);
    app.caption("AGG Example. Anti-Aliasing Demo");

	return 0;
}
