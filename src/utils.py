import random
from typing import List
from src.modules.types import RoadSign

cat_mapping = {
    'regulatory': 'Reglementaire',
    'warning': 'Avertissement',
    'information': 'Informationnel',
}


def select_items(
        choice: List[str],
        viewed: List[str],
        k: int = 3,
) -> List[str]:
    uniq_viewed = set(viewed)
    prob = len(uniq_viewed)/len(choice)
    weights = [min(prob, 0.3) if item in uniq_viewed else 1.0 for item in choice]
    # Check if all weights are zero
    if len(viewed) == 0: return random.choices(choice, k=k)
    return random.choices(choice, weights=weights, k=k)


def format_sign(sign: RoadSign):
    return f"""
*{sign.name}*

*Categorie*: {cat_mapping[sign.category.name.lower()]}
*Description*: {sign.description}

*Règles à suivre :*
{"\n".join([f"- {o}" for o in sign.rules])}

*Lieux typiques :*
{"\n".join([f"- {o}" for o in sign.typical_locations])}

*Forme :* {sign.shape}

*Erreurs courantes :*
{"\n".join([f"- {o}" for o in sign.common_mistakes or []])}
"""
