mkdir $HOME/www
mkdir $HOME/www/src
cd $HOME/www/src
wget https://pypi.python.org/packages/source/v/virtualenv/virtualenv-1.11.2.tar.gz
tar -xzvf virtualenv-1.11.2.tar.gz
cd virtualenv-1.11.2
./virtualenv.py $HOME/www
cd $HOME/www/src
source ./bin/activate
pip install mercurial
hg clone https://sarkozy@bitbucket.org/sarkozy/minard
pip install ./minard
