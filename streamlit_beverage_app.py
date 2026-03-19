import os
from openai import OpenAI
import streamlit as st
from dotenv import load_dotenv

load_dotenv()

st.set_page_config(page_title="BevMan Beverage Concept Studio", page_icon="🥤", layout="wide")

st.markdown(
    """
    <style>
        .main-header {
            padding: 0.25rem 0 1rem 0;
        }
        .hero-card {
            background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%);
            color: white;
            padding: 1.5rem;
            border-radius: 1rem;
            margin-bottom: 1rem;
        }
        .section-card {
            background: #f8fafc;
            padding: 1rem;
            border-radius: 0.75rem;
            border: 1px solid #e2e8f0;
            margin-bottom: 1rem;
        }
        .small-note {
            font-size: 0.9rem;
            color: #475569;
        }
    </style>
    """,
    unsafe_allow_html=True,
)


SWEETENER_OPTIONS = [
    "Cane Sugar",
    "High Fructose Corn Syrup",
    "Erythritol",
    "Monk Fruit",
    "Stevia",
    "Sucralose",
    "Allulose",
    "Agave Syrup",
    "Honey",
    "Dextrose",
]

NATURAL_PRESERVATIVE_OPTIONS = [
    "Ascorbic Acid",
    "Rosemary Extract",
    "Cultured Dextrose",
    "Fermented Preservative Systems",
    "Citric Acid",
    "Mixed Tocopherols",
    "Grapefruit Seed Extract",
]

ARTIFICIAL_PRESERVATIVE_OPTIONS = [
    "Potassium Sorbate",
    "Sodium Benzoate",
    "Calcium Disodium EDTA",
]

ALCOHOL_BASE_OPTIONS = [
    "Vodka",
    "Rum",
    "Tequila",
    "Whiskey",
    "Gin",
    "Malt Base",
    "Wine Base",
    "Neutral Grain Spirit",
    "Seltzer Base",
]

FUNCTIONAL_OPTIONS = [
    "Electrolytes",
    "B Vitamins",
    "Vitamin C",
    "Adaptogens",
    "Amino Acids",
    "Botanicals",
    "Collagen",
    "Protein",
    "No Functional Additions",
]


def get_client() -> OpenAI:
    api_key = os.getenv("OPENAI_API_KEY") or st.secrets.get("OPENAI_API_KEY")
    if not api_key:
        raise RuntimeError("OPENAI_API_KEY is not set.")
    return OpenAI(api_key=api_key)


def join_or_none(values: list[str]) -> str:
    cleaned = [value for value in values if value]
    return ", ".join(cleaned) if cleaned else "None specified"


def build_prompt(inputs: dict) -> str:
    alcohol_section = ""
    if inputs["category"] == "alcohol rtd":
        alcohol_section = (
            f"Alcohol Percentage (ABV): {inputs['alcohol_percentage']}\n"
            f"Alcohol Base Preference: {inputs['alcohol_base']}\n"
        )

    caffeine_section = ""
    if inputs["category"] == "energy":
        caffeine_section = f"Caffeine Level: {inputs['caffeine']}\n"

    return f"""
Create {inputs['num_concepts']} different beverage concepts based on the following requirements.

Client / Project Context:
- Brand or Project Name: {inputs['project_name']}
- Primary Goal: {inputs['project_goal']}

Flavor: {inputs['flavor']}
Target Market: {inputs['market']}
Category: {inputs['category']}
{caffeine_section}Sweetener Preferences: {inputs['sweeteners']}
Functional Ingredient Preferences: {inputs['functional_ingredients']}
Desired Ingredients: {inputs['other_ingredients']}
Ingredients to Avoid: {inputs['ingredients_avoid']}
Natural Preservative Preferences: {inputs['natural_preservatives']}
Artificial Preservative Preferences: {inputs['artificial_preservatives']}
Carbonation: {inputs['carbonation']}
Manufacturing Process: {inputs['process']}
Beverage Package Type: {inputs['package_type']}
Beverage Volume: {inputs['package_size']}
{alcohol_section}
Important rules:
- Make each concept meaningfully different in flavor, positioning, and branding.
- Follow the beverage type, carbonation, manufacturing process, package format, and alcohol targets exactly when provided.
- Do not include any ingredients listed in "Ingredients to Avoid."
- If any requirements conflict, clearly point out the conflict before generating concepts.
- Do not invent technical claims unless they are clearly labeled as suggestions.
- Keep the concepts realistic for commercial beverage development.
- Write in a polished, client-facing tone.

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
- Go / No-Go Recommendation
- Estimated Development Difficulty (Low / Medium / High)

At the end, include:
- Best concept for mass market appeal
- Best concept for premium positioning
- Best concept for easiest development path
- Client-Ready Summary (a short polished summary suitable to share with a client)
"""


