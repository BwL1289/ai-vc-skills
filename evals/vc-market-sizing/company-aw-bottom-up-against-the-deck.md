# Eval 1: Company AW, a bottom-up market against the deck's TAM, below the plan's target

A test prompt for the `vc-market-sizing` skill. The company is made up. The tool call and the excerpt are from a real
`equity_calculator market_sizing` run with these inputs. The answer states the expected behaviour; it is not a
recorded run, and this eval has not been run in a live session. A run passes when it makes the one tool call below
(field order free, money and percents as strings), leads with the TAM mismatch, quotes the break-even values from the
tool rather than working them out, names the 900 clinics as the shakiest assumption by the tool's swing, and computes
nothing in its own text.

## Prompt

> Help me size our market. We sell practice software to vet clinics. Our market slide says: "A $120M TAM in US
> veterinary software." Independent clinics: 18,000 in the US, from a state licensing list we bought; they pay $400 a
> month, which is what our 45 clinics pay today. 60% of them run one of the two practice-management systems we
> integrate with (from the same list). We plan to win 900 clinics in five years. We reach clinics through two inside
> sales reps and our booth at regional vet conferences. Multi-site groups: 400 groups with 15 locations each, from the
> same list, at $300 a location a month, which is what our 2 groups pay; 50% of them run those systems (from the same
> list), and we plan to win 10% of the groups we can serve. Our 45 clinics and 2 groups bring in $324,000 a year. An industry report from 2025 puts US
> veterinary software at $2.1B; about 40% of it is clinics and groups like ours. The plan needs $8M a year from this
> market in five years. The 900 and the 10% are our estimates. What if our price is lower? We could price clinics
> anywhere from $300 to $500 a month, win 600 to 1,200 clinics, and the groups' share could be 5% to 15%.

## Expected tool call

`equity_market_sizing`, once. The price row is in the call because the founder asked about price; the two other rows
are the founder's ranges for the two Estimates.

```json
{
  "inputs": {
    "segments": [
      {
        "customers": "18000",
        "price": "400",
        "price_period_months": 1,
        "serviceable_percent": "60",
        "obtainable_customers": "900",
        "customers_today": "45"
      },
      {
        "customers": "400",
        "price": "300",
        "price_period_months": 1,
        "units_per_customer": "15",
        "serviceable_percent": "50",
        "obtainable_percent": "10",
        "customers_today": "2"
      }
    ],
    "top_down": [
      {
        "amount": "2100000000",
        "comparable_percent": "40"
      }
    ],
    "sensitivity": [
      {
        "field": "price",
        "segment": 1,
        "values": ["300", "500"]
      },
      {
        "field": "obtainable_customers",
        "segment": 1,
        "values": ["600", "1200"]
      },
      {
        "field": "obtainable_percent",
        "segment": 2,
        "values": ["5", "15"]
      }
    ],
    "annual_revenue_today": "324000",
    "som_years": 5,
    "som_target": "8000000",
    "stated_tam": "120000000"
  }
}
```

## What the calculator prints (excerpt)

