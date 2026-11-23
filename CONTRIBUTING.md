# Contributing

Thanks for helping. Ideas for new skills, fixes to the math, clearer docs: all welcome.

## Requesting a skill

Open an issue with the [skill request](https://github.com/BwL1289/ai-vc-skills/issues/new?template=skill_request.yml)
form: the question a founder asks, an example, and the source you would trust for the answer.

## Reporting a wrong number

Open a [bug report](https://github.com/BwL1289/ai-vc-skills/issues/new?template=bug_report.yml) with the exact command
or prompt, what it printed, and the number you expected with its source. A wrong number is the most important kind of
bug here.

## Adding a skill

1. Copy the template: `cp -r template skills/<your-skill-name>`, then set `name:` in its `SKILL.md` to the folder name.
2. Write the `SKILL.md`. [docs/writing-a-skill.md](docs/writing-a-skill.md) has the rules: the frontmatter, a
   description that says when to use the skill, steps that get every number from a tool, and the limits.
3. Add a row to the skills table in the [README](README.md#skills) and a line under "Unreleased" in
   [CHANGELOG.md](CHANGELOG.md).
4. Run the checks below, then open a pull request.

The plugin picks up every folder in `skills/` by itself; there is nothing to register.

## Changing the calculator

The math lives in [`equity_calculator/`](equity_calculator/). Every formula comes with its source in the package
README's [The formulas](equity_calculator/README.md#the-formulas); a change to a formula needs the source that justifies
it, a test with a worked example, and an update to that section. Numbers are exact fractions: never introduce floating
point into a result.

## Checks

Set up a clone as in [docs/install.md](docs/install.md#from-a-clone), then:

```
pip install --group dev
pre-commit install
python scripts/validate_skills.py
pre-commit run --all-files
pytest
claude plugin validate .
```

CI runs the validator, the pre-commit hooks and pytest on every pull request.

## Quality checklist for a skill

- [ ] The founder is the user: the skill answers a founder's question, and an investor's view appears only as a lens
      in a review, never as the role the skill plays.
- [ ] The description says what the skill does and when to use it, in the words users actually type.
- [ ] Every number comes from a tool or the user's document; the skill says so.
- [ ] Missing inputs are asked for, never guessed.
- [ ] The skill states its limits, including that it is not investment, legal or tax advice.
- [ ] No named investor or firm is imitated; frameworks are named, people are not.
- [ ] `SKILL.md` is under 500 lines; long reference material sits in files beside it.

## License

By contributing you agree that your contribution is licensed under the repository's [MIT license](LICENSE).
