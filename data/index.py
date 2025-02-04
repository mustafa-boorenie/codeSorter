import pandas as pd
import openai
from dotenv import load_dotenv  # Added python-dotenv import

# --- Configuration ---
input_file = './data/codesTable.csv'      # Path to your Excel file
output_file = './output/output.csv'    # Path for the updated Excel file
load_dotenv() # loads dotenv files

# Load the OpenAI API key from an environment variable.
openai.api_key = os.getenv("API_KEY")
if openai.api_key is None:
    raise ValueError("Please set the OPENAI_API_KEY environment variable with your OpenAI API key.")

# Allowed categories for verification
ALLOWED_CATEGORIES = {
    "Visits",
    "Imaging",
    "Specialised treatment",
    "Labs",
    "Surgical Procedures",
    "Infusions",
    "Non-surgical Procedures",
    "Specialized Services",
    "Specialized Investigations",
    "General testing"
}

# --- Read the Excel File ---
try:
    df = pd.read_excel(input_file, engine='openpyxl')
except Exception as e:
    print(f"Error reading {input_file}: {e}")
    exit(1)

# Check that the expected first column exists; here we assume it's named "Item"
if 'Item' not in df.columns:
    print("The expected column 'Item' was not found in the Excel file.")
    exit(1)

# --- Define the Logic for Category Assignment Using OpenAI ---
def assign_category(item):
    """
    Uses OpenAI to determine the category for a given CPT/E&M code.
    """
    try:
        item_str = str(item)
    except Exception:
        return "Unknown"
    
    # Create a prompt for OpenAI with clear instructions
    prompt = (
        f"Categorize the following CPT/E&M code into one of these categories:\n"
        "Visits, Imaging, Specialised treatment, Labs, Surgical Procedures, Infusions, "
        "Non-surgical Procedures, Specialized Services, Specialized Investigations, General testing.\n"
        "Only provide the category name as your response.\n\n"
        f"Code: {item_str}"
    )
    
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",  # Using the newer GPT-4 model
            messages=[
                {"role": "system", "content": "You are an assistant that categorizes medical procedure codes."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.0,
            max_tokens=10
        )
        category = response.choices[0].message.content.strip()
        
        # Verify that the returned category is one of the allowed ones
        if category not in ALLOWED_CATEGORIES:
            # Optionally, log unexpected responses
            print(f"Warning: Received unexpected category '{category}' for code '{item_str}'.")
            return "Other"
        return category
    except Exception as e:
        print(f"Error categorizing code '{item_str}': {e}")
        return "Error"

# --- Apply the Function to Create a New Column ---
# This creates (or replaces) a column called 'Category' based on the 'Item' column.
df['Category'] = df['Item'].apply(assign_category)

# --- Write the Updated DataFrame Back to Excel ---
try:
    df.to_excel(output_file, index=False, engine='openpyxl')
    print(f"Updated Excel file saved to {output_file}")
except Exception as e:
    print(f"Error writing to {output_file}: {e}")