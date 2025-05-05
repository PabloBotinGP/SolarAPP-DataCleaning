import pandas as pd
import os
import numpy as np
import warnings
warnings.simplefilter(action='ignore', category=pd.errors.SettingWithCopyWarning)

# MAPPINGS. Set always everything lowecase. 

project_type_mapping = {
    # PV
    'photovoltaic system': 'PV',
    'pv - roof mount': 'PV',
    'pv': 'PV',
    'pv ': 'PV',
    
    # PV+ST
    'photovoltaic system with energy storage system': 'PV+ST',
    'pv w/battery - roof mount': 'PV+ST',
    'pv + storage': 'PV+ST',
    'pv + storage ': 'PV+ST'
}
 
permit_status_mapping = {
    # other
    'cancelled': 'other',
    'canceled': 'other',
    # 'closed': 'other',
    'closed - withdrawn': 'other',
    'withdrawn': 'other',
    'dead': 'other',
    'claim filed': 'other',
    'expired': 'other',
    'fees due': 'other',
    'plan approval expired': 'other',
    'rejected': 'other',
    'stop work order': 'other',
    'needs resubmittal': 'other',
    'stop work': 'other',

    # finaled
    'complete': 'finaled',
    'reinstated': 'finaled',
    'final - atmc': 'finaled',
    'finaled': 'finaled',
    'closed/final': 'finaled',
    'approved': 'finaled',
    'final': 'finaled',
    'inspections complete': 'finaled',
    'done': 'finaled',
    'final inspection done':'finaled',
    'closed': 'finaled',
    'pln ck approved': 'finaled',
    'administratively closed':'finaled',

    # issued
    'active': 'issued',
    'issued': 'issued',
    'issued - revision submitted': 'issued',
    'inspection phase': 'issued',
    'in review': 'issued',
    'review': 'issued',
    'open': 'issued',
    'issued - revision pending': 'issued',
    'issued (revision pending)':'issued',
    'payment pending': 'issued',
    'pend correction': 'issued',
    'plan check': 'issued',
    'other': 'issued',
    'correction alert': 'issued',
    'appointment req':'issued',
    'inspections': 'issued',
    'clearances required':'issued',

    # before issuance (map to blank)
    'void': '',
    'additional info required': '',
    'pending issuance': '',
    'ready to issue': '',
    'revision required': '',
    'pending resubmittal': '',
    'pending': '',
    'unk': '',
    'ready for issuance (revision)': '',
    'submitted - online': '',
    'applied': '',
    'applied online': ''
}

inspection_status_mapping = {
    # Passed
    'approved': 'passed',
    'apporved': 'passed',
    'aproved': 'passed',
    'passed': 'passed',
    'pass': 'passed',
    'approved w/ exception': 'passed',
    'approved w/ service release': 'passed',
    'pass - co not required': 'passed',
    'not applicable': 'passed',
    'approved for avista': 'passed',
    
    # Failed
    'denied': 'failed',
    'failed': 'failed',
    'fail': 'failed',
    'fal': 'failed',
    're-inspection required': 'failed',
    're-inspection required (with fee)': 'failed',
    'partial approval': 'failed',
    'denied/corrections': 'failed',
    'refee due - denied/corrections': 'failed',
    'partial': 'failed',
    'correction notice': 'failed',
    'correction notice issued': 'failed',
    'incomplete': 'failed',
    'corrections': 'failed',
    'corrections required': 'failed',
    'assess reinspection fee': 'failed',
    'disapproved': 'failed',
    'disapproved w/reinspection fee': 'failed',
    'reinsp fee chrg': 'failed',
    're-inpection': 'failed',    # typo included here
    're-inspection': 'failed',
    'reinspection': 'failed',
    'plan revisions required': 'failed',
    'fail - not ready': 'failed',           
    'fail - corrections required': 'failed',
    'fail - revision required': 'failed',   
    'conditional': 'failed',                
    'partial pass':'failed',
    'not ready': 'failed',
    'no access': 'failed',
    
    # Canceled
    'cancelled': 'canceled',
    'canceled': 'canceled',
    'cancel': 'canceled',
    'issued': 'canceled',
    'inspection not required': 'canceled',
    'cancelled - due to weather': 'canceled',    # added
    'cancelled - see comments': 'canceled',      # added
    'cancelled - contractor/owne': 'canceled',   # added
    
    # Empty (remove)
    'pending': '',
    'scheduled': '',
    'note': '',
    'incorrect inspection type': '',
    'comment': '',
    '2': ''
}