def run_checks(inputs: dict) -> list[str]:
    warnings = []

    combined_ingredients = " ".join([
        inputs["sweeteners"],
        inputs["natural_preservatives"],
        inputs["artificial_preservatives"],
        inputs["other_ingredients"],
    ]).lower()

    if "preservative" in combined_ingredients and "preservative" in inputs["ingredients_avoid"].lower():
        warnings.append("You asked to include preservatives and also avoid preservatives.")

    if inputs["category"] == "alcohol rtd" and not inputs["alcohol_percentage"]:
        warnings.append("Alcohol RTD selected but alcohol percentage is missing.")

    if inputs["category"] == "alcohol rtd" and inputs["alcohol_base"] == "":
        warnings.append("Alcohol RTD selected but alcohol base preference is missing.")

    if inputs["category"] == "hydration" and inputs["carbonation"] == "carbonated":
        warnings.append("Carbonated hydration concepts are possible, but they may be less typical for mainstream sports hydration positioning.")

    if inputs["category"] == "energy" and inputs["caffeine"] == "none":
        warnings.append("Energy category selected with no caffeine. Make sure that matches the intended market positioning.")

    return warnings


def save_markdown(inputs: dict, output: str) -> str:
    filename = f"{inputs['project_name']}_{inputs['flavor']}_{inputs['category']}_concept_output.md".replace(" ", "_").lower()
    with open(filename, "w", encoding="utf-8") as file:
        file.write(f"# {inputs['project_name']} - Beverage Concept Output\n\n")
        file.write("## Project Inputs\n")
        for key, value in inputs.items():
            if value != "":
                file.write(f"- {key.replace('_', ' ').title()}: {value}\n")
        file.write("\n## AI Generated Concepts\n\n")
        file.write(output)
    return filename


st.markdown('<div class="hero-card">', unsafe_allow_html=True)
st.markdown("## BevMan Beverage Concept Studio")
st.markdown(
    "Generate polished, client-facing beverage concepts for internal ideation, early-stage screening, and customer discussions."
)
st.markdown('</div>', unsafe_allow_html=True)

with st.sidebar:
    st.header("About this tool")
    st.write(
        "Use this concept studio to generate beverage directions based on category, format, ingredient systems, process, and market goals."
    )
    st.markdown(
        "<div class='small-note'>This tool supports concept generation and early-stage direction. Final formulation, regulatory, and commercial decisions still require technical review.</div>",
        unsafe_allow_html=True,
    )
    st.divider()
    st.subheader("Run locally")
    st.code("py -m streamlit run streamlit_beverage_app.py")

category = st.selectbox("Beverage Type", ["energy", "hydration", "alcohol rtd"], key="category_selector")

