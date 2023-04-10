from pydantic.main import BaseModel


class UIAvailabilityFields(BaseModel):
    display: bool = False
    create: bool = False
    edit: bool = False
    remove: bool = False
    delete: bool = False
    label: str = "Label"


class UIFeatures(BaseModel):
    containers: UIAvailabilityFields = UIAvailabilityFields(display=True, label="Containers")
    networks: UIAvailabilityFields = UIAvailabilityFields(display=True, label="Networks")
    groups: UIAvailabilityFields = UIAvailabilityFields(display=True, label="Pods")
    pasta: UIAvailabilityFields = UIAvailabilityFields()