standard_columns = [
    "solarAPP_or_traditional", "AHJ", "permit_ID", "solarAPP_ID", "address", 
    "project_type", "permit_status", "permit_submission_date", "permit_issuance_date", 
    "inspt_failed_once", "inspt_status_last", "inspt_date_last", "inspt_notes_last", 
    "inspt_status_1", "inspt_date_1", "inspt_notes_1", "inspt_status_2", "inspt_date_2", "inspt_notes_2", 
    "inspt_status_3", "inspt_date_3", "inspt_notes_3", "inspt_status_4", "inspt_date_4", "inspt_notes_4", 
    "inspt_status_5", "inspt_date_5", "inspt_notes_5", "inspt_status_6", "inspt_date_6", "inspt_notes_6", 
    "inspt_status_7", "inspt_date_7", "inspt_notes_7", "inspt_status_8", "inspt_date_8", "inspt_notes_8", 
    "inspt_status_9", "inspt_date_9", "inspt_notes_9", "inspt_status_10", "inspt_date_10", "inspt_notes_10"
]

# FUNCTIONS
def get_inspt_failed(row):
    """
    Determine if a permit has failed any inspections.
    
    Returns:
    - 'Yes' if any inspection status is 'failed'.
    - 'No' if inspt_status_last is passed and permit is finaled.
    - '' otherwise.
    """
    columns_to_check = [
        'inspt_status_last',
        'inspt_status_1', 'inspt_status_2', 'inspt_status_3', 'inspt_status_4',
        'inspt_status_5', 'inspt_status_6', 'inspt_status_7', 'inspt_status_8',
        'inspt_status_9', 'inspt_status_10'
    ]

    if any(row.get(col) == 'failed' for col in columns_to_check if col in row):
        return 'Yes'
    elif row.get('permit_status') == 'finaled' and row.get('inspt_status_last') == 'passed':
        return 'No'
    else:
        return ''

def add_inspt_failed_once_column(df):
    """
    Adds the 'inspt_failed_once' column to a DataFrame using the get_inspt_failed logic.
    Places the column immediately after 'permit_issuance_date'.

    Parameters:
    - df: pandas DataFrame with inspection status columns

    Returns:
    - Modified DataFrame with 'inspt_failed_once' column
    """
    # Generate the column
    df['inspt_failed_once'] = df.apply(get_inspt_failed, axis=1)

    # Reorder the column to be right after 'permit_issuance_date'
    cols = df.columns.tolist()

    try:
        cols.remove('inspt_failed_once')
        insert_idx = cols.index('permit_issuance_date') + 1
        cols.insert(insert_idx, 'inspt_failed_once')
        df = df[cols]
        print("✅ 'inspt_failed_once' column inserted after 'permit_issuance_date'.")
    except ValueError:
        print("⚠️ Could not reposition 'inspt_failed_once' because 'permit_issuance_date' was not found.")

    return df

def Merge_Inspections(df):
    # Step 1: Split permits and inspections
    permit_cols = [
        'solarAPP_or_traditional', 'AHJ', 'permit_ID', 'solarAPP_ID', 'address',
        'project_type', 'permit_status', 'permit_submission_date', 'permit_issuance_date'
    ]
    permit_df = df.drop_duplicates(subset='permit_ID')[permit_cols].set_index('permit_ID')

    inspections_df = df[['permit_ID', 'inspt_status_last', 'inspt_date_last', 'inspt_notes_last']].copy()
    inspections_df = inspections_df.dropna(subset=['inspt_date_last'])  # Ensure proper sorting

    # Step 2: Rank inspections by date
    inspections_df = inspections_df.sort_values(by=['permit_ID', 'inspt_date_last'])
    inspections_df['rnk'] = inspections_df.groupby('permit_ID').cumcount() + 1

    # Step 3: Pivot inspections to wide
    inspections_wide = pd.DataFrame()
    for i in range(1, 9):
        rnk_df = inspections_df[inspections_df['rnk'] == i].set_index('permit_ID')[
            ['inspt_status_last', 'inspt_date_last', 'inspt_notes_last']
        ].rename(columns={
            'inspt_status_last': f'inspt_status_{i}',
            'inspt_date_last': f'inspt_date_{i}',
            'inspt_notes_last': f'inspt_notes_{i}'
        })
        inspections_wide = inspections_wide.join(rnk_df, how='outer') if not inspections_wide.empty else rnk_df

    # Step 4: Join base permits with inspections
    combined = permit_df.join(inspections_wide, how='left')

    # Step 5: Final column ordering
    inspection_cols = []
    for i in range(1, 9):
        inspection_cols += [f'inspt_status_{i}', f'inspt_date_{i}', f'inspt_notes_{i}']

    reordered_cols = permit_cols + ['inspt_status_last', 'inspt_date_last', 'inspt_notes_last'] + inspection_cols 
    combined = combined.reset_index()
    combined = combined[[col for col in reordered_cols if col in combined.columns]]

    return combined

