# The outcome case: a worked call

The vc-investor-memo skill's "The outcome case" section links here. Company BM is made up: a $3,000,000 priced round
at a $12,000,000 pre-money with the pool topped up to 10% in the pre-money (the skill's "The round" section), and
the founder's plan exit of $150,000,000. One `equity_waterfall` call per exit value (step 5), with the whole share
counts from `equity_pool` (step 2) and the new series as its one class (step 4):

```json
{
  "inputs": {
    "exit_amount": "150000000",
    "common_shares": 9500000,
    "classes": [
      {
        "shares": 2714285,
        "invested": "3000000",
        "preference_multiple": "1",
        "rank": 1,
        "participation": "none"
      }
    ]
  }
}
```

Only when the tool is not in the session (search for it by name first), the same call from the command line:

```
equity_calculator waterfall --exit-amount 150000000 --common-shares 9500000 --class "shares=2714285 invested=3000000 preference-multiple=1 rank=1 participation=none"
```

Part of what it prints for Company BM at the founder's plan exit of $150,000,000:

```text
  Class 1: choice                                    converts  converts only when that pays strictly more
  Class 1: payout                              $33,333,326.51  preference paid + part of the rest
  Common stock's payout                       $116,666,673.49  common shares × per-share part
```

The skill's own test checks that the JSON is a valid call, that the command is the same call, and that each line
above is one the calculator prints.
