#!/bin/bash

# This file is used to install AppMAIS.
shopt -s expand_aliases
set -o pipefail
install_log="/var/log/AppMAIS_installation.log"

# Create bee and add it to the correct groups and the sudoers file
sudo useradd -m -s /bin/bash bee
sudo usermod -aG sudo bee
sudo usermod -aG audio bee
sudo usermod -aG video bee 
echo "bee     ALL=(ALL) NOPASSWD: ALL" | sudo EDITOR='tee -a' visudo 

# Variables to be able to switch context. 
sudo -u bee bash -c : && RUNAS_BEE="sudo -u bee"
sudo -u root bash -c : && RUNAS_ROOT="sudo -u root"

# A function to log commands and their output. 
# A function to log commands and their output. 
# Pass the argument -e to print something to both the log and output log -e "Sting"
# log -e is colorization enabled.
function log() {
    # If -e is passed as the first argument.
    if [ $1 == -e ] 
    then
        echo -e "\e[34m\e[1m\e[4m$(date +"%Y-%M-%d %H:%M:%S")\e[0m:$(printf ' %q' "echo")" >> $install_log
        echo -e "$2 $3" 2>&1 | tee -a "$install_log" 
        # Return the error code. 
        return $?
    else 
        echo -e "\e[34m\e[1m\e[4m$(date +"%Y-%M-%d %H:%M:%S")\e[0m:$(printf ' %q' "$@")" >> $install_log
        "$@" 2>&1 | tee -a "$install_log" 
        # Return the error code. 
        return $?
    fi
}

# A function to cleanup any changes that may have been made in the
# process of installing in the case of a canceled installation.
# TODO: Add anything that needs to be cleaned up to this. 
function cleanup() {
    echo "Cleaning up due to failure to setup or canceled setup."
    if id -u bee &>/dev/null ; then 
        echo "Removing 'bee' user."
        # sudo userdel -r bee
    else 
        echo "User 'bee' was not created yet."
    fi
}
# function to install Linux specific dependencies before cloning git repository
function install_Linux_dependencies(){
  echo -e $"\e[1;32mUpdating and Upgrading current packages \e[0m"

    sudo apt-get update -y
    sudo apt-get upgrade -y
    echo -e "\e[1;32mUpdating firmware to a 'stable' version for picamera2. "
    echo -e "\e[33m\e[1mWARNING!!! DON'T DO THIS IN  NORMAL PRACTICE, this is an exceptional scenario.\e[0m"
    sudo rpi-update 1a47eacfe05acf3a7c1d8602c28c0ad2b4ffd315 -y

    echo -e $"\e[1;32msudo apt-get install vim -y \e[0m"
    sudo apt-get install vim -y

    echo -e $"\e[1;32msudo apt-get install htop -y\e[0m"
    sudo apt-get install htop -y

    echo -e $"\e[1;32msudo apt-get install ecasound -y \e[0m"
    sudo apt-get install ecasound -y

    echo -e $"\e[1;32msudo apt-get install git -y \e[0m"
    sudo apt-get install git -y

    echo -e $"\e[1;32msudo apt-get install python3-pip -y \e[0m"
    sudo apt-get install python3-pip -y

    echo -e $"\e[1;32msudo apt-get install python-setuptools -y\e[0m"
    sudo apt-get install python-setuptools -y

    echo -e $"\e[1;32msudo apt-get install vlc -y \e[0m"
    sudo apt-get install vlc -y

    echo -e $"\e[1;32msudo apt-get install ffmpeg -y \e[0m"
    sudo apt-get install ffmpeg -y

    echo -e $"\e[1;32msudo apt-get install libgpiod2  -y \e[0m"
    sudo apt-get install libgpiod2 -y

    echo -e $"\e[1;32msudo apt-get install python3-picamera2 -y \e[0m"
    sudo apt-get install -y python3-picamera2
}

# A function to install all dependencies of the AppMAIS project that are 
# available through apt or pip. 
function install_dependencies() {

    echo -e $"\e[1;32mpython3 -m pip install -r /home/bee/pi_requirements.txt\e[0m"
    python3 -m pip install -r /home/bee/AppMAIS/pi_requirements.txt

}
# A function to clone the AppMAIS repo
function  clone_AppMAIS() {
    # This block is executed as the bee user. Anything between
    # the 2 underscores _ <here> _ is executes as bee.
    echo -e $"\e[1;32mCloning AppMAIS Repo \e[0m"
    $RUNAS_BEE bash<<_
    echo -e "Setting up ssh-agent for bee"

    eval "\$(ssh-agent)"

    ssh-add ~/.ssh/hx711_multi_deploy_id_rsa

    ssh-add ~/.ssh/AppMAIS_deploy_ed25519
    ssh-add ~/.ssh/adafruit_deploy_id_rsa
    ssh-add ~/.ssh/pyBeemonScripts_deploy_id_rsa

    ssh-keyscan -H github.com,140.82.112.4 >> ~/.ssh/known_hosts

    echo -e "Changing to bee's root directory"
    cd
    echo -e "\e[1;32mInstalling AppMAIS\e[0m"
    git clone --quiet git@AppMAIS.github.com:ASU-CS-Research/AppMAIS.git
_
}

