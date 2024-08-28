import warnings

from openpyxl import load_workbook
from states.definitions import OptimisationFlags

warnings.simplefilter(action="ignore", category=UserWarning)


def return_optimisation_flags(article, rewriting_process):
    flags = OptimisationFlags(
        flag_for_content_optimisation=False,
        flag_for_title_optimisation=True,
        flag_for_meta_desc_optimisation=True,
        flag_for_writing_optimisation=True,
    )

    match rewriting_process:
        case "optimisation":
            # Extracting article actions from Excel
            article_actions = article["Action"]

            # Checking for user annotated flags
            if "Send for title optimisation" not in article_actions:
                flags["flag_for_title_optimisation"] = False
            if "Send for meta description optimisation" not in article_actions:
                flags["flag_for_meta_desc_optimisation"] = False
            if "Send for content optimisation" not in article_actions:
                flags["flag_for_writing_optimisation"] = False

            # Checks if the content category is not diseases and conditions, as it will not require content optimisation if it's not.
            if article["content category"] != "diseases-and-conditions":
                flags["flag_for_content_optimisation"] = False

            return flags
        case "harmonisation":
            # Returning the other flags as true as this is a harmonisation flow
            return flags


def store_optimised_outputs(file_path, sheet_name, article_data):
    try:
        # Load the existing workbook
        workbook = load_workbook(file_path)
        if sheet_name in workbook.sheetnames:
            # Edit the existing sheet
            sheet = workbook[sheet_name]
            print(f"Editing existing sheet: {sheet_name}")
        else:
            # Create a new sheet
            sheet = workbook.create_sheet(title=sheet_name)
            print(f"Creating new sheet: {sheet_name}")

        sheet.append(article_data)

        # Save the workbook
        workbook.save(file_path)
        print(f"Workbook '{file_path}' saved successfully.")

    except FileNotFoundError:
        print(f"Workbook '{file_path}' not found")
