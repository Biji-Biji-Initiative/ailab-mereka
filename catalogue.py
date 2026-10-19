"""The AI Lab programme catalogue, as the pages state it, for structured data.

One source for the Course entries build.py emits on Home, Corporate and
Public. Everything here must match what the visible page says: a price only
appears where the page shows that price, and dates are left out on purpose,
because the public schedule moves and stale dates in a rich result are worse
than none.

Source of truth for the programmes: "AI Lab Main Catalogue.pptx" slides 12-20
(numbering, module counts) and Ambika's "Website Copy (v2)" doc (wording).
"""

PROD = "https://ailab.mereka.io"
ORG = {"@id": PROD + "/#organisation"}

# Public cohorts run at Mereka @ Publika (the address on the mereka.io listings).
PUBLIKA = {
    "@type": "Place", "name": "Mereka @ Publika",
    "address": {"@type": "PostalAddress", "streetAddress": "Publika Shopping Gallery, Solaris Dutamas",
                "addressLocality": "Kuala Lumpur", "postalCode": "50480",
                "addressRegion": "Wilayah Persekutuan Kuala Lumpur", "addressCountry": "MY"},
}

# key, number, name, page anchor, level, duration (ISO 8601), workload, prerequisite, summary, teaches
PROGRAMMES = [
    dict(key="foundation-half", n=1, name="AI Foundation (Level 1) — Half Day", anchor="programmes",
         level="Beginner", duration="PT4H", prereq="None",
         desc="The starting point. No jargon, no prerequisites: AI at work and its responsibilities, "
              "prompting from fundamentals to advanced techniques, and when to trust AI agents.",
         teaches=["Responsible AI use, ethics and compliance", "Structured prompting",
                  "Chatbots, assistants and agents"]),
    dict(key="foundation-full", n=1, name="AI Foundation (Level 1) — Full Day", anchor="programmes",
         level="Beginner", duration="PT8H", prereq="None",
         desc="Everything in the half day, plus understanding data as the foundation of good AI and "
              "AI security: threats, safety and reporting.",
         teaches=["Responsible AI use, ethics and compliance", "Understanding data for AI",
                  "Structured prompting", "Chatbots, assistants and agents", "AI security"]),
    dict(key="practitioner", n=2, name="AI Practitioner (Level 2)", anchor="pathway",
         level="Intermediate", duration="P2D", prereq="AI Foundation (Level 1)",
         desc="From experimenting to executing. For staff already using AI who need consistent, "
              "reliable results: data cleaning, AI-powered analysis, prompts for assistants and agents, "
              "automations, and monitoring AI output quality.",
         teaches=["Data cleaning and qualification", "AI-powered analysis",
                  "Prompting assistants and agents", "Building automations with agents",
                  "Monitoring AI outputs"]),
    dict(key="specialist", n=3, name="AI Specialist (Level 3)", anchor="pathway",
         level="Intermediate", duration="P2D", prereq="AI Practitioner (Level 2)",
         desc="From personal use to team-wide impact: data pipelines, production prompting, "
              "assistants grounded in your own data, production automations and monitoring at scale.",
         teaches=["Data pipelines", "Production prompting", "Knowledge-grounded assistants",
                  "Production automations", "Monitoring AI at scale"]),
    dict(key="integrator", n=4, name="AI Integrator (Level 4)", anchor="pathway",
         level="Advanced", duration="P2D", prereq="AI Specialist (Level 3)",
         desc="Connect AI to your systems: Model Context Protocol, securing AI integrations, "
              "automation workflows with n8n, scaling automations and open-source AI for enterprise.",
         teaches=["Model Context Protocol", "Securing AI integrations", "n8n automation workflows",
                  "Scaling automations", "Open-source AI tools"]),
    dict(key="architect", n=5, name="AI Architect (Level 5)", anchor="pathway",
         level="Advanced", duration="P2D", prereq="AI Integrator (Level 4)",
         desc="Build AI your organisation can trust: end-to-end AI system design, persistent knowledge "
              "systems, testing and guardrails, compliance and security, and domain fine-tuning.",
         teaches=["AI system design", "Persistent knowledge systems", "Testing and guardrails",
                  "AI compliance and security", "Model fine-tuning"]),
    dict(key="leadership", n=6, name="AI Leadership (Level 6)", anchor="leadership",
         level="Executive", duration="P2D", prereq="None; no technical background needed",
         desc="A standalone programme for senior leaders who govern AI rather than operate it: why AI "
              "fails differently, board-level AI exposure, investment and workforce decisions, legal versus "
              "responsible, and Malaysia's AI landscape.",
         teaches=["AI risk and failure modes", "Board-level AI exposure", "AI investment decisions",
                  "Responsible AI governance", "Malaysia's AI landscape"]),
    dict(key="deep-dive", n=7, name="AI Tool Deep Dive", anchor="programmes",
         level="Beginner", duration="PT4H", prereq="None",
         desc="Pick a tool and get great at it: ChatGPT, Microsoft Copilot, Claude, Gemini or Canva AI. "
              "Tool orientation, core workflows, advanced features and daily integration.",
         teaches=["ChatGPT", "Microsoft Copilot", "Claude", "Google Gemini", "Canva AI"]),
    dict(key="custom", n=8, name="Custom Solutions", anchor="custom-solutions",
         level="All levels", duration="PT8H", prereq="None",
         desc="Department-specific AI training built around your team's real workflows, documents and "
              "data, across sales, marketing, operations, support, HR, finance, legal and procurement.",
         teaches=["Department-specific AI workflows"]),
]

