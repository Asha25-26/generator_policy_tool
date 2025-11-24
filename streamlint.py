import io
import numpy as np
import pandas as pd
import streamlit as st


MASTER_COLUMNS = [
    "Sl No", "Title", "Type of document", "Publication/Adoption Date", "Country",
    "Goals/objectives/vision statements", "Problems/challenges identified",
    "Calls for action/intervention", "Demands with pledges, commitment, or funding (Yes/No)",
    "Indicators of urgency/priority", "Type of demand", "Description of the specific Innovation(s)",
    "Type of Innovation", "CGIAR Impact Area(s)", "SDG Contribution",
    "Stakeholder groups involved", "Stakeholder group needs/demand/effective demand", "URL"
]

mapper_clim = {
    "Sl No": "Sl No",
    "Country": "Country",
    "Title": ["Type of document (Policy; Program; Implementation plans; strategic plans, etc)", "Policy"],
    "Type of document": "Policy Type \n(e.g., Policy, Strategy, Action Plan.)",
    "Publication/Adoption Date": ["Publication/Adoption Date", "Year of adoption"],
    "Thematic Focus (Brief description of the main themes or sectors covered (e.g., agriculture, forestry, gender, employment).)":
        "Thematic Focus (Brief description of the main themes or sectors covered (e.g., agriculture, forestry, gender, employment).)",
    "Goals/objectives/vision statements":
        "Objectives/Goals (Short summary of the stated aims or goals of the policy).",
    "Problems/challenges identified":
        "Remarks \n(Additional notes, such as challenges, reforms in progress, or relevance to global frameworks (e.g., SDGs).)",
    "Calls for action/intervention":
        "Key Provisions or Measures\nSummary of major policy actions or mechanisms introduced.",
    "Demands with pledges, commitment, or funding (Yes/No)":
        "Budget Allocation (if any) Indicate if there is any budget attached and its size or source.",
    "Description of the specific Innovation(s)":
        "Implementation Mechanism (Description of how the policy is implemented (e.g., through specific programs, agencies, funding mechanisms).)",
    "SDG Contribution":
        "Policy Linkages\nRelated policies or alignment with international frameworks (e.g., SDGs, UNFCCC).",
    "Stakeholder groups involved":
        "Implementation Agency \n(Ministry/departments/boards, etc..)",
    "URL": ["URL", "Link to Full Document"],
    "Implementation Agency (Ministry/departments/boards, etc..)":
        "Implementation Agency (Ministry/departments/boards, etc..)",
    "Indicators of urgency/priority": None,
    "Type of demand": None,
    "Type of Innovation": None,
    "CGIAR Impact Area(s)": None,
    "Stakeholder group needs/demand/effective demand": None,
}



def process_file(file_obj, mapper):
    """
    Loads an Excel file from a file-like object, maps columns, and performs transformations.
    Returns a standardized DataFrame or None if something goes wrong.
    """
    try:
        df = pd.read_excel(file_obj)
    except Exception as e:
        st.error(f"Error reading file: {e}")
        return None

    standardized_df = pd.DataFrame(columns=MASTER_COLUMNS)

    # Column mapping logic
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

    # Handle the Yes/No logic for budget / demands
    budget_col_name = mapper.get("Demands with pledges, commitment, or funding (Yes/No)")

    if isinstance(budget_col_name, list):
        budget_col_name = next((col for col in budget_col_name if col in df.columns), None)

    if budget_col_name and budget_col_name in df.columns:
        no_strings = [
            "not specified", "no exclusive", "not publicly specified",
            "not direct", "no dedicated budget"
        ]

        original_budget = df[budget_col_name]
        budget_data = original_budget.fillna("").astype(str).str.lower()

        standardized_df["Demands with pledges, commitment, or funding (Yes/No)"] = np.where(
            (original_budget.isna()) |
            (budget_data == "") |
            (budget_data.isin(no_strings)),
            "No",
            "Yes"
        )

    # Drop rows that are completely empty
    standardized_df.dropna(how='all', inplace=True)

    return standardized_df



def main():
    st.title("Policy Inventory Master Dataset Builder")
    st.write(
        "Upload one or more Excel (`.xlsx` / `.xls`) policy inventory files. "
        "They will be standardized using the predefined column mapping and combined into a master dataset."
    )

    # File uploader (multiple files allowed)
    uploaded_files = st.file_uploader(
        "Upload Excel file(s)",
        type=["xlsx", "xls"],
        accept_multiple_files=True
    )

    if uploaded_files:
        all_dfs = []

        for f in uploaded_files:
            st.write(f"Processing: **{f.name}**")
            processed_df = process_file(f, mapper_clim)

            if processed_df is not None and not processed_df.empty:
                all_dfs.append(processed_df)
                st.success(f"Successfully processed {len(processed_df)} rows from {f.name}.")
            else:
                st.warning(f"No usable data found in {f.name} (after mapping and cleaning).")

        if all_dfs:
            master_dataset = pd.concat(all_dfs, ignore_index=True)

            # Recalculate Sl No
            master_dataset["Sl No"] = range(1, len(master_dataset) + 1)

            st.subheader("Preview of Master Dataset")
            st.dataframe(master_dataset.head(50))  # show first 50 rows

            st.write(f"**Total rows in master dataset:** {len(master_dataset)}")

            # Prepare Excel in memory for download
            output = io.BytesIO()
            with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
                master_dataset.to_excel(writer, index=False, sheet_name="MASTER")
            output.seek(0)

            st.download_button(
                label="📥 Download MASTER_POLICY_DATASET.xlsx",
                data=output,
                file_name="MASTER_POLICY_DATASET.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
        else:
            st.info("No data was processed from the uploaded files.")
    else:
        st.info("Please upload one or more Excel files to begin.")


if __name__ == "__main__":
    main()

