"""This module generates reports and summaries from the spreadsheet library."""

from spreadsheet_io import *

def ledger_summary(ledgers:dict) -> tuple:
    """This function creates a summary of all of the spreadsheets of type
    'ledger' including for each ledger such information as ledger name,
    balance (sum of all payments), last payment, etc."""

    summary = []

    summary_meta = {
        map_name("_name_"): map_name("ledger-summary"),
        map_name("_type_"): map_name("_summarytype_")
    }

    for ledger_name in ledgers:
        #Create a row summarizing each ledger.
        data, metadata = ledgers[ledger_name]

        row_summary = {
            "Ledger": metadata[map_name("_name_")]
        }

        if map_name("payment") in data.columns:
            row_summary[map_name("balance")] = f'{sum(data[map_name("payment")]):.2f}'
            #The balance is the sum of all payments.
            row_summary["Last Payment"] = f'{data[map_name("payment")].iloc[-1]:.2f}'
            #The last payment is the last item in the payment row.
            if map_name("paid by") in data.columns:
                 row_summary["Last Payment"] += f' from {data[map_name("paid by")].iloc[-1]}'
                 #Include (if specified) the source of the last payment on the ledger.

        if map_name("paid until") in data.columns:
            row_summary[map_name("paid until")] = data[map_name("paid until")].iloc[-1]
            #If specified, include how long the payment is good for.

        for metakey in ["phone","tenants"]:
            if map_name(metakey) in metadata:
                metaval = metadata[map_name(metakey)]
                row_summary[map_name(metakey)] = "\n".join(metaval) if isinstance(metaval,list) else metaval
                #For certain metadata, include them as-is if they are single-valued, or delimit multiple values
                #by line breaks.

        summary.append(row_summary)

    summary_table = pd.DataFrame(summary)

    return (summary_table, summary_meta)





def ledger_journal(ledgers:dict) -> tuple:
    journal = pd.concat([ledger for ledger,_ in ledgers.values()])

    journal = journal.loc[~journal[map_name("paid by")].isin(settings["journal-exclude"])]
    #Filter out payments from sources listed in "journal-include" setting.


    journal["_sorter_"] = pd.to_datetime(journal[map_name("date")])
    #Pandas appears to have some trouble sorthing by date, so we have to convert
    #to datetime. In order to preserve formatting, this is added as a temporary column.
    journal = journal.sort_values("_sorter_")
    #Sort by date.


    for column in journal.columns:
        if not column in settings["journal-columns"]:
            journal.drop(column,axis=1,inplace=True)
            #Only include columns listed in the "journal-columns" setting


    journal_meta = {
        map_name("_name_"): map_name("journal-name"),
        map_name("_type_"): map_name("_journaltype_"),
        "Last Entry": journal[map_name("date")].iloc[-1]
    }


    return (journal,journal_meta)
