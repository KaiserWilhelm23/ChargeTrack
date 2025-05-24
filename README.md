# ChargeTrack

ChargeTrack is a full-screen, professional-grade battery management system designed for all types of automotive businesses that offer free battery charging services. It helps you efficiently check in, track, and manage customer batteries for charging and pickup. 

Concept Program Only!!!! But can be added on to for commercial use.

# Features

  Customer check-in with name, phone number, and battery size (dropdown or manual entry).

  Automatic generation of unique battery IDs formatted as [battery_size]-[initials]-[random digits].

  PDF receipt generation with barcode for customers.
    
  Live management and tracking of batteries currently in possession.

  Full-screen, user-friendly interface designed for quick and easy use.

  Easily extensible for check-out, reporting, and settings.

# Installation

  Make sure Python 3.x is installed.

  Install required packages:

    pip install tkinter pillow python-barcode fpdf

Run the application:

    python battery_manager.py

# Usage

  Check In: Enter customer details and battery size to register the battery for charging.

  View Inventory: See all batteries currently checked in and awaiting pickup.

  Receipts: Generates customer receipts with barcode for easy identification.

  Settings: Configure pickup hours and other preferences (future enhancements).

# Notes

  Designed primarily for automotive shops, service centers, and similar businesses that provide free battery charging.

  Data is saved locally in CSV files, and receipts are saved as PDFs in a receipts folder.

  Intended to run on full-screen displays such as Raspberry Pi setups with 7-inch screens.

# License

MIT License
