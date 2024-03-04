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

The files at the /var/run/wpa_supplicant/ were blocking the creation of service. Removed and restarted the board.

    sudo rm /var/run/wpa_supplicant/wlan0
    sudo rm /var/run/wpa_supplicant/p2p-dev-wlan0

4. If your `wlan0` doesn't show the IP address, renew the IP with `dhclient wlan0`

