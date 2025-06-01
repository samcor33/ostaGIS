def vals_to_df(entries):
    """
    Description:
        df_name: name for new DataFrame
        entries: list of text to be in each row of the DataFrame
    """  
    if isinstance(entries, list):
        None
    else:
        raise Exception('entries param must be a list')
    
    import pandas as pd
    df = {"values": entries}
    df = pd.DataFrame(df)
    return df
