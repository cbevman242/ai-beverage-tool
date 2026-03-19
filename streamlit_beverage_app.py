import os
from openai import OpenAI
import streamlit as st
from dotenv import load_dotenv

load_dotenv()

st.set_page_config(page_title="BevMan Beverage Concept Studio", page_icon="🥤", layout="wide")

st.markdown(
    """
    <style>
        .hero-card {
            background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%);
            color: white;
            padding: 1.5rem;
            border-radius: 1rem;
            margin-bottom: 1rem;
        }
        .small-note {
            font-size: 0.9rem;
            color: #475569;
        }
        .output-card {
            background: #f8fafc;
            border: 1px solid #e2e8f0;
            border-radius: 0.75rem;
            padding: 1rem;
            margin-top: 0.75rem;
        }
    </style>
    """,
    unsafe_allow_html=True,
)


SWEETENER_OPTIONS = [
    "cane sugar",
    "high fructose corn syrup",
    "erythritol",
    "monk fruit",
    "stevia",
    "sucralose",
    "allulose",
    "agave syrup",
    "honey",
    "dextrose",
]

NATURAL_PRESERVATIVE_OPTIONS = [
    "ascorbic acid",
    "rosemary extract",
    "cultured dextrose",
    "fermented preservative systems",
    "citric acid",
    "mixed tocopherols",
    "grapefruit seed extract",
]

ARTIFICIAL_PRESERVATIVE_OPTIONS = [
    "potassium sorbate",
    "sodium benzoate",
    "calcium disodium edta",
]

ALCOHOL_BASE_OPTIONS = [
    "vodka",
    "rum",
    "tequila",
    "whiskey",
    "gin",
    "malt base",
    "wine base",
    "neutral grain spirit",
    "seltzer base",
]

FUNCTIONAL_OPTIONS = [
    "electrolytes",
    "b vitamins",
    "vitamin c",
    "adaptogens",
    "amino acids",
    "botanicals",
    "collagen",
    "protein",
    "no functional additions",
]

MANUFACTURING_PROCESS_OPTIONS = [
    "not specified yet",
    "htst",
    "cold fill",
    "hot fill",
    "aseptic",
    "tunnel pasteurization",
    "flash pasteurization",
]


def display_label(value: str) -> str:
    return value.title()


def get_client() -> OpenAI:
    api_key = os.getenv("OPENAI_API_KEY") or st.secrets.get("OPENAI_API_KEY")
    if not api_key:
        raise RuntimeError("OPENAI_API_KEY is not set.")
    return OpenAI(api_key=api_key)


def join_or_none(values: list[str]) -> str:
    cleaned = [display_label(value) for value in values if value]
    return ", ".join(cleaned) if cleaned else "None Specified"


def normalize_process(value: str) -> str:
    if not value or value == "not specified yet":
        return "Not Specified Yet"
    return display_label(value)


def build_prompt(inputs: dict) -> str:
    alcohol_section = ""
    if inputs["category"] == "Alcohol RTD":
        alcohol_section = (
            f"Alcohol Percentage (ABV): {inputs['alcohol_percentage']}\n"
            f"Alcohol Base Preference: {inputs['alcohol_base']}
"
            f"Calorie Target or Range: {inputs['calorie_limit']}
"
        )

    caffeine_section = ""
    if inputs["category"] == "Energy":
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
Desired Ingredients / Notes: {inputs['other_ingredients']}
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
- Suggested Formulation Direction:
  - Sweetener system approach
  - Acid system approach
  - Preservative strategy
  - Key functional ingredients
- Equipment Needed to Manufacture
- Packaging Summary
- Potential Claims / Positioning Ideas
- Key Technical Risks
- Suggested Next Development Step
- Potential Consumer Positioning
- Price Tier Suggestion
- Commercial Viability:
  - Estimated cost positioning (Low / Medium / High)
  - Target retail price range
  - Key cost drivers
- Manufacturing Reality Check:
  - Key manufacturing challenges
  - Shelf-life considerations
  - Process compatibility risks
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

    if inputs["category"] == "Alcohol RTD" and not inputs["alcohol_percentage"]:
        warnings.append("Alcohol RTD selected but alcohol percentage is missing.")

    if inputs["category"] == "Alcohol RTD" and inputs["alcohol_base"] in ["", "None Specified"]:
        warnings.append("Alcohol RTD selected but alcohol base preference is missing.")

    if inputs["category"] == "Alcohol RTD" and not inputs["calorie_limit"]:
        warnings.append("Alcohol RTD selected but calorie target or range is missing.")

    if inputs["category"] == "Hydration" and inputs["carbonation"] == "Carbonated":
        warnings.append("Carbonated hydration concepts are possible, but they may be less typical for mainstream sports hydration positioning.")

    if inputs["category"] == "Energy" and inputs["caffeine"] == "None":
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


