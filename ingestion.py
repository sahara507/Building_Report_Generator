# Pandas cha upayog CSV/Excel madhil data read karanyasathi kela jato.
import pandas as pd

# he function file read karanyasathi ahe.
def load_file(file_path: str):

    if file_path.endswith(".csv"):
        df = pd.read_csv(file_path)
      
 # file cha extension .xlsx / excel asel tr,
    elif file_path.endswith(".xlsx"):
        df = pd.read_excel(file_path)

    else:
        raise ValueError("Only CSV and Excel files are supported.")

    if df.empty:
        raise ValueError("The uploaded file is empty.")

    return df
