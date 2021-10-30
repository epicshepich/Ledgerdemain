# Changelog

## 0.1.3 - 29 Oct 2021 (Current)
- Changed GUI; now ledgers, ledger summary, and transaction journal are displayed in separate tabs
- Overhauled GUI backend
- Added a copy-to-clipboard button above tables (this feature is inconsistent)
- Started development of front-end settings menu

## [0.1.2] - 29 Oct 2021
- Reimplemented cefpython3 browser window; error addressed by using waitress package
- Added automatic installation of required packages
- Added support for updating settings.json (no front-end implementation yet)
- Attempted to use cx_Freeze to package application into executable; decided to leave that for later


## [0.1.1] - 28 Oct 2021
- Removed cefpython3 browser window because of errors
- Added support for disambiguation of column headers, metadata tags, special characters, etc.
- Added "name-map" setting to settings.json, which allows users to customize default names, meta-tag names, and disambiguation behavior
- Added analytics.py, which generates a ledger summary table and transaction journal table
- Added attributes to settings.json for customization of date display format and columns listed in the transaction journal


## [0.1.0] - 27 Oct 2021
- Added a rudimentary Dash GUI with a title, a metadata header, a data table, and a dropdown selector to switch between displayed ledgers
- Used cefpython3 to launch the Dash GUI in an individual window
- Added functionality to read in a ledger .xlsx spreadsheet, separating the metadata header from the body (data) of the sheet
- Added settings.json, which will allow users to modify certain behaviors


[0.1.0]: https://github.com/epicshepich/Ledgerdemain/commit/9564a1827f17f571a28d32e695265b68393ba667
[0.1.1]: https://github.com/epicshepich/Ledgerdemain/commit/7f46df79658b6fe9760259db5be392612b7e1f5b
[0.1.2]: https://github.com/epicshepich/Ledgerdemain/commit/1788ed6929759ec9668a6d1b2aa3ed2891ff4699
