"""
seed.py — inserts sample NominationRules so you can test comparisons
without needing real RulesDB data.

Field names match the real RulesDB schema.
"""
from clauseguard.database.schema import get_connection

SAMPLE_RULES = [
    {
        "AgreementGuid":             "AGR-001",
        "AgreementName":             "Solace-Harbor-DES-2024",
        "TradeGroupId":              "TG-100",
        "TradeName":                 "LNG Cargo Q3-2024",
        "NominationRuleId":          "NR-001",
        "NominationRuleDescription": "Buyer may narrow the delivery window no later than 14 days prior to the start of the initial delivery window.",
        "AgreementSection":          "ArrivalWindow",
        "OptionOwner":               "counterparty",
        "AnchorType":                "InitialWindow",
        "Complexity":                "SimpleAnchor",
        "AnchorDirection":           "Before",
        "NominationRuleTitle":       "Solace-Harbor-DES-2024 * counterparty shall nom * ArrivalWindow",
        "DateExpression":            None,
        "TargetDate":                None,
    },
    {
        "AgreementGuid":             "AGR-001",
        "AgreementName":             "Solace-Harbor-DES-2024",
        "TradeGroupId":              "TG-100",
        "TradeName":                 "LNG Cargo Q3-2024",
        "NominationRuleId":          "NR-002",
        "NominationRuleDescription": "Seller shall nominate the vessel no later than 5 days prior to the start of the sales window.",
        "AgreementSection":          "Vessel",
        "OptionOwner":               "seller",
        "AnchorType":                "SalesWindow",
        "Complexity":                "SimpleAnchor",
        "AnchorDirection":           "Before",
        "NominationRuleTitle":       "Solace-Harbor-DES-2024 * seller shall nom * Vessel",
        "DateExpression":            None,
        "TargetDate":                None,
    },
    {
        "AgreementGuid":             "AGR-002",
        "AgreementName":             "Solace-Meridian-FOB-2024",
        "TradeGroupId":              "TG-200",
        "TradeName":                 "LNG Cargo FOB Q4-2024",
        "NominationRuleId":          "NR-003",
        "NominationRuleDescription": "Buyer shall nominate the load quantity no later than 10 days after the start of the initial window.",
        "AgreementSection":          "Quantity",
        "OptionOwner":               "counterparty",
        "AnchorType":                "InitialWindow",
        "Complexity":                "SimpleAnchor",
        "AnchorDirection":           "After",
        "NominationRuleTitle":       "Solace-Meridian-FOB-2024 * counterparty shall nom * Quantity",
        "DateExpression":            None,
        "TargetDate":                None,
    },
]


def seed():
    conn = get_connection()
    cur = conn.cursor()
    cur.executemany("""
        INSERT INTO NominationRules (
            AgreementGuid, AgreementName, TradeGroupId, TradeName, NominationRuleId,
            NominationRuleDescription, AgreementSection, OptionOwner, AnchorType,
            Complexity, AnchorDirection, NominationRuleTitle, DateExpression, TargetDate
        ) VALUES (
            :AgreementGuid, :AgreementName, :TradeGroupId, :TradeName, :NominationRuleId,
            :NominationRuleDescription, :AgreementSection, :OptionOwner, :AnchorType,
            :Complexity, :AnchorDirection, :NominationRuleTitle, :DateExpression, :TargetDate
        )
    """, SAMPLE_RULES)
    conn.commit()
    conn.close()
    print(f"Seeded {len(SAMPLE_RULES)} nomination rules.")


if __name__ == "__main__":
    seed()
