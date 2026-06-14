First of all:
Thanks to N0ciple https://github.com/N0ciple/gbopyrator for the gb_gbc_roms_info.json 
archive for the cartridge's crc database.

The thing:
This is a share of the files that i'm using for my own project related with spanish
pokemon gen 1 and 2 gameboy cartridges, so the results may vary as the files are
heavily focused on that purpose, but the code is there and can be repurposed and used.

Currently I have a problem writing the gen 2 saves and I'd be pretty happy if someone
happens to help me fix it. (Seems some kind of security those cartridges have before
writing data to them through external sources or something like that),

I hope these files serve you in any way to whatever project you are making!

Notes:

This is meant to work with the Epilogue GB Operator with the firmware 10. I cannot guarantee
that i'll work with anything higher and certainly it wont work with anything below 10.

Use the Windows Device Manager to find your GB Operator and determine your COM port
on the "COM AND LPT" category. As you can see, mine is on "COM8":

<img width="328" height="92" alt="image" src="https://github.com/user-attachments/assets/3ded78c1-de9f-4580-b904-788ad7c6d93b" />

For advanced users, if anything goes wrong, this is the current driver status my
Epilogue GB Operator is working under (using zadig-2.9) (Disable Ignore hubs to see the composite parent):

<img width="703" height="309" alt="image" src="https://github.com/user-attachments/assets/f5e6c0ae-8d84-45cb-8059-6ca0d5bbfc63" />
<img width="713" height="311" alt="image" src="https://github.com/user-attachments/assets/45d7f412-1dda-4696-9bb4-ec73aca8f4c0" />
<img width="707" height="312" alt="image" src="https://github.com/user-attachments/assets/82bf6aed-bdb4-431e-beb2-041b35a87d7b" />

I think I left it stock, but as it is working now under these drivers, this is the first 
thing you should try to change while troubleshooting!


and edit the COM PORT on the .py files:
# COM PORT SETTINGS
PUERTO = 'COM8'
to whatever port your Epilogue GB Operator firmware version 10 is using.

How to setup to get it running:

Simply Install python 3.11.9 (The version I'm using to build this)
