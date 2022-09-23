#include <cstdio>

#include <libhal/pwm/interface.hpp>
#include <libhal/servo/rc.hpp>

class test_pwm : public hal::pwm
{
private:
  hal::status driver_frequency(hal::hertz p_frequency) noexcept override
  {
    std::printf("frequency = %f Hz\n", p_frequency);
    return {};
  }
  hal::status driver_duty_cycle(hal::percentage p_position) noexcept override
  {
    std::printf("duty cycle = %f %%\n", p_position.value());
    return {};
  }
};

int main()
{
  test_pwm pwm;
  auto rc_servo = hal::rc_servo::create(pwm).value();
  rc_servo.position(0.25).value();
  rc_servo.position(0.50).value();
  rc_servo.position(-0.25).value();
  rc_servo.position(-1.0).value();
  return 0;
}
