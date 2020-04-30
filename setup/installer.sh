BASE=/app
HOME=$BASE/maas
##############################
# Make Directories

mkdir -p $BASE

mkdir -p $BASE/grafana
mkdir -p $BASE/telegraf
mkdir -p $HOME/api $HOME/conf $HOME/install $HOME/www $HOME/setup
mkdir -p $BASE/git

mkdir -p $BASE/sw

mkdir -p $BASE/influx/data/influxdb
mkdir -p $BASE/influx/data/chronograf
mkdir -p $BASE/influx/data/kapacitor
mkdir -p $BASE/influx/logs
mkdir -p $BASE/influx/conf

mkdir -p $BASE/elk
mkdir -p $BASE/elk/conf
mkdir -p $BASE/elk/data
mkdir -p $BASE/elk/logs

##############################
# Download binaries
cd $BASE/sw

wget https://dl.influxdata.com/influxdb/releases/influxdb-1.8.0_linux_amd64.tar.gz -O influxdb-1.8.0_linux_amd64.tar.gz
#wget https://dl.influxdata.com/chronograf/releases/chronograf-1.8.2_linux_arm64.tar.gz -O chronograf-1.8.2_linux_arm64.tar.gz
wget https://dl.influxdata.com/chronograf/releases/chronograf-nightly_linux_amd64.tar.gz -O chronograf-nightly_linux_amd64.tar.gz
wget https://dl.influxdata.com/kapacitor/releases/kapacitor-1.5.5_linux_amd64.tar.gz -O kapacitor-1.5.5_linux_amd64.tar.gz
wget https://dl.grafana.com/oss/release/grafana-6.7.3.linux-amd64.tar.gz -O grafana-6.7.3.linux-amd64.tar.gz
wget https://dl.influxdata.com/telegraf/releases/telegraf-1.14.1_linux_amd64.tar.gz -O telegraf-1.14.1_linux_amd64.tar.gz
wget https://github.com/schmorgs/maas/archive/master.zip -O master.zip
wget https://artifacts.elastic.co/downloads/elasticsearch/elasticsearch-7.6.2-linux-x86_64.tar.gz -O elasticsearch-7.6.2-linux-x86_64.tar.gz

##############################
# Unzip binaries
# Influx components
cd $BASE/influx/
tar xzf $BASE/sw/influxdb-1.8.0_linux_amd64.tar.gz
#tar xzf $BASE/sw/chronograf-1.8.2_linux_arm64.tar.gz
tar xzf $BASE/sw/chronograf-nightly_linux_amd64.tar.gz
tar xzf $BASE/sw/kapacitor-1.5.5_linux_amd64.tar.gz
# Grafana
cd $BASE/grafana
tar xzf $BASE/sw/grafana-6.7.3.linux-amd64.tar.gz
# Telegraf agent
cd $BASE/telegraf
tar xzf $BASE/sw/telegraf-1.14.1_linux_amd64.tar.gz
# MaaS files
cd $HOME
rm -rf $HOME/api $HOME/install $HOME/setup $HOME/www
mkdir -p $HOME/api $HOME/conf $HOME/install $HOME/setup $HOME/www
unzip -o $BASE/sw/master.zip
cp -r $HOME/maas-master/maas/api/* $HOME/api
# Don't overwrite any existing config files
cp -rn $HOME/maas-master/maas/conf/* $HOME/conf
cp -r $HOME/maas-master/maas/install/* $HOME/install
cp -r $HOME/maas-master/maas/setup/* $HOME/setup
cp -r $HOME/maas-master/maas/www/* $HOME/www
# Remove rest of repo
rm -rf $HOME/maas-master
rm -rf $HOME/maas

# Elasticsearch 
cd $BASE/elk
tar xzf $BASE/sw/elasticsearch-7.6.2-linux-x86_64.tar.gz

##############################
# Symlink binaries to unversions directories
rm -f $BASE/influx/influxdb
ln -s $BASE/influx/influxdb-1.8.0-1 $BASE/influx/influxdb
rm -f $BASE/influx/chronograf
ln -s $BASE/influx/chronograf-202004242133~nightly-0 $BASE/influx/chronograf
rm -f $BASE/influx/kapacitor
ln -s $BASE/influx/kapacitor-1.5.5-1 $BASE/influx/kapacitor
rm -f $BASE/grafana/grafana
ln -s $BASE/grafana/grafana-6.7.3 $BASE/grafana/grafana
rm -f $BASE/elk/elastic
ln -s $BASE/elk/elasticsearch-7.6.2 $BASE/elk/elastic

##############################
# Copy config files only write if they are not already there
cp -n $BASE/sw/influx/conf/* $BASE/influx/conf
cp -n $BASE/sw/elastic/*yml $BASE/elk/conf
cp -n $BASE/sw/elastic/*options $BASE/elk/conf
cp -n $BASE/sw/elastic/*properties $BASE/elk/conf

##############################
# Copy startup scripts
cp $BASE/sw/influx/conf/*.sh $BASE/influx
cp $BASE/sw/telegraf/*.sh $BASE/telegraf
cp $BASE/sw/elastic/*.sh $BASE/elk
