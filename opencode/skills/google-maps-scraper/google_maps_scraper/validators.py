"""Google Maps Scraper - Validadores de Dados."""
from typing import Dict, Any, List
import re
from urllib.parse import urlparse


def validate_place_data(place: Dict[str, Any], must_have_website: bool = True) -> bool:
    """
    Valida se o lead tem dados mínimos para prospecção.
    """
    # Nome obrigatório
    if not place.get("name") or len(place["name"].strip()) < 2:
        return False
    
    # Endereço ou localização
    if not place.get("address") and not (place.get("latitude") and place.get("longitude")):
        return False
    
    # Website se obrigatório
    if must_have_website:
        website = place.get("website")
        if not website or not _is_valid_url(website):
            return False
        
        # Filtrar domínios que não são sites de negócio
        if _is_non_business_domain(website):
            return False
    
    # Rating mínimo (se disponível)
    rating = place.get("rating")
    if rating is not None and rating < 3.0:
        return False
    
    return True


def _is_valid_url(url: str) -> bool:
    """Valida se URL é bem formada."""
    try:
        result = urlparse(url)
        return all([result.scheme in ("http", "https"), result.netloc])
    except:
        return False


def _is_non_business_domain(url: str) -> bool:
    """Filtra domínios que não são sites de negócio próprios."""
    non_business = [
        "facebook.com", "instagram.com", "linkedin.com", "twitter.com", "x.com",
        "youtube.com", "tiktok.com", "pinterest.com",
        "google.com", "maps.google.com", "goo.gl",
        "waze.com", "yelp.com", "tripadvisor.com", "foursquare.com",
        "wikipedia.org", "wikidata.org",
        "blogspot.com", "wordpress.com", "medium.com",
        "linktr.ee", "bio.link", "linkin.bio",
    ]
    
    domain = urlparse(url).netloc.lower().replace("www.", "")
    return any(nb in domain for nb in non_business)


def enrich_with_domain_info(place: Dict[str, Any]) -> Dict[str, Any]:
    """Adiciona info do domínio (TLD, subdomínio, etc)."""
    website = place.get("website")
    if website:
        parsed = urlparse(website)
        place["domain"] = parsed.netloc.lower().replace("www.", "")
        place["tld"] = "." + place["domain"].split(".")[-1] if "." in place["domain"] else ""
        place["is_br_domain"] = place["tld"] == ".br" or place["domain"].endswith(".com.br")
    return place


def clean_phone(phone: str) -> str:
    """Limpa e formata telefone brasileiro."""
    if not phone:
        return ""
    # Remove tudo que não é dígito
    digits = re.sub(r"\D", "", phone)
    # Formata se for brasileiro válido
    if len(digits) == 11 and digits.startswith(("11", "12", "13", "14", "15", "16", "17", "18", "19",
                                                  "21", "22", "24", "27", "28",
                                                  "31", "32", "33", "34", "35", "37", "38",
                                                  "41", "42", "43", "44", "45", "46", "47", "48", "49",
                                                  "51", "53", "54", "55",
                                                  "61", "62", "63", "64", "65", "66", "67", "68", "69",
                                                  "71", "73", "74", "75", "77", "79",
                                                  "81", "82", "83", "84", "85", "86", "87", "88", "89",
                                                  "91", "92", "93", "94", "95", "96", "97", "98", "99")):
        return f"({digits[:2]}) {digits[2:7]}-{digits[7:]}"
    elif len(digits) == 10:
        return f"({digits[:2]}) {digits[2:6]}-{digits[6:]}"
    return phone


def normalize_categories(categories: List[str]) -> List[str]:
    """Normaliza categorias do Google Places."""
    mapping = {
        "psychologist": "psicólogo",
        "mental_health_clinic": "clínica_saúde_mental",
        "clinic": "clínica",
        "doctor": "médico",
        "dentist": "dentista",
        "physiotherapist": "fisioterapeuta",
        "nutritionist": "nutricionista",
        "lawyer": "advogado",
        "accountant": "contador",
        "real_estate_agency": "imobiliária",
        "marketing_agency": "agência_marketing",
        "advertising_agency": "agência_publicidade",
        "seo_agency": "agência_seo",
        "web_design": "web_design",
        "software_company": "empresa_software",
    }
    
    normalized = []
    for cat in categories:
        cat_lower = cat.lower().replace(" ", "_")
        normalized.append(mapping.get(cat_lower, cat_lower))
    
    return list(set(normalized))