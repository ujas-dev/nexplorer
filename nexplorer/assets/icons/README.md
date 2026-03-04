# NexPlorer Icons

Place the following icon files here before building:

| File | Used for | Size |
|---|---|---|
| `nexplorer.ico` | Windows .exe icon | 256x256 ICO |
| `nexplorer.icns` | macOS .app icon bundle | ICNS format |
| `nexplorer.png` | Linux taskbar / about dialog | 256x256 PNG |

## Quick way to generate all three from a single PNG:

```bash
# From a 1024x1024 source PNG:
pip install pillow

python -c "
from PIL import Image
img = Image.open('source_1024.png')

# PNG 256x256
img.resize((256,256)).save('nexplorer.png')

# ICO (multiple sizes embedded)
sizes = [(16,16),(32,32),(48,48),(64,64),(128,128),(256,256)]
img.save('nexplorer.ico', sizes=sizes)

print('Done')
"

# macOS ICNS (requires iconutil on macOS):
mkdir NexPlorer.iconset
sips -z 16 16     source_1024.png --out NexPlorer.iconset/icon_16x16.png
sips -z 32 32     source_1024.png --out NexPlorer.iconset/icon_16x16@2x.png
sips -z 32 32     source_1024.png --out NexPlorer.iconset/icon_32x32.png
sips -z 64 64     source_1024.png --out NexPlorer.iconset/icon_32x32@2x.png
sips -z 128 128   source_1024.png --out NexPlorer.iconset/icon_128x128.png
sips -z 256 256   source_1024.png --out NexPlorer.iconset/icon_128x128@2x.png
sips -z 256 256   source_1024.png --out NexPlorer.iconset/icon_256x256.png
sips -z 512 512   source_1024.png --out NexPlorer.iconset/icon_256x256@2x.png
sips -z 512 512   source_1024.png --out NexPlorer.iconset/icon_512x512.png
sips -z 1024 1024 source_1024.png --out NexPlorer.iconset/icon_512x512@2x.png
iconutil -c icns NexPlorer.iconset -o nexplorer.icns
```
