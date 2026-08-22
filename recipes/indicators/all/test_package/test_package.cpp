#include <indicators/cursor_control.hpp>
#include <indicators/progress_bar.hpp>
#include <indicators/progress_spinner.hpp>
#include <vector>

// Copied from indicators' demo

int main() {
  using namespace indicators;

  // Hide cursor
  show_console_cursor(false);

  {
    //
    // PROGRESS BAR 1
    //
    indicators::ProgressBar p{
        option::BarWidth{50},
        option::Start{"["},
        option::Fill{"■"},
        option::Lead{"■"},
        option::Remainder{" "},
        option::End{" ]"},
        option::ForegroundColor{indicators::Color::yellow},
        option::FontStyles{std::vector<indicators::FontStyle>{indicators::FontStyle::bold}}};

    std::atomic<size_t> index{0};
    std::vector<std::string> status_text = {"Rocket.exe is not responding",
                                            "Buying more snacks",
                                            "Finding a replacement engineer",
                                            "Assimilating the modding community",
                                            "Crossing fingers",
                                            "Porting KSP to a Nokia 3310",
                                            "Flexing struts",
                                            "Releasing space whales",
                                            "Watching paint dry"};

    auto job = [&p, &index, &status_text]() {
      while (true) {
        if (p.is_completed())
          break;
        p.set_option(option::PostfixText{status_text[index % status_text.size()]});
        p.set_progress(index * 10);
        index += 1;
        std::this_thread::sleep_for(std::chrono::milliseconds(1));
      }
    };
    std::thread thread(job);
    thread.join();
  }

  // Show cursor
  show_console_cursor(true);

  return 0;
}
