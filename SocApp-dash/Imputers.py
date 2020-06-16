
# make copy to avoid changing original data (when Imputing)
#new_data = df_soc.copy()

# make new columns indicating what will be imputed
#cols_with_missing = (col for col in new_data.columns
#                                 if new_data[col].isnull().any())
#print("cols_with_missing" , cols_with_missing)

#for col in numerical_col: #cols_with_missing:
#    new_data[col + '_was_missing'] = new_data[col].isnull()

# Imputation
import pandas as pd
from sklearn.impute import SimpleImputer

def impute_naive(df_soc, numerical_col):
    my_imputer = SimpleImputer()
    for e in numerical_col:
        s_array = df_soc[e].to_numpy()
        imputed = my_imputer.fit_transform(s_array.reshape(-1, 1))
        print(imputed, imputed.ndim)

        df_soc[e] = imputed
    return df_soc