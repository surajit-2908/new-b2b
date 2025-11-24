from math import ceil

def paginate(query, page: int, limit: int):
    """
    Reusable pagination helper for SQLAlchemy queries.
    
    Returns:
        items      → list of results
        meta       → pagination metadata
    """
    total = query.count()
    page = max(page, 1)

    items = (
        query.offset((page - 1) * limit)
             .limit(limit)
             .all()
    )

    meta = {
        "total": total,
        "page": page,
        "limit": limit,
        "pages": ceil(total / limit) if limit else 1
    }

    return items, meta
