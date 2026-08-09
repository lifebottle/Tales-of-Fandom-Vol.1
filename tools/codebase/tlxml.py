from dataclasses import dataclass, field

from lxml import etree as ET


@dataclass
class TlEntry:
    jp_text: str
    en_text: str | None
    notes: str | None
    id: int
    status: str
    voice_id: int | None = None
    speaker_id: int | None = None
    offsets: set[int] = field(default_factory=set)


def makeNode(root: ET._Element, n: TlEntry, id: int) -> ET._Element:
    entry = ET.SubElement(root, "Entry")

    if len(n.offsets) > 0:
        ET.SubElement(entry, "PointerOffset").text = ",".join(
            [str(x) for x in sorted(n.offsets)]
        )
    else:
        ET.SubElement(entry, "PointerOffset").text = None

    if n.voice_id is not None:
        ET.SubElement(entry, "VoiceId").text = n.voice_id

    ET.SubElement(entry, "JapaneseText").text = n.jp_text.replace("\r\n", "\n")
    ET.SubElement(entry, "EnglishText").text = n.en_text
    ET.SubElement(entry, "Notes").text = n.notes

    if n.speaker_id is not None:
        ET.SubElement(entry, "SpeakerId").text = str(n.speaker_id)

    ET.SubElement(entry, "Id").text = str(id)
    ET.SubElement(entry, "Status").text = n.status
    return entry


@dataclass
class TlXml:
    friend_name: str | None
    names: list[TlEntry]
    text: dict[str, list[TlEntry]]

    def makeXml(self) -> bytes:
        root = ET.Element("SceneText")

        if self.friend_name is not None:
            ET.SubElement(root, "FriendlyName").text = self.friend_name

        names_node = ET.SubElement(root, "Speakers")
        ET.SubElement(names_node, "Section").text = "Speaker"
        for n in self.names:
            makeNode(names_node, n, n.id)

        for name, items in self.text.items():
            text_node = ET.SubElement(root, "Strings")
            ET.SubElement(text_node, "Section").text = name
            for n in items:
                makeNode(text_node, n, n.id)

        return ET.tostring(root, encoding="UTF-8", pretty_print=True).replace(b"\n", b"\r\n")
