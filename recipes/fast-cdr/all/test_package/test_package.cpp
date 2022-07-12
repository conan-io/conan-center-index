// Copyright 2016 Proyectos y Sistemas de Mantenimiento SL (eProsima).
//
// Licensed under the Apache License, Version 2.0 (the "License");
// you may not use this file except in compliance with the License.
// You may obtain a copy of the License at
//
//     http://www.apache.org/licenses/LICENSE-2.0
//
// Unless required by applicable law or agreed to in writing, software
// distributed under the License is distributed on an "AS IS" BASIS,
// WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
// See the License for the specific language governing permissions and
// limitations under the License.

#include <fastcdr/Cdr.h>
#include <fastcdr/FastCdr.h>

#include <stdio.h>
#include <limits>
#include <iostream>

#define N_ARR_ELEMENTS 5

static const char char_seq_t[N_ARR_ELEMENTS] = {'E', 'D', 'C', 'B', 'A'};
static const std::wstring wstring_t = L"Hola a todos, esto es un test con widestring";

using namespace eprosima::fastcdr;

#define BUFFER_LENGTH 2000


void check_good_case()
{
    char buffer[BUFFER_LENGTH];
    const std::wstring& input_value = wstring_t;

    // Serialization.
    {
        FastBuffer cdrbuffer(buffer, BUFFER_LENGTH);
        Cdr cdr_ser(cdrbuffer);
        cdr_ser << input_value;
    }

    // Deserialization.
    {
        FastBuffer cdrbuffer(buffer, BUFFER_LENGTH);
        Cdr cdr_des(cdrbuffer);
        std::wstring output_value{};

        cdr_des >> output_value;
    }
}


int main()
{
    check_good_case();

    char buffer[BUFFER_LENGTH];

    // Serialization.
    FastBuffer cdrbuffer(buffer, BUFFER_LENGTH);
    Cdr cdr_ser(cdrbuffer);
    cdr_ser.serializeSequence(char_seq_t, 5);

    // Deserialization.
    Cdr cdr_des(cdrbuffer);

    char* char_seq_value = NULL; size_t char_seq_len = 0;

    cdr_des.deserializeSequence(char_seq_value, char_seq_len);

    return 0;
}
