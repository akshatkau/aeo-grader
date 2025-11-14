def enrich_brand_context(company_name, location, product, industry):
    return {
        "company_name": company_name.strip() if company_name else None,
        "location": location.strip() if location else None,
        "product": product.strip() if product else None,
        "industry": industry.strip().lower() if industry else None,
    }
