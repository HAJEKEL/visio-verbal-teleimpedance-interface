import aiohttp
import logging
import io
from fastapi import HTTPException
from fastapi.responses import StreamingResponse

class EyeTrackerProcessor:
    def __init__(self, eye_tracker_url: str):
        self.eye_tracker_url = eye_tracker_url
        logging.info(f"EyeTrackerProcessor initialized with URL: {self.eye_tracker_url}")

    async def calibrate(self):
        """
        Sends a calibration request to the eye tracker service.
        """
        logging.info("Starting calibration with the eye tracker service.")
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{self.eye_tracker_url}/calibrate") as response:
                    if response.status == 200:
                        data = await response.json()
                        logging.info("Calibration successful.")
                        return data
                    else:
                        detail = await response.text()
                        logging.error(f"Calibration failed with status {response.status}: {detail}")
                        raise HTTPException(status_code=response.status, detail=detail)
        except Exception as e:
            logging.error(f"Calibration failed: {str(e)}")
            raise HTTPException(status_code=500, detail="Calibration failed")

    async def capture_snapshot(self):
        """
        Captures a snapshot from the eye tracker service.
        """
        logging.info("Starting snapshot capture from the eye tracker service.")
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{self.eye_tracker_url}/capture_snapshot") as response:
                    if response.status == 200:
                        content = await response.read()
                        logging.info("Snapshot capture successful.")
                        return StreamingResponse(
                            io.BytesIO(content),
                            media_type=response.content_type
                        )
                    else:
                        detail = await response.text()
                        logging.error(f"Snapshot capture failed with status {response.status}: {detail}")
                        raise HTTPException(status_code=response.status, detail=detail)
        except Exception as e:
            logging.error(f"Snapshot capture failed: {str(e)}")
            raise HTTPException(status_code=500, detail="Snapshot capture failed")
