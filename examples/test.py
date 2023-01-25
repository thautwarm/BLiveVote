from BLiveVote import App
import pathlib
import asyncio

dbfile = (pathlib.Path(__file__).parent / "danmaku.db").as_posix()
app = App(3012597, '支持', dbfile)
asyncio.get_event_loop().run_until_complete(app.run())