def load_files(file_paths):
    """
    Concatenates multiple CSV/XLSX files if their column headers match in order.
    Drops fully duplicated rows in the final result.
    
    Args:
        file_paths (list of str): Paths to the files to be concatenated.
        
    Returns:
        pd.DataFrame: Cleaned DataFrame.
    """
    if len(file_paths) == 0:
        print("⚠️  No files provided.")
        return pd.DataFrame()
    
    if len(file_paths) == 1:
        file = file_paths[0]
        try:
            df = load_file_by_extension(file)
            print(f"✅ A single file with {len(df)} rows has been loaded.")
            return df.drop_duplicates()
        except Exception as e:
            print(f"❌ Error reading {file}: {e}")
            return pd.DataFrame()

    concatenated_df = pd.DataFrame()
    base_columns = None

    for file in file_paths:
        try:
            df = load_file_by_extension(file)

            if base_columns is None:
                base_columns = list(df.columns)
                concatenated_df = df
            elif list(df.columns) == base_columns:
                concatenated_df = pd.concat([concatenated_df, df], ignore_index=True)
                concatenated_df.dropna(how='all', inplace=True)
                print('Succesfully concatenated!')
                cleaned_df = concatenated_df.drop_duplicates()
                print(f"✅ Merged {len(file_paths)} files into a DataFrame with {len(cleaned_df)} rows.")
            else:
                print(f"⚠️  Header mismatch in file: {file}")
                print(f"    Expected: {base_columns}")
                print(f"    Found:    {list(df.columns)}")
        except Exception as e:
            print(f"❌ Error reading {file}: {e}")
    concatenated_df = concatenated_df.replace('NA', '')
    concatenated_df = concatenated_df.replace('NULL', '')
    return concatenated_df.drop_duplicates()

def load_file_by_extension(file_path):
    """
    Loads a file based on its extension.
    Supports .xlsx and .csv.

    Args:
        file_path (str): Path to the file.

    Returns:
        pd.DataFrame
    """
    ext = os.path.splitext(file_path)[-1].lower()
    if ext == '.xlsx':
        return pd.read_excel(file_path)
    elif ext == '.csv':
        return pd.read_csv(file_path)
    else:
        raise ValueError(f"Unsupported file type: {ext}")

def get_file_list(folder='raw', extensions=('xlsx', 'csv')):

    """
    Returns a list of file paths in the given folder that match the provided extensions.
    
    Args:
        folder (str): Subdirectory containing the files.
        extensions (tuple): File extensions to include (e.g., ('xlsx', 'csv')).

    Returns:
        list of str: Full paths to matching files.
    """
    return [
        os.path.join(folder, file)
        for file in os.listdir(folder)
        if file.lower().endswith(extensions)
    ]

def filter(df, column, values_to_keep):
    """
    Filters a DataFrame to keep only rows where the given column matches one or more specified values.
    Prints how many rows were removed and how many remain.

    Args:
        df (pd.DataFrame): The original DataFrame.
        column (str): The column to filter on.
        values_to_keep (str or list): Value or list of values to keep.

    Returns:
        pd.DataFrame: Filtered DataFrame.
    """
    original_len = len(df)

    # Convert single value to list
    if isinstance(values_to_keep, str):
        values_to_keep = [values_to_keep]

    # Filter and copy
    filtered_df = df[df[column].isin(values_to_keep)].copy()

    new_len = len(filtered_df)
    removed = original_len - new_len

    print(f"✅ Filtered DataFrame: {removed} rows removed, {new_len} rows remain with {column} == {values_to_keep}")
    return filtered_df

