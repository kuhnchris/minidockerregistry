from pydantic.main import BaseModel
from typing import Optional
from app.modules.interfaces.ui import UIFeatures
from app.modules.interfaces.containers import CommonContainerDataStructure


class CommonDataHolderModel(BaseModel):
    container_data: Optional[CommonContainerDataStructure] = CommonContainerDataStructure()
    features: Optional[UIFeatures] = UIFeatures()
