# ANDONLIFE-6000

Synthetic Andon Event-Lifecycle Dataset for Exception-Management Research

## About

This dataset is synthetic-by-construction. It was generated programmatically and does not contain real operational, personal, or proprietary manufacturing data. It is intended for research on Andon event lifecycles and exception management.

## Files

- `andonlife6000_events.csv` — event-lifecycle dataset in CSV format
- `andonlife6000_events.json` — event-lifecycle dataset in JSON format
- `generate_eandon_events.py` — generation script
- `DATA-DICTIONARY-AND-VALIDATION.md` — data dictionary and validation notes

## Regeneration

Regenerate the dataset with:

```bash
python3 generate_eandon_events.py
```

## Verification

Expected SHA-256 for `andonlife6000_events.csv`:

```
a04b8f25e39ad40f0d8dde50c08b3ee542fdef41e1e702077a44ab1c8f4849ed
```

## Citation

Zenodo: https://doi.org/10.5281/zenodo.23649337

Related Paper #5: https://doi.org/10.5281/zenodo.23648012

## License

- Data: CC BY 4.0
- Generation script (`generate_eandon_events.py`): MIT
