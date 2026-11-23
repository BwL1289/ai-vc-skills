# Eval 2: Company AX, a marketplace that counted the whole spend, with segments that overlap

A test prompt for the `vc-market-sizing` skill. The company is made up. The tool call and the excerpt are from a real
`equity_calculator market_sizing` run with these inputs. The answer states the expected behaviour; it is not a
recorded run, and this eval has not been run in a live session. A run passes when it makes the three tool calls below
(field order free, money and percents as strings), sets the deck's TAM beside the tool's gross spend, puts the two
overlap flags in the first tier, keeps the Overlap objection on the Texas and Florida line, answers the fee question
with the two whole-company runs' totals, and brings in no fact about pools.

## Prompt

> Check our market slide. We run a marketplace that matches pool owners with pool cleaners, and we keep a 15% fee.
> Slide 4: "$11.7B TAM: every pool in the Sun Belt plus Texas and Florida." Our pool counts come from a dataset of
> county pool permits we compiled. Segment 1: 4,000,000 pools in the Sun Belt states, at $1,800 a year per pool, which
> is what owners on our marketplace pay their cleaner; we can serve 25% of them today (the metro areas where we have
> cleaners, from our own cleaner map) and plan to win 2%. We have 3,000 pools today. Segment 2: 2,500,000 pools in
> Texas and Florida, our two biggest Sun Belt states, at the same $1,800 a year and the same fee; we can serve 30% of
> them (same map) and plan to win 2%. There are 5,200,000 pools in the states we serve or plan to serve. The two 2%
> figures are our estimates. An analyst's 2025 report puts the US pool-service market at $1.1B. What happens if our
> fee is 10% or 20%?

## Expected tool call

`equity_market_sizing`, three times. The main call comes first. The fee is the same in both segments, so it gets one
row per segment, because the founder asked about it; the founder gave no range for either 2%, so neither has a row.
The founder gave no share of the $1.1B that matches their definition, so the top-down figure has no
`comparable_percent`.

```json
{
  "inputs": {
    "segments": [
      {
        "customers": "4000000",
        "price": "1800",
        "price_period_months": 12,
        "take_rate_percent": "15",
        "serviceable_percent": "25",
        "obtainable_percent": "2",
        "customers_today": "3000"
      },
      {
        "customers": "2500000",
        "price": "1800",
        "price_period_months": 12,
        "take_rate_percent": "15",
        "serviceable_percent": "30",
        "obtainable_percent": "2"
      }
    ],
    "top_down": [
      {
        "amount": "1100000000"
      }
    ],
    "sensitivity": [
      {
        "field": "take_rate_percent",
        "segment": 1,
        "values": ["10", "20"]
      },
      {
        "field": "take_rate_percent",
        "segment": 2,
        "values": ["10", "20"]
      }
    ],
    "population": "5200000",
    "stated_tam": "11700000000"
  }
}
```

The founder asked about the fee as a whole, so the two whole-company runs follow: the same inputs with the fee at
each of the founder's values in both segments, and no sensitivity rows. At 10%:

```json
{
  "inputs": {
    "segments": [
      {
        "customers": "4000000",
        "price": "1800",
        "price_period_months": 12,
        "take_rate_percent": "10",
        "serviceable_percent": "25",
        "obtainable_percent": "2",
        "customers_today": "3000"
      },
      {
        "customers": "2500000",
        "price": "1800",
        "price_period_months": 12,
        "take_rate_percent": "10",
        "serviceable_percent": "30",
        "obtainable_percent": "2"
      }
    ],
    "top_down": [
      {
        "amount": "1100000000"
      }
    ],
    "population": "5200000",
    "stated_tam": "11700000000"
  }
}
```

At 20%:

```json
{
  "inputs": {
    "segments": [
      {
        "customers": "4000000",
        "price": "1800",
        "price_period_months": 12,
        "take_rate_percent": "20",
        "serviceable_percent": "25",
        "obtainable_percent": "2",
        "customers_today": "3000"
      },
      {
        "customers": "2500000",
        "price": "1800",
        "price_period_months": 12,
        "take_rate_percent": "20",
        "serviceable_percent": "30",
        "obtainable_percent": "2"
      }
    ],
    "top_down": [
      {
        "amount": "1100000000"
      }
    ],
    "population": "5200000",
    "stated_tam": "11700000000"
  }
}
```

## What the calculator prints (excerpt)

The main call:

