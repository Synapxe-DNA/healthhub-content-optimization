import warnings

from openpyxl import load_workbook
from states.definitions import OptimisationFlags

# Filters out warnings
warnings.simplefilter(action="ignore", category=UserWarning)


def return_optimisation_flags(article, rewriting_process: str):
    """
    Returns the user flags for article rewriting. Article harmonisation will return all flags as True while article optimisation will be dependent on the user flags in the User Annotation Excel File

    Args:
        article (DataFrame): A DataFrame consisting of articles from the User Annotation Excel file.
        rewriting_process (str): A String indicating which rewriting process. It can either be "optimisation" or "harmonisation"

    Returns:
        flags (OptimisationFlags): A TypedDict with keys for each optimisation flag. The flags will either be True or False, depending on the user input in the User Annotation Excel file

    """
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


def store_optimised_outputs(file_path: str, sheet_name: str, article_data: str):
    """
    Stores the optimised outputs into an Excel file.

    Args:
        file_path (str): A String indicating the file path to the destination Excel file
        sheet_name (str): A String indicating the name of the sheet to store the output in
        article_data (str): A String storing the article data to be stored

    """
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
