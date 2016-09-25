# P5: Linux Server Configuration

## Connection

* **IP address:** 52.89.88.117
* **SSH port:** 2200
* **connect command:** ssh grader@52.89.88.117 -p 2200 -i ~/.ssh/udacity_key

## Application
* **URL**: http://ec2-52-89-88-117.us-west-2.compute.amazonaws.com/

## Installed software:
* Apache
* WSGI
* PostgreSQL
* Git
* ntp
* Python modules

## Instructions to setup your server:

### 1. Manage users

#### 1.1. Create new user
  ```shell
  sudo add user username
  ```

#### 1.2. Give him permission to sudo
  ```shell
  # in the shell
  sudo nano /etc/sudoers.d/username

  # add this line to the file
  # with this configuration user has to enter his password for sudo
  username ALL=(ALL) ALL
  ```

#### 1.3. Password policy

  Update password policy for the user:
  * Force user to update his password on first login (expire):
```shell
sudo passwd -e username
```
  * Update number of days between password changes
    * Option 1: `sudo chage`
      ```shell
      # Check account status
      sudo chage -l username

      # Setup this values
      sudo chage username
      ```
    * Option 2: `sudo passwd`
      ```shell
      # Set the minimum number of days between password changes to MIN_DAYS
      sudo passwd --mindays MIN_DAYS username

      # Set the maximum number of days a password remains valid. After MAX_DAYS
      sudo passwd --maxdays MAX_DAYS username

      # Set the number of days of warning before a password change is required.
      sudo passwd --warndays WARN_DAYS username
      ```
  * Update minimum password length by editing `/etc/pam.d/common-password`
    ```shell
    # edit the file
    sudo nano /etc/pam.d/common-password

    # add minlen to the line:
    password        [success=1 default=ignore]      pam_unix.so obscure sha512 minlen=MIN_LEN
    ```

#### 1.4. Manage user key based authentication
  In your LOCAL machine:
  ```shell
  # Create key pairs with
  ssh-keygen # for example in ~/.ssh/key_pairs_name

  # copy the public key
  cat ~/.ssh/key_pairs_name.pub
  ```

  Configure the public key in the SERVER:
  ```shell
  # create the directory and file to configure public key for the new user
  mkdir /home/username/.ssh
  touch /home/username/authorized_keys
  # paste the public key in a new line in
  nano /home/username/authorized_keys
  ```
  Now you can connect with the new user from your local machine to the server:
  ```shell
  ssh username@your_server_ip -i ~/.ssh/key_pairs_name
  ```

### 2. Update software
  Update all currently installed packages
  ```shell
  # update the source lists
  sudo apt-get update

  # upgrade software
  sudo apt-get upgrade
  ```

### 3. Configure timezones and NTP

* Update timezone
```shell
sudo dpkg-reconfigure tzdata
```
* Configure NTP Synchronization
  The daemon will start automatically each boot and will continuously adjust the system time to be in-line with the global NTP servers throughout the day.
  This will allow your computer to stay in sync with other servers:
```shell
sudo apt-get install ntp
```



### 4. Secure your server

#### 4.1. Configure SSH
  Disable password logins, so you force users to use key based authentication:
  ```shell
  # edit ssh config file
  sudo nano /etc/ssh/sshd_config

  # Change your SSH port (example 2222)
  Port 2222
  # Ensure tunneled clear text passwords are disabled
  PasswordAuthentication no

  # After save changes we need to restart ssh service
  sudo service ssh restart
  ```

#### 4.2. Configure the firewall: UFW
  Configure the firewall to only accept connections needed by the server to do his job.
  ```shell
  # Check firewall status
  sudo ufw status

  # Deny by default all incoming connections
  # IMPORTANT: don't enable the firewall after this, the server will be inaccessible
  sudo ufw defautl deny incoming

  # Allow all outgoing connections
  sudo ufw default allow outgoing

  # Allow needed connections
  sudo ufw allow ssh
  sudo ufw allow 2222/tcp # set here your SSH new port number
  sudo ufw allow www
  sudo uft allow ntp

  # Now we can enable ufw
  sudo ufw enable
  ```

### 5. Install and configure software

#### 5.1. Apache
  Install Apache:
  ```shell
  sudo apt-get install apcache2
  ```
  Apache, by default, serves its files from the `/var/www/html` directory.