# A function to install all of the AppMAIS modules. 
# It is executed as the bee user. 
function install_AppMAIS() {
  $RUNAS_BEE bash<<_
    cd ~/AppMAIS/
    sudo python3 setup.py -q develop
    cd

    echo -e "\e[1;32mInstalling HX711 Library\e[0m"
    git clone --quiet git@hx711-multi.github.com:ASU-CS-Research/hx711-multi.git
    cd hx711-multi
    sudo python3 setup.py -q install
    cd
_
}

# A function to switch to the context of root and write the raspi-blacklist.conf file.
function write_blacklist_conf() {
    echo "Switching to 'root' context to update raspi-blacklist.conf"
    $RUNAS_ROOT bash<<_
    echo -e "Creating raspi-blacklist.conf if it doesn't exist. 
    touch /etc/modprobe.d/raspi-blacklist.conf
    
    # Writing to the config file. 
    echo -e "\e[1;32mWriting to raspi-blacklist.conf\e[0m"
    echo "#wifi
    blacklist brcmfmac
    blacklist brcmutil
    #bt
    blacklist btbcm
    blacklist hci_uart" | tee /etc/modprobe.d/raspi-blacklist.conf

    echo "The contents of /etc/modprobe.d/raspi-blacklist.conf are: "
    cat /etc/modprobe.d/raspi-blacklist.conf
_
}

# A function to write /etc/asound.conf. 
function write_asound_conf() {
    $RUNAS_ROOT bash<<_
    echo -e "\e[1;32mWriting to asound.conf\e[0m"
    echo "pcm.!default {
    type hw card 1
    }
    ctl.!default {
    type hw card 1
    }
    ctl.!left {
    type hw card 1
    }
    ctl.!right {
    type hw card 2
    }" | tee /etc/asound.conf 

    echo "The contents of '/etc/asound.conf' are: "
    cat /etc/asound.conf
_
}

# A function to switch to the context of root and install the systemd unit file
# through the pyBeemonScripts.
function install_systemd() {
    $RUNAS_ROOT bash<<_

    /home/bee/AppMAIS/installation/setup-systemd.sh
_
}

function setup_raspbian() {
    $RUNAS_ROOT bash<<_
    echo -e "\e[1;32mChanging raspi-config settings.\e[0m"
    raspi-config nonint do_camera 0
    raspi-config nonint do_hostname $1
    raspi-config nonint do_memory_split 256
    raspi-config nonint do_expand_rootfs

    echo "Removing the 'pi' user. 
    userdel -f -r pi
_
}

# A function to get the keys for the github repositories.
function get_keys() {

    $RUNAS_BEE bash<<_

    # pwd
    mkdir /home/bee/.ssh
    while true; do 
        echo "Enter the password for bee@appmais.cs.appstate.edu."
        if scp -o StrictHostKeyChecking=no bee@appmais.cs.appstate.edu:/usr/local/bee/.appmais_deploy_keys/* /home/bee/.ssh
        then 
            break
        else 
            echo-e "Failed to get the keys, authentication failed. 
            fail_count=fail_count+1
            echo -e "This is failure number $fail_count / $max_failcount. 
        fi
        echo $?
    
    done
_
}

# Read the hostname of the new build.
while true; do 
    log -e "Enter the new hostname: "
    read HOSTNAME 
    log -e "Press 'y' if $HOSTNAME the correct hostname? " 
    read -n 1 -r 
    if [[ $REPLY =~ ^[Yy]$ ]]
    then
        # Successfully got hostname.
        log -e "Success."
        break
    fi
    log -e "Entered the incorect hostname, try entering the hostname again: "
done

# Try to update password for user bee. 
while true;
do 
    if log sudo passwd bee
    then 
        break
    else 
        log -e "Passwords did not match, do you want to retry? <y, n>?"
        read -r 
        if [[ $REPLY =~ ^[Nn]$ ]]; then 
            log -e "Ok, exiting setup. " 
            log cleanup
            exit 1
        fi
        log -e "Try again."
    fi 
done 
log get_keys
log install_Linux_dependencies
log clone_AppMAIS
log install_dependencies
log install_AppMAIS
log write_blacklist_conf
log write_asound_conf
log install_systemd
log setup_raspbian $HOSTNAME

log -e "Removing user pi for security puropses."
log sudo userdel pi
log -e "\e[1;32mSetup complete, Rebooting... you can now login as 'bee' \e[0m"
sudo init 6
