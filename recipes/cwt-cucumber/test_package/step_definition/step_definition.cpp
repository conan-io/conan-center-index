
#include "../src/box.hpp"
#include "cucumber.hpp"

struct date {
  int day;
  std::string month;
  int year;
};

struct date_range {
  date start;
  date end;
};

CUSTOM_PARAMETER(
    custom_date, "{date}",
    R"(from ([A-Za-z]+) (\d{1,2}), (\d{4}) to ([A-Za-z]+) (\d{1,2}), (\d{4}))",
    "a custom date pattern") {
  date begin;
  begin.month = CUKE_PARAM_ARG(1).to_string();
  begin.day = int(CUKE_PARAM_ARG(2));
  begin.year = CUKE_PARAM_ARG(3).as<int>();

  date end;
  end.month = CUKE_PARAM_ARG(4).to_string();
  end.day = static_cast<int>(CUKE_PARAM_ARG(5));
  end.year = CUKE_PARAM_ARG(6).as<int>();

  return date_range{begin, end};
}

CUSTOM_PARAMETER(custom_event, "{event}", R"('(.*?)')", "a custom event") {
  std::string event = CUKE_PARAM_ARG(1);
  return event;
}

WHEN(using_date, "{event} is {date}") {
  std::string event = CUKE_ARG(1);
  date_range dr = CUKE_ARG(2);
  std::cout << "Event: " << event << std::endl;
  std::cout << "Begin: " << dr.start.month << ' ' << dr.start.day << ", "
            << dr.start.year << std::endl;
  std::cout << "End: " << dr.end.month << ' ' << dr.end.day << ", "
            << dr.end.year << std::endl;
  cuke::context<date_range>(dr);
}
THEN(checking_months,
     "The beginning month is {word} and the ending month is {word}") {
  std::string start = CUKE_ARG(1);
  std::string end = CUKE_ARG(2);

  cuke::equal(cuke::context<date_range>().start.month, start);
  cuke::equal(cuke::context<date_range>().end.month, end);
}

CUSTOM_PARAMETER(custom, "{pair of integers}", R"(var1=(\d+), var2=(\d+))",
                 "two integers") {
  int var1 = CUKE_PARAM_ARG(1);
  int var2 = CUKE_PARAM_ARG(2);
  return std::make_pair(var1, var2);
}

WHEN(custom_par_when, "this is {pair of integers}") {
  std::pair<int, int> p = CUKE_ARG(1);
  std::cout << "Pair initialized with CUKE_ARG(1) and two values: " << p.first
            << ' ' << p.second << std::endl;
  cuke::context<const std::pair<int, int>>(p);
}

THEN(custom_par_then, "their values are {int} and {int}") {
  const int var1 = CUKE_ARG(1);
  const int var2 = CUKE_ARG(2);
  cuke::equal(cuke::context<std::pair<int, int>>().first, var1);
  cuke::equal(cuke::context<const std::pair<int, int>>().second, var2);
}

struct foo {
  std::string word;
  std::string anonymous;
};

WHEN(word_anonymous_given, "A {word} and {}") {
  std::string word = CUKE_ARG(1);
  cuke::context<foo>().word = word;

  std::string anonymous = CUKE_ARG(2);
  cuke::context<foo>().anonymous = anonymous;
}

THEN(word_anonymous_then, "They will match {string} and {string}") {
  std::string expected_word = CUKE_ARG(1);
  std::string expected_anonymous = CUKE_ARG(2);

  cuke::equal(expected_word, cuke::context<foo>().word);
  cuke::equal(expected_anonymous, cuke::context<foo>().anonymous);
}

GIVEN(init_box, "An empty box") {
  const box &my_box = cuke::context<box>();
  cuke::equal(my_box.items_count(), 0);
}
WHEN(add_item, "I place {int} x {string} in it") {
  const std::size_t count = CUKE_ARG(1);
  const std::string item = CUKE_ARG(2);

  cuke::context<box>().add_items(item, count);
}
WHEN(doc_string, "There is a doc string:") {
  const std::string &str = CUKE_DOC_STRING();
  std::cout << "-------- Print from step definition: -----" << '\n';
  std::cout << str << '\n';
  std::cout << "------------------------------------------" << '\n';
}
WHEN(doc_string_vector, "There is a doc string as vector:") {
  const std::vector<std::string> doc_string = CUKE_DOC_STRING();
  std::cout << "-------- Print from step definition: -----" << '\n';
  for (const std::string &line : doc_string) {
    std::cout << line << '\n';
  }
  std::cout << "------------------------------------------" << '\n';
}
WHEN(add_table_raw, "I add all items with the raw function:") {
  const cuke::table &t = CUKE_TABLE();
  for (const cuke::table::row &row : t.raw()) {
    cuke::context<box>().add_items(row[0].to_string(), row[1].as<long>());
  }
}
WHEN(add_table_hashes, "I add all items with the hashes function:") {
  const cuke::table &t = CUKE_TABLE();
  for (const auto &row : t.hashes()) {
    cuke::context<box>().add_items(row["ITEM"].to_string(),
                                   row["QUANTITY"].as<long>());
  }
}
WHEN(add_table_rows_hash,
     "I add the following item with the rows_hash function:") {
  const cuke::table &t = CUKE_TABLE();
  cuke::table::pair hash_rows = t.rows_hash();

  cuke::context<box>().add_items(hash_rows["ITEM"].to_string(),
                                 hash_rows["QUANTITY"].as<long>());
}

THEN(test, "The {int}. item is {string}") {
  const std::size_t number = CUKE_ARG(1);
  const std::size_t idx_zero_based = number - 1;
  const std::string item = CUKE_ARG(2);

  cuke::equal(item, cuke::context<box>().at(idx_zero_based));
}

THEN(check_box_size, "The box contains {int} item(s)") {
  const int items_count = CUKE_ARG(1);
  const box &my_box = cuke::context<box>();
  cuke::equal(my_box.items_count(), items_count);
}

THEN(alternative_words, "{int} item(s) is/are {string}") {
  const std::size_t count = CUKE_ARG(1);
  const std::string item = CUKE_ARG(2);
  cuke::equal(count, cuke::context<box>().count(item));
}

STEP(doc, "doc string:") {
  std::string s = CUKE_ARG(1);
  std::cout << s << std::endl;
}
