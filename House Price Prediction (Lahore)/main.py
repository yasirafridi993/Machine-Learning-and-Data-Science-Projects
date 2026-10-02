from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

from src.predict import (
    get_locations,
    predict_house_price,
)


# =========================================================
# FASTAPI APP
# =========================================================

app = FastAPI(
    title="Lahore House Price Prediction API",
    description="ML API for Lahore house price prediction",
    version="1.0.0",
)


# =========================================================
# REQUEST MODEL
# =========================================================

class HouseInput(BaseModel):

    area_sqft: float = Field(
        ...,
        gt=0,
        description="House area in square feet"
    )

    location: str = Field(
        ...,
        min_length=1,
        description="House location"
    )

    bedrooms: int = Field(
        ...,
        ge=0,
        description="Number of bedrooms"
    )

    baths: int = Field(
        ...,
        ge=0,
        description="Number of bathrooms"
    )


# =========================================================
# ROOT
# =========================================================

@app.get("/")
def root():

    return {
        "message": "Lahore House Price Prediction API is running"
    }


# =========================================================
# HEALTH CHECK
# =========================================================

@app.get("/health")
def health():

    return {
        "status": "healthy"
    }


# =========================================================
# LOCATIONS
# =========================================================

@app.get("/locations")
def locations():

    try:

        return {
            "locations": get_locations()
        }

    except Exception as error:

        raise HTTPException(
            status_code=500,
            detail=str(error)
        )


# =========================================================
# PREDICTION
# =========================================================

@app.post("/predict")
def predict(data: HouseInput):

    try:

        price = predict_house_price(

            area_sqft=data.area_sqft,

            location=data.location,

            bedrooms=data.bedrooms,

            baths=data.baths,

        )


        return {
            "predicted_price": price
        }


    except ValueError as error:

        raise HTTPException(
            status_code=400,
            detail=str(error)
        )


    except Exception as error:

        raise HTTPException(
            status_code=500,
            detail=f"Prediction failed: {error}"
        )


if __name__ == "__main__":

    import flet as ft

    from ui import main as run_dashboard

    ft.app(
        target=run_dashboard,
        view=ft.AppView.FLET_APP,
    )