def assign_project_type(df):
    """
    Assigns or standardizes the 'project_type' column in the DataFrame.

    - If 'project_type' doesn't exist and 'DESCRIPTION' does, create it based on description content.
    - If 'project_type' exists, clean and map it using utils.proyect_type_mapping.

    Args:
        df (pd.DataFrame): The DataFrame to modify.

    Returns:
        pd.DataFrame: The modified DataFrame.
    """
    if 'project_type' not in df.columns and 'DESCRIPTION' in df.columns:
        df['project_type'] = np.where(
            df['DESCRIPTION'].isna() | (df['DESCRIPTION'].str.strip() == ''),
            '',
            np.where(
                df["DESCRIPTION"].str.contains("ess|bat|storage", case=False, na=False),
                'PV+ST',
                'PV'
            )
        )
        print("✅ 'project_type' column created based on 'DESCRIPTION' values.")
    
    elif 'project_type' in df.columns:
        df['project_type'] = (
            df['project_type']
            .astype(str)
            .str.strip()
            .str.lower()
            .map(project_type_mapping)
            .fillna(df['project_type'])  # keep original if not mapped
        )
        unique_vals = df['project_type'].dropna().unique()
        print(f"✅ 'project_type' column cleaned and standardized using mapping. ⚠️ Unique values: {list(unique_vals)} — Need to check these values!!")

    
    else:
        print("ℹ️  No action taken. 'project_type' column not present, and 'DESCRIPTION' column missing.")

    return df

def standardize_inspection_status_old(df):
    """
    Ensures inspection status columns exist, creates 'inspt_status_last' if missing,
    and standardizes all inspection status values using mapping.

    Args:
        df (pd.DataFrame): The DataFrame to modify.

    Returns:
        pd.DataFrame: The modified DataFrame.
    """

    # Define status columns
    status_columns = [f'inspt_status_{i}' for i in range(1, 11)]
    columns_to_map = ['inspt_status_last'] + status_columns

    # Ensure all numbered status columns exist
    for col in status_columns:
        if col not in df.columns:
            df[col] = ''

    # Create 'inspt_status_last' if missing
    if 'inspt_status_last' not in df.columns:
        def get_last_value(row, cols):
            for col in reversed(cols):
                value = row.get(col)
                if pd.notnull(value) and str(value).strip() != '':
                    return value
            return ''
        df['inspt_status_last'] = df.apply(lambda row: get_last_value(row, status_columns), axis=1)
        print("✅ 'inspt_status_last' column created based on last non-empty status.")

    # Standardize values using mapping
    for col in columns_to_map:
        if col in df.columns:
            df[col] = (
                df[col]
                .astype(str)
                .str.strip()
                .str.lower()
                .map(inspection_status_mapping)
                .combine_first(df[col])
            )
    unique_vals = df['inspt_status_last'].dropna().unique()
    print(f"✅ Inspection status columns standardized using mapping. ⚠️ Unique values in 'inspt_status_last': {list(unique_vals)} — Need to check these values!")

    return df

def assign_permit_status(df):
    """
    Standardizes or infers the 'permit_status' column in the DataFrame.

    - If 'permit_status' exists: normalize and map using utils.permit_status_mapping.
      Also update 'inspt_status_last' to 'passed' where appropriate.
    - If 'permit_status' is missing: infer it based on inspection status and submission date.

    Args:
        df (pd.DataFrame): The DataFrame to modify.

    Returns:
        pd.DataFrame: The modified DataFrame.
    """
    #if 'permit_status' in df.columns:
    if 'permit_status' in df.columns and df['permit_status'].replace('', pd.NA).notna().any():

        df['permit_status'] = (
            df['permit_status']
            .astype(str)
            .str.strip()
            .str.lower()
            .map(permit_status_mapping)
            .fillna(df['permit_status'])  # retain original if not mapped
        )
        print(f"✅ 'permit_status' column standardized. Check unique values: {df['permit_status'].dropna().unique()}")

        if 'inspt_status_last' in df.columns:
            condition = (
                (df['permit_status'] == 'finaled') &
                ((df['inspt_status_last'].isna()) | (df['inspt_status_last'] == ''))
            )
            df.loc[condition, 'inspt_status_last'] = 'passed'
            print(f"✅ 'inspt_status_last' updated to 'passed' where permit was 'finaled' and status was missing.")
    
    else:
        def infer_permit_status(row):
            status = row.get('inspt_status_last', '')
            submitted = row.get('permit_submission_date', '')

            # Condition 1: clearly passed
            if status == 'passed':
                return 'finaled'
            # Condition 2: clearly failed
            elif status in ['failed', 'canceled']:
                return 'issued'

            # Condition 3: no status but something was submitted and we have inspection signs
            elif status == '' and submitted != '':
                has_any_inspection = any(
                    str(row.get(col, '')).strip() != ''
                    for col in ['inspt_status_1', 'inspt_date_1', 'inspt_notes_1']
                )
                if has_any_inspection:
                    return 'issued'
                else:
                    return 'issued'  # still counts as submitted
            return ''

        df['permit_status'] = df.apply(infer_permit_status, axis=1)
        print("✅ 'permit_status' column inferred from inspection status and submission date.")

    return df

