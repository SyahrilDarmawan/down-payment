# Purchase Order Down Payment for 16.0 Version

## Overview
Purchase Order Down Payment is an add-on module for the Odoo Purchase module, specifically designed to extend its functionality by adding support for down payments. This module enables users to record and manage advance payments for Purchase Orders (POs), track payment statuses, and calculate the remaining balance, all while seamlessly integrating with Odoo's existing Purchase workflow.

This module does not replace the core Purchase module but enhances it by introducing down payment capabilities, making it easier to handle partial payments before invoicing.

## Features
- **Down Payment Integration**: Adds a "Pay purchase advanced" button to the Purchase Order form, allowing users to record advance payments via a dedicated wizard.
- **Payment Tracking**: Introduces a "Payment advances" tab on the Purchase Order form to display the list of advance payments associated with the PO.
- **Residual Amount Calculation**: Automatically calculates the remaining amount due by subtracting advance payments and paid invoices from the total PO amount.
- **Payment Status Monitoring**: Tracks the advance payment status (Not Paid, Paid, Partially Paid) with real-time updates based on payment activities.
- **Multi-Currency Support**: Handles currency conversions between the payment journal and the PO currency for accurate calculations.

## Dependencies
- `base`
- `purchase`
- `account`

## Installation
1. Clone this repository into your Odoo `addons` directory:
   ```bash
   git clone https://github.com/SyahrilDarmawan/down-payment.git
