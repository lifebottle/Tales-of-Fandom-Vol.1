from dataclasses import dataclass
from itertools import pairwise
from pathlib import Path

from fileio import FileIO
from pak import Pak
from tlxml import TlEntry, TlXml

FILE = Path("./0_disc/TOF.BIN")
OUT_FOLDER = Path("./1_extracted/TOF/")
SKIT_FILES_FOLDER = OUT_FOLDER / "SKITS"
XML_FOLDER = Path("./2_translated/story/")
SECTOR_SIZE = 0x800

NAMES = {
    100:  ("リッド・ハーシェル", "Reid Hershel"),
    200:  ("ファラ・エルステッド", "Farah Oersted"),
    300:  ("キール・ツァイベル", "Keele Zeibel"),
    400:  ("メルディ", "Meredy"),
    600:  ("チャット", "Chat"),
    500:  ("レイシス・フォーマルハウト", "Rassius Luine"),
    700:  ("フォッグ", "Max"),
    800:  ("クィッキー", "Quickie"),
    900:  ("アイラ", "Ayla"),
    1000: ("ワンダーシェフ", "Wonder Chef"),
    1100: ("プリムラ・ロッソ", "Primula Rosso"),
    1200: ("ウィリアム・ウォーベック", "William Warbeck"),
    1300: ("アン・ハ イダ ウェ イ", "Anne Hideaway"),
    1400: ("アルジェント", "Argento"),
    1500: ("ロエン・ラーモア", "Roen Lamoa"),
    1600: ("ヒューラ・ヴェルミリオン", "Hyura Vermillion"),
    1700: ("サンク・リザジュー", "Zank Lissajous"),
    1800: ("ジャッコ・リベラ", "Janko Ribera"),
    1900: ("アルサー・リトルトン", "Alther Littleton"),
    2000: ("ルナリア・バーンズ", "Lunaria Burns"),
    2100: ("キーファ・パッカード", "Kiefer Packard"),
    2200: ("スタン・エルロン", "Stahn Aileron"),
    2300: ("ルーティ・カトレット", "Rutee Katrea"),
    2400: ("リオン・マグナス", "Leon Magnus"),
    2500: ("フィリア・フィリス", "Philia Felice"),
    2600: ("リリス・エルロン", "Lilith Aileron"),
    2700: ("チェルシー・トーン", "Chelsea Torn"),
    2800: ("マリアン・フュステル", "Marian Fustel"),
    2900: ("ソーディアン ディムロス", "Swordian Dymlos"),
    3000: ("ソーディアン ディムロス（破損）", "Swordian Dymlos (Broken)"),
    3100: ("味 マ スタ ー1号", "Taste Master No. 1"),
    3200: ("クレス・アルベイン", "Cless Albane"),
    3300: ("ミント・アドネード", "Mint Adenade"),
    3400: ("アーチェ・クライン", "Arche Klein"),
    3500: ("クラース・Ｆ・レスター", "Claus F. Lester"),
    3700: ("アミィ・バークライト", "Ami Burklight"),
    3600: ("チェスター・バークライト", "Chester Burklight"),
    3800: ("アミィ・バークライト（幼少）", "Ami Burklight (Young-er)"),
    3900: ("クレス・アルベイン（幼少）", "Cless Albane (Young)"),
    4000: ("チェスター・バークライト（幼少）", "Chester Burklight (Young)"),
    4100: ("藤林 すず", "Suzu Fujibayashi"),
    4200: ("ミラルド・ルーン", "Milard Rune"),
    4300: ("ミゲール・アルベイン", "Miguel Albane"),
    4400: ("ゴーリ・シュタイン", "Goalie Stein"),
    4500: ("マリア・アルベイン", "Maria Albane"),
    4600: ("クレイトン", "Clayton"),
    4700: ("イライザ・シュタイン", "Elisa Stein"),
    4800: ("司祭", "Priest"),
    5100: ("イフリート", "Efreet"),
    5300: ("セルシウス", "Celsius"),
    5400: ("ドラ ゴン", "Dragon"),
    5500: ("トーマス・エルロン", "Thomas Aileron"),
    5600: ("Lady 1", "Lady 1"),
    5700: ("Male 1", "Male 1"),
    5800: ("Lady 2", "Lady 2"),
    5900: ("Captain", "Captain"),
    6000: ("Male 2", "Male 2"),
    6100: ("Male 3", "Male 3"),
    6200: ("Pink Haired girl", "Pink Haired girl"),
    6300: ("Male 4", "Male 4"),
    6400: ("番犬", "Watchdog"),
    6500: ("ビストロジャンバール司会者", "Bistro Chambard presenter"),
    6600: ("OBJ 1", "OBJ 1"),
    6700: ("OBJ 2", "OBJ 2"),
    6800: ("OBJ 3", "OBJ 3"),
    6900: ("OBJ 4", "OBJ 4"),
}


@dataclass
class SkitFile:
    id: int
    off: int


