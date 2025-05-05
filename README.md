# Data Cleanser Tool

This project provides a compact and reusable Python notebook for cleaning and preprocessing raw data, specifically designed for cleaning the data for the SolarAPP+ performance review. 

## Project Files

- `cleanser.ipynb` – Main Jupyter Notebook with step-by-step data cleaning.
- `utils.py` – Contains reusable helper functions used in the notebook.
- `Things2Check.txt` – List of issues that need to be addressed. They wont be an issue most of the times but might be at specific situations. 

## How to set-up the working environment. 
You can use this project with either **Jupyter Notebook** or **Visual Studio Code (VS Code)** — both are great tools for running and editing Python code. If you're new to this kind of work, Jupyter is better for step-by-step exploration, while VS Code is better for full-script execution and modular development. I worked on VSCode. 

### 1. Set up the environment (optional but recommended)

Before running the project, it's recommended to install the required Python packages listed in `requirements.txt`. This ensures your environment has everything the code needs to run correctly.

To install the dependencies, open terminal and run:

pip install -r requirements.txt

Or download them one by one: 
    1. pip install pandas
    2. pip install numpy

### 2. Get the Project Files

You can start by either **cloning the repository** (if you are using Git) or **downloading the files manually**, if you are downloading them from SharePoint. 

- **Option A: Clone via Git (recommended for version control)**

   Open a terminal and run:

   git clone https://github.com/your-username/your-repo-name.git
   cd your-repo-name


### 3. Adapt the Cleanser Script to Your Working Environment

Before running the notebook, make sure the script knows where to find your custom utility functions.

Locate the following line in the first few cells of `cleanser.ipynb`:
sys.path.append('/Users/pbotin/Documents/SolarAPP/Scripts/DataCleaningProject')
and replace it whith the ones that matches the location of `utils.py`. 


## How to clean each specific AHJ

To clean data for a specific **AHJ (Authority Having Jurisdiction)**, follow these steps:

### Create a New Folder with the complete name of the AHJ

It is important to properly set the name of the AHJ with the state included (i.e. Golden CO), 
because it will be used by the script. 

In terminal:
mkdir Pima_County_AZ
cd Pima_County_AZ

### 2. Add a `raw/` Subfolder

Inside the AHJ folder, create a subfolder called `raw` and place all your raw input files there:

1) In terminal: mkdir raw
2) Download raw files from the SharePoint into the raw folder. 


### 3. Copy 'cleanser.ipynb' into the folder. 
In terminal:
cp ../cleanser.ipynb .


### 4. Adapt `cleanser.ipynb` to the Specific AHJ

This is the core of the cleaning process.

Go through the notebook **cell by cell**, verifying whether each step is appropriate for the AHJ you're working on. Some AHJs may require specific adjustments to formats, mappings, or file structures.

Whenever you encounter a function call, refer to `utils.py` to understand what the function does. All utility functions are documented with comments to clarify their purpose and behavior.

---

#### Step 1: Verify Module Imports

Ensure that all necessary Python modules are properly imported. This includes:
- `pandas`
- `numpy`
- `os`, `sys`
- `utils` (your custom helper module)

Adjust import paths if necessary depending on your working directory.

---

#### Step 2: Prepare the Raw Data for Loading

Depending on how your raw data is structured, you may need to make small adjustments before loading it into the notebook.

##### 🔹 Single File
- Check whether the file includes a proper header.
- If the header is offset (e.g., starts on the second row), adapt the file manually or call the load function yourself within the cell using `read_excel()` or `read_csv()` command modifying `header=` or `skiprows=`.

##### 🔹 Multiple Files
- If files contain the **same kind of information** but with **different column names**, standardize the headers so they match before merging.
- You may want to manually rename columns or use a mapping dictionary for automation.

#### Step 2: Map Columns to the Standard Template

In this step, you’ll rename columns from the raw files so they align with the **standardized column names** used throughout the project. This is essential to ensure that all downstream functions and logic run correctly.

It's common for different AHJs to use slightly different headers for the same type of data — for example, `Permit #`, `Permit Number`, or `PERMIT_ID` might all refer to the same field.

- Perform the renaming using the large, commented **`# Rename columns`** cell provided in the notebook.
- Modify this cell to reflect the specific column names present in your raw data.

> **Tip**: Open the raw Excel file side-by-side with the notebook. Use exploratory notebook cells (e.g., `df['column_name'].unique()`) to investigate the values and better understand which raw column corresponds to which standardized field.

This approach is especially helpful when dealing with inconsistent or unclear column names across different jurisdictions.

#### Step 3: Filter Inspections

Not all inspection records are relevant for the analysis. In this step, we selectively keep only the inspections of interest — for example, `"Electric Final"`, `"Permit Final"`, or other specific types defined by the project logic.

- Use the provided commented cell in the notebook that includes a call to `utils.filter()`.
- This function is designed to filter the inspection records according to predefined criteria.

Example usage:
df = utils.filter(df, 'Inspection Type', ['Solar Final', 'Solar Rough'])  # multiple values


#### Step 4: Run the Final Cleaning Cell

The last cell in the notebook calls all the cleaning functions in a specific order. This cell is designed to:

- Automatically clean and standardize the dataset
- Apply mapping logic and formatting
- Save the final cleaned output to a file named `Clean.xlsx`

While this step should produce a clean, ready-to-use dataset, **it is critical to review the output carefully** and verify that all values have been correctly assigned, formatted, and transformed.

Some AHJs may introduce unexpected issues or data variations. In those cases:

- You may need to edit the logic inside this final cell.
- You might also need to modify the helper functions in `utils.py`.

> **Note**: Some known issues have already been documented in `Things2Check.txt`. As you process more AHJs, you’ll likely encounter new edge cases, these will help improve the robustness of the script over time.

#### Step 5: Save the Cleaned File

Once you’ve completed a **detailed review** of the cleaned data and confirmed that all fields have been properly processed, you should save the output file with the **name of the AHJ** (e.g., `Pima_County_AZ.xlsx`) into a centralized `/clean` directory. This folder should be located outside of the AHJ-specific workspace, as a general repository for all cleaned AHJ data.

### Concatenate All Files

Once all individual AHJs have been cleaned and saved into the `/clean` folder, you can merge them into a single consolidated dataset.

#### Steps:

1. **Copy the Concatenation Notebook**

   Copy `concatenate.ipynb` into either:
   - The `/clean` folder (where all cleaned AHJ files are stored), **or**
   - The parent directory, and update the script’s file path references accordingly.

#### 2. **Run the Notebook Cells**

The notebook is structured to perform the following steps:

1. **Concatenate Files**
   - Combines all Excel files in the `/clean` folder into a single DataFrame.
   - Saves the result as `Clean_Merged.xlsx`.
   - Prints out any errors that occurred during concatenation (e.g., missing columns or file issues).

2. **Standardize Date Formats**
   - Ensures all date columns follow a consistent format (e.g., `YYYY-MM-DD`).
   - You can choose to include this logic in the first cell for automation.

3. **Print Summary**
   - Displays a quick summary of the final merged dataset: number of rows, number of AHJs, column consistency, and more.

---

🎉 You’re almost there!

Now it’s time to give the merged dataset a **final, very detailed review** — check for formatting consistency, missing values, or any AHJ-specific quirks that may have slipped through.

Once everything looks good, go ahead and **save it as your final cleaned dataset**. This file will serve as the foundation for all downstream analysis, reporting, or visualization.

Well done!
