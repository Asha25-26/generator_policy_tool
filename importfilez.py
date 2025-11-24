import pandas as pd
import numpy as np

MASTER_COLUMNS = [
    "Sl No","Title", "Type of document", "Publication/Adoption Date", "Country",
    "Goals/objectives/vision statements", "Problems/challenges identified",
    "Calls for action/intervention", "Demands with pledges, commitment, or funding (Yes/No)",
    "Indicators of urgency/priority", "Type of demand", "Description of the specific Innovation(s)",
    "Type of Innovation", "CGIAR Impact Area(s)", "SDG Contribution",
    "Stakeholder groups involved", "Stakeholder group needs/demand/effective demand", "URL"
]

mapper_clim = {
    "Sl No": "Sl No",
    "Country":"Country",
    "Title":[ "Type of document (Policy; Program; Implementation plans; strategic plans, etc)","Policy"],
    "Type of document": "Policy Type \n(e.g., Policy, Strategy, Action Plan.)",
    "Publication/Adoption Date": ["Publication/Adoption Date","Year of adoption"],
    "Thematic Focus (Brief description of the main themes or sectors covered (e.g., agriculture, forestry, gender, employment).)": "Thematic Focus (Brief description of the main themes or sectors covered (e.g., agriculture, forestry, gender, employment).)",
    "Goals/objectives/vision statements":"Objectives/Goals (Short summary of the stated aims or goals of the policy).",
    "Problems/challenges identified" : "Remarks \n(Additional notes, such as challenges, reforms in progress, or relevance to global frameworks (e.g., SDGs).)",
    "Calls for action/intervention": "Key Provisions or Measures\nSummary of major policy actions or mechanisms introduced.",
    "Demands with pledges, commitment, or funding (Yes/No)": "Budget Allocation (if any) Indicate if there is any budget attached and its size or source.",
    "Description of the specific Innovation(s)": "Implementation Mechanism (Description of how the policy is implemented (e.g., through specific programs, agencies, funding mechanisms).)",
    "SDG Contribution": "Policy Linkages\nRelated policies or alignment with international frameworks (e.g., SDGs, UNFCCC).",
    "Stakeholder groups involved": "Implementation Agency \n(Ministry/departments/boards, etc..)",
    "URL": ["URL","Link to Full Document"],
    "Implementation Agency (Ministry/departments/boards, etc..)": "Implementation Agency (Ministry/departments/boards, etc..)",
    "Indicators of urgency/priority": None, "Type of demand": None,
    "Type of Innovation": None, "CGIAR Impact Area(s)": None, 
    "Stakeholder group needs/demand/effective demand": None,
}

def process_file(filepath, mapper):
    """
    Loads a CSV, maps columns, and performs transformations.
    """
    try:
        df = pd.read_excel(filepath) 
    except Exception as e:
        print(f"Error reading {filepath}: {e}")
        return None

    standardized_df = pd.DataFrame(columns=MASTER_COLUMNS)

    for target_col, source_col in mapper.items():
        if isinstance(source_col, list):
            found_col = False
            for col_name in source_col:
                if col_name in df.columns:
                    standardized_df[target_col] = df[col_name]
                    found_col = True
                    break 
            if not found_col:
                standardized_df[target_col] = np.nan
                
        elif source_col and source_col in df.columns:
            standardized_df[target_col] = df[source_col]
            
        else:
            standardized_df[target_col] = np.nan

    budget_col_name = mapper.get("Demands with pledges, commitment, or funding (Yes/No)")
    
    if isinstance(budget_col_name, list):
        budget_col_name = next((col for col in budget_col_name if col in df.columns), None)

    if budget_col_name and budget_col_name in df.columns:
        no_strings = ['not specified', 'no exclusive', 'not publicly specified', 'not direct', 'no dedicated budget']
        
        budget_data = df[budget_col_name].astype(str).str.lower()
        
        standardized_df["Demands with pledges, commitment, or funding (Yes/No)"] = np.where(
            (budget_data.isna()) | (budget_data == '') | (budget_data.isin(no_strings)), 
            "No", 
            "Yes"
        )

    standardized_df.dropna(how='all', inplace=True)
    
    return standardized_df


