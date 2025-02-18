#pragma once

#include <string>
#include <vector>

class box
{
 public:
  box() = default;

  void add_item(const std::string& item) { m_items.push_back(item); }
  void add_items(const std::string& item, std::size_t count)
  {
    for ([[maybe_unused]] int i = 0; i < count; i++)
    {
      add_item(item);
    }
  }
  [[nodiscard]] std::size_t items_count() const noexcept
  {
    return m_items.size();
  }
  [[nodiscard]] const std::string& at(const std::size_t idx) const
  {
    return m_items.at(idx);
  }
  void close() noexcept { m_is_open = false; }

  std::size_t count(std::string_view item)
  {
    return std::count(m_items.begin(), m_items.end(), item);
  }

 private:
  bool m_is_open{true};
  std::vector<std::string> m_items;
};
