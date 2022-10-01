g++ main.cpp $(pkg-config --cflags --libs libmongocxx) -fpermissive -pthread
./a.out