with st.form("concept_form"):
    st.markdown("### Project Details")
    project_col1, project_col2 = st.columns(2)
    with project_col1:
        project_name = st.text_input("Client or Project Name", placeholder="Project Atlas")
    with project_col2:
        project_goal = st.text_input("Primary Goal", placeholder="Launch a clean-label gaming energy drink")

    st.markdown("### Product Inputs")
    col1, col2 = st.columns(2)

    with col1:
        flavor = st.text_input("Flavor", placeholder="tropical punch")
        market = st.text_input("Target Market", placeholder="gamers")
        if category == "energy":
            caffeine = st.selectbox("Caffeine Level", ["low", "medium", "high"])
        else:
            caffeine = "not applicable"
        carbonation = st.selectbox("Carbonation", ["carbonated", "non-carbonated"])

    with col2:
        package_type = st.selectbox("Package Type", ["can", "pet bottle"])
        package_size = st.text_input("Package Size", placeholder="12 oz")
        process = st.text_input("Manufacturing Process", placeholder="HTST")
        num_concepts = st.selectbox("Number of Concepts", [1, 3, 5], index=1)

    alcohol_percentage = ""
    alcohol_base = ""
    if category == "alcohol rtd":
        alcohol_col1, alcohol_col2 = st.columns(2)
        with alcohol_col1:
            alcohol_percentage = st.text_input("Alcohol Percentage (ABV)", placeholder="5%")
        with alcohol_col2:
            alcohol_base_options = st.multiselect("Alcohol Base Options", ALCOHOL_BASE_OPTIONS)
            alcohol_base = join_or_none(alcohol_base_options)

    st.markdown("### Ingredient System Selection")
    sweetener_options = st.multiselect("Sweeteners", SWEETENER_OPTIONS)
    functional_options = st.multiselect("Functional Ingredients", FUNCTIONAL_OPTIONS)

    preservative_col1, preservative_col2 = st.columns(2)
    with preservative_col1:
        natural_preservative_options = st.multiselect("Natural Preservatives", NATURAL_PRESERVATIVE_OPTIONS)
    with preservative_col2:
        artificial_preservative_options = st.multiselect("Artificial Preservatives", ARTIFICIAL_PRESERVATIVE_OPTIONS)

    other_ingredients = st.text_area(
        "Other Desired Ingredients or Notes",
        placeholder="electrolytes, juice content, natural colors, botanical extracts"
    )
    ingredients_avoid = st.text_area(
        "Ingredients to Avoid",
        placeholder="erythritol, sodium benzoate, cane sugar"
    )

    submitted = st.form_submit_button("Generate Client-Ready Concepts", use_container_width=True)

if submitted:
    inputs = {
        "project_name": project_name.strip(),
        "project_goal": project_goal.strip(),
        "flavor": flavor.strip(),
        "market": market.strip(),
        "category": category,
        "caffeine": caffeine,
        "sweeteners": join_or_none(sweetener_options),
        "functional_ingredients": join_or_none(functional_options),
        "other_ingredients": other_ingredients.strip(),
        "ingredients_avoid": ingredients_avoid.strip(),
        "natural_preservatives": join_or_none(natural_preservative_options),
        "artificial_preservatives": join_or_none(artificial_preservative_options),
        "carbonation": carbonation,
        "process": process.strip(),
        "package_type": package_type,
        "package_size": package_size.strip(),
        "num_concepts": num_concepts,
        "alcohol_percentage": alcohol_percentage.strip(),
        "alcohol_base": alcohol_base.strip(),
    }

    missing = [key for key, value in inputs.items() if value == "" and key not in ["alcohol_percentage", "alcohol_base"]]
    if category == "alcohol rtd" and inputs["alcohol_percentage"] == "":
        missing.append("alcohol_percentage")
    if category == "alcohol rtd" and inputs["alcohol_base"] in ["", "None specified"]:
        missing.append("alcohol_base")

    if missing:
        pretty_missing = ", ".join(name.replace("_", " ") for name in missing)
        st.error(f"Please complete all required fields before generating concepts. Missing: {pretty_missing}")
    else:
        warnings = run_checks(inputs)
        if warnings:
            st.markdown("### Input Warnings")
            for warning in warnings:
                st.warning(warning)

        prompt = build_prompt(inputs)

        try:
            client = get_client()
            with st.spinner("Generating concepts and client-ready summary..."):
                response = client.responses.create(
                    model="gpt-4.1-mini",
                    input=prompt,
                )
            output = response.output_text

            st.success("Concept package generated.")
            st.markdown("### Concept Output")
            st.markdown(output)

            filename = save_markdown(inputs, output)
            with open(filename, "r", encoding="utf-8") as file:
                st.download_button(
                    label="Download Client Concept Package",
                    data=file.read(),
                    file_name=filename,
                    mime="text/markdown",
                    use_container_width=True,
                )
        except Exception as exc:
            st.error(f"Error: {exc}")

st.divider()
st.subheader("Recommended next phase")
st.write(
    "Next, expand the formula selection logic even further with acid systems, color systems, juice content, claim targets, sweetener loading guidance, and packaging-specific development constraints."
)