with FileIO(FILE) as f:
    header_size = f.read_uint32() * SECTOR_SIZE
    file_count = f.read_uint32()

    sectors = f.read_struct(f"<{file_count}I")
    for i, (curr, next) in enumerate(pairwise(sectors)):
        next *= SECTOR_SIZE
        curr *= SECTOR_SIZE
        
        blob = f.read_at(header_size + curr, next - curr)
        pak_t = Pak.get_pak_type(blob)

        folder = "BIN"

        if pak_t == 1:
            folder = "PAK1"
        elif pak_t == 3:
            folder = "PAK3"
        
        # print(f"{i:03d}.bin - {pak_t}")
        if i == 5:
            with FileIO(blob) as pk:
                count = pk.read_uint32()

                files: list[SkitFile] = []
                for i in range(count):
                    files.append(SkitFile(pk.read_uint32(), pk.read_uint32()))

                for sk0, sk1 in pairwise(files):
                    pos = sk0.off
                    size = sk1.off - pos
                    sblob = pk.read_at(pos, size)
                    # print(f"pos 0x{pos:08X} - size: 0x{size:08X}")

                    with FileIO(sblob) as sb:
                        _asset_count = sb.read_uint32(0x18)
                        _asset_off = sb.read_uint32(0x1C)
                        if _asset_count > 0:
                            sblob = sblob[:_asset_off + _asset_count * 4]
                        else:
                            sblob = sblob[:_asset_off]

                    # Create an new xml
                    xml = TlXml(
                        # friend_name=f"{sk0.id // 10000:02d}_{sk0.id % 10000:03d}",
                        friend_name=None,
                        names= [],
                        text={"Main Text": [] }
                    )

                    # print(xml.friend_name)

                    with FileIO(sblob) as sb:
                        string_off = sb.read_uint32(0x14)
                        sb.seek(0x20)
                        i = 0
                        j = 0
                        stack = []
                        last_param = -1
                        
                        last_name = 0
                        seen_names = {}
                        notes = None
                        while sb.tell() < string_off:
                            opcode = sb.read_uint32()
                            param = sb.read_uint32()

                            if opcode == 0x2 or opcode == 0x3:
                                stack.append(param)
                            elif opcode == 0x4:
                                if param == 1 or param == 2:
                                    stack.pop()
                            elif opcode == 0x11:
                                last_param = param
                            elif opcode == 0x12:
                                if param == 4 or param == 2 or param == 23:
                                    last_name = stack[-last_param]
                                    # print(stack[-last_param], sb.tell()-4)
                                elif param == 12:
                                    if stack[-last_param] == 0:
                                        last_name = None
                                elif param == 11:
                                    if stack[-last_param] == 2:
                                        notes = "System Message"
                                    elif stack[-last_param] == 8:
                                        notes = "Title Card"
                                    elif stack[-last_param] == 0:
                                        notes = None
                            elif opcode == 0x18 and param == 0 or opcode == 0x19 and param == 0:
                                notes = None
                            elif opcode == 0x1A and param == 0:
                                notes = "Choice text"
                            elif opcode == 0x17:
                                text = sb.read_string("sjis", string_off + param)
                                if notes:
                                    last_name = None
            
                                if text == "":
                                    last_name = None
                                    notes = "Empty Line"
                                    status = "Done"
                                    jp = text
                                elif text == "　":
                                    last_name = None
                                    notes = "Single JP space line"
                                    status = "Done"
                                    jp = text
                                else:
                                    jp = None
                                    status = "To Do"

                                if text.endswith("\n"):
                                    text = text[:-1] + "<nl>"

                                # Add a text entry
                                entry = TlEntry(
                                    jp_text=text,
                                    en_text=jp,
                                    notes=notes,
                                    id=i,
                                    status=status,
                                    voice_id=None,
                                    speaker_id=last_name
                                )
                                # Optionally add file offsets for the insertor to use
                                entry.offsets.add(sb.tell() - 4)
                                xml.text["Main Text"].append(entry)

                                if not notes and last_name is not None:
                                    seen_names[last_name] = True

                                i += 1

                        for id in seen_names:
                            # Add a name entry
                            names = NAMES.get(id, (f"NO_NAME_{id}", f"NO_NAME_{id}"))
                            entry = TlEntry(
                                jp_text=names[0],
                                en_text=names[1],
                                notes="Reference only",
                                id=id,
                                status="Done",
                            )
                            xml.names.append(entry)

                    # Save
                    skit_name = f"{sk0.id // 10000:02d}_{sk0.id % 10000:03d}"
                    out = XML_FOLDER / f"{skit_name}.xml"
                    with out.open("wb") as o:
                        o.write(xml.makeXml())

                    out_file = SKIT_FILES_FOLDER / f"{skit_name}.bin"
                    out_file.parent.mkdir(parents=True, exist_ok=True)
                    out_file.write_bytes(sblob)
        else:
            out_file = OUT_FOLDER / folder / f"{i:03d}.bin"
            out_file.parent.mkdir(parents=True, exist_ok=True)
            
            out_file.write_bytes(blob)
