#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
RECEIPT PARSER - Practice 5: Python Regular Expressions
Author: Aldiyar Nurbekov
Purpose: Extract structured data from a pharmacy receipt using RegEx
"""

# Import required modules
import re      # Regular Expressions module for pattern matching
import json    # JSON module for saving structured data
import os      # OS module for file path handling


def parse_receipt(filename):
    """
    Main function to parse a receipt file.
    
    Args:
        filename (str): Path to the raw.txt receipt file
    
    Returns:
        dict: Dictionary containing all extracted receipt data
    """
    
    # ========================================================
    # STEP 0: GET FILE PATH AND READ CONTENT
    # ========================================================
    # Get the directory where this script is located
    # This ensures the script works regardless of where it's run from
    script_dir = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(script_dir, filename)
    
    # Try multiple encodings because Cyrillic text might be saved in different formats
    # UTF-8 is standard, but Windows-1251 is common for Russian/Kazakh text
    content = None
    for encoding in ['utf-8', 'windows-1251', 'cp1251']:
        try:
            with open(file_path, 'r', encoding=encoding) as f:
                content = f.read()  # Read entire file into one string
            if content and len(content) > 0:
                break  # Stop if we successfully read content
        except:
            continue  # Try next encoding if this one fails
    
    # Safety check: if file is still empty, stop execution
    if not content:
        print("❌ ERROR: Could not read file!")
        return
    
    # Create empty dictionary to store all extracted data
    result = {}
    
    # ========================================================
    # STEP 1: EXTRACT DATE AND TIME
    # ========================================================
    # Pattern explanation:
    # Время:           - Literal text "Время:" (Russian for "Time:")
    # \s*              - Zero or more whitespace characters (spaces/tabs)
    # (                - Start CAPTURING GROUP 1 (we extract this part)
    #   \d{2}          - Exactly 2 digits for day (e.g., "18")
    #   \.             - Literal dot "." (escaped because . normally means "any char")
    #   \d{2}          - Exactly 2 digits for month (e.g., "04")
    #   \.             - Literal dot "."
    #   \d{4}          - Exactly 4 digits for year (e.g., "2019")
    #   \s+            - One or more spaces (between date and time)
    #   \d{2}          - Exactly 2 digits for hour (e.g., "11")
    #   :              - Literal colon
    #   \d{2}          - Exactly 2 digits for minute (e.g., "13")
    #   :              - Literal colon
    #   \d{2}          - Exactly 2 digits for second (e.g., "58")
    # )                - End capturing group
    # Full match: "18.04.2019 11:13:58"
    dt_match = re.search(r'Время:\s*(\d{2}\.\d{2}\.\d{4}\s+\d{2}:\d{2}:\d{2})', content)
    
    # If match found, extract group(1), otherwise store "N/A"
    result['date_time'] = dt_match.group(1) if dt_match else "N/A"
    
    # ========================================================
    # STEP 2: EXTRACT PAYMENT METHOD AND AMOUNT
    # ========================================================
    # Pattern explanation:
    # Банковская карта:  - Literal text "Банковская карта:" (Bank card)
    # \s*              - Zero or more spaces
    # \n               - Newline character (amount is on next line!)
    # \s*              - Zero or more spaces (indentation)
    # (                - Start CAPTURING GROUP 1
    #   [\d\s]+        - One or more digits OR spaces (handles "18 009" with space)
    #   ,              - Literal comma (decimal separator in KZ/RU format)
    #   \d{2}          - Exactly 2 digits for cents (e.g., "00")
    # )                - End capturing group
    # Full match: "18 009,00"
    payment_match = re.search(r'Банковская карта:\s*\n\s*([\d\s]+,\d{2})', content)
    
    if payment_match:
        result['payment_method'] = 'Банковская карта'
        # Remove spaces: "18 009,00" → "18009,00" for easier processing
        result['payment_amount'] = payment_match.group(1).replace(' ', '')
    else:
        result['payment_method'] = 'Unknown'
        result['payment_amount'] = 'N/A'
    
    # ========================================================
    # STEP 3: EXTRACT GRAND TOTAL (ИТОГО)
    # ========================================================
    # Pattern explanation:
    # ИТОГО:           - Literal text "ИТОГО:" (Russian for "TOTAL:")
    # \s*              - Zero or more spaces
    # \n               - Newline (total amount is on separate line!)
    # \s*              - Zero or more spaces (indentation)
    # (                - Start CAPTURING GROUP 1
    #   [\d\s]+        - One or more digits OR spaces (handles "18 009")
    #   ,              - Literal comma (decimal separator)
    #   \d{2}          - Exactly 2 digits for cents
    # )                - End capturing group
    total_match = re.search(r'ИТОГО:\s*\n\s*([\d\s]+,\d{2})', content)
    
    if total_match:
        # Remove spaces for clean number: "18 009,00" → "18009,00"
        result['receipt_total'] = total_match.group(1).replace(' ', '')
    else:
        result['receipt_total'] = "N/A"
    
    # ========================================================
    # STEP 4: EXTRACT ALL PRICES FROM RECEIPT
    # ========================================================
    # This pattern finds ANY price-like number in the receipt
    # Pattern explanation:
    # \b               - Word boundary (ensures whole number match, not partial)
    # (                - Start CAPTURING GROUP 1
    #   \d{1,3}        - 1 to 3 digits (start: "1", "15", "154", "730")
    #   (?:            - Start NON-CAPTURING GROUP (group but don't extract)
    #     \s           - A space character (thousands separator)
    #     \d{3}        - Exactly 3 digits (e.g., "200" in "1 200")
    #   )*             - Non-capturing group repeats 0 or more times
    #                  - Handles: "154,00" OR "1 200,00" OR "7 330,00"
    #   ,              - Literal comma (decimal separator)
    #   \d{2}          - Exactly 2 digits for cents
    # )                - End capturing group
    # \b               - Word boundary at end
    # Examples matched: "154,00", "1 200,00", "7 330,00", "18 009,00"
    price_pattern = r'\b(\d{1,3}(?:\s\d{3})*,\d{2})\b'
    
    # re.findall() returns LIST of ALL matches (not just first one)
    # This finds ~83 matches: quantities, unit prices, item totals, grand total, etc.
    result['all_prices'] = re.findall(price_pattern, content)
    
    # ========================================================
    # STEP 5: EXTRACT PRODUCT ITEMS (THE COMPLEX PART)
    # ========================================================
    # Each product block in receipt looks like:
    #   1.                          ← Item number line
    #   Натрия хлорид 0,9%...      ← Product name (can be multi-line!)
    #   2,000 x 154,00             ← Quantity × Unit Price
    #   308,00                     ← Line total
    #   Стоимость                   ← Label (can ignore)
    #   308,00                     ← Line total repeated
    
    items = []  # List to store each product as a dictionary
    lines = content.split('\n')  # Split file into individual lines
    
    i = 0  # Index pointer to iterate through lines
    while i < len(lines):
        line = lines[i].strip()  # Remove leading/trailing whitespace
        
        # Check if this line is an item number: "1.", "2.", "20.", etc.
        # Pattern explanation:
        # ^            - Start of line
        # \d+          - One or more digits
        # \.           - Literal dot
        # $            - End of line
        if re.match(r'^\d+\.$', line):
            
            # Initialize variables for this item
            product_name = ""  # Accumulator for multi-line product names
            quantity = ""      # Will store quantity (e.g., "2,000")
            unit_price = ""    # Will store unit price (e.g., "154,00")
            item_total = ""    # Will store line total (e.g., "308,00")
            
            # Move to next line to start collecting product name
            i += 1
            
            # Loop to collect product name (may span multiple lines)
            while i < len(lines):
                name_line = lines[i].strip()
                
                # STOP CONDITION 1: Found quantity × price line
                # Check if line contains " x " (with spaces) AND has comma (for price format)
                # This is simpler and more reliable than complex regex
                if ' x ' in name_line and ',' in name_line:
                    # Split by " x " to separate quantity and unit price
                    # Example: "2,000 x 154,00" → ["2,000", "154,00"]
                    parts = name_line.split(' x ')
                    if len(parts) == 2:
                        # Clean and store quantity and unit price
                        # Remove spaces: "2,000" stays "2,000", "1 200,00" → "1200,00"
                        quantity = parts[0].strip().replace(' ', '')
                        unit_price = parts[1].strip().replace(' ', '')
                    i += 1  # Move past this line
                    break  # Exit the name collection loop
                
                # STOP CONDITION 2: Empty line or "Стоимость" label (skip these)
                if name_line == '' or name_line == 'Стоимость':
                    i += 1
                    continue  # Skip to next iteration
                
                # STOP CONDITION 3: Hit next item number (e.g., "2.")
                if re.match(r'^\d+\.$', name_line):
                    i -= 1  # Go back one line so main loop catches it
                    break  # Exit name collection loop
                
                # If none of above, this line is part of product name
                # Add to accumulator with space separator
                product_name += name_line + " "
                i += 1  # Move to next line
            
            # Clean up accumulated product name (remove extra spaces)
            product_name = product_name.strip()
            
            # Next line should be item total (e.g., "308,00")
            if i < len(lines):
                total_line = lines[i].strip()
                # Check if this line is just a price (the item total)
                # Pattern: digits/spaces + comma + 2 digits, nothing else
                if re.match(r'^[\d\s]+,\d{2}$', total_line):
                    item_total = total_line.replace(' ', '')
                    i += 1  # Move past total line
            
            # Add item to list ONLY if we have valid data
            # This prevents adding incomplete/corrupted entries
            if product_name and quantity and unit_price:
                items.append({
                    'name': product_name,
                    'quantity': quantity,
                    'unit_price': unit_price,
                    'total': item_total
                })
        else:
            # This line wasn't an item number, move to next line
            i += 1
    
    # Store items list and count in result dictionary
    result['items'] = items
    result['items_count'] = len(items)
    
    # ========================================================
    # STEP 6: CALCULATE TOTAL FROM INDIVIDUAL ITEMS
    # ========================================================
    # This verifies the receipt total by recalculating from items
    # Formula: SUM(quantity × unit_price) for all items
    calculated = 0.0  # Accumulator for calculated total
    
    for item in items:
        try:
            # Convert KZ/RU format "2,000" to Python float 2.000
            # Step 1: Replace comma with dot for Python: "2,000" → "2.000"
            qty = float(item['quantity'].replace(',', '.'))
            price = float(item['unit_price'].replace(',', '.'))
            # Multiply quantity × price and add to running total
            calculated += qty * price
        except ValueError:
            # If conversion fails (bad data), skip this item silently
            pass
    
    # Format calculated total BACK to KZ/RU format for display
    # Step 1: f"{calculated:,.2f}" formats with comma: "18009.00"
    # Step 2: .replace(',', 'X') temporarily swap comma: "18009X00"
    # Step 3: .replace('.', ',') change decimal to comma: "18009,00"
    # Step 4: .replace('X', ' ') add thousand separator: "18 009,00"
    result['calculated_total'] = f"{calculated:,.2f}".replace(',', 'X').replace('.', ',').replace('X', ' ')
    
    # ========================================================
    # STEP 7: PRINT FORMATTED OUTPUT TO CONSOLE
    # ========================================================
    print("=" * 60)
    print("🧾 PARSED RECEIPT DATA")
    print("=" * 60)
    print(f"📅 Date/Time:      {result['date_time']}")
    print(f"💳 Payment:        {result['payment_method']}")
    print(f"💰 Payment Amount: {result['payment_amount']} ₸")
    print(f"💰 Receipt Total:  {result['receipt_total']} ₸")
    print(f"🧮 Calculated:     {result['calculated_total']} ₸")
    print(f"📦 Items Count:    {result['items_count']}")
    
    print("\n📋 PRODUCTS:")
    # enumerate(items, 1) gives index starting at 1 + item dictionary
    for idx, item in enumerate(items, 1):
        print(f"  {idx}. {item['name']}")
        print(f"     {item['quantity']} × {item['unit_price']} ₸ = {item['total']} ₸")
    
    print(f"\n💵 All prices found ({len(result['all_prices'])})")
    
    # ========================================================
    # STEP 8: SAVE TO JSON FILE
    # ========================================================
    # json.dump() writes dictionary to file in JSON format
    # ensure_ascii=False preserves Cyrillic characters (otherwise they become \uXXXX)
    # indent=2 makes JSON file human-readable with nice formatting
    json_path = os.path.join(script_dir, 'parsed_receipt.json')
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    print(f"\n✅ Saved to: {json_path}")
    
    # Return result dictionary in case other code wants to use it
    return result


# ========================================================
# ENTRY POINT: Run the parser when script is executed directly
# ========================================================
# This check ensures code only runs when you execute this file,
# NOT when it's imported as a module in another script.
if __name__ == "__main__":
    parse_receipt('raw.txt')