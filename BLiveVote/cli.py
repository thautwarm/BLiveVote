from BLiveVote import App
import pathlib
import asyncio
import wisepy2
import os

def cmd(*, room: int, pattern: str, db: str = ""):
    dbfile = db or (pathlib.Path(os.getcwd()) / "danmaku.db").as_posix()
    app = App(room, pattern, dbfile)
    asyncio.get_event_loop().run_until_complete(app.run())

def main():
    wisepy2.wise(cmd)()
