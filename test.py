import snapchat_dlp
import shutil

# try:
#     shutil.rmtree("ellenaabol")
# except Exception:
#     pass
snapper = snapchat_dlp.SnapchatDL(max_workers=1)
# snapper = snapchat_dlp.SnapchatDL()

snapper.download(username="ellenaabol")