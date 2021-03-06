- Add a function to make sheet names unique
- Error logging
    - https://docs.python.org/3/howto/logging.html
- Add optional ETX footer for data
- Add settings menu
    - Tick and untick ledgers for calculations
    - Front-end management of library
        - Allow loading all spreadsheets from folder; add wildcard tolerance to
            `load_spreadsheets`
    - https://stackoverflow.com/questions/69678621/input-with-multiple-removable-values-in-dash
    - Display error when trying to add a restricted name to a name map
        - Any name that exists as a default or an alt is restricted
        - Restricted as column names as well
        - Add description key to certain names (display as tooltip?)
            - sheet types

- Date formatting:
    - https://pandas.pydata.org/docs/reference/api/pandas.Period.strftime.html
- Plot the running total versus date
- Filter dropdown by sheet type
- Export journal/summary
    - copy from table: https://dash.plotly.com/dash-core-components/clipboard
- Think about table overflow
- PyInstaller
    - https://realpython.com/pyinstaller-python/
    - cx_Freeze: https://community.plotly.com/t/convert-dash-to-executable-file-exe/14222/3
- Auto-install dependencies
- Splash screen while loading data
- Work on
- Date picker range
    - https://community.plotly.com/t/datepickerrange-to-update-data-table/16193/6
- Draft a readme
