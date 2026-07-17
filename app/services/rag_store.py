import re
from typing import List, Dict

# Knowledge base data chunks
KNOWLEDGE_BASE = [
    {
        "id": "wc_general",
        "title": "FIFA World Cup 2026 Overview",
        "content": "The FIFA World Cup 2026 will run from June 11 to July 19, 2026. It is co-hosted by the USA, Canada, and Mexico. A record 48 teams will participate in 104 matches. The tournament features 16 host cities. The opening match is at Estadio Azteca, Mexico City. The Final match is scheduled to take place at MetLife Stadium in New York/New Jersey on July 19, 2026.",
        "tags": ["world cup", "dates", "venues", "teams", "final", "mexico", "canada", "usa"]
    },
    {
        "id": "stadium_gates",
        "title": "MetLife Stadium Gates & Entrances",
        "content": "MetLife Stadium has four main public gates: Gate A (East), Gate B (North), Gate C (West), and Gate D (South). There is also the Verizon VIP Entrance and the HCL Tech Suite Entrance. Gates open 3 hours prior to kickoff. We recommend arriving early as security checks are thorough.",
        "tags": ["gates", "entrances", "gate a", "gate b", "gate c", "gate d", "vip", "hours"]
    },
    {
        "id": "transportation_train",
        "title": "Meadowlands Rail Station & Trains",
        "content": "The NJ Transit Meadowlands Rail Line runs directly to the stadium station. Trains run from Secaucus Junction starting 3.5 hours before kickoff and continue running up to 2 hours after the match ends. Fans are highly encouraged to purchase round-trip train tickets in advance via the NJ Transit app.",
        "tags": ["train", "transit", "transportation", "rail", "secaucus", "nj transit", "subway"]
    },
    {
        "id": "transportation_parking",
        "title": "Parking Lots & Rideshare Info",
        "content": "Parking lots open 5 hours before kickoff. Lots are color-coded: Gold (closest, permits required), Platinum (VIP, permits required), Red, Yellow, and Green (general public parking, must pre-book). The designated Rideshare Zone (Uber/Lyft) is located in Lot E. Bicycle parking racks are available near Gate A and Gate C.",
        "tags": ["parking", "rideshare", "uber", "lyft", "lot e", "bike", "bicycle", "car"]
    },
    {
        "id": "accessibility_services",
        "title": "Accessibility & ADA Services",
        "content": "MetLife Stadium offers comprehensive accessibility services. Wheelchair-accessible seating is available on all levels (Sections 109, 124, 143, 201, 224, 317, 335). Elevators are located at the HCL Suite Entrance and near Gates A, C, and D. Assistive Listening Devices (ALDs) can be checked out at Guest Services booths (Sections 124, 224, 324). Sensory bags containing noise-cancelling headphones and fidget tools are available at guest services for fans with sensory sensitivities.",
        "tags": ["accessibility", "disabled", "wheelchair", "ada", "elevator", "sensory", "deaf", "blind", "guest services"]
    },
    {
        "id": "sustainability_waste",
        "title": "Sustainability & Recycling Guidelines",
        "content": "MetLife Stadium is a Zero-Waste partner for FIFA 2026. All beverage cups served inside are 100% compostable. Cans (aluminum) and plastic bottles go into the Blue Recycle bins. Food remains, napkins, and cups must go into the Green Compost bins. Non-recyclable packaging goes into the Gray Landfill bins. Fans get points for using correct bins by scanning QR codes on the containers.",
        "tags": ["sustainability", "recycle", "compost", "green", "waste", "carbon", "eco", "plastic", "cup", "can"]
    },
    {
        "id": "sustainability_energy",
        "title": "Stadium Eco-Footprint & Renewable Energy",
        "content": "MetLife Stadium utilizes 1,350 solar panels on its canopy to generate clean energy, powering stadium ring lights and operations. Waterless urinals and low-flow plumbing systems reduce water consumption by 25%. Organic grass clipping turf is composted locally. By utilizing public transit (Meadowlands Rail Line), fans reduce transit emissions by 80% compared to individual cars.",
        "tags": ["sustainability", "solar", "energy", "water", "carbon", "eco-friendly", "emissions"]
    },
    {
        "id": "emergency_protocols",
        "title": "Emergency, Lost & Found, and First Aid",
        "content": "First Aid stations are staffed by medical personnel and located at Sections 109, 131, 201, 227, 309, and 331. A designated Lost Children area is situated at the Guest Services Center (Section 124). In case of evacuation alerts, follow stadium screens, audio announcements, and directions from volunteers in neon green vests.",
        "tags": ["emergency", "first aid", "doctor", "lost", "child", "evacuation", "safety", "police"]
    },
    {
        "id": "volunteer_guidelines",
        "title": "Volunteer Operations & Coordination Guide",
        "content": "Volunteers are the backbone of the tournament. They wear Neon Green Vests. Daily shifts begin 4 hours before kickoff. Check-in is at the Volunteer Hub in Lot C. Volunteers are responsible for crowd routing, accessibility escorting, ticket scanning support, and language interpretation. Emergency line for volunteers is *55 from any stadium intercom or dial extension 2026 from the internal phone system.",
        "tags": ["volunteer", "shift", "vest", "hub", "lot c", "tasks", "emergency", "coordinator"]
    },
    {
        "id": "prohibited_items",
        "title": "Prohibited Items & Bag Policy",
        "content": "All bags must be clear plastic, vinyl, or PVC, not exceeding 12in x 6in x 12in. Small clutch bags (4.5in x 6.5in) are allowed. Prohibited items include: umbrellas, video cameras, recording devices, selfie sticks, banners/flags larger than 3ft x 5ft, laptops, outside food/beverages, and noise makers (vuvuzelas). Strollers are permitted but must be checked at Guest Services.",
        "tags": ["prohibited", "bag", "clear bag", "umbrella", "camera", "food", "stroller", "security"]
    }
]

def search_rag(query: str, limit: int = 3) -> str:
    """
    Search the local knowledge base using a token overlap ranking.
    Returns a formatted context string for LLM prompting.
    """
    query_tokens = set(re.findall(r'\w+', query.lower()))
    if not query_tokens:
        # Return default general context if query is empty/short
        return "\n\n".join([f"[{chunk['title']}]: {chunk['content']}" for chunk in KNOWLEDGE_BASE[:2]])
    
    scored_chunks = []
    for chunk in KNOWLEDGE_BASE:
        score = 0
        # Match inside title, content and tags
        text_to_search = f"{chunk['title']} {chunk['content']} {' '.join(chunk['tags'])}".lower()
        for token in query_tokens:
            if len(token) > 2:  # Skip tiny words like to, an, is, on
                score += text_to_search.count(token)
                # Boost weight if word in tags or title
                if token in chunk['tags']:
                    score += 2
                if token in chunk['title'].lower():
                    score += 3
        
        if score > 0:
            scored_chunks.append((score, chunk))
            
    # Sort by score descending
    scored_chunks.sort(key=lambda x: x[0], reverse=True)
    
    # Take top results
    results = [chunk for _, chunk in scored_chunks[:limit]]
    
    # Fallback to general chunks if nothing matches
    if not results:
        results = KNOWLEDGE_BASE[:2]
        
    context_str = ""
    for r in results:
        context_str += f"### {r['title']}\n{r['content']}\n\n"
        
    return context_str.strip()
