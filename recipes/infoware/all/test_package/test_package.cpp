#include <iostream>

#include <infoware/system.hpp>
#include <infoware/cpu.hpp>

static const char* kernel_variant_name(iware::system::kernel_t variant) noexcept {
	switch(variant) {
		case iware::system::kernel_t::windows_nt:
			return "Windows NT";
		case iware::system::kernel_t::linux:
			return "Linux";
		case iware::system::kernel_t::darwin:
			return "Darwin";
		default:
			return "Unknown";
	}
}

void infoware_system() {
    {
		std::cout << "\n"
		             "  Connected HIDs:\n"
		          << "    Mice     : " << iware::system::mouse_amount() << '\n'
		          << "    Keyboards: " << iware::system::keyboard_amount() << '\n'
		          << "    Other    : " << iware::system::other_HID_amount() << '\n';
	}

	{
		const auto memory = iware::system::memory();
		std::cout << "\n"
		             "  Memory:\n"
		             "    Physical:\n"
		          << "      Available: " << memory.physical_available << "B\n"
		          << "      Total    : " << memory.physical_total << "B\n"
		          << "    Virtual:\n"
		          << "      Available: " << memory.virtual_available << "B\n"
		          << "      Total    : " << memory.virtual_total << "B\n";
	}

	{
		const auto kernel_info = iware::system::kernel_info();
		std::cout << "\n"
		             "  Kernel:\n"
		          << "    Variant: " << kernel_variant_name(kernel_info.variant) << '\n'
		          << "    Version: " << kernel_info.major << '.' << kernel_info.minor << '.' << kernel_info.patch << " build " << kernel_info.build_number << '\n';
	}

	{
		const auto OS_info = iware::system::OS_info();
		std::cout << "\n"
		             "  OS:\n"
		          << "    Name     : " << OS_info.name << '\n'
		          << "    Full name: " << OS_info.full_name << '\n'
		          << "    Version  : " << OS_info.major << '.' << OS_info.minor << '.' << OS_info.patch << " build " << OS_info.build_number << '\n';
	}

	{
		const auto displays = iware::system::displays();
		std::cout << "\n"
		             "  Displays:\n";
		if(displays.empty())
			std::cout << "    None connected or no detection method enabled\n";
		else
			for(auto i = 0u; i < displays.size(); ++i) {
				const auto& display = displays[i];
				std::cout << "    #" << (i + 1) << ":\n"
				          << "      Resolution  : " << display.width << 'x' << display.height << '\n'
				          << "      DPI         : " << display.dpi << '\n'
				          << "      Colour depth: " << display.bpp << "b\n"
				          << "      Refresh rate: " << display.refresh_rate << "Hz\n";
			}
	}

	{
		const auto configs = iware::system::available_display_configurations();
		std::cout << "\n"
		             "  Display configurations:\n";
		if(configs.empty())
			std::cout << "    No displays connected, no detection method enabled, or not supported\n";
		else
			for(auto i = 0u; i < configs.size(); ++i) {
				const auto& display_configs = configs[i];
				std::cout << "    Display #" << (i + 1) << ":\n";

				for(auto j = 0u; j < display_configs.size(); ++j) {
					const auto& config = display_configs[j];
					std::cout << "      #" << (j + 1) << ":\n"
					          << "        Resolution   : " << config.width << 'x' << config.height << '\n'
					          << "        Refresh rates: ";

					bool first = true;
					for(auto rate : config.refresh_rates) {
						if(first)
							first = false;
						else
							std::cout << ", ";

						std::cout << rate << "Hz";
					}

					std::cout << '\n';
				}
			}
	}

	std::cout << '\n';
}

int main() {
	infoware_system();

	return 0;
}
