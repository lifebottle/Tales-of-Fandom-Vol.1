"""
Yo, this script converts hex pointers to decimal and changes 'editing' to 'edited' in the xml files for translation.

This is because the current files are incompatible with the translation app.

If your files are working in the translation app, you don't need to run this.
"""

import re
import shutil
from pathlib import Path

def print_progress(i, maxval, item):
	if i < maxval:
		print(f"Converting {item} {i} of {maxval}", end="\r")
	else:
		print(f"Converting {item} {i} of {maxval}")

def has_xml_files(folder):
    return any(folder.glob("*.xml"))

def get_all_folders(basepath):
	folders = [
		d for d in basepath.iterdir()
		if d.is_dir() and has_xml_files(d)
	]
	return folders

def get_all_xml_files(folder):
	xml_files = list(folder.glob("*.xml"))
	return xml_files

def convert_ptr_to_int(ptr):
	if ptr.startswith("0x"):
		ptr_int = int(ptr, 16)
		return ptr_int
	else:
		print(f"Failed to convert {ptr} to int.")
		return ptr

def replace_ptrs_with_ints(xml):
	ptrs = re.findall(r"<PointerOffset>(0x[0-9a-fA-F]+)</PointerOffset>", xml)

	i = 1
	for ptr in ptrs:
		print_progress(i, len(ptrs), "ptr")

		ptr_int = convert_ptr_to_int(ptr)
		xml = xml.replace(
		    f"<PointerOffset>{ptr}</PointerOffset>",
		    f"<PointerOffset>{ptr_int}</PointerOffset>",
		)
		i += 1

	return xml

def replace_ids(xml):
	count = xml.count("<Id></Id>")
	new_xml = xml
	for i in range(0, count):
		print_progress(i, count, "Id")
		new_xml = new_xml.replace("<Id></Id>", f"<Id>{i}</Id>", 1)
	return new_xml

def fix_scenetext(xml):
	if "<SceneText>" in xml:
		xml = xml.replace(
			"<Section>Speaker</Section>",
			"<Section>Speaker</Section>\n  </Strings>\n  <Strings>\n    <Section>Main</Section>"
		)
	else:
		print("MenuText found. Skipping replacing Speaker with Main.")
	return xml


def update_all_xml(folder):
	files = get_all_xml_files(folder)
	for file in files:
		print(f"Processing {file.parent.name}/{file.name}...")
		xml = file.read_text(encoding="utf-8")

		new_xml = xml

		# this is where we replace teh xml
		#new_xml = xml.replace("<Status>Editing</Status>", "<Status>Edited</Status>")
		new_xml = new_xml.replace("<Status/>", "<Status>To Do</Status>")
		new_xml = new_xml.replace("<Status></Status>", "<Status>To Do</Status>")
		new_xml = new_xml.replace("<Notes> </Notes>", "<Notes/>")
		new_xml = new_xml.replace("<Notes></Notes>", "<Notes/>")
		new_xml = new_xml.replace("<EnglishText></EnglishText>", "<EnglishText/>")
		new_xml = new_xml.replace("<EnglishText> </EnglishText>", "<EnglishText/>")
		#new_xml = replace_ptrs_with_ints(new_xml)
		new_xml = replace_ids(new_xml)
		new_xml = fix_scenetext(new_xml)

		xml = file.write_text(new_xml, encoding="utf-8")

if __name__ == '__main__':
	if Path("2_translated").exists():
		basepath = Path("2_translated")
	else:
		basepath = Path(input("paste path to [2_translated] folder: "))

	#backup just incase
	backup_path = Path(basepath.parent / "2_translated_backup")

	if backup_path.exists():
		print("restoring backup...")
		shutil.copytree(backup_path, basepath, dirs_exist_ok=True)
	else:
		print("Backing up content to 2_translated_backup folder...")
		shutil.copytree(basepath, backup_path)

	# update bad xml in all files in all folders
	folders = get_all_folders(basepath)
	for folder in folders:
		print(f"Updating XML in {folder}...")
		update_all_xml(folder)
	print("Finished!")

	# delete the mfin backup?
	deletebackup = input("Delete backup folder? (y/n): ")
	if deletebackup == "y":
		shutil.rmtree(backup_path)
		print("Backup deleted.")
	else:
		print("Backup was not deleted.")

