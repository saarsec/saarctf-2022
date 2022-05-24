[(back to gamelib manual)](../README.md)

HowTo build and install services
================================

Before your service can be used, it needs to be built and installed. 
- Build runs before the vulnbox is assembled, in docker, and produces a folder containing binaries and/or source code (whatever you want to publish)
- Install runs when the vulnbox is assembled, on the actual VM, and has access to the build artifacts.

We provide [example configurations](#example-configurations) below.

Build and installation can be accelerated by installing `apt-cacher-ng` on the building machine (host).
`apt-cacher-ng` caches the necessary apt downloads between subsequent runs. 
There is no configuration necessary, all scripts will auto-detect the caching server.
On Debian and Ubuntu-based systems installation is as simple as: `sudo apt install apt-cacher-ng`  


Build script
------------
The build script (`build.sh`) does not have a special structure. 
It is launched with your repository root as working directory and should place its results in `/service/` (where your code lies).
Base operating system is a plain Debian with Python3, you can install additional software there.
The build process uses a separate docker container and does not modify actual files on your disk (read: you can safely delete files you don't want to publish). 

The build script can be empty, in this case your source code is copied to the vulnbox. 
It can be tested with `gamelib/run-build`, the output can be inspected in `/build_output/`. 


### Other build environments (optional)
You can optionally use a different docker image for your build process. 
For example you can use a docker image where compilers are preinstalled. 
If possible chose a docker image which is based on Debian (for best compatibility with our build process and the vulnbox).
To change the base docker image edit `.gitlab-ci.yml` and uncomment / edit these lines:
```yaml
build:
  image: mcr.microsoft.com/dotnet/core/sdk:3.1
```



Install script
--------------
The `install.sh` should copy your build artifact on the actual machine and set it up. It gets:
- The script is started in a working directory similar to your repository root: In `./service` it finds the artifacts from your build.
- A user account for your service, same name as defined in `/servicename` (defined as `$SERVICENAME`)
- A directory to install your service to (`$INSTALL_DIR`)
- Access to several commands (see below)

The install script must:
- Copy all necessary files to `$INSTALL_DIR` and set appropriate owners and permissions
- Install all dependencies on the system (`apt update && apt install -y ...`)
- Create a systemd service that starts and manages the service (see commands `service-add-...`)
- (Optionally) create a cronjob that cleans the stored data from time to time (to avoid disk space shortage)
- Perform all other setup steps if necessary


### Available commands
#### Cronjobs
`cronjob-add <line>` and `cronjob-add-root <line>` add lines to your service user's crontab (or root's crontab). 
Useful for cleanup scripts. Example:
```shell
cronjob-add "*/6 * * * * find $INSTALL_DIR/data -mmin +45 -type f -delete"
cronjob-add-root '*/6 * * * * find /root/data -mmin +45 -type f -delete'
```

#### Systemd Services
`service-add-simple <command> <workingdirectory> <description>` creates a new systemd .service file named after your service.
`service-add-advanced` has the same syntax but accepts additional configuration input on stdin.

If you need more than one service set `$SERVICESUFFIX` for additional ones.

Examples: 
```shell
service-add-simple "python3 service.py" "$INSTALL_DIR/" "my very cool service"

# additional service
SERVICESUFFIX=-watcher service-add-simple "python3 service-watcher.py" "$INSTALL_DIR/" "my very cool service, part 2"

# custom systemd configuration (for instable services or to contain RCEs)
service-add-advanced "./my-binary" "$INSTALL_DIR/bin/" "my very cool RCE" <<EOF
Restart=always
RestartSec=5
LimitNPROC=1024
MemoryAccounting=true
MemoryMax=1024M
EOF

```

#### Append-only directories
`make-append-only <directory>` creates a directory where files can be written only once. 
If your service creates a file in that directory it will immediately be owned by root and only be readable - only the file descriptor that created this file will stay open for writing.
This construction prevents attackers from deleting flags even if they have RCE. 
If you want to cleanup your files from time to time create a cronjob that runs as root. 





Example configurations
----------------------
These example configurations worked for other services and can be used as starting point.
Please always check if the used versions are still up to date. 

We have examples for:
- [Binary with socat](#binary-with-socat)
- [C/C++ with CMake](#cc-with-cmake)
- [C# dotnet core binary](#c-dotnet-core-binary)
- [Go Binary](#go-binary)
- [Go Application with sources](#go-application-with-sources)
- [Java / Kotlin with Gradle](#java-kotlin-with-gradle)
- [MongoDB](#mongodb)
- [NPM build for frontend](#npm-build-for-frontend)
- [NPM / NodeJS server](#npm-nodejs-server)
- [PHP with nginx/php-fpm](#php-with-nginxphp-fpm)
- [Python/Django with uwsgi](#pythondjango-with-uwsgi)
- [PostgreSQL](#postgresql)
- [Rust Binary](#rust-binary)


### Binary with socat
We build the binary in `build.sh` and deploy it in `install.sh`. Binary is owned by root (not modifiable by attackers).
```shell
# in build.sh:
cd service
make -j4
rm -rf Makefile *.c *.h *.o *.cpp *.cc *.hpp
```

```shell
# in install.sh:
# 1. Install dependencies
apt-get update
apt-get install -y socat

# 2. Copy/move files
mv service/my_binary "$INSTALL_DIR/"
chown -R "root:root" $INSTALL_DIR/*
mkdir -p "$INSTALL_DIR/data"
chown -R "$SERVICENAME:$SERVICENAME" "$INSTALL_DIR/data"

# 4. Configure startup for your service
service-add-simple "socat -s -T20 TCP-LISTEN:12345,fork,reuseaddr EXEC:"./my_binary",setsid" "$INSTALL_DIR/" "..."
```


### C/C++ with CMake
On the vulnbox we place sources and a pre-compiled binary. To avoid tampering with an RCE, all files are owned by root.
See [SchlossbergCaves](https://gitlab.saarsec.rocks/MarkusBauer/schlossbergcaves) for the full example.

`build.sh` is empty, `install.sh` looks like this:
```shell
# 1. Install dependencies
apt-get update
apt-get install -y build-essential gcc g++ cmake

# 2. Copy/move files
cp -r service/* "$INSTALL_DIR/"
chown root:root "$INSTALL_DIR/*"
mkdir -p "$INSTALL_DIR/data"
chown -R "$SERVICENAME:$SERVICENAME" "$INSTALL_DIR/data"

# 3. Compile
pushd .
mkdir -p "$INSTALL_DIR/build"
cd "$INSTALL_DIR/build"
cmake ..
make -j 4
find -iname '*.o' -delete
popd

# 4. Configure startup for your service
service-add-advanced "$INSTALL_DIR/backend/build/SchlossbergCaveServer" "$INSTALL_DIR/backend/build/" "..." <<EOF
SystemCallFilter=~@debug kill
EOF
cronjob-add '*/6 * * * * find $INSTALL_DIR/data/ -mmin +45 -type f -delete'
```


### C# dotnet core binary
This example builds a binary from C# source code and deploys it without giving the actual source code.
See [saarXiv](https://gitlab.saarsec.rocks/jkrupp/saarXiv) for the full example.
To build we use Microsoft's dotnet core container, edit `.gitlab-ci.yml`:
```yaml
build:
  image: mcr.microsoft.com/dotnet/core/sdk:3.1
```
To build in `build.sh`:
```shell
cd service
dotnet publish saarXiv/saarXiv.csproj -c Release --self-contained false
# find result in service/saarXiv/bin/Release/netcoreapp3.1/publish/
```

On the vulnbox we need to install dotnet core from a third-party repository (`install.sh`):
```shell
# 1. Install dependencies - dotnet core aspnet
wget -qO- https://packages.microsoft.com/keys/microsoft.asc | gpg --dearmor > /etc/apt/trusted.gpg.d/microsoft.asc.gpg
wget -q https://packages.microsoft.com/config/debian/10/prod.list -O/etc/apt/sources.list.d/microsoft-prod.list
chown root:root /etc/apt/trusted.gpg.d/microsoft.asc.gpg
chown root:root /etc/apt/sources.list.d/microsoft-prod.list
sed -i 's|https:|http:|' /etc/apt/sources.list.d/microsoft-prod.list  # we rely on HTTP for now, otherwise our apt package cache has problems.
apt-get update
apt-get install -y apt-transport-https aspnetcore-runtime-3.1

# 2. Copy/move files
# /bin/ is our binary file directory (owned by root)
# /app.db is the database (owned by service user)
# some symlinks so that the program finds its files
mkdir "$INSTALL_DIR/bin"
mv service/*/bin/Release/netcoreapp3.1/publish/* "$INSTALL_DIR/bin/"
chown -R root "$INSTALL_DIR/bin"
ln -s $INSTALL_DIR/bin/appsettings.json $INSTALL_DIR/
ln -s $INSTALL_DIR/bin/wwwroot $INSTALL_DIR/

# 4. Configure startup for your service
service-add-advanced "dotnet $INSTALL_DIR/bin/saarXiv.dll --urls=http://0.0.0.0:5000" "$INSTALL_DIR/" "..." <<EOF
LimitNPROC=1024
MemoryAccounting=true
MemoryMax=1024M
EOF
```


### Go Binary
To build a Go binary you need to match Go's directory expectations. 
See [stahl4](https://gitlab.saarsec.rocks/dweber/stahl4) for a full example.
```shell
apt-get update
apt-get -y install golang-go

# create build structure
pushd .
mkdir -p go/src/$SERVICENAME
cp -r service go/src/$SERVICENAME/

# set $GOPATH to repo go folder
export GOPATH=$PWD/go

# start building
cd go/src/$SERVICENAME
go build -o $SERVICENAME.bin ./service

popd
mv go/src/$SERVICENAME/$SERVICENAME.bin service/$SERVICENAME.bin
```

Installation is straightforward:
```shell
mv service/$SERVICENAME.bin "$INSTALL_DIR/$SERVICENAME"
chmod +x $INSTALL_DIR/$SERVICENAME
service-add-advanced "$INSTALL_DIR/$SERVICENAME" "$INSTALL_DIR" "..." <<EOF
Restart=always
RestartSec=10
EOF
```



### Go Application with sources
You can host Go applications with source code. Debian currently ships Go 1.15. 
For a full example, see [TuringMachines++](https://gitlab.saarsec.rocks/MarkusBauer/turing-machines).
We create a readonly home directory, and a writeable `data` folder in `install.sh`:
```shell
# 1. Install dependencies
apt-get update
apt-get install -y golang-go

# 2. Copy/move files
mv service/* "$INSTALL_DIR/"
mkdir "$INSTALL_DIR/data"
chown -R "$SERVICENAME:$SERVICENAME" "$INSTALL_DIR/data"
# make-append-only "$INSTALL_DIR/data"

# 3. Compile
cd "$INSTALL_DIR"
go build

# 4. Configure startup for your service
service-add-simple "$INSTALL_DIR/created-go-binary" "$INSTALL_DIR/" "..."
```



### Java / Kotlin with Gradle
We give sources and compiled jar on vulnbox. 
The service will be recompiled if the jar is missing on startup.
See [Saarschleife.net](https://gitlab.saarsec.rocks/MarkusBauer/saarschleife_net) for the full example.

In `build.sh` we do some cleanup: 
```shell
cd service/backend
rm -rf .idea .gradle build gradle* out .gitignore *.iml src/test
```

```shell
export DEBIAN_FRONTEND=noninteractive
apt-get update
apt-get install -y unzip openjdk-11-jdk-headless
# Gradle
wget -O /tmp/gradle.zip 'https://services.gradle.org/distributions/gradle-5.6.4-bin.zip'
unzip -d /opt/ /tmp/gradle.zip
ln -s /opt/gradle*/bin/gradle /usr/local/bin/

# 2. Copy/move files
mv service/* "$INSTALL_DIR/"
# create init script
cat - <<EOF > $INSTALL_DIR/run-server.sh
#!/usr/bin/env bash
if [ ! -f $INSTALL_DIR/backend/build/libs/YOUR_JAR_NAME.jar ]; then
    echo "Building ..."
    pushd .
    cd $INSTALL_DIR/backend/
    gradle shadowJar --no-daemon
    gradle --stop
    popd
fi

exec java -jar $INSTALL_DIR/backend/build/libs/YOUR_JAR_NAME.jar
EOF
chmod +x $INSTALL_DIR/run-server.sh
# chown things
chown -R "$SERVICENAME:$SERVICENAME" "$INSTALL_DIR"

# 3. Build on box
pushd .
cd $INSTALL_DIR/backend
sudo -u $SERVICENAME gradle dependencies --no-daemon
sudo -u $SERVICENAME gradle shadowJar --no-daemon
popd

# 4. Configure startup for your service
# Typically use systemd for that:
# Install backend as systemd service
service-add-advanced "$INSTALL_DIR/run-server.sh" "$INSTALL_DIR/backend/" "..." <<EOF
Restart=on-failure
RestartSec=10
EOF
```


### MongoDB
Installing a non-ancient MongoDB is not easy, we need a third-party repository. 
To secure access to MongoDB you can either use a socket and set its permissions (if your client permits) or use iptables to limit access.
This example includes iptables:
```shell
export DEBIAN_FRONTEND=noninteractive
apt-get update
apt-get install -y gnupg iptables-persistent
wget -qO - https://www.mongodb.org/static/pgp/server-4.2.asc | apt-key add -
echo "deb http://repo.mongodb.org/apt/debian buster/mongodb-org/4.2 main" > /etc/apt/sources.list.d/mongodb-org-4.2.list
apt-get update
apt-get install -y mongodb-org
systemctl enable mongod

# Configure iptables to protect the mongo daemon from other users
iptables -A OUTPUT -o lo -p tcp --dport 27017 -m owner --uid-owner root -j ACCEPT
iptables -A OUTPUT -o lo -p tcp --dport 27017 -m owner ! --uid-owner $SERVICENAME -j REJECT
iptables-save > /etc/iptables/rules.v4
```



### NPM build for frontend
Sometimes you want to ship a HTTP frontend that uses AJAX to communicate with your service. 
Because that frontend code is typically not interesting, we can build it locally and copy the final bundle to the vulnbox. 
For example [SchlossbergCaves](https://gitlab.saarsec.rocks/MarkusBauer/schlossbergcaves) uses this structure.
To build with `npm` we start with a different build container, edit `.gitlab-ci.yml`:
```yaml
build:
  image: node:lts-buster
```
`build.sh` can look like this:
```shell
cd service/frontend
npm install
npm run build
cd ..
```
Last we can use `nginx` to serve the frontend and proxy the service API (`install.sh`):
```shell
# 1. Install dependencies
apt-get update
apt-get install -y nginx

# 2. Copy/move files
cp -r service/frontend/dist/* "$INSTALL_DIR/frontend/"
# Give nginx access rights on the homedir
usermod -aG $SERVICENAME www-data

# 4. Configure the server
cat - > /etc/nginx/sites-available/$SERVICENAME <<EOF
server {
    listen 10000;
    location / {
        charset utf-8;
        alias $INSTALL_DIR/frontend/;
    }
    location /api {
        proxy_pass http://127.0.0.1:10001;
    }
}
EOF
ln -s /etc/nginx/sites-available/$SERVICENAME /etc/nginx/sites-enabled/$SERVICENAME
```



### NPM / NodeJS server
We run a simple NodeJS server. See [Grenzschutzkontrolle](https://gitlab.saarsec.rocks/MarkusBauer/grenzschutzkontrolle) for the full example.

In `build.sh` we clean up artifacts from local tests:
```shell
mkdir -p service/data
rm -f service/data/*
rm -rf service/node_modules
rm -f service/*.log
```

In `install.sh` we download a recent NodeJS from a third-party repository and configure the service:
```shell
# 1. Install dependencies
wget --quiet -O - https://deb.nodesource.com/gpgkey/nodesource.gpg.key | apt-key add -
VERSION=node_14.x
DISTRO=bullseye
echo "deb http://deb.nodesource.com/$VERSION $DISTRO main" > /etc/apt/sources.list.d/nodesource.list
echo "deb-src http://deb.nodesource.com/$VERSION $DISTRO main" >> /etc/apt/sources.list.d/nodesource.list
apt-get update
apt-get install -y nodejs

# 2. Copy/move files
mv service/* "$INSTALL_DIR/"
chmod -R g-w $INSTALL_DIR/*
chown -R "root:$SERVICENAME" "$INSTALL_DIR"
chown -R "$SERVICENAME:$SERVICENAME" "$INSTALL_DIR/data"
cd $INSTALL_DIR
npm install

# 4. Configure startup for your service
service-add-simple "node $INSTALL_DIR/server.js" "$INSTALL_DIR" "..."
```



### PHP with nginx/php-fpm
This example installs nginx/PHP and configures it to serve files from your service's install directory. 
Be aware of potential leaks, nginx might hand out every file there.
See [mensaar](https://gitlab.saarsec.rocks/sebrot/saarctf-mensaar) for the full example.

```shell
# 1. Install dependencies
apt-get update
apt-get install -y nginx php-fpm # + php-pgsql or other extensions

# 2. Copy/move files
mv service/* "$INSTALL_DIR/"
chown -R "root:$SERVICENAME" "$INSTALL_DIR"

# 3. Configure the server
# configure php-fpm pool
sed -i "s|^user = .*|user = $SERVICENAME|" /etc/php/*/fpm/pool.d/www.conf
sed -i "s|^group = .*|group = $SERVICENAME|" /etc/php/*/fpm/pool.d/www.conf
echo 'cgi.fix_pathinfo=0' >> /etc/php/*/fpm/php.ini

# configure the nginx
cat - > /etc/nginx/sites-available/$SERVICENAME <<'EOF'
server {
    listen 12345;
	location / {
		charset utf-8;
		alias $INSTALL_DIR/;
		index index.php;

		if ($uri ~ "\.php$") {
			fastcgi_pass unix:/run/php/php7.3-fpm.sock;
		}
		include fastcgi_params;
		fastcgi_param  SCRIPT_FILENAME  $INSTALL_DIR/$fastcgi_script_name;
		fastcgi_param  SCRIPT_NAME  $fastcgi_script_name;
	}
}
EOF
sed -i "s|\$INSTALL_DIR|$INSTALL_DIR|" /etc/nginx/sites-available/$SERVICENAME
ln -s /etc/nginx/sites-available/$SERVICENAME /etc/nginx/sites-enabled/$SERVICENAME
# Give nginx access rights on the homedir
usermod -aG $SERVICENAME www-data

# If you have a RCE, limit the php fpm daemon:
mkdir -p /etc/systemd/system/php7.3-fpm.service.d
cat > /etc/systemd/system/php7.3-fpm.service.d/override.conf <<'EOF'
[Service]
MemoryAccounting=true
MemoryMax=1024M
LimitNPROC=1024
EOF
```



### Python/Django with uwsgi
We can host Django services with uwsgi and nginx frontend. 
See [billeroy-voch](https://gitlab.saarsec.rocks/ben/villeroy-boch) for a full example.

In `build.sh`, you can patch the configuration if necessary:
```shell
sed -i 's/DEBUG = True/DEBUG = False/' service/servicename/servicename/settings.py
```

In `install.sh` (change `servicename`):
```shell
# 1. Install dependencies
apt-get update
apt-get install -y python3 nginx python3-wheel python3-pip python3-setuptools python3-psycopg2 postgresql libpcre3 libpcre3-dev libjpeg-dev libfreetype6-dev zlib1g-dev
pip3 install uwsgi
chmod +x /usr/local/bin/uwsgi  # Bugfix (?)
pip3 install -r service/servicename/requirements.txt

# 2. Copy/move files
mv service/* "$INSTALL_DIR/"
chown -R "$SERVICENAME:$SERVICENAME" "$INSTALL_DIR"
sudo -u "$SERVICENAME" python3 "$INSTALL_DIR/servicename/manage.py" collectstatic

# 3. Configure the server
cat - > /etc/nginx/sites-available/$SERVICENAME <<EOF
server {
    listen 8000;
    location / {
        include uwsgi_params;
        uwsgi_pass unix:/tmp/$SERVICENAME.sock;
    }
}
EOF
ln -s /etc/nginx/sites-available/$SERVICENAME /etc/nginx/sites-enabled/$SERVICENAME

# 4. Configure startup for your service
service-add-advanced "/usr/local/bin/uwsgi $INSTALL_DIR/uwsgi.ini" "$INSTALL_DIR/" "..." <<'EOF'
KillSignal=SIGQUIT
NotifyAccess=all
EOF
sed -i 's/Type=simple/Type=forking/' "/etc/systemd/system/$SERVICENAME.service"

# Later, init database:
sudo -u "$SERVICENAME" python3 "$INSTALL_DIR/servicename/manage.py" migrate
```

Finally, you need a uwsgi config file in `service/uwsgi.ini`, like this one:
```ini
[uwsgi]
chdir=/home/servicename/servicename
wsgi-file=/home/servicename/servicename/servicename/wsgi.py
master=true
processes=4
#harakiri=20
max-requests=5000
vacuum=true
static-map=/static=/home/servicename/static
daemonize=//home/servicename/%n.log
socket=/tmp/servicename.sock
chmod-socket=777
```



### PostgreSQL
To initialize a PostgreSQL database it needs to be started manually (for CI/Docker). We can do that in `install.sh`:
```shell
if detect-docker; then
  pg_ctlcluster 13 main start
fi

# Create a SQL user and database for your service (with peer authentication)
sudo -u postgres psql -v ON_ERROR_STOP=1 <<EOF
CREATE ROLE $SERVICENAME LOGIN VALID UNTIL 'infinity';
CREATE DATABASE $SERVICENAME WITH ENCODING='UTF8' CONNECTION LIMIT=-1;
EOF
# run sql code with your services database user
sudo -u $SERVICENAME psql -v ON_ERROR_STOP=1 <<EOF
-- ... 
EOF
# or: use a .sql file to init your database
cp $INSTALL_DIR/init.sql /tmp/
sudo -u $SERVICENAME psql -v ON_ERROR_STOP=1 -f "/tmp/init.sql"

if detect-docker; then
  pg_ctlcluster 13 main stop
fi
``` 



### Rust Binary
We build the binary in `build.sh` with the official rust container.
See [vault](https://gitlab.saarsec.rocks/simeon.hoffmann/vault) for a full example.
To this end, we edit `.gitlab-ci.yml` and add:
```yaml
build:
  image: rust:latest 
```

Then in `build.sh`, we run (patch `binaryname`):
```shell
cd service && cargo build --release
cd ..
cp service/target/release/binaryname ./
# copy other files from service directory you want to keep...
rm -rf service
mkdir service
mv binaryname service/
# move other files back ...
```

Install like any other [Binary with socat](#binary-with-socat).



### Rust Application (with source)
See [saarbahn](https://gitlab.saarsec.rocks/simeon.hoffmann/saarbahn) for a full example.
In `build.sh`, you can do the usual code cleanup. 

In `install.sh`, we install rust using rustup and build the application. 
This example assumes that you have one folder `<your-dir-name>` in your `service` directory.
```shell
# Install Rust
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs > $HOME/tmp.sh
if mount | grep '/dev/shm' | grep -q 'noexec'; then
    mkdir -p /root/tmp
    export TMPDIR=/root/tmp
else
    export TMPDIR=/dev/shm
fi
sh $HOME/tmp.sh -y
rm -f $HOME/tmp.sh
# if you need additional CLI tools from cargo:
source $HOME/.cargo/env
cargo install diesel_cli

# Copy and build service
mv service/<your-dir-name> "$INSTALL_DIR/"
chown -R "root:$SERVICENAME" "$INSTALL_DIR"
chmod 0750 "$INSTALL_DIR"
cd "$INSTALL_DIR/<your-dir-name>"
cargo build

# Cleanup
rm -rf /root/tmp
unset TMPDIR

# Add the service (standalone webserver)
service-add-simple "$INSTALL_DIR/<your-dir-name>/target/debug/<your-binary>" "$INSTALL_DIR/<your-dir-name>" "..."
# OR: socat binary
```
If your application is a binary communicating by stdin/stdout: configure like [Binary with socat](#binary-with-socat).

