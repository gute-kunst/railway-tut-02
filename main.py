import fastapi
import vtk

print("hi")
from fastapi import FastAPI
from fastapi.responses import HTMLResponse

app = FastAPI()


@app.get("/")
async def root(response_class=HTMLResponse):
    html_content = """
    <html>
        <head>
            <title>Some HTML in here</title>
        </head>
        <body>
            <h1>Fancy Surface Reconstruction 🐝</h1>
        </body>
    </html>
    """
    return HTMLResponse(content=html_content, status_code=200)
