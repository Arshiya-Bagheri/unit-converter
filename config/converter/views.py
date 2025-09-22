"""
---------
This module contains the Django views for the Unit Converter project.
Each view handles rendering of HTML templates or processing user input
to perform unit conversions (length, weight, temperature).

Functions:
- base: Render the base layout (main entry template).
- length: Render the length conversion form.
- weight: Render the weight conversion form.
- temperature: Render the temperature conversion form.
- smart_format: Helper function for rounding/formatting numbers.
- result: Process the conversion logic and display the result.
"""

from django.shortcuts import render
from decimal import Decimal


# -------------------------------------------------------------------
# Simple views for rendering templates (no logic)
# -------------------------------------------------------------------
def base(request):
    """
    Render the base.html template.
    This page provides the shared layout and navigation.
    """
    return render(request, 'converter/base.html')


def length(request):
    """
    Render the length.html template.
    Contains form for length conversions.
    """
    return render(request, 'converter/length.html')


def weight(request):
    """
    Render the weight.html template.
    Contains form for weight conversions.
    """
    return render(request, 'converter/weight.html')


def temperature(request):
    """
    Render the temperature.html template.
    Contains form for temperature conversions.
    """
    return render(request, 'converter/temperature.html')


# -------------------------------------------------------------------
# Helper function: formatting numbers
# -------------------------------------------------------------------
def smart_format(value: float) -> str:
    """
    Format numeric values in a user-friendly way:
    - Handles zero case directly.
    - Uses Decimal for precise rounding.
    - Rounds to 4 significant digits.
    - Removes scientific notation if present.
    - Strips trailing zeros and dots.

    Args:
        value (float): The numeric value to format.

    Returns:
        str: Clean, human-readable number string.
    """
    if value == 0:
        return "0"

    # Use Decimal for precise rounding
    d = Decimal(str(value))

    # Round to 4 significant digits
    formatted = f"{d:.4g}"

    # Convert back to float if scientific notation appears
    if "e" in formatted or "E" in formatted:
        formatted = f"{float(formatted):f}"

    # Remove trailing zeros and decimal point if unnecessary
    return formatted.rstrip("0").rstrip(".")


# -------------------------------------------------------------------
# Main logic: result page
# -------------------------------------------------------------------
def result(request, category):
    """
    Process user input and perform unit conversions.
    Supports 3 categories: length, weight, and temperature.

    Args:
        request (HttpRequest): Incoming HTTP request object.
        category (str): Conversion category (length, weight, temperature).

    Returns:
        HttpResponse: Renders result.html with either an error or conversion result.
    """
    if request.method == "POST":
        # Read input values
        value_input = request.POST.get("value", "").strip()
        from_unit = request.POST.get("from_unit")
        to_unit = request.POST.get("to_unit")

        # Input validation: check if value is empty
        if not value_input:
            error = "Please enter a value to convert."
            return render(request, "converter/result.html", {
                "error": error,
                "category": category
            })

        # Input validation: check if value is a valid number
        try:
            value = float(value_input)
        except ValueError:
            error = "Invalid number entered."
            return render(request, "converter/result.html", {
                "error": error,
                "category": category
            })

        # -----------------------------
        # Conversion factors
        # -----------------------------
        length_units = {
            "meter": 1,
            "kilometer": 1000,      # 1 km = 1000 m
            "mile": 1609.34,        # 1 mi = 1609.34 m
            "yard": 0.9144,         # 1 yd = 0.9144 m
            "foot": 0.3048,         # 1 ft = 0.3048 m
            "inch": 0.0254,         # 1 in = 0.0254 m
            "centimeter": 0.01,     # 1 cm = 0.01 m
            "millimeter": 0.001     # 1 mm = 0.001 m
        }

        weight_units = {
            "gram": 1,
            "milligram": 0.001,
            "kilogram": 1000,
            "ounce": 28.3495,
            "pound": 453.592
        }

        # Note: For temperature, formula-based conversion is required.
        # Dictionary here only shows identity conversion for reference.
        temperature_units = {
            "Celsius": lambda x: x,
            "Fahrenheit": lambda x: (x * 9/5) + 32,
            "Kelvin": lambda x: x + 273.15
        }

        # -----------------------------
        # Handle conversions by category
        # -----------------------------
        if category == "length":
            # Convert to meters and then to target unit
            converted_value = value * (length_units[from_unit] / length_units[to_unit])
            result = f"{value} {from_unit} = {smart_format(converted_value)} {to_unit}"

        elif category == "weight":
            # Convert to grams and then to target unit
            converted_value = value * (weight_units[from_unit] / weight_units[to_unit])
            result = f"{value} {from_unit} = {smart_format(converted_value)} {to_unit}"

        elif category == "temperature":
            # Temperature requires special formulas
            if from_unit == "celsius":
                if to_unit == "fahrenheit":
                    converted_value = (value * 9/5) + 32
                elif to_unit == "kelvin":
                    converted_value = value + 273.15
            elif from_unit == "fahrenheit":
                if to_unit == "celsius":
                    converted_value = (value - 32) * 5/9
                elif to_unit == "kelvin":
                    converted_value = (value - 32) * 5/9 + 273.15
            elif from_unit == "kelvin":
                if to_unit == "celsius":
                    converted_value = value - 273.15
                elif to_unit == "fahrenheit":
                    converted_value = (value - 273.15) * 9/5 + 32

            result = f"{value} {from_unit} = {smart_format(converted_value)} {to_unit}"

        # Return conversion result
        return render(request, "converter/result.html", {
            "result": result,
            "category": category
        })

    # Default: GET request, show empty result page
    return render(request, "converter/result.html", {
        "result": "",
        "category": category
    })