logo_path = "logo.png"
logo_col, title_col = st.columns([1, 5])
with logo_col:
    if os.path.exists(logo_path):
        st.image(logo_path, use_container_width=True)
with title_col:
    st.markdown('<div class="hero-card">', unsafe_allow_html=True)
    st.markdown("## BevMan Beverage Concept Studio")
    st.markdown(
        "Generate polished, client-facing beverage concepts for internal ideation, early-stage screening, and customer discussions."
    )
    st.markdown('</div>', unsafe_allow_html=True)

with st.sidebar:
    st.header("About This Tool")
    st.write(
        "Use this concept studio to generate beverage directions based on category, format, ingredient systems, process, and market goals."
    )
    st.markdown(
        "<div class='small-note'>This tool supports concept generation and early-stage direction. Final formulation, regulatory, and commercial decisions still require technical review.</div>",
        unsafe_allow_html=True,
    )
    st.divider()
    st.subheader("Run Locally")
    st.code("py -m streamlit run streamlit_beverage_app.py")
    st.markdown("<div class='small-note'>Optional logo: place a file named <b>logo.png</b> in the project folder to display your company logo.</div>", unsafe_allow_html=True)

category_raw = st.selectbox(
    "Beverage Type",
    ["energy", "hydration", "alcohol rtd"],
    key="category_selector",
    format_func=display_label,
)
category = display_label(category_raw)

input_tab, output_tab = st.tabs(["Project Inputs", "Generated Concept Package"])

with input_tab:
    with st.form("concept_form"):
        with st.expander("Project Details", expanded=True):
            project_col1, project_col2 = st.columns(2)
            with project_col1:
                project_name = st.text_input("Client or Project Name", placeholder="Project Atlas")
            with project_col2:
                project_goal = st.text_input("Primary Goal", placeholder="Launch a clean-label gaming energy drink")

        with st.expander("Product Inputs", expanded=True):
            col1, col2 = st.columns(2)

            with col1:
                flavor = st.text_input("Flavor", placeholder="Tropical Punch")
                market = st.text_input("Target Market", placeholder="Gamers")
                if category == "Energy":
                    caffeine_raw = st.selectbox(
                        "Caffeine Level",
                        ["low", "medium", "high"],
                        format_func=display_label,
                    )
                    caffeine = display_label(caffeine_raw)
                else:
                    caffeine = "Not Applicable"
                carbonation_raw = st.selectbox(
                    "Carbonation",
                    ["carbonated", "non-carbonated"],
                    format_func=display_label,
                )
                carbonation = display_label(carbonation_raw)

            with col2:
                package_type_raw = st.selectbox(
                    "Package Type",
                    ["can", "pet bottle"],
                    format_func=display_label,
                )
                package_type = display_label(package_type_raw)
                package_size = st.text_input("Package Size", placeholder="12 oz")
                process_choice = st.selectbox(
                    "Manufacturing Process",
                    MANUFACTURING_PROCESS_OPTIONS,
                    format_func=display_label,
                    help="Clients often may not know the process. You can leave this as 'Not Specified Yet' or choose an example such as HTST, Aseptic, or Hot Fill.",
                )
                process = normalize_process(process_choice)
                num_concepts = st.selectbox("Number of Concepts", [1, 3, 5], index=1)

            alcohol_percentage = ""
            alcohol_base = ""
            calorie_limit = ""
            if category == "Alcohol RTD":
                alcohol_col1, alcohol_col2, alcohol_col3 = st.columns(3)
                with alcohol_col1:
                    alcohol_percentage = st.text_input("Alcohol Percentage (ABV)", placeholder="5%")
                with alcohol_col2:
                    alcohol_base_options = st.multiselect(
                        "Alcohol Base Options",
                        ALCOHOL_BASE_OPTIONS,
                        format_func=display_label,
                    )
                    alcohol_base = join_or_none(alcohol_base_options)
                with alcohol_col3:
                    calorie_limit = st.text_input("Calorie Target or Range", placeholder="100-120 calories")

        with st.expander("Ingredient System Selection", expanded=True):
            st.caption("Use these selections to identify ingredients or ingredient systems the client wants to include. Use the separate avoidance box for anything they do not want in the concept.")
            sweetener_options = st.multiselect(
                "Sweeteners To Include",
                SWEETENER_OPTIONS,
                format_func=display_label,
            )
            functional_options = st.multiselect(
                "Functional Ingredients To Include",
                FUNCTIONAL_OPTIONS,
                format_func=display_label,
            )

            preservative_col1, preservative_col2 = st.columns(2)
            with preservative_col1:
                natural_preservative_options = st.multiselect(
                    "Natural Preservatives To Include",
                    NATURAL_PRESERVATIVE_OPTIONS,
                    format_func=display_label,
                )
            with preservative_col2:
                artificial_preservative_options = st.multiselect(
                    "Artificial Preservatives To Include",
                    ARTIFICIAL_PRESERVATIVE_OPTIONS,
                    format_func=display_label,
                )

            other_ingredients = st.text_area(
                "Other Desired Ingredients or Notes",
                placeholder="Electrolytes, juice content, natural colors, botanical extracts"
            )
            ingredients_avoid = st.text_area(
                "Ingredients To Avoid",
                placeholder="Erythritol, sodium benzoate, cane sugar"
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
            "process": process,
            "package_type": package_type,
            "package_size": package_size.strip(),
            "num_concepts": num_concepts,
            "alcohol_percentage": alcohol_percentage.strip(),
            "alcohol_base": alcohol_base.strip(),
            "calorie_limit": calorie_limit.strip(),
        }

        missing = [key for key, value in inputs.items() if value == "" and key not in ["alcohol_percentage", "alcohol_base"]]
        if category == "Alcohol RTD" and inputs["alcohol_percentage"] == "":
            missing.append("alcohol_percentage")
        if category == "Alcohol RTD" and inputs["alcohol_base"] in ["", "None Specified"]:
            missing.append("alcohol_base")
        if category == "Alcohol RTD" and inputs["calorie_limit"] == "":
            missing.append("calorie_limit")

        if missing:
            pretty_missing = ", ".join(name.replace("_", " ") for name in missing)
            st.error(f"Please complete all required fields before generating concepts. Missing: {pretty_missing}")
        else:
            warnings = run_checks(inputs)
            st.session_state["bevman_inputs"] = inputs
            st.session_state["bevman_warnings"] = warnings

            try:
                client = get_client()
                with st.spinner("Generating concepts and client-ready summary..."):
                    response = client.responses.create(
                        model="gpt-4.1-mini",
                        input=build_prompt(inputs),
                    )
                output = response.output_text
                st.session_state["bevman_output"] = output
                st.session_state["bevman_filename"] = save_markdown(inputs, output)
                st.success("Concept package generated. Open the 'Generated Concept Package' tab to review it.")
            except Exception as exc:
                st.error(f"Error: {exc}")

