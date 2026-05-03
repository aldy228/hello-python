"""
json.py - JSON Parsing Exercise

Task: Parse sample-data.json and output interface status in formatted table.

Expected output format:
Interface Status
================================================================================
DN                                                 Description           Speed    MTU  
-------------------------------------------------- --------------------  ------  ------
topology/pod-1/node-201/sys/phys-[eth1/33]                              inherit   9150 
"""

import json
import os


def load_sample_data(filename="sample-data.json"):
    """
    Load and parse JSON file
    
    Parameters:
    filename (str): Path to JSON file
    
    Returns:
    dict: Parsed JSON data or None if error
    """
    try:
        # Get directory where this script is located
        script_dir = os.path.dirname(os.path.abspath(__file__))
        filepath = os.path.join(script_dir, filename)
        
        with open(filepath, "r", encoding="utf-8") as file:
            data = json.load(file)  # Parse JSON string to Python dict
        return data
    except FileNotFoundError:
        print(f"❌ Error: {filename} not found")
        return None
    except json.JSONDecodeError as e:
        print(f"❌ Error parsing JSON: {e}")
        return None


def format_interface_status(data):
    """
    Format and print interface data as table
    
    Parameters:
    data (dict): Parsed JSON data with 'imdata' key containing interfaces
    """
    if not data or "imdata" not in data:
        print("No interface data found")
        return
    
    # Print header
    print("Interface Status")
    print("=" * 80)
    print(f"{'DN':<50} {'Description':<20} {'Speed':<8} {'MTU':<6}")
    print("-" * 50 + " " + "-" * 20 + " " + "-" * 8 + " " + "-" * 6)
    
    # Extract and print each interface
    # Data structure: data["imdata"] is a list of dicts
    # Each dict has "l1PhysIf" key with interface attributes
    for item in data.get("imdata", []):
        if "l1PhysIf" in item:
            attrs = item["l1PhysIf"]["attributes"]
            
            # Extract fields with defaults for missing values
            dn = attrs.get("dn", "N/A")           # Distinguished Name
            descr = attrs.get("descr", "")         # Description (often empty)
            speed = attrs.get("speed", "inherit")  # Speed or "inherit"
            mtu = attrs.get("mtu", "9150")         # MTU value
            
            # Print formatted row
            print(f"{dn:<50} {descr:<20} {speed:<8} {mtu:<6}")


def main():
    """Main function to run JSON exercise"""
    print("\n=== JSON Exercise: Interface Status ===\n")
    
    # Load data from file
    data = load_sample_data()
    
    if data:
        # Format and display
        format_interface_status(data)
    
    print("\n✓ JSON parsing complete\n")


if __name__ == "__main__":
    main()