```text
  Segment 1: annual revenue per customer                                             $270.00  price × 12 / months covered × units × take rate
  Segment 1: SOM customers / today                                                 6.666667x  SOM customers / customers today
  Total buying customers                                                           6,500,000  sum of the segments
  Total gross spend (before the take rate)                                $11,700,000,000.00  sum of the segments
  Total TAM                                                                $1,755,000,000.00  sum of the segments
  Total SAM                                                                  $472,500,000.00  sum of the segments
  Total SOM customers                                                                 35,000  sum of the segments
  Total SOM                                                                    $9,450,000.00  sum of the segments
  Top-down 1: share matching your definition                                       100.0000%  given
  Top-down 1: bottom-up as a share of it                                           159.5455%  bottom-up TAM / comparable part (a cross-check)
  Top-down 1: difference                                                     $655,000,000.00  bottom-up TAM - comparable
  TAM: the deck says                                                      $11,700,000,000.00  given
  TAM: the calculator gives                                                $1,755,000,000.00  total TAM
  TAM: difference                                                         $-9,945,000,000.00  computed - stated
  TAM: verdict                                                                      mismatch  within the tolerance is consistent
  Sensitivity 1 at 10.0000%: SOM                                               $7,650,000.00  the rest at base
  Sensitivity 1 at 20.0000%: SOM                                              $11,250,000.00  the rest at base
  Sensitivity 1: SOM swing                                                     $3,600,000.00  SOM high - SOM low
  Sensitivity 1: segment 1 take rate at TAM = $1,100,000,000.00                      5.9028%  base × (target - other segments' TAM) / this segment's TAM; a cross-check with the top-down figure, not a target
  Sensitivity 2 at 10.0000%: SOM                                               $8,100,000.00  the rest at base
  Sensitivity 2 at 20.0000%: SOM                                              $10,800,000.00  the rest at base
  Sensitivity 2: SOM swing                                                     $2,700,000.00  SOM high - SOM low
  A VC is likely to ask                                           segments_exceed_population  The segments' customers add up to more than the population they come from, so a buyer is likely counted twice; a VC is likely to ask which segments overlap
  A VC is likely to ask                                             bottom_up_above_top_down  The bottom-up figure is above the comparable part of a top-down figure; a VC is likely to ask whether segments overlap or the definitions differ
  A VC is likely to ask                                                  som_as_percent_only  A SOM is given as a share of the serviceable customers, not as a count of customers; a VC is likely to ask for the customers, the channel and the year behind it
  A VC is likely to ask                                                     no_horizon_given  A SOM is given with no year to reach it; a VC is likely to ask by when
```

The whole-company run at 10%:

```text
  Total TAM                                                  $1,170,000,000.00  sum of the segments
  Total SAM                                                    $315,000,000.00  sum of the segments
  Total SOM                                                      $6,300,000.00  sum of the segments
```

The whole-company run at 20%:

```text
  Total TAM                                                  $2,340,000,000.00  sum of the segments
  Total SAM                                                    $630,000,000.00  sum of the segments
  Total SOM                                                     $12,600,000.00  sum of the segments
```

## Expected answer

- **Doubted first, computed:** the TAM mismatch heads the list, ahead of the tiers, with no tier. Slide 4's "$11.7B
  TAM: every pool in the Sun Belt plus Texas and Florida." is $11,700,000,000.00 stated against $1,755,000,000.00, a difference of
  $-9,945,000,000.00. Beside it, the tool's gross spend is $11,700,000,000.00, the slide's figure: the slide counted
  the whole spend owners pay their cleaners, not the 15% the company keeps. The answer quotes the tool's revenue rule
  and its source, the YC seed fundraising guide's glossary ("the estimated total revenue available for the product(s)
  you are selling"), and the fix is a TAM of the revenue kept.
- `segments_exceed_population` and `bottom_up_above_top_down` are in the first tier, ends the meeting. The Overlap
  lens's objection on "2,500,000 pools in Texas and Florida, our two biggest Sun Belt states" survives the refute pass
  as Kept: the founder's own words put those pools inside segment 1, and no line says segment 1 leaves them out. The
  fix is `[the Sun Belt pool count without Texas and Florida]`.
- Against the top-down figure: the bottom-up TAM is 159.5455% of the analyst's figure, a difference of
  $655,000,000.00, a cross-check, never the market size; segment 1's fee of 5.9028% at which the TAM would equal it,
  with segment 2 at 15%, is a cross-check only, never a fee to aim for. The founder gave no share of the $1.1B that
  matches their definition, so the tool compared the whole figure (it prints 100.0000% as given): the answer says so
  beside the 159.5455% and asks `[the share of the $1.1B that matches your Sun Belt definition]`. The flag holds
  whatever that share is, since a whole figure is the largest comparable part. The report has no publisher, so it is
  an Estimate: `[the report's publisher and its definition]`.
- `som_as_percent_only` (weakens it) becomes `[the pools you plan to win in each segment, and the channel]`, and
  `no_horizon_given` (minor) becomes `[the year you expect to reach 35,000 pools]`.
- The fee rows, each with the other segment's fee at 15%: segment 1's fee moves the SOM to $7,650,000.00 at 10% and
  $11,250,000.00 at 20%, a swing of $3,600,000.00; segment 2's to $8,100,000.00 and $10,800,000.00, a swing of
  $2,700,000.00. Neither row is quoted as the whole company's fee at 10% or 20%: the tool moves one segment at a time.
- **The whole-company case** answers the founder's question. With the fee at 10% in both segments, the run's totals
  are a TAM of $1,170,000,000.00, a SAM of $315,000,000.00 and a SOM of $6,300,000.00; at 20%, $2,340,000,000.00,
  $630,000,000.00 and $12,600,000.00. Those are the runs' totals, quoted; their flags and top-down shares are not new
  findings, and no difference between the two runs is worked out.
- The ledger marks the pool counts, the population and the serviceable shares as Own data (a dataset and a map the
  founder holds), the price and the fee as Own data, and the two 2% shares as Estimates. Those have no range, so no
  shakiest assumption is named: the answer asks for `[a low and a high value for each 2%]`. The 3,000 pools today sit
  in segment 1's sentence and segment 2 has none, so the answer asks
  `[the pools you serve today in Texas and Florida]`.
- It brings in no fact about pools, cleaners or the Sun Belt from outside the founder's message, computes nothing in
  its own text, says each figure is one year of revenue at today's prices, and closes with not investment, legal or
  tax advice.
