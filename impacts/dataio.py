import pandas as pd
import os
from glob import glob

_all_ = [
        'load_scimagojr'
]


def load_scimagojr(file_path=None):
    """
    Try to read in a preformatted dataframe for all scimagojr journals that include 'Psy', 'Neuro', or 'Misc' in their categorization. This helps reduce the amount of plotting to be done since plotting all journals data requires reading in a ~550mb csv file.

    If this csv file doesn't exist, create it from raw scraped scimagojr files for each year. This data was obtained from: https://www.scimagojr.com/journalrank.php
    """
    if file_path is None:
        file_path = os.path.join('data', 'all_years_psyneuro.csv')
    if os.path.exists(file_path):
        print("LOADING EXISTING FILE")
        dfs = pd.read_csv(file_path)
    else:
        print("CREATING NEW FILE")
        data_files = glob(os.path.join('data', 'scimagojr*.csv'))
        names = [e.split('_')[-1][:4] for e in data_files]
        dfs = []
        for f, n in zip(data_files, names):
            _df = pd.read_csv(f, delimiter=';')
            _df = _df.assign(Year=n)
            dfs.append(_df)
        dfs = pd.concat(dfs, axis=0, ignore_index=True)

        # Combine total docs which are broken up across differently named columns
        dfs = dfs.fillna(0)
        total_docs = dfs['Total Docs. (2010)']+dfs['Total Docs. (2011)']+dfs['Total Docs. (2012)']+dfs['Total Docs. (2013)']+dfs['Total Docs. (2014)']+dfs['Total Docs. (2015)']+dfs['Total Docs. (2016)']+dfs['Total Docs. (2017)']
        dfs = dfs.assign(Total_Docs=total_docs).drop(columns=['Total Docs. (2010)', 'Total Docs. (2011)', 'Total Docs. (2012)', 'Total Docs. (2013)', 'Total Docs. (2014)', 'Total Docs. (2015)', 'Total Docs. (2016)', 'Total Docs. (2017)'])
        # Filter for psych, neuro, and general only
        dfs = dfs[dfs.Categories.apply(lambda x: ('Psy' in x) or ('Neuro' in x) or ('Multidiscip' in x))]
        dfs = dfs.assign(Color='black')

        def _catz(val):
            if 'psy' in val.lower():
                if 'neuro' in val.lower():
                    return 'Psych & Neuro'
                else:
                    return 'Psych'
            if 'neuro' in val.lower():
                return 'Neuro'
            if 'multi' in val.lower():
                return 'General'

        dfs['Field'] = dfs['Categories'].apply(_catz)
        # Make sure the SJR stat gets coerced properly
        dfs['SJR'] = dfs['SJR'].apply(lambda x: str(x).replace(',', '.'))

        # Long format for plotly
        dfs = pd.melt(dfs, id_vars=['Title', 'Year', 'Country', 'Color', 'Field'], var_name='Dimension', value_name='Value')
        dfs.to_csv(os.path.join('data', 'all_years_psyneuro.csv'), index=False)

    return dfs
