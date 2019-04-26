sudo apt-get update
sudo apt-get install libcups2-dev libcupsimage2-dev git build-essential cups system-config-printer
sudo apt install build-essential cmake
git clone https://github.com/klirichek/zj-58.git
cd zj-58
mkdir build && cd build && cmake  ../ && cmake --build . && sudo make install
sudo usermod -a -G lp pi
