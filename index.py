import os                
import pandas as pd
import openai
from dotenv import load_dotenv  # Added python-dotenv import

load_dotenv()  # loads .env file

# Load the OpenAI API key from an environment variable.
openai.api_key = os.getenv("API_KEY")
if openai.api_key is None:
    raise ValueError("Please set the API_KEY environment variable with your OpenAI API key.")

# Allowed categories for verification
ALLOWED_CATEGORIES = {
    "Visits",
    "Imaging",
    "Specialised treatment",
    "Labs",
    "Hospital Procedures",
    "Infusions",
    "In-office Procedures",
    "Specialized Services",
    "Specialized Investigations",
    "General testing"
}

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

# --- Configuration ---
input_file = './data/codesTable.csv'      # Path to your CSV file
output_file = './output/output.csv'         # Path for the updated output file

# --- Read the CSV File ---
try:
    df = pd.read_csv(input_file)  # Changed from read_excel to read_csv
except Exception as e:
    print(f"Error reading {input_file}: {e}")
    exit(1)

# Check that the expected column exists; here we expect it's named "CPT_Code"
if 'CPT_Code' not in df.columns:
    print("The expected column 'CPT_Code' was not found in the CSV file.")
    exit(1)

# Rename 'CPT_Code' to 'Item' so we can use it with our function
df.rename(columns={'CPT_Code': 'Item'}, inplace=True)

# Now you can safely use 'Item'
df['Category'] = df['Item'].apply(assign_category)

# --- Write the Updated DataFrame Back to CSV ---
try:
    df.to_csv(output_file, index=False)  # Writing output as CSV
    print(f"Updated file saved to {output_file}")
except Exception as e:
    print(f"Error writing to {output_file}: {e}")