files_to_process = [
    
    {"path": r"D:\Company_Ins\all\Mood\PolicyInventory_COL_CLIM_202507.xlsx", "mapper": mapper_clim},
    {"path": r"D:\Company_Ins\all\Mood\PolicyInventory_COL_DIET_202507.xlsx", "mapper": mapper_clim},
    {"path": r"D:\Company_Ins\all\Mood\PolicyInventory_COL_GEND_202507.xlsx", "mapper": mapper_clim},
    {"path": r"D:\Company_Ins\all\Mood\PolicyInventory_COL_NTRL_202507.xlsx", "mapper": mapper_clim},
    {"path": r"D:\Company_Ins\all\Mood\PolicyInventory_COL_POVT_202507.xlsx", "mapper": mapper_clim},
    {"path": r"D:\Company_Ins\all\Mood\Policies Inventory_Nigeria.xlsx", "mapper": mapper_clim},
    {"path": r"D:\Company_Ins\all\Mood\PolicyInventory_Bangladesh_CLIM.xlsx", "mapper": mapper_clim},
    {"path": r"D:\Company_Ins\all\Mood\PolicyInventory_Bangladesh_GEND.xlsx", "mapper": mapper_clim},
    {"path": r"D:\Company_Ins\all\Mood\PolicyInventory_Bangladesh_NTRL.xlsx", "mapper": mapper_clim},
    {"path": r"D:\Company_Ins\all\Mood\4. PolicyInventory_Bangladesh_DIET.xlsx", "mapper": mapper_clim},
    {"path": r"D:\Company_Ins\all\Mood\5. PolicyInventory_Bangladesh_POVT_20250713.xlsx", "mapper": mapper_clim},
    {"path": r"D:\Company_Ins\all\Mood\Policy Inventory_Ethiopia_CLIM.xlsx", "mapper": mapper_clim},
    {"path": r"D:\Company_Ins\all\Mood\Base de datos de políticas y programas COL.xlsx", "mapper": mapper_clim},
    {"path": r"D:\Company_Ins\all\Mood\Policies Inventory_Nigeria_by CG impact areas_Charity_Mesay.xlsx", "mapper": mapper_clim},
    {"path": r"D:\Company_Ins\all\Mood\Policy Inventory_Ethiopia_NHFS.xlsx", "mapper": mapper_clim},
    {"path": r"D:\Company_Ins\all\Mood\Inventory_IND_GEND b.xlsx", "mapper": mapper_clim},
    {"path": r"D:\Company_Ins\all\Mood\Inventory_IND_GEND a.xlsx", "mapper": mapper_clim}
]

all_dataframes = []

print("Starting dataset processing...")

for file_info in files_to_process:
    filepath = file_info["path"]
    mapper = file_info["mapper"]
    
    print(f"Processing {filepath}...")
    processed_df = process_file(filepath, mapper)
    
    if processed_df is not None:
        all_dataframes.append(processed_df)
        print(f"Successfully processed and standardized {len(processed_df)} rows.")


if all_dataframes:
    master_dataset = pd.concat(all_dataframes, ignore_index=True)
    
    master_dataset["Sl No"] = range(1, len(master_dataset) + 1)
    
    # Save the final file
    output_filename = "MASTER_POLICY_DATASET.xlsx"
    master_dataset.to_excel(output_filename, index=False)
    
    print(f"\n--- SUCCESS ---")
    print(f"All datasets combined into '{output_filename}'")
    print(f"Total rows in master dataset: {len(master_dataset)}")
else:
    print("\nNo data was processed. Please check file paths and errors.")