sudo apt-get install python3-pip
pip install --upgrade pip

mkdir ~/envs # 儲存環境地方(~代表使用者資料夾底下)
cd ~/envs
virtualenv -p python3 DSRP

cd <YOUR PROJECT FOLDER>
source ~/envs/DSRP/bin/activate # 之後要使用時只要跑這行就可進入環境

pip install -r requirements.txt