def standardize_format(df):
    """
    Standardizes the DataFrame in place:
    - Ensures all required columns (from utils.standard_columns) are present
    - Reorders columns
    - Drops duplicate rows
    - Merges inspections if duplicate permit_IDs exist
    - Adds 'inspt_failed_once' column
    - Saves the cleaned DataFrame to 'Clean.xlsx'
    """
    required_cols = standard_columns
    df['permit_ID'] = df['permit_ID'].astype(str).str.strip()

    # Add missing columns
    for col in required_cols:
        if col not in df.columns:
            df[col] = None

    # Reorder and copy to avoid SettingWithCopyWarning
    df = df[required_cols].copy()

    # Drop duplicate rows
    df.drop_duplicates(inplace=True)

    return df

def assign_solarAPP_or_traditional(df):
    """
    Assigns 'solarAPP_or_traditional' column based on:
    - 'solarAPP_ID' if available and 'solarAPP_or_traditional' is not already populated
    - Fallback to 'DESCRIPTION' if available and contains 'solarapp' keywords

    Args:
        df (pd.DataFrame): The DataFrame to modify.

    Returns:
        pd.DataFrame: The modified DataFrame.
    """
    # If the column already exists and has meaningful values, skip reassignment
    if 'solarAPP_or_traditional' in df.columns:
        existing = df['solarAPP_or_traditional'].astype(str).str.strip().replace('nan', '')
        if (existing != '').any():
            print("ℹ️ 'solarAPP_or_traditional' column already provided — no reassignment needed.")
            return df

    # If solarAPP_ID exists, assign based on it
    if 'solarAPP_ID' in df.columns:
        cleaned_ids = df['solarAPP_ID'].astype(str).str.strip()
        has_values = (cleaned_ids != '') & (cleaned_ids.str.lower() != 'nan')

        if has_values.any():
            df['solarAPP_or_traditional'] = np.where(
                has_values,
                'solarAPP',
                'traditional'
            )
            print("✅ 'solarAPP_or_traditional' column assigned based on 'solarAPP_ID'.")
            return df

        else:
            print("ℹ️ 'solarAPP_ID' exists but contains no usable values.")

    # If DESCRIPTION exists, fallback method (optional you can add here)
    if 'DESCRIPTION' in df.columns:
        description = df['DESCRIPTION'].astype(str).str.lower()
        df['solarAPP_or_traditional'] = np.where(
            description.str.contains('solarapp'),
            'solarAPP',
            'traditional'
        )
        print("✅ 'solarAPP_or_traditional' column assigned based on 'DESCRIPTION' field.")
        return df

    print("⚠️ Could not assign 'solarAPP_or_traditional'. No suitable fields found.")
    return df

