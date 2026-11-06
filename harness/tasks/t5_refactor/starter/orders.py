"""Order processing (legacy module)."""


def process_orders(orders, inventory, discounts):
    """Process orders in sequence against inventory.

    orders:    list of dicts {"id": int, "customer": str, "items": [{"sku": str, "qty": int}], "coupon": str (optional)}
    inventory: dict sku -> {"price": float, "stock": int}; it is NOT mutated
    discounts: dict coupon code -> percent off (int)
    returns:   {"fulfilled": [{"id", "customer", "total"}], "rejected": [{"id", "reason"}],
                "revenue": float, "inventory": updated copy of inventory}
    """
    results = {"fulfilled": [], "rejected": [], "revenue": 0.0}
    inv = {}
    for k in inventory:
        inv[k] = {"price": inventory[k]["price"], "stock": inventory[k]["stock"]}
    for o in orders:
        ok = True
        reason = None
        total = 0.0
        for it in o["items"]:
            if it["sku"] not in inv:
                ok = False
                reason = "unknown sku " + it["sku"]
                break
            if it["qty"] <= 0:
                ok = False
                reason = "bad qty"
                break
            if inv[it["sku"]]["stock"] < it["qty"]:
                ok = False
                reason = "out of stock " + it["sku"]
                break
            total = total + inv[it["sku"]]["price"] * it["qty"]
        if ok:
            if "coupon" in o and o["coupon"]:
                if o["coupon"] in discounts:
                    total = total - total * discounts[o["coupon"]] / 100.0
                else:
                    ok = False
                    reason = "bad coupon"
        if ok:
            for it in o["items"]:
                inv[it["sku"]]["stock"] = inv[it["sku"]]["stock"] - it["qty"]
            total = round(total, 2)
            results["fulfilled"].append({"id": o["id"], "customer": o["customer"], "total": total})
            results["revenue"] = round(results["revenue"] + total, 2)
        else:
            results["rejected"].append({"id": o["id"], "reason": reason})
    results["inventory"] = inv
    return results
