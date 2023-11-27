#include <cstdio>

#ifdef LIBHAL_LESS_2

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

#else

#include <libhal/pwm.hpp>

class test_pwm : public hal::pwm {
private:
  virtual hal::result<frequency_t> driver_frequency(hal::hertz p_frequency) {
    std::printf("frequency = %f Hz\n", p_frequency);

    return frequency_t{};
  }
  virtual hal::result<duty_cycle_t> driver_duty_cycle(float p_position) {
    error_count_down--;
    if (error_count_down == 0) {
      return hal::new_error(std::errc::io_error);
    }

    std::printf("duty cycle = %f %%\n", p_position);

    return duty_cycle_t{};
  }
  int error_count_down = 2;
};

int main() {
  using namespace hal::literals;

  int status = 0;
  test_pwm pwm;
  hal::attempt_all(
    [&pwm]() -> hal::status {
      HAL_CHECK(pwm.frequency(10.0_kHz));

      HAL_CHECK(pwm.duty_cycle(0.25));
      HAL_CHECK(pwm.duty_cycle(0.50));
      HAL_CHECK(pwm.duty_cycle(-0.25));
      HAL_CHECK(pwm.duty_cycle(-1.0));

      return hal::success();
    },
    [](std::errc p_errc) {
      std::printf("Caught error successfully!\n");
      std::printf("    Error value: %s\n",
                  std::strerror(static_cast<int>(p_errc)));
    },
    [&status]() {
      std::printf("Unknown error!\n");
      status = -1;
    });

  return status;
}

#endif