```text
  Segment 1: annual revenue per customer                                         $4,800.00  price × 12 / months covered × units × take rate
  Segment 1: SOM customers / today                                              20.000000x  SOM customers / customers today
  Segment 1: new customers a year to SOM                                               171  (SOM customers - customers today) / years, a straight line
  Segment 2: SOM customers                                                              20  customers to win, or SAM customers × share to win
  Total gross spend (before the take rate)                                 $108,000,000.00  sum of the segments
  Total TAM                                                                $108,000,000.00  sum of the segments
  Total SAM                                                                 $62,640,000.00  sum of the segments
  Total SOM customers                                                                  920  sum of the segments
  Total SOM                                                                  $5,400,000.00  sum of the segments
  SOM / annual revenue today                                                    16.666667x  total SOM / annual revenue today
  Top-down 1: bottom-up as a share of it                                          12.8571%  bottom-up TAM / comparable part (a cross-check)
  Top-down 1: difference                                                  $-732,000,000.00  bottom-up TAM - comparable
  TAM: the deck says                                                       $120,000,000.00  given
  TAM: the calculator gives                                                $108,000,000.00  total TAM
  TAM: difference                                                          $-12,000,000.00  computed - stated
  TAM: verdict                                                                    mismatch  within the tolerance is consistent
  Sensitivity 1: SOM swing                                                   $2,160,000.00  SOM high - SOM low
  Sensitivity 1: segment 1 price at SOM = $8,000,000.00                            $640.74  base × (target - other segments' SOM) / this segment's SOM
  Sensitivity 1: segment 1 price at TAM = $840,000,000.00                        $3,788.89  base × (target - other segments' TAM) / this segment's TAM; a cross-check with the top-down figure, not a target
  Sensitivity 2: SOM swing                                                   $2,880,000.00  SOM high - SOM low
  Sensitivity 2: segment 1 customers to win at SOM = $8,000,000.00                1,441.67  base × (target - other segments' SOM) / this segment's SOM
  Sensitivity 3: SOM swing                                                   $1,080,000.00  SOM high - SOM low
  Sensitivity 3: segment 2 share to win at SOM = $8,000,000.00                    34.0741%  base × (target - other segments' SOM) / this segment's SOM
  A VC is likely to ask                                                som_as_percent_only  A SOM is given as a share of the serviceable customers, not as a count of customers; a VC is likely to ask for the customers, the channel and the year behind it
  A VC is likely to ask                                                   som_below_target  The SOM total is below the revenue the plan needs from this market; a VC is likely to ask where the rest comes from
```

## Expected answer

- **Doubted first, computed:** the TAM mismatch leads the first tier. The slide's "A $120M TAM in US veterinary
  software." is $120,000,000.00 stated against $108,000,000.00 from the founder's own inputs, a difference of
  $-12,000,000.00. There is no take rate here, so the tool's gross spend is the same $108,000,000.00: the gap is not a
  gross-spend count. The fix is to put the tool's figure on the slide or show `[the inputs behind the $120M]`.
- `som_below_target` (weakens it): the SOM is $5,400,000.00 against the plan's $8,000,000.00. The answer quotes the
  tool's break-even values, each with the rest at base: a clinic price of $640.74 a month, or 1,441.67 clinics, or a
  34.0741% share of the groups it can serve. It works none of them out itself.
- `som_as_percent_only` (weakens it): the groups' "we plan to win 10% of the groups we can serve" rests on a share.
  The Path lens's objection on that line survives the refute pass as Kept, with `[the channel that reaches multi-site
groups]` and `[the number of groups you plan to win]`.
- A Path objection on "We plan to win 900 clinics in five years." (20.000000x today's clinics, 171 new clinics a year
  in the tool's straight line) is **Dropped, answered** by another line of the material, "We reach clinics through two
  inside sales reps and our booth at regional vet conferences." The answer says to put that channel on the market
  slide.
- **The market table** carries the tool's values per segment and in total: TAM $108,000,000.00, SAM $62,640,000.00, SOM
  $5,400,000.00 (920 customers), and SOM at 16.666667x today's annual revenue.
- **The shakiest assumption** is segment 1's 900 clinics: an Estimate, with the largest swing of the Estimates,
  $2,880,000.00, against $1,080,000.00 for the groups' 10%. Its value at the SOM target is 1,441.67 clinics. The clinic
  price is Own data; its swing, $2,160,000.00, is reported but is not a candidate.
- **Against the top-down figure:** the bottom-up TAM is 12.8571% of the comparable part of the report's figure, a
  difference of $-732,000,000.00, given as a cross-check, never as the market size. The $3,788.89 price at the top-down
  figure is a cross-check only and is never offered as a price to aim for.
- **The ledger** marks the counts, the prices and the 60% and 50% as Own data (a list the founder holds, what
  customers pay today), the 900 and the 10% as Estimates, and the 2025 report as an Estimate until it has a publisher:
  `[the report's publisher and its definition]`.
- It says each figure is one year of revenue at today's prices, quotes the tool's assumption rows with their sources
  (the YC pitch guide for the bottom-up rule; SAM and SOM unverified), says whether the lenses ran as subagents, and
  closes with not investment, legal or tax advice.
