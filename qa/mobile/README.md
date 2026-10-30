# Mobile emulation against the published Site

Run `npm ci --ignore-scripts`, `npx --no-install playwright install --with-deps chromium`, then `npm test` in this directory.

The dedicated GitHub Actions workflow runs 12 journeys: widths 360/390/412, portrait and landscape, light and dark. Touch and mobile viewport handling are enabled. Each journey checks live content, touch navigation, CVE search/detail, recovery table contract, page overflow, broken images and uncaught application errors. Screenshots are saved for each section. No source data, production settings or deployments are modified.

This tests the currently **published Site**, not the application source on the PR branch. Record the Actions run, tested URL, observation time and deployed version when reporting results. A green run proves only these automated assertions. Review its screenshots separately before claiming visual QA. It does not certify all accessibility criteria, Safari/iOS, physical devices or performance on slow hardware. No scheduled job is added.