def load_files(file_paths):
    """
    Concatenates multiple CSV/XLSX files if their column headers match in order.
    Drops fully duplicated rows in the final result.

    Args:
        file_paths (list of str): Paths to the files to be concatenated.

    Returns:
        pd.DataFrame: Cleaned DataFrame.
    """
    if len(file_paths) == 0:
        print("⚠️  No files provided.")
        return pd.DataFrame()

    if len(file_paths) == 1:
        file = file_paths[0]
        try:
            df = load_file_by_extension(file)
            print(f"✅ Loaded single file '{file}' with {len(df)} rows.")
            return df.drop_duplicates()
        except Exception as e:
            print(f"❌ Error reading {file}: {e}")
            return pd.DataFrame()

    concatenated_df = pd.DataFrame()
    base_columns = None
    total_rows_before_dedup = 0

    for file in file_paths:
        try:
            df = load_file_by_extension(file)
            print(f"📄 File '{file}' loaded with {len(df)} rows.")

            if base_columns is None:
                base_columns = list(df.columns)
                concatenated_df = df
            elif list(df.columns) == base_columns:
                concatenated_df = pd.concat([concatenated_df, df], ignore_index=True)
            else:
                print(f"⚠️  Header mismatch in file: {file}")
                print(f"    Expected: {base_columns}")
                print(f"    Found:    {list(df.columns)}")

        except Exception as e:
            print(f"❌ Error reading {file}: {e}")

    # Remove fully empty rows and drop duplicates
    concatenated_df.dropna(how='all', inplace=True)
    total_rows_before_dedup = len(concatenated_df)
    cleaned_df = concatenated_df.drop_duplicates()

    # Replace NULL by empty
    cleaned_df = cleaned_df.replace('NULL', '')
    cleaned_df = cleaned_df.replace('NA', '')


    print(f"\n✅ Finished merging {len(file_paths)} files.")
    print(f"📊 Total rows before deduplication: {total_rows_before_dedup}")
    print(f"📉 Rows after deduplication: {len(cleaned_df)}")

    return cleaned_df

def assign_last_inspection_fields(df):
    """
    Creates 'inspt_status_last', 'inspt_date_last', and 'inspt_notes_last'
    by taking the last non-empty value from their respective series of columns.
    Inserts them immediately before 'inspt_status_1'.
    """
    # Define the inspection columns to search
    status_cols = [f'inspt_status_{i}' for i in range(1, 11)]
    date_cols = [f'inspt_date_{i}' for i in range(1, 11)]
    notes_cols = [f'inspt_notes_{i}' for i in range(1, 11)]

    # Ensure all expected columns exist
    for col_list in [status_cols, date_cols, notes_cols]:
        for col in col_list:
            if col not in df.columns:
                df[col] = ''

    # Define helper to get last non-empty value
    def get_last_value(row, cols):
        for col in reversed(cols):
            value = row.get(col)
            if pd.notnull(value) and str(value).strip() != '':
                return value
        return ''

    # Create the _last columns if they don't already exist
    if 'inspt_status_last' not in df.columns:
        df['inspt_status_last'] = df.apply(lambda row: get_last_value(row, status_cols), axis=1)
        print("✅ 'inspt_status_last' column created from last non-empty status.")

    if 'inspt_date_last' not in df.columns:
        df['inspt_date_last'] = df.apply(lambda row: get_last_value(row, date_cols), axis=1)
        print("✅ 'inspt_date_last' column created from last non-empty date.")

    if 'inspt_notes_last' not in df.columns:
        df['inspt_notes_last'] = df.apply(lambda row: get_last_value(row, notes_cols), axis=1)
        print("✅ 'inspt_notes_last' column created from last non-empty notes.")
    if (
        'inspt_failed_once' not in df.columns or
        df['inspt_failed_once'].astype(str).str.strip().eq('').all()
    ):
        df = add_inspt_failed_once_column(df)
    else:
        print("ℹ️ 'inspt_failed_once' column already exists and has values — skipping.")


    # Move the 3 _last columns right before 'inspt_status_1'
    last_cols = ['inspt_failed_once','inspt_status_last', 'inspt_date_last', 'inspt_notes_last']
    cols = df.columns.tolist()

    for col in last_cols:
        if col in cols:
            cols.remove(col)

    try:
        insert_idx = cols.index('inspt_status_1')
    except ValueError:
        insert_idx = len(cols)  # fallback to end if 'inspt_status_1' not found

    for col in reversed(last_cols):
        cols.insert(insert_idx, col)

    # Reorder DataFrame
    df = df[cols]

    return df

