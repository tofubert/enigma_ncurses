sudo apt install build-essential cmake libcups2-dev libcupsimage2-dev
git clone https://github.com/klirichek/zj-58.git
cd zj-58
mkdir build && cd build && cmake  ../ && cmake --build . && sudo make install
