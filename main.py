from __future__ import annotations

import time
import json
import asyncio
from typing import Type, cast
from functools import wraps

import structlog
import selenium_stealth
from pydantic import BaseModel
from bottle import Bottle, request, response
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.bidi.network import Network, Request

from models import ErrorResponse, GetNetworkUrlsRequest, GetNetworkUrlResponse

structlog.configure(
    processors=[
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.JSONRenderer()
    ]
)

log = structlog.get_logger()

app = Bottle()

def typed_endpoint(request_model: Type[BaseModel], response_model: Type[BaseModel]):
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            try:
                # Parse and validate JSON body
                data = request.json
                model = request_model(**(data or {})) # type: ignore
            except Exception as e:
                response.status = 400
                err = ErrorResponse(error="Invalid request", details=str(e))
                return err.model_dump()

            try:
                result = fn(model, *args, **kwargs)
                # Ensure proper typing on return
                if not isinstance(result, response_model):
                    result = response_model(**result)
                response.content_type = "application/json"
                return result.model_dump()
            except Exception as e:
                response.status = 500
                err = ErrorResponse(error="Internal error", details=str(e))
                return err.model_dump()
        return wrapper
    return decorator

@app.hook('before_request')
def log_request():
    request.environ['start_time'] = time.time()
    log.info("request_start", method=request.method, path=request.path)

@app.hook('after_request')
def log_response():
    duration = time.time() - request.environ['start_time']
    log.info(
        "request_end",
        method=request.method,
        path=request.path,
        status=response.status_code,
        duration_ms=round(duration * 1000, 2)
    )

def construct_options() -> webdriver.ChromeOptions:
    options = webdriver.ChromeOptions()
    options.add_argument("start-maximized")

    options.add_argument("--headless")
    options.enable_bidi = True

    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option('useAutomationExtension', False)
    return options

def construct_driver(stealth: bool = True) -> webdriver.Chrome:
    options = construct_options()
    driver = webdriver.Chrome(options=options)

    if stealth:
        selenium_stealth.stealth(driver,
                languages=["en-US", "en"],
                vendor="Google Inc.",
                platform="Win32",
                webgl_vendor="Intel Inc.",
                renderer="Intel Iris OpenGL Engine",
                fix_hairline=True,
                )

    return driver

def store_urls(request: Request, url_list: list[str]):
    url = cast(str, request.url)
    if url.startswith("data:"): # continue_request is not supported for data URLs at this time
        return
    
    log.info(f"Storing URL: {url}")
    url_list.append(url)
    request.continue_request()

@app.post("/get_network_urls") # type: ignore
@typed_endpoint(GetNetworkUrlsRequest, GetNetworkUrlResponse)
def get_network_urls(req: GetNetworkUrlsRequest) -> GetNetworkUrlResponse:
    request_urls = []
    driver = construct_driver()
    driver.network.add_request_handler("before_request", lambda request: store_urls(request, request_urls))
    driver.browsing_context.navigate(
        url=req.url, context=driver.current_window_handle
    )
    time.sleep(req.timeout)
    driver.quit()
    return GetNetworkUrlResponse(urls=request_urls)

def main():
    app.run(host="0.0.0.0", port=5000)

if __name__ == "__main__":
    main()