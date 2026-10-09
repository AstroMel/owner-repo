window.WHEELIE_QUEUE = [
  {
    "id": 1,
    "sender": "Dana Whitfield <dana@sunshinewholesale.example>",
    "subject": "Wholesale SUVs for our lot",
    "excerpt": "Hello, we are looking to buy 20 SUVs this month, mostly Toyota and Honda. Our dealer license is VW12345. Do you have any available?",
    "category": "lead",
    "optOut": false,
    "score": 95,
    "tier": "hot",
    "action": "draft",
    "reasons": [
      "+50 verified VW license",
      "+15 names a vehicle",
      "+15 mentions volume",
      "+5 classified as lead",
      "+10 registered address looks like a real office"
    ],
    "license": {
      "status": "verified",
      "business": "Sunshine Wholesale Autos LLC",
      "type": "VW",
      "number": "VW12345",
      "notes": [
        "license VW12345 matches Sunshine Wholesale Autos LLC",
        "active, eligible type",
        "sender domain matches"
      ]
    },
    "draft": {
      "to": "dana@sunshinewholesale.example",
      "subject": "Re: Wholesale SUVs for our lot",
      "body": "Hello Dana,\n\nThank you for reaching out to Wheelie Wholesale.\n\nWe have received your note about the vehicles you are looking for and would be glad to help.\n\nTo make sure we match you with the right inventory, could you tell us the makes, models and quantities you are after, and your preferred timing?\n\nKind regards,\nAlex Morgan\n\n--\nWheelie Wholesale\n100 Sample Street, Orlando, FL 32801\n(407) 555-0100\n\nIf you would rather not hear from us, reply \"STOP\" and we will remove you right away.",
      "needsReview": false
    }
  },
  {
    "id": 2,
    "sender": "Marcus Bell <marcus@palmmotors.example>",
    "subject": "Interested in your trucks",
    "excerpt": "I want to buy 30 trucks over the next quarter. Do you have any available? Palm Motors.",
    "category": "lead",
    "optOut": false,
    "score": 65,
    "tier": "warm",
    "action": "review",
    "reasons": [
      "+20 partial license match, needs a person to confirm",
      "+15 names a vehicle",
      "+15 mentions volume",
      "+5 classified as lead",
      "+10 registered address looks like a real office"
    ],
    "license": {
      "status": "review",
      "business": "Palm Motors Inc",
      "type": "VI",
      "number": "VI22222",
      "notes": [
        "sender domain palmmotors.example matches Palm Motors Inc; no license number given"
      ]
    },
    "draft": {
      "to": "marcus@palmmotors.example",
      "subject": "Re: Interested in your trucks",
      "body": "Hello Marcus,\n\nThank you for reaching out to Wheelie Wholesale.\n\nWe have received your note about the vehicles you are looking for and would be glad to help.\n\nAs we trade only with licensed dealers, could you please send your Florida dealer license number? Once we have it, we will follow up with details on current inventory.\n\nKind regards,\nAlex Morgan\n\n--\nWheelie Wholesale\n100 Sample Street, Orlando, FL 32801\n(407) 555-0100\n\nIf you would rather not hear from us, reply \"STOP\" and we will remove you right away.",
      "needsReview": true
    }
  },
  {
    "id": 3,
    "sender": "Priya Nair <priya.nair@gmail.com>",
    "subject": "Sedans for resale",
    "excerpt": "Looking for 8 sedans per month for resale. Dealer license VI55555.",
    "category": "lead",
    "optOut": false,
    "score": 95,
    "tier": "hot",
    "action": "draft",
    "reasons": [
      "+50 verified VI license",
      "+15 names a vehicle",
      "+15 mentions volume",
      "+5 classified as lead",
      "+10 registered address looks like a real office"
    ],
    "license": {
      "status": "verified",
      "business": "No Website Auto",
      "type": "VI",
      "number": "VI55555",
      "notes": [
        "license VI55555 matches No Website Auto",
        "active, eligible type"
      ]
    },
    "draft": {
      "to": "priya.nair@gmail.com",
      "subject": "Re: Sedans for resale",
      "body": "Hello Priya,\n\nThank you for reaching out to Wheelie Wholesale.\n\nWe have received your note about the vehicles you are looking for and would be glad to help.\n\nTo make sure we match you with the right inventory, could you tell us the makes, models and quantities you are after, and your preferred timing?\n\nKind regards,\nAlex Morgan\n\n--\nWheelie Wholesale\n100 Sample Street, Orlando, FL 32801\n(407) 555-0100\n\nIf you would rather not hear from us, reply \"STOP\" and we will remove you right away.",
      "needsReview": false
    }
  },
  {
    "id": 4,
    "sender": "Tom Hargrove <tom@oldlot.example>",
    "subject": "Buying cars",
    "excerpt": "I want to buy 50 cars. Dealer license VW44444. Do you have any available?",
    "category": "lead",
    "optOut": false,
    "score": 20,
    "tier": "cold",
    "action": "ignore",
    "reasons": [
      "cap 20: license is not active",
      "+15 names a vehicle",
      "+15 mentions volume",
      "+5 classified as lead"
    ],
    "license": {
      "status": "inactive",
      "business": "Old Lot Autos",
      "type": "VW",
      "number": "VW44444",
      "notes": [
        "license VW44444 matches Old Lot Autos",
        "status is Expired"
      ]
    },
    "draft": null
  },
  {
    "id": 5,
    "sender": "Lena Ortiz <lena@citrusford.example>",
    "subject": "Fleet vehicles",
    "excerpt": "We want to buy a fleet of vehicles. License VF33333. Do you have any available?",
    "category": "lead",
    "optOut": false,
    "score": 30,
    "tier": "cold",
    "action": "ignore",
    "reasons": [
      "cap 30: license type VF is not a wholesale buyer",
      "+15 names a vehicle",
      "+15 mentions volume",
      "+5 classified as lead"
    ],
    "license": {
      "status": "ineligible_type",
      "business": "Citrus Ford Sales",
      "type": "VF",
      "number": "VF33333",
      "notes": [
        "license VF33333 matches Citrus Ford Sales",
        "type VF is not VW/VI/VA"
      ]
    },
    "draft": null
  },
  {
    "id": 6,
    "sender": "billing@towco.example",
    "subject": "Invoice INV-2041",
    "excerpt": "Invoice attached. Amount due within 30 days, please remit.",
    "category": "invoice",
    "optOut": false,
    "score": 0,
    "tier": "drop",
    "action": "ignore",
    "reasons": [
      "classified as invoice, not a lead"
    ],
    "license": {
      "status": "no_claim",
      "business": null,
      "type": null,
      "number": null,
      "notes": [
        "no license number, matching domain, or business name"
      ]
    },
    "draft": null
  },
  {
    "id": 7,
    "sender": "deals@promo.example",
    "subject": "WINNER!!!",
    "excerpt": "Act now, guaranteed traffic. Click here!!!",
    "category": "spam",
    "optOut": false,
    "score": 0,
    "tier": "drop",
    "action": "ignore",
    "reasons": [
      "classified as spam, not a lead"
    ],
    "license": {
      "status": "no_claim",
      "business": null,
      "type": null,
      "number": null,
      "notes": [
        "no license number, matching domain, or business name"
      ]
    },
    "draft": null
  },
  {
    "id": 8,
    "sender": "Rae Collins <rae@example.org>",
    "subject": "Re: Wholesale SUVs",
    "excerpt": "STOP",
    "category": "unknown",
    "optOut": true,
    "score": 0,
    "tier": "drop",
    "action": "ignore",
    "reasons": [
      "sender asked to stop"
    ],
    "license": {
      "status": "no_claim",
      "business": null,
      "type": null,
      "number": null,
      "notes": [
        "no license number, matching domain, or business name"
      ]
    },
    "draft": null
  }
];
