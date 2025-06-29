from fastapi import APIRouter, Header
from typing import Optional

from .schemas import UserDevicesResponse, UnlinkResponse

router = APIRouter()

# This is our "virtual" kettle. In a real application,
# this data would be retrieved from a database.
MY_KETTLE = {
    "id": "kettle-12345",
    "name": "Электрический чайник",
    "description": "Мой умный чайник на кухне",
    "room": "Кухня",
    "type": "devices.types.kettle",
    "capabilities": [
        {
            "type": "devices.capabilities.on_off",
            "retrievable": True,
            "reportable": True,
            "parameters": {"split": False}
        },
        {
            "type": "devices.capabilities.range",
            "retrievable": True,
            "reportable": True,
            "parameters": {
                "instance": "temperature",
                "name": "температура",
                "unit": "unit.temperature.celsius",
                "random_access": True,
                "range": {
                    "min": 40,
                    "max": 100,
                    "precision": 5
                }
            }
        }
    ],
    "device_info": {
        "manufacturer": "My DIY Devices",
        "model": "DIY-Kettle-v1",
        "hw_version": "1.0",
        "sw_version": "1.1"
    }
}

@router.get("/")
def health_check():
    """Health check endpoint."""
    return "I'm alive!"

@router.post("/v1.0/user/unlink", response_model=UnlinkResponse)
def unlink_user(x_request_id: Optional[str] = Header(None, alias="X-Request-Id")):
    """Unlink user account."""
    # Logic for deleting user token from your system should be here.
    print(f"User unlinked! Request ID: {x_request_id}")
    return {"request_id": x_request_id}


@router.get("/v1.0/user/devices", response_model=UserDevicesResponse)
def get_user_devices(x_request_id: Optional[str] = Header(None, alias="X-Request-Id")):
    """
    Responds to Yandex's request for a list of devices.
    This is where we "add" our kettle.
    """
    print(f"Request for devices list. Request ID: {x_request_id}")

    # In a real application, user_id should be obtained from the Authorization header
    # and used to find the user's devices in your database.
    response_payload = {
        "user_id": "some_user_id_from_your_system",
        "devices": [
            MY_KETTLE
        ]
    }
    
    return {
        "request_id": x_request_id,
        "payload": response_payload
    }

# TODO: You will also need to implement the /v1.0/devices/query and /v1.0/devices/action endpoints
# for managing the kettle and getting its state. Without them, it will be visible but inactive.
