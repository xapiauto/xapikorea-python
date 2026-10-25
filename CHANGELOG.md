# Changelog

## 0.2.1

- Simplify the package README title to "XAPI Korea Python SDK".

## 0.2.0

- Add Encar, KB ChaChaCha and combined searches, retaining listing source,
  original listing URL, successful sources and partial-source errors.
- Add EUR price bounds, mileage, sale type, color, trim, generation, badge group
  and badge search filters.
- Add `count`, `get_filters`, `get_makes`, `get_models`, `get_trims`,
  `get_insurance`, `get_images` and `get_similar` methods and response models.
- Pass marketplace source through vehicle requests; existing calls still
  default to Encar.
- Preserve sale type, lease/rent terms and contract/listing statuses in search
  results, and source and statuses in vehicle details.
- Accept missing or null optional listing fields, including KB listings
  without an Encar URL. Default metadata for older Encar responses.

## 0.1.0

- Initial synchronous client with account information, Encar search, vehicle
  details and inspection reports.
