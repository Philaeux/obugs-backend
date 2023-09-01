import asyncio
import tornado


class MainHandler(tornado.web.RequestHandler):
  def get(self):
    self.write("Hello, world")


class Obugs:

  def __init__(self):
    pass

  def start(self):
    asyncio.run(self.run())

  async def run(self):
    self.application = tornado.web.Application([
      (r"/", MainHandler),
    ])
    self.application.listen(8888)
    await asyncio.Event().wait()