def Merge_Inspections(df):
    """
    Reshapes inspection records into a wide format with one row per permit.
    The inspection data have to be originally stored in the first inspection. 
    For each permit_ID, up to 8 inspection attempts (status, date, notes) are pivoted into separate columns.

    Returns:
        pd.DataFrame: One row per permit with wide-format inspection columns.
    """

    # Step 1: Define columns related to permits
    permit_cols = [
        'solarAPP_or_traditional', 'AHJ', 'permit_ID', 'solarAPP_ID', 'address',
        'project_type', 'permit_status', 'permit_submission_date', 'permit_issuance_date'
    ]

    # Step 2: Extract permit-level data (drop duplicates based on permit_ID)
    permit_df = df.drop_duplicates(subset='permit_ID')[permit_cols].set_index('permit_ID')

    # Step 3: Prepare inspection data (only keep rows with a valid inspection date)
    inspections_df = df[['permit_ID', 'inspt_status_1', 'inspt_date_1', 'inspt_notes_1']].copy()
    inspections_df = inspections_df.dropna(subset=['inspt_date_1'])

    # Step 4: Sort inspections and rank them per permit
    inspections_df = inspections_df.sort_values(by=['permit_ID', 'inspt_date_1'])
    inspections_df['rnk'] = inspections_df.groupby('permit_ID').cumcount() + 1

    # Step 5: Pivot inspections into wide format (inspt_status_1, inspt_status_2, ..., inspt_notes_8)
    inspections_wide = pd.DataFrame()

    for i in range(1, 9):  # Support up to 8 inspections per permit
        rnk_df = inspections_df[inspections_df['rnk'] == i].set_index('permit_ID')[
            ['inspt_status_1', 'inspt_date_1', 'inspt_notes_1']
        ].rename(columns={
            'inspt_status_1': f'inspt_status_{i}',
            'inspt_date_1': f'inspt_date_{i}',
            'inspt_notes_1': f'inspt_notes_{i}'
        })

        # Join each ranked inspection attempt
        inspections_wide = inspections_wide.join(rnk_df, how='outer') if not inspections_wide.empty else rnk_df

    # Step 6: Join the permit data with the wide-format inspections
    combined = permit_df.join(inspections_wide, how='left')

    # Step 7: Flatten index and reorder columns
    inspection_cols = []
    for i in range(1, 9):
        inspection_cols += [f'inspt_status_{i}', f'inspt_date_{i}', f'inspt_notes_{i}']

    reordered_cols = permit_cols + inspection_cols
    combined = combined.reset_index()
    combined = combined[[col for col in reordered_cols if col in combined.columns]]

    return combined

def map_inspection_status(df):
    """
    Maps all 'inspt_status_1' to 'inspt_status_10' columns using inspection_status_mapping.
    Prints unique values across all mapped columns.
    Skips mapping if no inspection data is present.
    """
    columns_to_map = [f'inspt_status_{i}' for i in range(1, 11)]
    columns_to_map = [col for col in columns_to_map if col in df.columns]

    if not columns_to_map:
        print("ℹ️ No inspection status columns found.")
        return df

    has_inspections = df[columns_to_map].notna().any(axis=1).any()
    if not has_inspections:
        print("ℹ️ No inspections to be mapped.")
        return df

    # Map values
    for col in columns_to_map:
        df[col] = (
            df[col]
            .astype(str)
            .str.strip()
            .str.lower()
            .map(inspection_status_mapping)
            .combine_first(df[col])
        )

    # Collect all unique mapped values
    unique_vals = set()
    for col in columns_to_map:
        unique_vals.update(df[col].dropna().unique())

    print(f"✅ Inspection status columns mapped. ⚠️ Unique values across status_1–10: {list(unique_vals)} — Need to check these values!")

    return df

def final_save(df, filename='Clean.xlsx', sheet_name='Clean'):
    """
    Saves the given DataFrame to an Excel file.

    Args:
        df (pd.DataFrame): The DataFrame to save.
        filename (str): Output filename (default: 'Clean.xlsx').
        sheet_name (str): Sheet name inside the Excel file (default: 'Clean').
    """
    df.to_excel(filename, sheet_name=sheet_name, index=False)
    print(f"📁 Cleaned DataFrame saved to '{filename}'.")

def Do_Merge_Inspections_OLD(df):
    """
    Checks for duplicate permit_IDs and available inspection data.
    If both exist, merges inspection records using Merge_Inspections() and assigns *_last fields.

    Args:
        df (pd.DataFrame): Input DataFrame.

    Returns:
        pd.DataFrame: Modified DataFrame (merged if needed).
    """
    has_duplicates = df['permit_ID'].duplicated().any()
    has_inspections = df[['inspt_status_last', 'inspt_date_last', 'inspt_notes_last']].notna().any(axis=1).any()

    if has_duplicates and has_inspections:
        df = Merge_Inspections(df)
        df = assign_last_inspection_fields(df)
        print("🔁 Duplicate permit_IDs and inspections found — merging performed.")
        print("✅ Last inspection fields assigned. ")
    else:
        df= assign_last_inspection_fields(df)
        print("✅ No inspection merging needed — either no duplicates or no inspections.")
        print("✅ Last inspection fields assigned. ")

    return df

