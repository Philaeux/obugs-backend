from fastapi import FastAPI
import uvicorn

from obugs.obugs import Obugs


app = FastAPI()
obugs = Obugs(app)

if __name__ == '__main__':
    uvicorn.run(app, host="0.0.0.0", port=5000)