#### 5.2. WSGI
  Configure Apache to hand-off certain requests to an application handler: _mod_wsgi_.
  ```shell
  sudo apt-get install libapache2-mod-wsgi
  ```
  You then need to configure Apache to handle requests using the WSGI module.

  ```shell
  # Add an Apache config file:
  sudo touch /etc/apache2/conf-available/catalog.conf

  # Enable the new config file:
  sudo ae2ecnconf catalog
  ```

#### 5.3. DB: Postgre SQL
  A useful gide [here](https://www.digitalocean.com/community/tutorials/how-to-install-and-use-postgresql-on-ubuntu-14-04)
  Install PostgreSQL:
  ```shell
  # install PostgreSQL
  sudo apt-get install postgresql

  # First of all we need to create a cluster
  sudo pg_createcluster 9.3 main --start

  # check postgresql service status
  service postgresql status

  ## output shoul be:
  9.3/main (port 5432): online
  ```

  Run PostgreSQL under a separate user account:
  The installation procedure created a user account called postgres that is associated with the default Postgres role. In order to use Postgres, we'll need to log into that account.
  ```shell
  # login into postgres account
  sudo -i -u postgres

  # create the new role with limited rights
  createuser -P catalog
  ```
  Postgres assumes that a matching database will exist for the role to connect to.
  ``` shell
  # create the catalog database
  createdb catalog

  # connect to DB (with postgres user)
  psql -d catalog
  ```
  In the psql shell:
  ```sql
  # change database owner
  ALTER DATABASE catalog OWNER TO catalog;
  # quit
  \q
  ```
  In the ubuntu shell:
  ```shell
  # exit form postgres useraccount
  exit
  ```


#### 5.4. Git
  Install git and clone your project from your git repo
  ```shell
  # install git
  sudo apt-get install git

  # clone your git repo
  git clone your_git_repo_url
  ```

#### 5.5. Python modules
  I have a config.sh in my app that install all python modules I need to run my app
  ```shell
  # chang config.sh permissions to allow execute the file
  sudo chmod 774 ./config.sh

  # execute config.sh to install python modules
  sudo ./config.sh
  ```

### 6. SETUP

#### 6.1. Setup Database
  Setup database with the catalog database user
  ```shell
  # copy setup files to catlog user home
  sudo cp database_setup.py /home/catalog/
  sudo cp insertitems.py /home/catalog/
  # change owner and group of the copied files
  sudo chown -R catalog /home/catalog

  # login with catalog user
  sudo -i -u catalog

  # execute database setup files
  python database_setup.py
  python insertitems.py

  # exit from catlog user account
  exit
  ```

#### 6.2. Modify the app
  In the Pyhon app we need to modify:
  * Paths to absolute paths
```python
# for example:
GOOGLE_SECRETS_PATH = '/var/www/html/catalog/clientsecrets/clientsecrets_google.json'
```
  * Database connection to use the catalog user and the correct SQL Database
```python
# Connect to Database and create database session
engine = create_engine('postgresql://catalog:dbPassword@localhost/catalog')
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
session = DBSession()
```

#### 6.3. Put app files under `/var/www`
  Copy app files to work with apache
  ```shell
  # make an special dir for your app
  sudo mkdir /var/www/html/catalog

  # copy all app files to it
  sudo cp -R app/* /var/www/html/catalog

  # create debug.log to save app logs
  sudo touch /var/log/catalog.log
  # change user to allow apache to write in the file
  sudo chown www-data /var/log/catalog.log
  sudo chgrp www-data /var/log/catalog.log
  ```

#### 6.4. Configure WSGI for your app
  I used `app/catalog.wsgi` and `catalog.conf` from this repo.
  ```shell
  # create and edit a .wsgi file for your app (see app/catalog.wsgi)
  sudo touch /var/www/html/catalog/catalog.wsgi
  sudo nano /var/www/html/catalog/catalog.wsgi

  # edit the .conf file (see catalog.conf and modify your public IP)
  sudo nano /etc/apache2/sites-enabled/catalog.config
  # restart apache service
  sudo apache2ctl restart
  ```

## NOTES:
* If you have problems with your locale you can run:
```shell
# ex: if your locale is en_US:
suddo locale-gen en_US.UTF-8
```

* You can see logs of the apache server with:
```shell
# to see las 50 lines:
tail -50 /var/log/apache2/error.log
```

* If you have configured your app for logging you can also see the logs with:
```shell
tail -50 /var/log/catalog.log
```
