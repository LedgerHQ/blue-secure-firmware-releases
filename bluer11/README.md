# Official Secure firmware update instructions for Ledger Blue, version 1.1

For this specific release, proceed as follows : 

  - Make sure to install the Python loader application from https://github.com/LedgerHQ/blue-loader-python (latest version or release 1.1) and operate in the same Python virtual environment 
  - Install Protocol Buffers 
```
pip install protobuf
```
  - Turn on Ledger Blue, keeping the button pressed until "secure bootloader" is displayed
  - Update the Operating System (hash 07c9d1b82709d0babe5159836d0c85f3cefd1db8328ac970e95cca9bf0ec6a3f) - the device turns off
```
python updateFirmware.py --url https://shop.hardwarewallet.com/hsm/process --perso perso_10 --firmware upgrade_bluer11 --firmwareKey upgrade_bluer11_key 
```
  - When restarting, the firmware will display "Connect USB" - at this moment, perform the Non Secure Operating System update as described in https://github.com/LedgerHQ/blue-nonsecure-firmware-releases/bluer11 
  - When this is done, finalize the firmware personalization with
``` 
python refactory.py --url https://shop.hardwarewallet.com/hsm/process --perso perso_10 --persoNew perso_11
```

