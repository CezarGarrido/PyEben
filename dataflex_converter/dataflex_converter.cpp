#include <pybind11/pybind11.h>
#include <pybind11/stl.h>
#include <iostream>
#include <fstream>
#include <vector>
#include <string>
#include <cstring>
#include <sstream>
#include <iomanip>
#include <locale>
#include <codecvt>
#include <iconv.h>
#include <string>

std::string convertToUTF8(const std::string &input) {
    iconv_t conv = iconv_open("UTF-8", "ISO-8859-1");
    if (conv == (iconv_t)-1) return input;

    size_t in_size = input.size();
    size_t out_size = in_size * 2;
    char *in_buf = const_cast<char *>(input.data());
    char *out_buf = new char[out_size];
    char *out_ptr = out_buf;

    std::memset(out_buf, 0, out_size);
    iconv(conv, &in_buf, &in_size, &out_ptr, &out_size);
    iconv_close(conv);

    std::string result(out_buf);
    delete[] out_buf;
    return result;
}

struct Field {
    uint16_t offset;
    uint8_t size;
    uint8_t type;
};

void convertDataFlexToCSV(const std::string& inputFile, const std::string& outputFile, char separator = '|') {
    std::ifstream fin(inputFile, std::ios::binary);
    if (!fin) {
        throw std::runtime_error("Erro: não foi possível abrir o arquivo de entrada.");
    }

    std::ofstream fout(outputFile);
    if (!fout) {
        throw std::runtime_error("Erro: não foi possível abrir o arquivo de saída.");
    }
    
    char buffer[4096];
    fin.read(buffer, 4096);
    std::string fileRootName(buffer + 180, 8);
    
    uint32_t recordCount, highestRecordCount, maxNumRecords;
    uint16_t recordSize;
    uint8_t numOfFields;
    
    std::memcpy(&recordCount, buffer + 8, sizeof(uint32_t));
    std::memcpy(&recordSize, buffer + 78, sizeof(uint16_t));
    std::memcpy(&highestRecordCount, buffer, sizeof(uint32_t));
    std::memcpy(&maxNumRecords, buffer + 12, sizeof(uint32_t));
    std::memcpy(&numOfFields, buffer + 89, sizeof(uint8_t));
    
    std::vector<Field> fields(numOfFields);
    for (uint8_t i = 0; i < numOfFields; ++i) {
        uint16_t offset = 196 + (8 * i);
        std::memcpy(&fields[i].offset, buffer + offset, sizeof(uint16_t));
        std::memcpy(&fields[i].size, buffer + offset + 3, sizeof(uint8_t));
        std::memcpy(&fields[i].type, buffer + offset + 4, sizeof(uint8_t));
    }
    
    fout << "DATABASE: [" << fileRootName << "]\n";
    
    std::vector<char> recordBuffer(recordSize);
    fin.seekg(512 + recordSize, std::ios::beg);
    
    while (fin.read(recordBuffer.data(), recordSize)) {
        bool skip = false;
        std::ostringstream row;
        
        for (uint8_t r = 0; r < numOfFields; ++r) {
            uint16_t pos = fields[r].offset - 1;
            uint8_t size = fields[r].size;
            uint8_t type = fields[r].type;
            
            switch (type) {
                case 0: // string
                    row << convertToUTF8(std::string(recordBuffer.data() + pos, size));
                    break;
                case 1: // numerico
                {
                    uint32_t id = 0;
                    std::memcpy(&id, recordBuffer.data() + pos + 1, size - 1);
                    if (r == 0 && id == 0) {
                        skip = true;
                    }
                    row << id;
                    break;
                }
                case 2: // data (ajuste para DataFlex)
                {
                    uint32_t jd = 0;
                    std::memcpy(&jd, recordBuffer.data() + pos, size);
                    if (jd <= 100000) jd = 0;
                    else jd -= 465263;
                    row << (jd ? std::to_string(jd) : "01/01/1000");
                    break;
                }
                default:
                    row << "<[UNKNOWN]>";
            }
            
            if (r < numOfFields - 1) row << separator;
        }
        
        if (!skip) {
            fout << row.str() << "\n";
        }
    }
    
    fin.close();
    fout.close();
}

PYBIND11_MODULE(dataflex_converter, m) {
    m.doc() = "Módulo para conversão de arquivos DataFlex .dat para CSV";
    m.def("convert", &convertDataFlexToCSV, "Converte um arquivo DataFlex para CSV",
          pybind11::arg("inputFile"), pybind11::arg("outputFile"), pybind11::arg("separator") = '|');
}

