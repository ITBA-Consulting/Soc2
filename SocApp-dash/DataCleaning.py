import pandas as pd
from scipy import stats
import numpy as np
from scipy import stats


def od(df_soc, numerical_col, type):
    print("type" , type, type == 'naive')
    if type == 'naive':
        for e in numerical_col:
            print("enter od")
            removed_outliers = df_soc[e].between(df_soc[e].quantile(0.05), df_soc[e].quantile(.95))
            #print("-------------->from column " , removed_outliers.value_counts(), " are removed.")# e,
            index_names = df_soc[~removed_outliers].index # INVERT removed_outliers!!
            df_soc.drop(index_names, inplace=True)
        print("Cleaned DF is of size: ", df_soc.size)
        print("left od")
        return df_soc
    elif type == 'zscore':
        print("enter od2")
        df_soc[(np.abs(stats.zscore(df_soc)) < 3).all(axis=1)]
        print("left od2")
        return df_soc

    return df_soc



