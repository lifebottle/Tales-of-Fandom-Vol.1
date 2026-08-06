import xml.etree.ElementTree as ET
import xml.dom.minidom
import os
import re
import sys

def convert_multiline_txt_to_xml(input_filename, output_filename):
    if not os.path.exists(input_filename):
        print(f"Error: {input_filename} not found.")
        return

    # 1. Parse the text file into memory
    entries = []
    current_pointer = None
    current_text = []

    with open(input_filename, 'r', encoding='utf-8') as file:
        for line in file:
            stripped_line = line.strip()
            
            # Forgiving regex for accidental extra spaces around the hex pointer
            match = re.match(r"^\s*(0?x[0-9a-fA-F]+):\s*$", stripped_line)
            
            if match:
                # If we already have a pointer, save its text before starting the next one
                if current_pointer:
                    entries.append({
                        "pointer": current_pointer,
                        "text": '\n'.join(current_text).strip()
                    })
                
                pointer = match.group(1)
                # Ensure pointers strictly start with 0x
                if pointer.startswith('x'):
                    pointer = '0' + pointer
                
                current_pointer = pointer
                current_text = [] 
                
            elif stripped_line:
                # Append non-empty lines to the current text block
                current_text.append(stripped_line)

    # Catch the very last entry in the file
    if current_pointer:
        entries.append({
            "pointer": current_pointer,
            "text": '\n'.join(current_text).strip()
        })

    # 2. Set up the XML structure
    root = ET.Element("SceneText")
    ET.SubElement(root, "FriendlyName")
    speakers = ET.SubElement(root, "Speakers")
    ET.SubElement(speakers, "Section")

    # 3. Populate the XML (WITH THE TWEAK APPLIED)
    # Using enumerate to automatically generate an ID number starting from 0
    for index, data in enumerate(entries):
        entry = ET.SubElement(speakers, "Entry")
        
        ET.SubElement(entry, "PointerOffset").text = data["pointer"]
        ET.SubElement(entry, "JapaneseText").text = data["text"]
        
        ET.SubElement(entry, "EnglishText")
        ET.SubElement(entry, "Notes") 
        
        # Here is where the data is populated into Id and Status
        ET.SubElement(entry, "Id").text = str(index)
        ET.SubElement(entry, "Status").text = "To Do"

    # 4. Format the XML
    xml_string = ET.tostring(root, encoding='utf-8')
    parsed_xml = xml.dom.minidom.parseString(xml_string)
    pretty_xml = parsed_xml.toprettyxml(indent="  ")

    # 5. FORCE EXACT TAG FORMATTING
    # This prevents the parser from collapsing these tags into <Tag/>
    tags_to_expand = ["FriendlyName", "Section", "EnglishText", "Id", "Status"]
    for tag in tags_to_expand:
        # Catch both potential parser formatting styles
        pretty_xml = pretty_xml.replace(f"<{tag}/>", f"<{tag}></{tag}>")
        pretty_xml = pretty_xml.replace(f"<{tag} />", f"<{tag}></{tag}>")
        
    # Ensure Notes remains perfectly self-closing as requested
    pretty_xml = pretty_xml.replace("<Notes></Notes>", "<Notes/>")

    # 6. Save the file
    with open(output_filename, 'w', encoding='utf-8') as output_file:
        output_file.write(pretty_xml)
        
    print(f"Success! Converted {len(entries)} entries.")
    print(f"Saved as: {output_filename}")


# --- DRAG AND DROP LOGIC ---
if __name__ == "__main__":
    if len(sys.argv) > 1:
        input_path = sys.argv[1]
        base_name = os.path.splitext(input_path)[0]
        output_path = base_name + ".xml"
        
        print(f"Processing: {input_path}")
        convert_multiline_txt_to_xml(input_path, output_path)
    else:
        print("Error: No input file detected.")
        print("Please drag and drop a .txt file directly onto this script.")

    # Keep the window open so you can confirm it worked
    input("\nPress Enter to close this window...")