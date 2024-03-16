# Prepare the SD Card from scratch

This project used the `2023-12-11-raspios-bookworm-armhf-lite.img.xz` image from the raspberry organization. This is a light version, i.e no Windows or GUI. All the interactions with it are to be done from the Command Line interface (CLI) using Linux Shell.

Used BalenaEtcher to program the image in to sdcard. To simplify the use from a Windows PC, as a headless board attached over USB, below instructions will make that possible.

1. Re-insert the sdcard image in to USB drive of Windows PC. It should be able to see the `boot` partition which is a FAT32 filesystem. This partion contains the bootloader and additional instructions for it.

2. Modify the `config.txt` to add under the `[all]` section on a newline `dtoverlay=dwc2`. This makes the OS load USB gadget.

3. Modify the `cmdline.txt` file to append the `modules-load=dwc2,g_serial`. This will load the serial driver automatically on the USB gadget.

# Building a custom Pi Image

An attempt was made to build a tailored image using `pi-gen`

## References

* [`pi-gen`, an image generator for pi](https://github.com/RPi-Distro/pi-gen)
* [Geoff Hodik's blog](https://geoffhudik.com/tech/2020/05/15/using-pi-gen-to-build-a-custom-raspbian-lite-image/)

## Steps

1. clone the `pi-gen`

        git clone https://github.com/RPi-Distro/pi-gen.git
        cd pi-gen

2. create a sub-folder `stage2_proxima` and copy the couple of files there from `stage2`

        cp stage2/EXPORT_IMAGE stage_proxima/
        cp stage2/prerun.sh stage_proxima/

Create a file at `stage_proxima/01-sys-tweaks/01-run.sh` with the below contents. This will activate a console login over USB.

        #!/bin/bash -e

        # Append to /boot/firmware/config.txt under the [all] section
        echo "dtoverlay=dwc2" | tee -a "${ROOTFS_DIR}/boot/firmware/config.txt"

        # Append to /boot/firmware/cmdline.txt after "rootwait", to activate serial gadget
        sed -i 's/rootwait/rootwait modules-load=dwc2,g_serial/' "${ROOTFS_DIR}/boot/cmdline.txt"

        # Enable the serial console login
        on_chroot << EOF
        systemctl enable getty@ttyGS0.service
        EOF


3. Config file as below:

        IMG_NAME=proxima-raspios
        RELEASE=bookworm
        PI_GEN_RELEASE=proxima_sls
        DEPLOY_COMPRESSION=xz
        LOCALE_DEFAULT=en_US.UTF-8
        KEYBOARD_KEYMAP=us
        KEYBOARD_LAYOUT="English (US)"
        TIMEZONE_DEFAULT=America/Los_Angeles
        TARGET_HOSTNAME=proxima-zero
        ENABLE_SSH=1
        DISABLE_FIRST_USER_BOOT_USER_RENAME=1
        FIRST_USER_NAME=pi
        FIRST_USER_PASS=pi
        WPA_COUNTRY=US
        STAGE_LIST="stage0 stage1 stage2 stage_proxima"

4. Build 

        touch ./stage3/SKIP ./stage4/SKIP ./stage5/SKIP
        touch ./stage2/SKIP_IMAGES ./stage2/SKIP_NOOBS ./stage4/SKIP_IMAGES ./stage5/SKIP_IMAGES
        sudo ./build-docker.sh

Resulting image under `deploy/image_2024-03-09-proxima-raspios-lite.img.xz` can be etched on the sd card.

# Clone the SD Card images

This activity is for cloning the RPI image from the `GOLD` card to `SILVER` card

## Copy from Source Card `GOLD`

Insert the `GOLD` card in to Linux workstation
1. Identify the partitions

    lsblk

In my case the SD card showed up as `/dev/sdb1` and `/dev/sdb2`. These are two partitions. First partiton contains the `boot` image which is a FAT32 filesystem with the overlays and Linux kernel. Second partition contains the Linux Filesystem where all programs and rest of the Operating system (except Linux kernel) reside. Lets call the second partition as `root` image, which is a Linux native Filesystem named EXT4.

2. Make a subdirectory to mount the partitions of interest

    mkdir -p mnt/boot
    sudo mount /dev/sdb1 mnt/boot
    mkdir -p mnt/root
    sudo mount /dev/sdb2 mnt/root

3. Now copy the contents of both partitions using `rsync`. This style of copy preserves the file attributes. For example the linux file has date, owner's user and group, file type such as directory, file, symbolic link, etc, etc.

    sudo rsync -aHAXxv mnt/boot/ gold/boot/
    sudo rsync -aHAXxv mnt/root/ gold/root/

To keep the names consistent, we already named the folder `gold/` for receiving the gold card contents. Further on using the `rsync` we can perform incremental (or delta) copies in subsequent operations.

4. Eject the `GOLD` card safely

    sudo eject /dev/sdb

Linux maintains the hierarchy of the drive and partitions. In this case the `/dev/sdb` is the name of the disk drive, while the `/dev/sdb1` is a partition on that drive.

## Copy to Destination Card `SILVER`

Insert the `SILVER` card in to Linux workstation. NOTE: You may be destroying the old contents. We are going to reformat the disk drive to prepare for receiving the `GOLD` card's contents. 

1. Identify the drive and detemine the paritions to be created. If this is a brand new card, there is likely a partition or nothing. If this is a pre-existing card with different contents, we are deciding to reformat anyways. Followed this guide [How to Partition and Format SD Card w/ fdisk](https://www.youtube.com/watch?v=EFzHj-GbR7c).

2. Copy the `gold` contents

    sudo mount /dev/sdb1 mnt/boot
    sudo mount /dev/sdb2 mnt/root
    sudo rsync -avxHAX --progress gold/boot/ mnt/boot/
    sudo rsync -avxHAX --progress gold/root/ mnt/root/

3. This step of `umount` is important because though the `rsync` states the contents are copied, they actually doesn't make it to disk.

    sudo umount mnt/boot
    sudo umount mnt/root

This will flush any pending writes in to the disk drive.

4. Perform the checks

    sudo fsck.vfat -av /dev/sdb1
    sudo fsck.ext4 -pf /dev/sdb2

and eject the card

    sudo eject /dev/sdb

# Setup wlan0 to a WiFi Access point

Configured the `wlan0` using the `wpa_supplicant`. The service was disabled as well as it was looking for a specific configuration file, not available from the instructions.

1. Enable the service

        sudo systemctl enable wpa_supplicant@wlan0.service

2. Edit the configuration file here, if not present create one at that path

        sudo nano /etc/wpa_supplicant/wpa_supplicant-wlan0.conf

3. Add the configuration for the WLAN access point. Make sure it is available in 2.4GHz

        network={
            ssid="WLAN_AP_NAME"
            psk="password"
            key_mgmt=WPA-PSK
        }

    NOTE: To view the accesspoints `iwlist scanning | grep -iE "ESSID|Quality"`

The files at the /var/run/wpa_supplicant/ were blocking the creation of service. Removed and restarted the board.

    sudo rm /var/run/wpa_supplicant/wlan0
    sudo rm /var/run/wpa_supplicant/p2p-dev-wlan0

4. If your `wlan0` doesn't show the IP address, renew the IP with `sudo dhclient wlan0`

# Enable Bluetooth

The package `pi-bluetooth` appeared to have been installed. Checking the installed packages with `dpkg -l` shows the `bluez` and `bluez-firmware`.

1. activate bluetooth service `sudo systemctl enable blueooth`.
2. use `bluetoothctl` to pair with android phone. This runs in the interactive mode. Here is the screenshot


        pi@proxima-zero:~$ bluetoothctl
        Agent registered
        [CHG] Controller B8:27:EB:E7:5A:75 Pairable: yes
        [bluetooth]# help
        Menu main:
        Available commands:
        -------------------
        ...

        [bluetooth]# discoverable on
        Changing discoverable on succeeded
        [CHG] Controller B8:27:EB:E7:5A:75 Discoverable: yes
        [NEW] Device EC:7C:B6:D6:9E:2B Galaxy S21 5G
        Request confirmation
        [agent] Confirm passkey 368987 (yes/no): yes
        [CHG] Device EC:7C:B6:D6:9E:2B Bonded: yes
        [CHG] Device EC:7C:B6:D6:9E:2B Modalias: bluetooth:v0075p0100d0201
        [CHG] Device EC:7C:B6:D6:9E:2B UUIDs: 00001105-0000-1000-8000-00805f9b34fb
        [CHG] Device EC:7C:B6:D6:9E:2B UUIDs: 0000110a-0000-1000-8000-00805f9b34fb
        [CHG] Device EC:7C:B6:D6:9E:2B UUIDs: 0000110c-0000-1000-8000-00805f9b34fb
        [CHG] Device EC:7C:B6:D6:9E:2B UUIDs: 0000110e-0000-1000-8000-00805f9b34fb
        [CHG] Device EC:7C:B6:D6:9E:2B UUIDs: 00001112-0000-1000-8000-00805f9b34fb
        [CHG] Device EC:7C:B6:D6:9E:2B UUIDs: 00001115-0000-1000-8000-00805f9b34fb
        [CHG] Device EC:7C:B6:D6:9E:2B UUIDs: 00001116-0000-1000-8000-00805f9b34fb
        [CHG] Device EC:7C:B6:D6:9E:2B UUIDs: 0000111f-0000-1000-8000-00805f9b34fb
        [CHG] Device EC:7C:B6:D6:9E:2B UUIDs: 0000112f-0000-1000-8000-00805f9b34fb
        [CHG] Device EC:7C:B6:D6:9E:2B UUIDs: 00001132-0000-1000-8000-00805f9b34fb
        [CHG] Device EC:7C:B6:D6:9E:2B UUIDs: 00001200-0000-1000-8000-00805f9b34fb
        [CHG] Device EC:7C:B6:D6:9E:2B UUIDs: 00001800-0000-1000-8000-00805f9b34fb
        [CHG] Device EC:7C:B6:D6:9E:2B UUIDs: 00001801-0000-1000-8000-00805f9b34fb
        [CHG] Device EC:7C:B6:D6:9E:2B ServicesResolved: yes
        [CHG] Device EC:7C:B6:D6:9E:2B Paired: yes

3. Enable rfcomm, the virtual serial (UART style) port.
