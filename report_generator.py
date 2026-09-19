# Business report generate karanyasathi function ahe.
def generate_report(df):

    total_records = len(df)

    # Available columns chi list tayar karato.
    columns = df.columns.tolist()

      if "Revenue" in df.columns:

        #calculate Total Revenue.
        total_revenue = df["Revenue"].sum()

    else:

        total_revenue = 0


    # Quantity column asel tr check karato.
    if "Quantity" in df.columns:

        # Total Quantity calculate करतो.
        total_quantity = df["Quantity"].sum()

    else:

      
        total_quantity = 0


    # report information yeka dictionary madhe thevto.
    report = {
        "total_records": total_records,
        "columns": columns,
        "total_revenue": total_revenue,
        "total_quantity": total_quantity
    }


    #tayar zalela report parat karato.
    return report
