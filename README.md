# pokepi
weird pokemon / raspberry pi project

## What is this?
Every year at the office there's a Pokemon tournament. This year the format will be [Orre Colosseum](https://www.smogon.com/forums/threads/orre-colosseum-now-playable.3698894/) (effectively gen 3 VGC). We play on real hardware, so this year that means playing on Pokemon XD for the Gamecube. This project uses a RaspberryPi to facilitate this tournament.

Despite playing on real hardware, players do not have to raise their own Pokemon or provide their own copy of a gen 3 Pokemon game. In order to play on XD with these custom teams, we need to connect two Gameboy Advances (GBAs) with generation 3 Pokemon games (Ruby, Sapphire, FireRed, LeafGreen, or Emerald) to a Gamecube. XD reads the save data off the GBA carts and loads the six Pokemon in the players' parties for battle. XD must believe the GBA cart is an actual cart; something like an [EverDrive](https://krikzz.com/our-products/cartridges/everdrive-gba-mini.html) won't work.

Rearranging Pokemon on the GBA doesn't really scale; many teams will have similar Pokemon (i.e. same species but different moves / stats / items), and boxes become messy very quickly with so much rearranging. Instead, we use the Raspberry Pi and a GBA cart flasher to flash save files onto the carts with the correct teams preloaded. The Raspberry Pi has a small screen players can use to load the correct save.

Additionally, we want to record videos of all the matches, so we also have an HDMI input device. We only record when there is an incoming video signal.

## Software
There are two programs: one for flashing the GBA carts, and one for recording HDMI. Both are written in Python.

## Hardware List
* [Raspberry Pi 5](https://www.raspberrypi.com/products/raspberry-pi-5/)
* [Adafruit Blue&White 16x2 LCD+Keypad Kit for Raspberry Pi](https://www.adafruit.com/product/1115)
* [HDMI Input to USB 2.0 Video Capture Adapter](https://www.adafruit.com/product/4669)
* [GBxCart RW](https://www.gbxcart.com/)
* [GBA 32MB, 1Mbit Flash Save with RTC, Flash Cart](https://shop.insidegadgets.com/product/gba-32mb-1mbit-flash-save-with-rtc-flash-cart-works-with-pokemon-games/) x2
* [Wave ID® Solo Keystroke HID™ Prox Black USB Reader](https://www.rfideas.com/products/readers/single-frequency/wave-id-solo) (Someone at work had one of these lying around.)
* Nintendo Gamecube and controller
* Nintendo Gameboy Advance x2 (with some nice screen mods and usb battery packs, but this is not necessary)
* [CARBY](https://insurrectionindustries.com/product/carby-v2/) (I think I have a v1)
* A powered HDMI splitter
* Various and sundry cables
