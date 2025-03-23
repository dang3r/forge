from typing import Any
import httpx
import cv2
import io
from mcp.server.fastmcp import FastMCP
from mcp.server.fastmcp.utilities.types import Image
from PIL import Image as PILImage
import numpy as np

# Initialize FastMCP server
mcp = FastMCP("weather")

# Constants
NWS_API_BASE = "https://api.weather.gov"
USER_AGENT = "weather-app/1.0"


async def make_nws_request(url: str) -> dict[str, Any] | None:
    """Make a request to the NWS API with proper error handling."""
    headers = {"User-Agent": USER_AGENT, "Accept": "application/geo+json"}
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(url, headers=headers, timeout=30.0)
            response.raise_for_status()
            return response.json()
        except Exception:
            return None


def format_alert(feature: dict) -> str:
    """Format an alert feature into a readable string."""
    props = feature["properties"]
    return f"""
Event: {props.get('event', 'Unknown')}
Area: {props.get('areaDesc', 'Unknown')}
Severity: {props.get('severity', 'Unknown')}
Description: {props.get('description', 'No description available')}
Instructions: {props.get('instruction', 'No specific instructions provided')}
"""


@mcp.tool()
async def get_alerts(state: str) -> str:
    """Get weather alerts for a US state.

    Args:
        state: Two-letter US state code (e.g. CA, NY)
    """
    url = f"{NWS_API_BASE}/alerts/active/area/{state}"
    data = await make_nws_request(url)

    if not data or "features" not in data:
        return "Unable to fetch alerts or no alerts found."

    if not data["features"]:
        return "No active alerts for this state."

    alerts = [format_alert(feature) for feature in data["features"]]
    return "\n---\n".join(alerts)


@mcp.tool()
async def get_forecast(latitude: float, longitude: float) -> str:
    """Get weather forecast for a location.

    Args:
        latitude: Latitude of the location
        longitude: Longitude of the location
    """
    # First get the forecast grid endpoint
    points_url = f"{NWS_API_BASE}/points/{latitude},{longitude}"
    points_data = await make_nws_request(points_url)

    if not points_data:
        return "Unable to fetch forecast data for this location."

    # Get the forecast URL from the points response
    forecast_url = points_data["properties"]["forecast"]
    forecast_data = await make_nws_request(forecast_url)

    if not forecast_data:
        return "Unable to fetch detailed forecast."

    # Format the periods into a readable forecast
    periods = forecast_data["properties"]["periods"]
    forecasts = []
    for period in periods[:5]:  # Only show next 5 periods
        forecast = f"""
{period['name']}:
Temperature: {period['temperature']}°{period['temperatureUnit']}
Wind: {period['windSpeed']} {period['windDirection']}
Forecast: {period['detailedForecast']}
"""
        forecasts.append(forecast)

    return "\n---\n".join(forecasts)


@mcp.tool()
async def last_workout() -> str:
    """Get the last workout from the Obsidian vault."""
    from pathlib import Path

    vault_path = Path("/home/dang3r/Documents/Obsidian Vault/6. Workout")
    newest_file = max(vault_path.glob("*.md"))
    return newest_file.read_text()


@mcp.tool()
async def capture_webcam() -> Image:
    """Take a picture using the webcam and return it as an image.

    Returns:
        An image captured from the webcam
    """
    # Initialize webcam
    cap = cv2.VideoCapture(0)

    if not cap.isOpened():
        raise Exception("Could not access webcam")

    try:
        # Capture a single frame
        ret, frame = cap.read()
        if not ret:
            raise Exception("Failed to capture image from webcam")

        # Convert from BGR (OpenCV format) to RGB
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        # Convert to PIL Image
        pil_image = PILImage.fromarray(rgb_frame)

        # Save to buffer
        buffer = io.BytesIO()
        pil_image.save(buffer, format="JPEG", quality=85)

        # save it to disk as a jpeg
        pil_image.save("webcam_image.jpeg", format="JPEG", quality=85)

        return Image(data=buffer.getvalue(), format="jpeg")
    finally:
        # Always release the webcam
        cap.release()


if __name__ == "__main__":
    # Initialize and run the server
    mcp.settings.port = 8001
    mcp.settings.log_level = "DEBUG"
    mcp.run(transport="sse")
