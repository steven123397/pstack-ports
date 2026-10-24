# Install and link

Installation is how a user gets pstack into omp at all: a developer links this checkout so edits are live, and a consumer adds this repo as a marketplace and installs the plugin from the catalog. Both land in the same install directory, and the marketplace registry is what decides whether the catalog is visible.

## Sub-features

- `install-link` points omp's plugin directory at `./pstack-omp` from this checkout.
- `install-marketplace-add` registers this repo as a marketplace by its catalog in `.omp-plugin/marketplace.json`.
- `install-marketplace-resolve` resolves the catalog entry `pstack-omp@pstack-ports` without touching the install.
- `install-registry` reports which marketplaces are configured.

## How to get to it (user POV)

- Run `omp plugin link ./pstack-omp` in the repo.
- Run `omp plugin marketplace add ./` in the repo.
- Run `omp plugin install pstack-omp@pstack-ports` to install from the catalog.
- Run `omp plugin marketplace list` to see configured marketplaces.

## Driving it with omp CLI

Preconditions:

- The working directory is the repo root.
- `pstack-omp/package.json` and `.omp-plugin/marketplace.json` are present.
- No marketplace named `pstack-ports` is configured unless the recipe says otherwise.

- **Link the checkout.** Run `omp plugin link ./pstack-omp`. Stdout is `✔ Linked pstack-omp from ./pstack-omp`. Then `omp plugin list --json` lists `pstack-omp` with `"enabled": true` and `path` under `~/.omp/plugins/node_modules/pstack-omp`.
- **Add the marketplace.** Run `omp plugin marketplace add ./`. Stdout is `✔ Added marketplace: ./`. `omp plugin marketplace list` then shows `pstack-ports  D:\codex_project\pstack-ports` (the absolute path of the repo the catalog was added from).
- **Resolve the catalog entry.** Run `omp plugin install pstack-omp@pstack-ports --dry-run`. Stdout is `[dry-run] Would install pstack-omp@pstack-ports`; the install directory is unchanged.
- **Read the registry.** Run `omp plugin marketplace list` before and after the remove step. With the catalog registered it names `pstack-ports`; on a clean machine it prints `No marketplaces configured` and `Add one with: omp plugin marketplace add <source>`.
- **Proof.** Save `omp plugin list --json`, the marketplace `list` output, and the dry-run line under `artifacts/install/`.

## Gotchas

- `omp plugin install pstack-omp@pstack-ports` without `--dry-run` rewrites `~/.omp/plugins/node_modules/pstack-omp`. On this machine that path is a junction to the checkout, so a session already using the plugin can see files disappear and reappear mid-run. Use `--dry-run` for catalog proof and leave the full install to a moment when no session depends on the plugin.
- `omp plugin marketplace add ./` records the absolute path it was given. Adding the catalog from a second checkout creates a second registration that shadows nothing but confuses `list`.
- `omp plugin uninstall pstack-omp` removes the junction, which also removes the maintainer's live plugin. Only uninstall an install this run created.
- `omp plugin list` has a `marketplace` array as well as `npm`; a link install appears under `npm`. Empty `marketplace` does not mean the plugin is missing.
- The catalog name in `.omp-plugin/marketplace.json` is `pstack-ports` while the plugin inside it is `pstack-omp`; the install target is `<plugin>@<marketplace>`.