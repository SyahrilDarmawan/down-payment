# VIT PO Down Payment

## Overview
VIT PO Down Payment is an Odoo module that enhances the Purchase Order functionality by adding support for down payments. This module allows users to manage advance payments before invoicing, track payment statuses (Not Paid, Paid, Partially Paid), and automatically calculate the remaining amount due.

## Features
- **Down Payment Wizard**: Record advance payments directly from the Purchase Order form using an intuitive wizard.
- **Residual Amount Calculation**: Automatically computes the remaining amount due by subtracting advance payments and paid invoices from the total order amount.
- **Payment Tracking**: View a list of related payments in the "Payment Advances" tab on the Purchase Order form.
- **Payment Status**: Monitors payment progress with real-time status updates (Not Paid, Paid, Partially Paid).
- **Multi-Currency Support**: Handles currency conversions between the payment journal and the Purchase Order currency.

## Dependencies
- `base`
- `purchase`
- `account`

## Installation
1. Clone this repository into your Odoo `addons` directory:
   ```bash
   git clone https://github.com/SyahrilDarmawan/vit_po_down_payment.git
