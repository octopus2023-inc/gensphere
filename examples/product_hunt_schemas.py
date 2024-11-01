# product_hunt_schemas.py

from pydantic import BaseModel, Field
from typing import List

class StartupInformation(BaseModel):
    product_name: str = Field(..., description="The name of the product")
    company_name: str = Field(..., description="The name of the company that offers the product. Could be equal to name of the product")
    url: str = Field(..., description="URL associated with the product.")
    number_upvotes: int = Field(..., description="Number of upvotes associated with the product")
    business_model: str = Field(..., description="A brief description about the business model of the product or company")
    brief_description: str = Field(..., description="A brief description about the product")

class StartupInformationList(BaseModel):
    information_list:List[StartupInformation]