import pandas as pd
from scipy import stats

def dc_naive(df_soc, numerical_col):
    for e in numerical_col:
        removed_outliers = df_soc[e].between(df_soc[e].quantile(0.05), df_soc[e].quantile(.95))
        #print("-------------->from column " , removed_outliers.value_counts(), " are removed.")# e,
        index_names = df_soc[~removed_outliers].index # INVERT removed_outliers!!
        df_soc.drop(index_names, inplace=True)
    print("Cleaned DF is of size: ", df_soc.size)
    return df_soc