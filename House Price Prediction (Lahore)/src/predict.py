from pathlib import Path
import json
import joblib
import pandas as pd


# =========================================================
# PATHS
# =========================================================

BASE_DIR = Path(__file__).resolve().parent.parent

MODEL_PATH = BASE_DIR / "model" / "home_prices_model.pickle"

COLUMNS_PATH = BASE_DIR / "model" / "columns.json"


# =========================================================
# LOAD MODEL
# =========================================================

if not MODEL_PATH.exists():
    raise FileNotFoundError(
        f"Model file not found: {MODEL_PATH}"
    )

model = joblib.load(MODEL_PATH)


# =========================================================
# LOAD COLUMNS.JSON
# =========================================================

if not COLUMNS_PATH.exists():
    raise FileNotFoundError(
        f"columns.json not found: {COLUMNS_PATH}"
    )


with open(COLUMNS_PATH, "r", encoding="utf-8") as file:
    columns_data = json.load(file)


# =========================================================
# EXTRACT COLUMNS
# =========================================================

if isinstance(columns_data, dict):

    if "data_columns" not in columns_data:
        raise ValueError(
            "columns.json must contain a 'data_columns' key."
        )

    ALL_COLUMNS = columns_data["data_columns"]

elif isinstance(columns_data, list):

    ALL_COLUMNS = columns_data

else:

    raise ValueError(
        "Invalid columns.json format."
    )


if not isinstance(ALL_COLUMNS, list):
    raise ValueError(
        "'columns' inside columns.json must be a list."
    )


ALL_COLUMNS = [
    str(column).strip()
    for column in ALL_COLUMNS
]

MODEL_COLUMNS = getattr(model, "feature_names_in_", None)

if MODEL_COLUMNS is not None:
    MODEL_COLUMNS = [str(column).strip() for column in MODEL_COLUMNS]

    if len(MODEL_COLUMNS) != len(ALL_COLUMNS) or any(
        model_column.casefold() != data_column.casefold()
        for model_column, data_column in zip(MODEL_COLUMNS, ALL_COLUMNS)
    ):
        raise ValueError(
            "columns.json features do not match the model feature order."
        )

    ALL_COLUMNS = MODEL_COLUMNS


# =========================================================
# FIND LOCATION DUMMY COLUMNS
# =========================================================

LOCATION_PREFIX = "_"

LOCATION_COLUMNS = [
    column
    for column in ALL_COLUMNS
    if column.lower().startswith(LOCATION_PREFIX)
]


# =========================================================
# EXTRACT ACTUAL LOCATION NAMES
# =========================================================

LOCATION_MAP = {}

for column in LOCATION_COLUMNS:

    location_name = column[
        len(LOCATION_PREFIX):
    ].strip()

    LOCATION_MAP[location_name.lower()] = column


# =========================================================
# REQUIRED NUMERIC COLUMNS
# =========================================================

AREA_COLUMN = "Area_sqft"
BEDROOM_COLUMN = "Bedroom(s)"
BATH_COLUMN = "Bath(s)"


# =========================================================
# VALIDATE COLUMNS
# =========================================================

required_columns = [
    AREA_COLUMN,
    BEDROOM_COLUMN,
    BATH_COLUMN,
]


missing_columns = [
    column
    for column in required_columns
    if column not in ALL_COLUMNS
]


if missing_columns:

    raise ValueError(
        "These required columns are missing from columns.json: "
        + ", ".join(missing_columns)
    )


if not LOCATION_COLUMNS:

    raise ValueError(
        "No location dummy columns found in columns.json."
    )


# =========================================================
# GET LOCATIONS
# =========================================================

def get_locations() -> list[str]:

    return sorted(
        [
            location
            for location in LOCATION_MAP.keys()
        ],
        key=str.lower
    )


# =========================================================
# FIND LOCATION COLUMN
# =========================================================

def get_location_column(location: str) -> str:

    location_clean = location.strip().lower()

    if location_clean not in LOCATION_MAP:

        raise ValueError(
            f"Location '{location}' is not available."
        )

    return LOCATION_MAP[location_clean]


# =========================================================
# CREATE MODEL INPUT
# =========================================================

def create_input_dataframe(
    area_sqft: float,
    location: str,
    bedrooms: int,
    baths: int,
) -> pd.DataFrame:

    # -----------------------------------------------------
    # Create all columns with 0
    # -----------------------------------------------------

    input_data = {
        column: 0
        for column in ALL_COLUMNS
    }


    # -----------------------------------------------------
    # Numeric values
    # -----------------------------------------------------

    input_data[AREA_COLUMN] = area_sqft

    input_data[BEDROOM_COLUMN] = bedrooms

    input_data[BATH_COLUMN] = baths


    # -----------------------------------------------------
    # Selected location = 1
    # -----------------------------------------------------

    location_column = get_location_column(location)

    input_data[location_column] = 1


    # -----------------------------------------------------
    # DataFrame
    # -----------------------------------------------------

    dataframe = pd.DataFrame(
        [input_data],
        columns=ALL_COLUMNS
    )


    return dataframe


# =========================================================
# PREDICTION
# =========================================================

def predict_house_price(
    area_sqft: float,
    location: str,
    bedrooms: int,
    baths: int,
) -> float:

    input_dataframe = create_input_dataframe(
        area_sqft=area_sqft,
        location=location,
        bedrooms=bedrooms,
        baths=baths,
    )


    # -----------------------------------------------------
    # Prediction
    # -----------------------------------------------------

    prediction = model.predict(
        input_dataframe
    )


    if len(prediction) == 0:

        raise RuntimeError(
            "Model returned no prediction."
        )


    return float(prediction[0])