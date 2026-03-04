"""
NexPlorer Universal Metadata Engine
Reads metadata from PDF, ePub, Office, Image (EXIF), Audio (ID3/FLAC), Video.
Writes/strips EXIF fields for images.
"""
from pathlib import Path
from nexplorer.core.constants import get_category

def read(fp: Path) -> dict:
    cat = get_category(fp.suffix)
    fn  = {
        "pdf":    _pdf,
        "ebook":  _epub,
        "office": _office,
        "image":  _image,
        "audio":  _audio,
        "video":  _video,
    }.get(cat, lambda p: {})
    base = {"name": fp.name, "size": fp.stat().st_size,
            "mtime": fp.stat().st_mtime, "category": cat}
    base.update(fn(fp))
    return base


def _pdf(fp):
    m = {}
    for lib in ("fitz","pypdf","pikepdf"):
        try:
            if lib == "fitz":
                import fitz
                doc = fitz.open(str(fp)); raw = doc.metadata or {}
                m = {"title":raw.get("title",""),"author":raw.get("author",""),
                     "pages":doc.page_count,"creator":raw.get("creator","")}
                doc.close()
            elif lib == "pypdf":
                from pypdf import PdfReader
                info = PdfReader(str(fp)).metadata or {}
                m = {"title":str(info.get("/Title","")),"author":str(info.get("/Author","")),
                     "pages":len(PdfReader(str(fp)).pages)}
            elif lib == "pikepdf":
                import pikepdf
                with pikepdf.open(str(fp)) as pdf:
                    di = pdf.docinfo
                    m = {"title":str(di.get("/Title","")),"author":str(di.get("/Author",""))}
            if m.get("title") or m.get("author"): return m
        except Exception: continue
    return m


def _epub(fp):
    try:
        import zipfile, xml.etree.ElementTree as ET
        ns = {"dc":"http://purl.org/dc/elements/1.1/"}
        with zipfile.ZipFile(str(fp)) as zf:
            cont = ET.fromstring(zf.read("META-INF/container.xml"))
            opf_path = cont.find(".//{urn:oasis:names:tc:opendocument:xmlns:container}rootfile").get("full-path")
            opf  = ET.fromstring(zf.read(opf_path))
            t    = opf.find(".//dc:title",ns)
            a    = opf.find(".//dc:creator",ns)
            lang = opf.find(".//dc:language",ns)
            return {"title":  (t.text or "").strip() if t else "",
                    "author": (a.text or "").strip() if a else "",
                    "language":(lang.text or "").strip() if lang else ""}
    except Exception: return {}


def _office(fp):
    ext = fp.suffix.lower(); m = {}
    try:
        if ext in {".docx",".doc"}:
            import docx; p = docx.Document(str(fp)).core_properties
            m = {"title":p.title or "","author":p.author or "","subject":p.subject or ""}
        elif ext in {".xlsx",".xls"}:
            import openpyxl; wb = openpyxl.load_workbook(str(fp),read_only=True,data_only=True)
            p = wb.properties; m = {"title":p.title or "","author":p.creator or ""}; wb.close()
        elif ext in {".pptx",".ppt"}:
            from pptx import Presentation; p = Presentation(str(fp)).core_properties
            m = {"title":p.title or "","author":p.author or "","slides": "?"}
    except Exception: pass
    return m


def _image(fp):
    m = {}
    try:
        from PIL import Image
        from PIL.ExifTags import TAGS, GPSTAGS
        img = Image.open(str(fp))
        m["width"], m["height"] = img.size
        m["mode"] = img.mode
        raw = img._getexif() or {}
        tag = {v:k for k,v in TAGS.items()}
        m["camera"]  = str(raw.get(tag.get("Model",0),"")).strip()
        m["make"]    = str(raw.get(tag.get("Make",0),"")).strip()
        m["date"]    = str(raw.get(tag.get("DateTime",0),"")).strip()
        m["iso"]     = str(raw.get(tag.get("ISOSpeedRatings",0),"")).strip()
        m["focal"]   = str(raw.get(tag.get("FocalLength",0),"")).strip()
        gps = raw.get(tag.get("GPSInfo",0),{})
        m["has_gps"] = bool(gps)
        img.close()
    except Exception: pass
    return m


def _audio(fp):
    try:
        from mutagen import File as MFile
        f = MFile(str(fp))
        if not f: return {}
        return {"title": str(f.get("title",[""])[0]),
                "artist":str(f.get("artist",[""])[0]),
                "album": str(f.get("album",[""])[0]),
                "duration_s": round(f.info.length,1) if hasattr(f,"info") else 0}
    except Exception: return {}


def _video(fp):
    try:
        import subprocess, json as _json
        out = subprocess.run(
            ["ffprobe","-v","quiet","-print_format","json",
             "-show_format","-show_streams", str(fp)],
            capture_output=True, text=True, timeout=10
        )
        data = _json.loads(out.stdout)
        fmt  = data.get("format",{})
        tags = fmt.get("tags",{})
        streams = data.get("streams",[])
        vstream = next((s for s in streams if s.get("codec_type")=="video"),{})
        return {
            "duration_s": round(float(fmt.get("duration",0)),1),
            "bitrate_kbps": round(int(fmt.get("bit_rate",0))/1000,1),
            "width":  vstream.get("width",0),
            "height": vstream.get("height",0),
            "codec":  vstream.get("codec_name",""),
            "title":  tags.get("title",""),
        }
    except Exception: return {}


def strip_exif(fp: Path, cfg: dict, dry_run: bool = False):
    """
    cfg keys:
      remove_gps, remove_device, remove_datetime,
      set_author (str|None), set_description (str|None), set_datetime (str|None)
    """
    if get_category(fp.suffix) != "image": return
    try:
        import piexif
        from PIL import Image
        img  = Image.open(str(fp))
        try:    exif = piexif.load(img.info.get("exif",b""))
        except: exif = {"0th":{},"Exif":{},"GPS":{},"1st":{}}
        changed = False
        if cfg.get("remove_gps"):          exif["GPS"]={};  changed=True
        if cfg.get("remove_device"):
            for t in [piexif.ImageIFD.Make,piexif.ImageIFD.Model,
                      piexif.ImageIFD.Software,piexif.ImageIFD.HostComputer]:
                exif["0th"].pop(t,None)
            changed = True
        if cfg.get("remove_datetime"):
            for t in [piexif.ImageIFD.DateTime]:
                exif["0th"].pop(t,None)
            for t in [piexif.ExifIFD.DateTimeOriginal,piexif.ExifIFD.DateTimeDigitized]:
                exif["Exif"].pop(t,None)
            changed = True
        if "set_author" in cfg:
            v = (cfg["set_author"] or "").encode()
            if v: exif["0th"][piexif.ImageIFD.Artist]=v
            else: exif["0th"].pop(piexif.ImageIFD.Artist,None)
            changed = True
        if "set_description" in cfg:
            v = (cfg["set_description"] or "").encode()
            if v: exif["0th"][piexif.ImageIFD.ImageDescription]=v
            else: exif["0th"].pop(piexif.ImageIFD.ImageDescription,None)
            changed = True
        if changed and not dry_run:
            img.save(str(fp), exif=piexif.dump(exif))
        img.close()
    except Exception: pass