# In-house group prices the Corporate page shows (base group of up to 20).
INHOUSE_PRICE = {"foundation-half": "4500", "foundation-full": "7000", "deep-dive": "3000"}

# Public seats the Public page sells, each with its own mereka.io listing.
PUBLIC_SEATS = [
    ("foundation-half", "AI Foundation (Level 1) — Half Day", "450", "ai-foundation-half-day"),
    ("foundation-full", "AI Foundation (Level 1) — Full Day", "700", "ai-foundation-full-day"),
    ("deep-dive", "AI Tool Deep Dive: ChatGPT", "300", "ai-tool-deep-dive-chatgpt"),
    ("deep-dive", "AI Tool Deep Dive: Microsoft Copilot", "300", "ai-tool-deep-dive-microsoft-copilot"),
    ("deep-dive", "AI Tool Deep Dive: Claude", "300", "ai-tool-deep-dive-claude"),
    ("deep-dive", "AI Tool Deep Dive: Gemini", "300", "ai-tool-deep-dive-gemini"),
    ("deep-dive", "AI Tool Deep Dive: Canva AI", "300", "ai-tool-deep-dive-canva-ai"),
]
BY_KEY = {p["key"]: p for p in PROGRAMMES}


def _course(p, page, name=None, offers=None, mode="Onsite", location=None):
    inst = {"@type": "CourseInstance", "courseMode": mode, "courseWorkload": p["duration"]}
    if location:
        inst["location"] = location
    c = {"@type": "Course", "name": name or p["name"], "description": p["desc"],
         "url": f"{PROD}{page}#{p['anchor']}", "provider": ORG, "inLanguage": "en-MY",
         "educationalLevel": p["level"], "timeRequired": p["duration"],
         "coursePrerequisites": p["prereq"], "teaches": p["teaches"],
         "isAccessibleForFree": False, "hasCourseInstance": [inst]}
    if offers:
        c["offers"] = offers
    return c


def corporate_courses():
    """All eight programmes. Only Foundation and the Deep Dive show a price there."""
    out = []
    for p in PROGRAMMES:
        offer = None
        if p["key"] in INHOUSE_PRICE:
            offer = {"@type": "Offer", "category": "In-house group (up to 20 participants)",
                     "price": INHOUSE_PRICE[p["key"]], "priceCurrency": "MYR",
                     "availability": "https://schema.org/InStock",
                     "url": f"{PROD}/corporate-training/#{p['anchor']}"}
        out.append(_course(p, "/corporate-training/", offers=offer, mode="Onsite"))
    return out


def public_courses():
    """The seven bookable public seats, each pointing at its mereka.io listing."""
    out = []
    for key, name, price, slug in PUBLIC_SEATS:
        p = BY_KEY[key]
        offer = {"@type": "Offer", "category": "Public seat (per participant)",
                 "price": price, "priceCurrency": "MYR",
                 "availability": "https://schema.org/InStock",
                 "url": f"https://mereka.io/experience/{slug}"}
        out.append(_course(p, "/public-training/", name=name, offers=offer,
                           mode="Onsite", location=PUBLIKA))
    return out


def item_list(name, courses):
    return {"@type": "ItemList", "name": name, "numberOfItems": len(courses),
            "itemListElement": [{"@type": "ListItem", "position": i, "item": c}
                                for i, c in enumerate(courses, 1)]}
