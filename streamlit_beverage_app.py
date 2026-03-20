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

SWEETENER_STRATEGY_OPTIONS = [
    "not specified yet",
    "natural only",
    "artificial allowed",
    "blend for taste",
    "zero sugar focus",
    "cost optimized",
    "premium taste focus",
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

SUGAR_TARGET_OPTIONS = [
    "not specified yet",
    "zero sugar",
    "low sugar",
    "reduced sugar",
    "full sugar",
]

CARB_TARGET_OPTIONS = [
    "not specified yet",
    "0g carbs",
    "low carb",
    "moderate carb",
    "higher carb",
]

ACID_SYSTEM_OPTIONS = [
    "not specified yet",
    "citric acid",
    "malic acid",
    "phosphoric acid",
    "tartaric acid",
    "lactic acid",
    "citric + malic blend",
]

CLAIM_TARGET_OPTIONS = [
    "zero sugar",
    "low calorie",
    "natural",
    "clean label",
    "no artificial sweeteners",
    "electrolyte support",
    "energy support",
    "recovery support",
    "premium",
    "mass market",
    "better-for-you",
]

JUICE_CONTENT_OPTIONS = [
    "not specified yet",
    "no juice",
    "splash of juice",
    "1-5% juice",
    "5-10% juice",
    "juice-forward",
]

COLOR_APPEARANCE_OPTIONS = [
    "not specified yet",
    "clear",
    "light tint",
    "bold color",
    "natural color only",
    "artificial color allowed",
    "cloudy / juice-style appearance",
]


def display_label(value: str) -> str:
    parts = value.split()
    out = []
    for p in parts:
        if p.lower() == "rtd":
            out.append("RTD")
        elif p.lower() == "b":
            out.append("B")
        elif p.lower() == "hfcs":
            out.append("HFCS")
        else:
            out.append(p.capitalize())
    return " ".join(out)


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


def normalize_choice(value: str) -> str:
    if not value or value == "not specified yet":
        return "Not Specified Yet"
    return display_label(value)


def build_prompt(inputs: dict) -> str:
    alcohol_section = ""
    if inputs["category"] == "Alcohol RTD":
        alcohol_section = (
            f"Alcohol Percentage (ABV): {inputs['alcohol_percentage']}\n"
            f"Alcohol Base Preference: {inputs['alcohol_base']}\n"
            f"Calorie Target or Range: {inputs['calorie_limit']}\n"
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
{caffeine_section}Sugar Target: {inputs['sugar_target']}
Carbohydrate Target: {inputs['carb_target']}
Acid System Preference: {inputs['acid_system']}
Sweetener Strategy: {inputs['sweetener_strategy']}
Juice Content Preference: {inputs['juice_content']}
Color / Appearance Direction: {inputs['color_appearance']}
Claim Targets: {inputs['claim_targets']}
Sweetener Preferences: {inputs['sweeteners']}
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
- Follow the beverage type, carbonation, manufacturing process, package format, sugar target, carb target, acid system, sweetener strategy, juice content, appearance direction, claim targets, and alcohol targets exactly when provided.
- Do not include any ingredients listed in "Ingredients to Avoid."
- If any requirements conflict, clearly point out the conflict before generating concepts.
- Do not invent technical claims unless they are clearly labeled as suggestions.
- Keep the concepts realistic for commercial beverage development.
- Prioritize feasibility over creativity.
- Avoid generic language and be commercially realistic.
- Write in a polished, client-facing tone.
- Be specific and commercially realistic.
- Call out technical tensions clearly instead of smoothing over them.
- Prefer feasible formulation direction over overly creative ideas.

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
  - Juice strategy
  - Appearance / color direction
  - Claim-fit considerations
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
- Claim Feasibility Score (1-10)
- Claim Conflicts or Tensions
- Formulation Compatibility Notes
- Flavor System Strategy:
  - Top note direction
  - Mid-palate direction
  - Finish profile
  - Masking considerations

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

    if inputs["category"] == "Energy" and inputs["sugar_target"] == "Zero Sugar" and inputs["sweeteners"] == "None Specified":
        warnings.append("Zero Sugar was selected without a sweetener direction. Consider selecting sweeteners to guide formulation direction.")

    if inputs["claim_targets"] != "None Specified" and "Zero Sugar" in inputs["claim_targets"] and inputs["sugar_target"] not in ["Zero Sugar", "Not Specified Yet"]:
        warnings.append("Claim target includes Zero Sugar, but sugar target does not match that direction.")

    if inputs["claim_targets"] != "None Specified" and "Low Calorie" in inputs["claim_targets"] and inputs["category"] == "Alcohol RTD" and inputs["calorie_limit"] == "":
        warnings.append("Low Calorie claim target is selected for Alcohol RTD, but no calorie target was provided.")

    if inputs["claim_targets"] != "None Specified" and "Natural" in inputs["claim_targets"] and inputs["artificial_preservatives"] != "None Specified":
        warnings.append("Natural claim target is selected, but artificial preservatives were also selected.")

    if inputs["claim_targets"] != "None Specified" and "No Artificial Sweeteners" in inputs["claim_targets"]:
        artificial_sweeteners = ["Sucralose"]
        selected = inputs["sweeteners"]
        if any(item in selected for item in artificial_sweeteners):
            warnings.append("No Artificial Sweeteners claim target is selected, but the sweetener selection includes Sucralose.")

    if inputs["juice_content"] == "No Juice" and "juice" in inputs["other_ingredients"].lower():
        warnings.append("Juice content is set to No Juice, but other desired ingredients mention juice.")

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

                if category_raw == "energy":
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

                sugar_target_raw = st.selectbox(
                    "Sugar Target",
                    SUGAR_TARGET_OPTIONS,
                    format_func=display_label,
                )
                sugar_target = normalize_choice(sugar_target_raw)

                carb_target_raw = st.selectbox(
                    "Carbohydrate Target",
                    CARB_TARGET_OPTIONS,
                    format_func=display_label,
                )
                carb_target = normalize_choice(carb_target_raw)

                juice_content_raw = st.selectbox(
                    "Juice Content Preference",
                    JUICE_CONTENT_OPTIONS,
                    format_func=display_label,
                )
                juice_content = normalize_choice(juice_content_raw)

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
                    help="Clients may not know the process. Leave as Not Specified Yet or choose an example like HTST, Aseptic, or Hot Fill.",
                )
                process = normalize_process(process_choice)

                acid_system_raw = st.selectbox(
                    "Acid System Preference",
                    ACID_SYSTEM_OPTIONS,
                    format_func=display_label,
                    help="This helps guide flavor brightness, tartness, and formulation direction.",
                )
                acid_system = normalize_choice(acid_system_raw)

                color_appearance_raw = st.selectbox(
                    "Color / Appearance Direction",
                    COLOR_APPEARANCE_OPTIONS,
                    format_func=display_label,
                )
                color_appearance = normalize_choice(color_appearance_raw)

                num_concepts = st.selectbox("Number of Concepts", [1, 3, 5], index=1)

            alcohol_percentage = ""
            alcohol_base = ""
            calorie_limit = ""

            if category_raw == "alcohol rtd":
                alcohol_col1, alcohol_col2, alcohol_col3 = st.columns(3)

                with alcohol_col1:
                    alcohol_percentage = st.text_input(
                        "Alcohol Percentage (ABV)",
                        placeholder="5%"
                    )

                with alcohol_col2:
                    alcohol_base_options = st.multiselect(
                        "Alcohol Base Options",
                        ALCOHOL_BASE_OPTIONS,
                        format_func=display_label,
                    )
                    alcohol_base = join_or_none(alcohol_base_options)

                with alcohol_col3:
                    calorie_limit = st.text_input(
                        "Calorie Target or Range",
                        placeholder="100-120 calories"
                    )

        with st.expander("Ingredient System Selection", expanded=True):
            st.caption("Use these selections to identify ingredients the client wants to include. Use the separate avoidance box for anything they do not want.")

            sweetener_options = st.multiselect(
                "Sweeteners To Include",
                SWEETENER_OPTIONS,
                format_func=display_label,
            )

            sweetener_strategy_raw = st.selectbox(
                "Sweetener Strategy",
                SWEETENER_STRATEGY_OPTIONS,
                format_func=display_label,
                help="Use this to guide whether the concept should focus on natural systems, zero sugar systems, cost, or premium taste.",
            )
            sweetener_strategy = normalize_choice(sweetener_strategy_raw)

            functional_options = st.multiselect(
                "Functional Ingredients To Include",
                FUNCTIONAL_OPTIONS,
                format_func=display_label,
            )

            claim_target_options = st.multiselect(
                "Claim Targets",
                CLAIM_TARGET_OPTIONS,
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

        submitted = st.form_submit_button(
            "Generate Client-Ready Concepts",
            use_container_width=True
        )

    if submitted:
        inputs = {
            "project_name": project_name.strip(),
            "project_goal": project_goal.strip(),
            "flavor": flavor.strip(),
            "market": market.strip(),
            "category": category,
            "caffeine": caffeine,
            "sugar_target": sugar_target,
            "carb_target": carb_target,
            "acid_system": acid_system,
            "sweetener_strategy": sweetener_strategy,
            "juice_content": juice_content,
            "color_appearance": color_appearance,
            "claim_targets": join_or_none(claim_target_options),
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

        missing = [key for key, value in inputs.items() if value == "" and key not in ["alcohol_percentage", "alcohol_base", "calorie_limit"]]
        if category_raw == "alcohol rtd" and inputs["alcohol_percentage"] == "":
            missing.append("alcohol_percentage")
        if category_raw == "alcohol rtd" and inputs["alcohol_base"] in ["", "None Specified"]:
            missing.append("alcohol_base")
        if category_raw == "alcohol rtd" and inputs["calorie_limit"] == "":
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
                st.write(f"**Sugar Target:** {inputs['sugar_target']}")
                st.write(f"**Carbohydrate Target:** {inputs['carb_target']}")
                st.write(f"**Acid System:** {inputs['acid_system']}")
                st.write(f"**Juice Content:** {inputs['juice_content']}")
            with right:
                st.write(f"**Package Type:** {inputs['package_type']}")
                st.write(f"**Package Size:** {inputs['package_size']}")
                st.write(f"**Manufacturing Process:** {inputs['process']}")
                st.write(f"**Claim Targets:** {inputs['claim_targets']}")
                st.write(f"**Sweetener Strategy:** {inputs['sweetener_strategy']}")
                st.write(f"**Color / Appearance:** {inputs['color_appearance']}")
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
    "Next, expand the formula selection logic even further with claim-specific scoring, ingredient compatibility guidance, flavor system direction, and packaging-specific development constraints."
)