with output_tab:
    warnings = st.session_state.get("bevman_warnings", [])
    inputs = st.session_state.get("bevman_inputs")
    output = st.session_state.get("bevman_output")
    filename = st.session_state.get("bevman_filename")

    if warnings:
        st.markdown("### Input Warnings")
        for warning in warnings:
            st.warning(warning)

    if inputs:
        with st.expander("Submitted Project Summary", expanded=True):
            left, right = st.columns(2)
            with left:
                st.write(f"**Project Name:** {inputs['project_name']}")
                st.write(f"**Primary Goal:** {inputs['project_goal']}")
                st.write(f"**Category:** {inputs['category']}")
                st.write(f"**Flavor:** {inputs['flavor']}")
                st.write(f"**Target Market:** {inputs['market']}")
                st.write(f"**Carbonation:** {inputs['carbonation']}")
            with right:
                st.write(f"**Package Type:** {inputs['package_type']}")
                st.write(f"**Package Size:** {inputs['package_size']}")
                st.write(f"**Manufacturing Process:** {inputs['process']}")
                if inputs['category'] == 'Energy':
                    st.write(f"**Caffeine Level:** {inputs['caffeine']}")
                if inputs['category'] == 'Alcohol RTD':
                    st.write(f"**Alcohol Percentage:** {inputs['alcohol_percentage']}")
                    st.write(f"**Alcohol Base:** {inputs['alcohol_base']}")
                    st.write(f"**Calorie Target / Range:** {inputs['calorie_limit']}")

    if output:
        st.markdown("### Client Concept Package")
        st.markdown('<div class="output-card">', unsafe_allow_html=True)
        st.markdown(output)
        st.markdown('</div>', unsafe_allow_html=True)

        if filename and os.path.exists(filename):
            with open(filename, "r", encoding="utf-8") as file:
                st.download_button(
                    label="Download Client Concept Package",
                    data=file.read(),
                    file_name=filename,
                    mime="text/markdown",
                    use_container_width=True,
                )
    else:
        st.info("Generate a concept package from the Project Inputs tab to see the structured output here.")

st.divider()
st.subheader("Recommended Next Phase")
st.write(
    "Next, expand the formula selection logic even further with acid systems, color systems, juice content, claim targets, sweetener loading guidance, and packaging-specific development constraints."
)
