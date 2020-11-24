#include <rtm/constants.h>
#include <rtm/scalarf.h>
#include <rtm/scalard.h>

using namespace rtm;

int main()
{
    scalar_near_equal(float(constants::pi()), 3.141592653589793238462643383279502884F, 1.0e-6F);
	scalar_near_equal(float(-constants::pi()), -3.141592653589793238462643383279502884F, 1.0e-6F);
	scalar_near_equal(float(+constants::pi()), +3.141592653589793238462643383279502884F, 1.0e-6F);
	scalar_near_equal(float(constants::pi()) * 2.0F, 3.141592653589793238462643383279502884F * 2.0F, 1.0e-6F);
	scalar_near_equal(float(2.0F * constants::pi()), 2.0F * 3.141592653589793238462643383279502884F, 1.0e-6F);
	scalar_near_equal(float(constants::pi()) / 2.0F, 3.141592653589793238462643383279502884F / 2.0F, 1.0e-6F);
	scalar_near_equal(float(2.0F / constants::pi()), 2.0F / 3.141592653589793238462643383279502884F, 1.0e-6F);
	scalar_near_equal(float(constants::pi()) + 1.0F, 3.141592653589793238462643383279502884F + 1.0F, 1.0e-6F);
	scalar_near_equal(float(1.0F + constants::pi()), 1.0F + 3.141592653589793238462643383279502884F, 1.0e-6F);
	scalar_near_equal(float(constants::pi()) - 1.0F, 3.141592653589793238462643383279502884F - 1.0F, 1.0e-6F);
	scalar_near_equal(float(1.0F - constants::pi()), 1.0F - 3.141592653589793238462643383279502884F, 1.0e-6F);

	// Double
	scalar_near_equal(double(constants::pi()), 3.141592653589793238462643383279502884, 1.0e-6);
	scalar_near_equal(double(-constants::pi()), -3.141592653589793238462643383279502884, 1.0e-6);
	scalar_near_equal(double(+constants::pi()), +3.141592653589793238462643383279502884, 1.0e-6);
	scalar_near_equal(double(constants::pi() * 2.0), 3.141592653589793238462643383279502884 * 2.0, 1.0e-6);
	scalar_near_equal(double(2.0 * constants::pi()), 2.0 * 3.141592653589793238462643383279502884, 1.0e-6);
	scalar_near_equal(double(constants::pi() / 2.0), 3.141592653589793238462643383279502884 / 2.0, 1.0e-6);
	scalar_near_equal(double(2.0 / constants::pi()), 2.0 / 3.141592653589793238462643383279502884, 1.0e-6);
	scalar_near_equal(double(constants::pi() + 1.0), 3.141592653589793238462643383279502884 + 1.0, 1.0e-6);
	scalar_near_equal(double(1.0 + constants::pi()), 1.0 + 3.141592653589793238462643383279502884, 1.0e-6);
	scalar_near_equal(double(constants::pi() - 1.0), 3.141592653589793238462643383279502884 - 1.0, 1.0e-6);
	scalar_near_equal(double(1.0 - constants::pi()), 1.0 - 3.141592653589793238462643383279502884, 1.0e-6);

    return 0;
}
