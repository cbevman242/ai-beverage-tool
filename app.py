from openai import OpenAI
import os

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


def get_choice(prompt_text, valid_options):
    while True:
        value = input(prompt_text).strip().lower()
        if value in valid_options:
            return value
        print(f"Please enter one of: {', '.join(valid_options)}")


def get_nonempty_input(prompt_text):
    while True:
        value = input(prompt_text).strip()
        if value:
            return value
        print("This field cannot be empty.")


def run_concept_generator():

    flavor = get_nonempty_input("Enter a flavor: ")
    market = get_nonempty_input("Enter a target market: ")

    category = get_choice(
        "Enter beverage type (energy, hydration, alcohol rtd): ",
        ["energy", "hydration", "alcohol rtd"]
    )

    caffeine = get_choice(
        "Enter caffeine level (none/low/medium/high): ",
        ["none", "low", "medium", "high"]
    )

    ingredients = get_nonempty_input("Enter desired ingredients to use: ")
    ingredients_avoid = get_nonempty_input("Enter ingredients to avoid: ")

    carbonation = get_choice(
        "Enter carbonation (carbonated or non-carbonated): ",
        ["carbonated", "non-carbonated"]
    )

    process = get_nonempty_input("Enter desired manufacturing process: ")

    package_type = get_choice(
        "Enter package type (can or PET bottle): ",
        ["can", "pet bottle"]
    )

    package_size = get_nonempty_input("What size package? (i.e. 12 oz, 16 oz, 500 mL): ")

    num_concepts = get_choice(
        "How many concepts do you want to generate? (1, 3, or 5): ",
        ["1", "3", "5"]
    )

    # Simple contradiction checks
    if "preservative" in ingredients.lower() and "preservative" in ingredients_avoid.lower():
        print("\nWarning: You asked to include and avoid preservatives.")

    if category == "hydration" and caffeine in ["medium", "high"]:
        print("\nWarning: Hydration drink with caffeine may conflict with positioning.")

    if category == "alcohol rtd" and caffeine != "none":
        print("\nWarning: Alcohol + caffeine may cause regulatory issues.")

    prompt = f"""
Create {num_concepts} different beverage concepts based on the following requirements.

Flavor: {flavor}
Target Market: {market}
Category: {category}
Caffeine Level: {caffeine}
Desired Ingredients: {ingredients}
Avoid Ingredients: {ingredients_avoid}
Carbonation: {carbonation}
Manufacturing Process: {process}
Beverage Package Type: {package_type}
Beverage Volume: {package_size}

Important rules:
- Make each concept meaningfully different
- Follow constraints exactly
- Avoid restricted ingredients
- Keep concepts commercially realistic

For each concept include:
- Product Name
- Beverage Description
- Flavor Profile
- Branding Angle
- Ingredient List
- Equipment Needed
- Packaging Summary

At the end include:
- Best concept for mass market
- Best for premium
- Easiest to develop
"""

    response = client.responses.create(
        model="gpt-4.1-mini",
        input=prompt
    )

    output = response.output_text

    print("\n==============================")
    print("AI GENERATED CONCEPTS")
    print("==============================\n")
    print(output)

    filename = f"{flavor}_{category}_concept_output.md".replace(" ", "_")

    with open(filename, "w", encoding="utf-8") as file:
        file.write(output)

    print(f"\nSaved output to {filename}")


# 🔁 Restart loop
while True:
    run_concept_generator()

    again = input("\nDo you want to generate another concept set? (yes/no): ").strip().lower()

    if again != "yes":
        print("Goodbye.")
        break