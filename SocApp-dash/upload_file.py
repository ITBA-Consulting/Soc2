import pandas as pd
import base64
import datetime
import io

path = 'E:\\Gdrive\\WorkSG\\projets\\Socorro\\Soc2\\SocApp-dash\\data\\'
def parse_contents( filename):
    #content_type, content_string = contents.split(',')
    print("in  ", filename[0] , [ 'csv' in filename[0]])
    #decoded = base64.b64decode(content_string)
    try:
        if  'csv' in filename[0]:
            print("read csv")
            # Assume that the user uploaded a CSV file
            df = pd.read_csv(path + filename[0]
               # io.StringIO(decoded.decode('utf-8'))
               )
        elif 'xls' in filename[0]:
            # Assume that the user uploaded an excel file
            print("read excel1")
            df = pd.read_excel(path + filename[0] , header=0, parse_dates=[0], index_col=0)#
            print("read excel2")
    except Exception as e:
        print("read except")
        print(e)
        return html.Div([
            'There was an error processing this file.'
        ])

    return df, path + filename[0]


