from app.services.product_catalog import get_product, list_products, load_catalog
from app.services.product_report import build_product_report
from app.services.saju_engine import SajuEngine
from datetime import date


def test_catalog_loaded():
    cat = load_catalog()
    assert len(cat.get("products") or []) >= 50
    assert cat.get("menu")
    items = list_products()
    assert len(items) == len(cat["products"])
    p = items[0]
    assert get_product(p["id"]) is not None


def test_product_report_sections():
    cat = load_catalog()
    p = cat["products"][0]
    r = SajuEngine().calculate(date(1990, 8, 27), 8, 0, "male")
    rep = build_product_report(p, r, date(1990, 8, 27), "male", display_name="테스트")
    assert rep["sections"]
    assert rep["header"]["day_master"]
    assert "FortuneOne" in rep["disclaimer"] or "자체" in rep["disclaimer"] or "규칙" in rep["disclaimer"]
