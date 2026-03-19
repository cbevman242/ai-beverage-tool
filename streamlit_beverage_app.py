import os
from openai import OpenAI
import streamlit as st
from dotenv import load_dotenv

load_dotenv()


st.set_page_config(page_title="BevMan Concept Generator", page_icon="🥤", layout="wide")


def get_client() -> OpenAI:
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise RuntimeError("OPENAI_API_KEY is not set.")
    return OpenAI(api_key=api_key)


def build_prompt(inputs: dict) -> str:
    alcohol_section = ""
    if inputs["category"] == "alcohol rtd":
        alcohol_section = f"Alcohol Percentage (ABV): {inputs['alcohol_percentage']}\n"

    return f"""
Create {inputs['num_concepts']} different beverage concepts based on the following requirements.

Flavor: {inputs['flavor']}
Target Market: {inputs['market']}
Category: {inputs['category']}
Caffeine Level: {inputs['caffeine']}
Desired Ingredients: {inputs['ingredients']}
Avoid Ingredients: {inputs['ingredients_avoid']}
Carbonation: {inputs['carbonation']}
Manufacturing Process: {inputs['process']}
Beverage Package Type: {inputs['package_type']}
Beverage Volume: {inputs['package_size']}
{alcohol_section}
Important rules:
- Make each concept meaningfully different in flavor, positioning, and branding.
- Follow the beverage type, carbonation, manufacturing process, package format, and ABV target exactly when provided.
- Do not include any ingredients listed in "Avoid Ingredients."
- If any requirements conflict, clearly point out the conflict before generating concepts.
- Do not invent technical claims unless they are clearly labeled as suggestions.
- Keep the concepts realistic for commercial beverage development.

For each concept, include:
- Product Name
- Beverage Description
- Flavor Profile
- Branding Angle
- Suggested Ingredient List
- Equipment Needed to Manufacture
- Packaging Summary
- Potential Claims / Positioning Ideas
- Key Technical Risks
- Suggested Next Development Step
- Potential Consumer Positioning
- Price Tier Suggestion
- Risks or Formulation Watchouts

At the end, include:
- Best concept for mass market appeal
- Best concept for premium positioning
- Best concept for easiest development path
- Client-Ready Summary (a short, polished summary suitable to share with a client)
"""


def run_checks(inputs: dict) -> list[str]:
    warnings = []

    if "preservative" in inputs["ingredients"].lower() and "preservative" in inputs["ingredients_avoid"].lower():
        warnings.append("You asked to include preservatives and also avoid preservatives.")

    if inputs["category"] == "hydration" and inputs["caffeine"] in ["medium", "high"]:
        warnings.append("A hydration drink with medium or high caffeine may conflict with typical hydration positioning.")

    if inputs["category"] == "alcohol rtd" and inputs["caffeine"] != "none":
        warnings.append("Alcohol RTD plus caffeine may create regulatory, formulation, or positioning issues depending on market.")

    if inputs["category"] == "alcohol rtd" and not inputs["alcohol_percentage"]:
        warnings.append("Alcohol RTD selected but alcohol percentage is missing.")

    return warnings


def save_markdown(inputs: dict, output: str) -> str:
    filename = f"{inputs['flavor']}_{inputs['category']}_concept_output.md".replace(" ", "_").lower()
    with open(filename, "w", encoding="utf-8") as file:
        file.write("# Beverage Concept Output\n\n")
        file.write("## Inputs\n")
        for key, value in inputs.items():
            if value != "":
                file.write(f"- {key.replace('_', ' ').title()}: {value}\n")
        file.write("\n## AI Generated Concepts\n\n")
        file.write(output)
    return filename


st.title("🥤 BevMan Beverage Concept Generator")
st.caption("Generate beverage concepts in your browser using your existing OpenAI API key.")

with st.sidebar:
    st.header("How to run")
    st.markdown(
        """
1. Set your `OPENAI_API_KEY` environment variable.
2. Install dependencies:
   ```bash
   py -m pip install streamlit openai
   ```
3. Run the app:
   ```bash
   py -m streamlit run streamlit_beverage_app.py
   ```
        """
    )

category = st.selectbox("Beverage type", ["energy", "hydration", "alcohol rtd"], key="category_selector")

with st.form("concept_form"):
    col1, col2 = st.columns(2)

    with col1:
        flavor = st.text_input("Flavor", placeholder="tropical punch")
        market = st.text_input("Target market", placeholder="gamers")
        caffeine = st.selectbox("Caffeine level", ["none", "low", "medium", "high"])
        carbonation = st.selectbox("Carbonation", ["carbonated", "non-carbonated"])

    with col2:
        package_type = st.selectbox("Package type", ["can", "pet bottle"])
        package_size = st.text_input("Package size", placeholder="12 oz")
        process = st.text_input("Manufacturing process", placeholder="HTST")
        num_concepts = st.selectbox("Number of concepts", [1, 3, 5], index=1)

    alcohol_percentage = ""
    if category == "alcohol rtd":
        alcohol_percentage = st.text_input("Alcohol percentage (ABV)", placeholder="5%")

    ingredients = st.text_area("Desired ingredients to use", placeholder="natural flavors, stevia, monk fruit")
    ingredients_avoid = st.text_area("Ingredients to avoid", placeholder="erythritol, sodium benzoate")

    submitted = st.form_submit_button("Generate concepts", use_container_width=True)

if submitted:
    inputs = {
        "flavor": flavor.strip(),
        "market": market.strip(),
        "category": category,
        "caffeine": caffeine,
        "ingredients": ingredients.strip(),
        "ingredients_avoid": ingredients_avoid.strip(),
        "carbonation": carbonation,
        "process": process.strip(),
        "package_type": package_type,
        "package_size": package_size.strip(),
        "num_concepts": num_concepts,
        "alcohol_percentage": alcohol_percentage.strip(),
    }

    missing = [key for key, value in inputs.items() if value == "" and key != "alcohol_percentage"]
    if category == "alcohol rtd" and inputs["alcohol_percentage"] == "":
        missing.append("alcohol_percentage")

    if missing:
        st.error(f"Please complete all required fields before generating concepts. Missing: {', '.join(missing)}")
    else:
        warnings = run_checks(inputs)
        for warning in warnings:
            st.warning(warning)

        prompt = build_prompt(inputs)

        try:
            client = get_client()
            with st.spinner("Generating beverage concepts..."):
                response = client.responses.create(
                    model="gpt-4.1-mini",
                    input=prompt,
                )
            output = response.output_text
            st.success("Concepts generated.")
            st.markdown(output)

            filename = save_markdown(inputs, output)
            with open(filename, "r", encoding="utf-8") as file:
                st.download_button(
                    label="Download markdown output",
                    data=file.read(),
                    file_name=filename,
                    mime="text/markdown",
                    use_container_width=True,
                )
        except Exception as exc:
            st.error(f"Error: {exc}")

st.divider()
st.subheader("What to build next")
st.write(
    "Once this is working, the next useful upgrades are concept comparison, marketing copy generation, and client-ready summary sheets."
)