def assign_AHJ(df):
    """
    Assigns the current folder name as the 'AHJ' value for all rows in the DataFrame.

    Args:
        df (pd.DataFrame): The DataFrame to modify.

    Returns:
        pd.DataFrame: The modified DataFrame with 'AHJ' column added.
    """
    ahj_name = os.path.basename(os.getcwd())
    df['AHJ'] = ahj_name
    print(f"✅ 'AHJ' column assigned using current directory: '{ahj_name}'")
    return df

def standardize_inspection_status(df):
    """
    Ensures inspection status columns exist, creates 'inspt_status_last' if missing,
    replaces certain canceled inspections with 'failed' based on notes,
    and standardizes all inspection status values using mapping.

    Args:
        df (pd.DataFrame): The DataFrame to modify.

    Returns:
        pd.DataFrame: The modified DataFrame.
    """

    # -------- Step 0: Replace canceled inspection notes with 'failed' ----------
    canceled2failed = [
        "no access", "not onsite", "not on site", "not at home",
        "no answer", "not answer", "no one home", "nobody", "nobody answer",
        "no one onsite", "no one", "no one at home"
    ]
    notes_cols = ['inspt_notes_last'] + [f'inspt_notes_{i}' for i in range(1, 9)]

    modified_cells = 0
    for col in notes_cols:
        if col in df.columns:
            mask = df[col].astype(str).apply(lambda x: any(word in x.lower() for word in canceled2failed))
            modified_cells += mask.sum()
            df.loc[mask, col] = 'failed'
    print(f"🔁 Replaced {modified_cells} canceled notes with 'failed' in notes columns.")

    # -------- Step 1: Ensure all status columns exist ----------
    status_columns = [f'inspt_status_{i}' for i in range(1, 11)]
    columns_to_map = ['inspt_status_last'] + status_columns

    for col in status_columns:
        if col not in df.columns:
            df[col] = ''

    # -------- Step 2: Create 'inspt_status_last' if missing ----------
    if 'inspt_status_last' not in df.columns:
        def get_last_value(row, cols):
            for col in reversed(cols):
                value = row.get(col)
                if pd.notnull(value) and str(value).strip() != '':
                    return value
            return ''
        df['inspt_status_last'] = df.apply(lambda row: get_last_value(row, status_columns), axis=1)
        print("✅ 'inspt_status_last' column created based on last non-empty status.")

    # -------- Step 3: Apply mapping to standardize status values ----------
    for col in columns_to_map:
        if col in df.columns:
            df[col] = (
                df[col]
                .astype(str)
                .str.strip()
                .str.lower()
                .map(inspection_status_mapping)
                .combine_first(df[col])
            )

    unique_vals = df['inspt_status_last'].dropna().unique()
    print(f"✅ Inspection status columns standardized using mapping. ⚠️ Unique values in 'inspt_status_last': {list(unique_vals)} — Need to check these values!")

    return df

def Do_Merge_Inspections(df):
    """
    Checks for duplicate permit_IDs and available inspection data.
    If both exist, merges inspection records using Merge_Inspections() and assigns *_last fields.

    Args:
        df (pd.DataFrame): Input DataFrame.

    Returns:
        pd.DataFrame: Modified DataFrame (merged if needed).
    """
    has_duplicates = df['permit_ID'].duplicated().any()
    has_inspections = df[['inspt_status_last', 'inspt_date_last', 'inspt_notes_last']].notna().any(axis=1).any()

    if has_duplicates and has_inspections:
        df = Merge_Inspections(df)
        df = assign_last_inspection_fields(df)
        print("🔁 Duplicate permit_IDs and inspections found — merging performed.")
        print("✅ Last inspection fields assigned. ")
    else:
        df= assign_last_inspection_fields(df)
        print("✅ No inspection merging needed — either no duplicates or no inspections.")
        print("✅ Last inspection fields assigned. ")

    return df