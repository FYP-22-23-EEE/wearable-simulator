from pydantic import BaseModel


class ReqActivity(BaseModel):
    activity: str


class ReqDeviceState(BaseModel):
    device: str
    state: bool
